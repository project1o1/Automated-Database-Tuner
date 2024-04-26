import psycopg2
from database import connect

conn = connect()

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

def update_profits(profit, indexes, conn):
    print("Profit: ", profit)
    print("Indexes: ", indexes)
    print("")
    cur = None
    try:
        cur = conn.cursor()
        if len(indexes) == 0:
            return
        cur.execute("""
            SELECT * FROM index_info WHERE field_name in %s;
        """, (tuple(indexes),))
        rows = cur.fetchall()
        print("Rows: ", rows)
        # rel_name | field_name | profit | type | size 
        profit_sum = sum(float(row[2]) for row in rows)
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
    except psycopg2.DatabaseError as error:
        print(error)
        conn.rollback()  # Rollback transaction in case of error
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