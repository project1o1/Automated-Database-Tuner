import psycopg2
import itertools
from database import connect
from update import update_types, update_profits, update_indexes
from cost import getreplacmentcost, calc_profit

conn = connect()

def find_optimal_index_set(query):
    print("finding optimal index set")
    optimal_indexes = []
    profit = 0
    indexable_columns = query["columns_accessed"]
    try:
        cur = conn.cursor()
        print("Inserting columns into index_info table")
        # insert the columns into the index_info table if not already present
        for column in indexable_columns:
            cur.execute("""
                INSERT INTO index_info (rel_name, field_name, profit, type, size)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (rel_name,field_name) DO NOTHING;
            """, ("tuner", column, 0, 0, 100))
        conn.commit()
        print("Columns inserted into index_info table") 
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
    print("creating permutations")
    permutations = []
    for i in range(1,len(indexable_columns)+1):
        permutations += list(itertools.combinations(indexable_columns, i))
    for index_set in permutations:
        print("Index set: ", index_set)
        index_set_profit = calc_profit(query, index_set)
        if index_set_profit > profit:
            profit = index_set_profit
            optimal_indexes = index_set
    print("Optimal indexes: ", optimal_indexes, "Profit: ", profit)
    return optimal_indexes, profit

def getMaterializedIndexes():
    materialized_indexes = []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM index_info WHERE type = 1;
        """)
        rows = cur.fetchall()
        # rel_name | field_name | profit | type | size
        materialized_indexes = rows
        print("Materialized indexes: ", materialized_indexes)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
    return materialized_indexes


def findReplacement(indexes,MAX_SIZE):
    materialized_indexes = []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM index_info WHERE type = 1;
        """)
        rows = cur.fetchall()
        # rel_name | field_name | profit | type | size
        materialized_indexes = rows
        print("Replacement indexes: ", materialized_indexes)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()

    size_sum = 0
    try:
        cur = conn.cursor()
        if len(indexes) == 0:
            return [], 0
        cur.execute("""
            SELECT size FROM index_info WHERE field_name in %s;
        """, (indexes,))
        rows = cur.fetchall()
        # size
        for row in rows:
            size_sum += row[0]
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
    

    #sort materialized_indexes by profit
    materialized_indexes = sorted(materialized_indexes, key=lambda x: x[2], reverse=True)
    total_sum = sum(index[4] for index in materialized_indexes)
    replacable_size = (size_sum + total_sum) - MAX_SIZE
    replacement_indexes = []
    if replacable_size <= 0:
        return [], total_sum
    for index in materialized_indexes:
        if replacable_size > 0:
            replacement_indexes.append(index[1])
            replacable_size -= index[4]
            total_sum -= index[4]
        else:
            break
    print("Replacement indexes: ", replacement_indexes)
    return replacement_indexes, total_sum

def localOptimalStrategy(query, SIZE, MIN_DIFF):
    print("Query: ", query["query"])
    optimal_indexes, profit = find_optimal_index_set(query)
    update_profits(profit, optimal_indexes)
    print("Profit: ", profit)
    replacement_indexes,mat_size = findReplacement(optimal_indexes, SIZE)

    materialized_indexes = getMaterializedIndexes()

    union_list = list(optimal_indexes) + materialized_indexes
    replacement_indexes = set(replacement_indexes)
    union_list = set(union_list) - replacement_indexes
    # Calculate the profit difference between the new index set (optimal union replacement) and the original optimal set
    union_profit = calc_profit(query, list(union_list))
    original_profit = calc_profit(query, materialized_indexes)
    profit_diff = union_profit - original_profit

    if profit_diff <= 0:
        print("No profit difference")
        return
    
    print("Profit diff: ", profit_diff)
    print("Mat size: ", mat_size)
    print("Size: ", SIZE)
    
    # Calculate the total cost of building replacement indexes
    replacement_cost = sum(getreplacmentcost(index) for index in replacement_indexes)

    print("Replacement cost: ", replacement_cost)
    if profit_diff - replacement_cost > MIN_DIFF:
        print("Updating types")
        print("Optimal indexes: ", len(optimal_indexes))
        update_types(optimal_indexes, 1)
        print("Replacement indexes: ", len(replacement_indexes))
        update_types(replacement_indexes, 0)

        print("Updating indexes to database")
        update_indexes(optimal_indexes, 1)
        update_indexes(replacement_indexes, 0)

    print("")
    print("-----------------------------------")

