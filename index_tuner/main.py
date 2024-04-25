import itertools
import random
import psycopg2
import os
from dotenv import load_dotenv
import time

load_dotenv()

host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

try:
    conn = psycopg2.connect(
        host=host,
        database=database,
        user=user,
        password=password
    )
except (Exception, psycopg2.DatabaseError) as error:
    print(error)
    exit()

def getcost(query,indexes):
    if indexes == []:
        return query["cost"]
    else:
        cost = query["cost"]
        for index in indexes:
            if index in query["columns_accessed"]:
                random_val = random.random() + random.randint(0,1)
                cost = cost * random_val
        return cost

def getreplacmentcost(index):
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT type, size FROM index_info WHERE field_name = %s;
        """, (index,))
        row = cur.fetchone()
        # type | size
        if row[0] == 1:
            # normalize the cost of building replacement indexes
            return float(row[1]) * random.random()
        else:
            return 0
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()

def update_types(indexes, type):
    try:
        cur = conn.cursor()
        if len(indexes) == 0:
            return
        cur.execute("""
            UPDATE index_info SET type = %s WHERE field_name in %s;
        """, (type, tuple(indexes)))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()

def update_profits(profit, indexes):
    print("Profit: ", profit)
    print("Indexes: ", indexes)
    print("")
    try:
        cur = conn.cursor()
        if len(indexes) == 0:
            return
        cur.execute("""
            SELECT * FROM index_info WHERE field_name in %s;
        """, (indexes,))
        rows = cur.fetchall()
        print("Rows: ", rows)
        # rel_name | field_name | profit | type | size 
        profit_sum = 0
        for row in rows:
            # row[2] type is decimal.Decimal convert to float
            profit_sum += float(row[2])
        print("Profit sum: ", profit_sum)
        for row in rows:
            if row[2] == 0:
                print("Profit sum is 0")
                updated_profit = profit
            else:
                print("Profit sum is not 0")
                updated_profit = float(row[2]) + (profit * (float(row[2]) / profit_sum))
            cur.execute("""
                UPDATE index_info SET profit = %s WHERE field_name = %s;
            """, (updated_profit, row[1]))
        conn.commit()
        print("Profits updated")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()

def update_indexes(indexes, index_type):
    if not indexes:
        return

    cur = None
    try:
        cur = conn.cursor()
        if index_type == 1:
            # Materialized indexes
            for index in indexes:
                cur.execute("CREATE INDEX ON tuner (%s);" % index)
            conn.commit()
            print("Materialized indexes created")
        elif index_type == 0:
            # Replacement indexes
            for index in indexes:
                cur.execute("DROP INDEX IF EXISTS tuner_%s_idx;" % index)
            conn.commit()
            print("Replacement indexes dropped")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur:
            cur.close()



def calc_profit(query, indexes):
    base_cost = getcost(query,[])
    index_set_cost = getcost(query,indexes)
    return base_cost - index_set_cost

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


def main():
    queries = [
        {"query": "SELECT * FROM tuner;", 
        "cost": 10,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT value FROM tuner;", 
        "cost": 8,
        "columns_accessed": ["value"]},
        {"query": "SELECT * FROM tuner WHERE value = 'specific_value';", 
        "cost": 12,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT * FROM tuner WHERE value LIKE '%substring%';", 
        "cost": 15,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT DISTINCT value FROM tuner;", 
        "cost": 10,
        "columns_accessed": ["value"]},
        {"query": "SELECT * FROM tuner ORDER BY value ASC;", 
        "cost": 12,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT * FROM tuner ORDER BY id LIMIT 5;", 
        "cost": 13,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT * FROM tuner WHERE id LIKE 'specific_char%';", 
        "cost": 11,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT * FROM tuner WHERE value2 IS NOT NULL;", 
        "cost": 9,
        "columns_accessed": ["id", "value", "value2"]},
        {"query": "SELECT * FROM tuner WHERE LENGTH(value) > 5;", 
        "cost": 14,
        "columns_accessed": ["id", "value", "value2"]}
    ]

    SIZE = 200
    MIN_DIFF = 0.5
    # for query in queries:
    #     print("Query: ", query["query"])
    #     print("Cost: ", query["cost"])
    #     print("Columns accessed: ", query["columns_accessed"])
    #     print("")

    #     base_cost = getcost(query,[])
    #     print("Base cost: ", base_cost)

    #     permutations = []
    #     for i in range(1,len(query["columns_accessed"])+1):
    #         permutations += list(itertools.combinations(query["columns_accessed"], i))
    #     print("Permutations: ", permutations)
    #     print("")

    #     costs = [] 
    #     for index_set in permutations:
    #         index_set_cost = getcost(query,index_set)
    #         print("Index set: ", index_set)
    #         print("Cost: ", index_set_cost)
    #         print("")
    #         costs.append(index_set_cost)

    #     for index_set in permutations:
    #         print("Index set: ", index_set)
    #         print("Cost: ", costs[permutations.index(index_set)])
    #         print("")        

    #     print("Optimal index set: ", permutations[costs.index(min(costs))])
    #     print("Optimal cost: ", min(costs))

    for query in queries:
        localOptimalStrategy(query, SIZE, MIN_DIFF)
        time.sleep(5)

if __name__ == '__main__':
    main()