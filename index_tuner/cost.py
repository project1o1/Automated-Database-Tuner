import random
import psycopg2
from database import connect

conn = connect()

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

def calc_profit(query, indexes):
    base_cost = getcost(query,[])
    index_set_cost = getcost(query,indexes)
    return base_cost - index_set_cost
