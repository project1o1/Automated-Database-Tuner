import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

host = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

def connect():
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
    return conn