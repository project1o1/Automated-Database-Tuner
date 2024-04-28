import psycopg2
import itertools
from database import connect
from update import update_types, update_profits, update_indexes
from cost import getreplacmentcost, calc_profit
import requests
import logging
from graph import plot_graph
import threading
conn = connect()
batch_size = 5      
all_optimal_indexes = []
all_graph_y_points = []
sumation = 0
def format_columns_for_model(columns):
    # user_id-username-age-last_name-password-email username-last_name username-first_name password-username-first_name-email-age
    formatted_columns = ""
    for column in columns:
        formatted_columns += column + "-"
    return formatted_columns[:-1]


def find_optimal_index_set(query):
    print("finding optimal index set")
    optimal_indexes = []
    profit = 0
    indexable_columns = query["columns"]
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
    # formatted_indexable_columns = format_columns_for_model(indexable_columns)
    # url = "http://172.16.15.54:5000"
    # payload = {
    #     "columns": formatted_indexable_columns
    # }
    # response = requests.post(url, json=payload)
    # permutations = response.json()["permutations"]

    for i in range(1,len(indexable_columns)+1):
        permutations += list(itertools.combinations(indexable_columns, i))
    print("Permutations: ", permutations)
    print("indexable_columns: ", indexable_columns)
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
    print("SIZE: ", SIZE)
    print("MIN_DIFF: ", MIN_DIFF)
    global batch_size
    global all_optimal_indexes
    print(batch_size)
    global sumation
    global all_graph_y_points
    # if batch_size == 5:
    try:
        all_optimal_indexes.append(format_columns_for_model(query["columns"]))
        sumation += float(query["cost"])
        if batch_size > 0:
            batch_size -= 1
            print("Waiting for more queries")
            return
        else:
            permutations = []
            all_graph_y_points.append(sumation)
            plot_graph(all_graph_y_points)
            # plot_graph(all_graph_y_points)
            # threading.Thread(target=plot_graph, args=(all_graph_y_points,)).start()
            sumation = 0
            formatted_indexable_columns = ""
            for columns in all_optimal_indexes:
                formatted_indexable_columns += columns + " "
            url = "http://172.16.15.54:5000/generate/"
            payload = {
                "no_of_tokens": 100,
                "no_max": 5,
                "queries": formatted_indexable_columns
            }
            headers = {
                "Content-Type": "application/json"
            }
            print("Sending request to model")
            response = requests.post(url, json=payload, headers=headers)
            logging.info("Sent request to model")
            response = requests.post(url, json=payload)
            permutations = response.json()
            print("Permutations: ", permutations)
            best_columns = []
            for q in permutations:
                print("Query: ", q)
                best_columns.append(q[0])
            print("Best columns: ", best_columns)
            query["columns"] = best_columns
            
            all_optimal_indexes = []
            batch_size = 5
        optimal_indexes, profit = find_optimal_index_set(query)
        print("-----------------------------------")
        print("Optimal indexes: ", optimal_indexes)
        print("Profit: ", profit)
        print("-----------------------------------")
        update_profits(profit, optimal_indexes,conn)
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
    except Exception as e:
        print("Error: ", e)
        return

# def render_graph(y_points):
#     import matplotlib.pyplot as plt
#     x_points = [i for i in range(1, len(y_points)+1)]
#     plt.plot(x_points, y_points)
#     plt.xlabel("Batch")
#     plt.ylabel("Execution Time")
#     plt.title("Execution Time vs Batch")
#     plt.show()
#     plt.savefig("Execution Time vs Batch.png")
#     plt.close()