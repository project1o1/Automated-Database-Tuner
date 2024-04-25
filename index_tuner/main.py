from strategy import localOptimalStrategy
import time

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
    for query in queries:
        start = time.time()
        localOptimalStrategy(query, SIZE, MIN_DIFF)
        end = time.time()
        print("Time: ", end - start)
        print("--------------------------------------------------------------------------------------------------------------------------------------------")

if __name__ == '__main__':
    main()