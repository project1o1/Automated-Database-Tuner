# import random
# with open("text.txt", "w") as file:
#     alphas = ["a", "b", "c", "d", "e", "f"]
#     print("Writing")
#     for i in range(6000000):
#         file.write(random.choice(alphas))
#     print("Done")

import os
from dotenv import load_dotenv
import psycopg2
import random
import string
from index_tuner.database import connect

def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def populate_tuner_table():
    conn = connect()
    cur = conn.cursor()
    try:
        for _ in range(1000):  # Adjust the range to the desired number of dummy records
            id_val = generate_random_string(32)
            value_val = generate_random_string(32)
            value2_val = generate_random_string(10)
            cur.execute("INSERT INTO tuner (id, value, value2) VALUES (%s, %s, %s)", (id_val, value_val, value2_val))
            conn.commit()
        print("Dummy data inserted successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error inserting dummy data:", error)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

populate_tuner_table()
