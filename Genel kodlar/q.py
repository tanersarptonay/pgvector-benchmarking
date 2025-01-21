from db_config import *

import psycopg2
import random
import time
from concurrent.futures import ThreadPoolExecutor

# Query workload settings
NUM_QUERIES = 100  # Total number of queries to run
CONCURRENT_CLIENTS = 10  # Number of concurrent clients
DIMENSIONS = 10  # Vector dimension

QUERY_CONFIGS = [
    (100, 10),  # (NUM_QUERIES, CONCURRENT_CLIENTS)
    # (1000, 50),
    # (5000, 100),
    # (10000, 200)
]
# 

# Connect to PostgreSQL
def run_query():
    query_vector = [round(random.uniform(0, 1), 2) for _ in range(DIMENSIONS)]
    query_vector_str = "[" + ",".join(map(str, query_vector)) + "]"  # Convert list to PostgreSQL array format
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        start_time = time.time()
        cursor.execute(
            """
            SELECT id, embedding <-> %s::VECTOR AS distance
            FROM items
            ORDER BY distance
            LIMIT 5
            """,
            [query_vector_str],
        )
        results = cursor.fetchall()
        elapsed_time = time.time() - start_time
        conn.close()
        return elapsed_time, results
    except Exception as e:
        print("Error running query:", e)
        return None, None


# Run queries concurrently
def run_benchmark():
    latencies = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_CLIENTS) as executor:
        futures = [executor.submit(run_query) for _ in range(NUM_QUERIES)]
        for future in futures:
            result = future.result()
            if result:
                latency, _ = result
                if latency is not None:
                    latencies.append(latency)

    return latencies

if __name__ == "__main__":
    for num_queries, num_clients in QUERY_CONFIGS:
        print(f"\nRunning benchmark with {num_queries} queries and {num_clients} clients...")
        NUM_QUERIES = num_queries
        CONCURRENT_CLIENTS = num_clients
        latencies = run_benchmark()
        if latencies:
            print(f"Average latency: {sum(latencies) / len(latencies):.4f} seconds")
            print(f"Min latency: {min(latencies):.4f} seconds")
            print(f"Max latency: {max(latencies):.4f} seconds")
        else:
            print("No results collected.")

