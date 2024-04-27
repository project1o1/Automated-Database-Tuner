import random
import psycopg2
from database import connect
import requests

conn = connect()

def getcost(query,indexes):
    print("get cost",query,indexes)
    print(query)
    if indexes == []:
        return float(query["cost"])
    else:
        try:
            # request server for cost
            url = "http://172.16.12.214:5000/cost"
            payload = {
                "query": query,
                "indexes": indexes
            }
            response = requests.post(url, json=payload)
            cost = response.json()["cost"]
            return cost
        except (Exception, psycopg2.DatabaseError) as error:
            cost = float(query["cost"])
            for index in indexes:
                if index in query["columns"]:
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
            # return float(row[1]) * random.random()
            url = "http://172.16.12.214:5000/replacement_cost"
            payload = {
                "index": index
            }
            response = requests.post(url, json=payload)
            cost = response.json()["cost"]
            return cost
        else:
            return 0
    except (Exception, psycopg2.DatabaseError) as error:
        # print(error)
        return 0
    finally:
        if cur is not None:
            cur.close()

def calc_profit(query, indexes):
    base_cost = getcost(query,[])
    index_set_cost = getcost(query,indexes)
    return base_cost - index_set_cost
