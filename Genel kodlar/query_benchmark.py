#!/usr/bin/env python3

from db_config import *
from try_connection import try_connection
import psycopg2
import random
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import logging
import csv

current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

# Query workload settings
QUERY_CONFIGS = [
    {"num_queries": 100, "num_clients": 10},
    #{"num_queries": 1000, "num_clients": 50},
    #{"num_queries": 5000, "num_clients": 100},
]
TABLES = [
    "items_no_index", 
    "items_ivfflat", 
    "items_hnsw"
]
DIMENSIONS = 128
RESULTS_FILE = f"benchmark_results_{current_time}.csv"

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"query_benchmark_{current_time}.log"), 
        logging.StreamHandler()
    ]
)


# Connect to PostgreSQL
def run_query(table_name):
    query_vector = [round(random.uniform(0, 1), 2) for _ in range(DIMENSIONS)]
    query_vector_str = "[" + ",".join(map(str, query_vector)) + "]"  # Convert list to PostgreSQL array format
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        cursor = conn.cursor()
        start_time = time.time()
        cursor.execute(
            f"""
            SELECT id, embedding <-> %s::VECTOR AS distance
            FROM {table_name}
            ORDER BY distance
            LIMIT 5;
            """,
            [query_vector_str],
        )
        results = cursor.fetchall()
        elapsed_time = time.time() - start_time
        conn.close()
        return elapsed_time, results, True  # Mark success
    except Exception as e:
        logging.error(f"Error running query on {table_name}: {e}")
        return None, None, False  # Mark failure

# Run queries concurrently
def run_benchmark(table_name, num_queries, num_clients):
    latencies = []
    success_count = 0
    failure_count = 0
    logging.info(f"Starting benchmark on table: {table_name} with {num_queries} queries and {num_clients} clients")
    with ThreadPoolExecutor(max_workers=num_clients) as executor:
        futures = [executor.submit(run_query, table_name) for _ in range(num_queries)]
        for future in futures:
            result = future.result()
            if result:
                latency, _, success = result
                if success:
                    success_count += 1
                    latencies.append(latency)
                else:
                    failure_count += 1

    # Calculate success/failure rates
    success_rate = (success_count / num_queries) * 100 if num_queries > 0 else 0
    failure_rate = (failure_count / num_queries) * 100 if num_queries > 0 else 0

    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        throughput = len(latencies) / sum(latencies)
        logging.info(
            f"Results for {table_name}: "
            f"Avg Latency: {avg_latency:.4f}s, Min Latency: {min_latency:.4f}s, Max Latency: {max_latency:.4f}s, "
            f"Throughput: {throughput:.2f} queries/sec, Success Rate: {success_rate:.2f}%, Failure Rate: {failure_rate:.2f}%"
        )
        return avg_latency, min_latency, max_latency, throughput, success_rate, failure_rate
    else:
        logging.warning(f"No results collected for {table_name}")
        return None, None, None, None, success_rate, failure_rate

# Save results to CSV
def save_results_to_csv(results):
    with open(RESULTS_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Table Name", "Num Queries", "Num Clients", "Avg Latency (s)", "Min Latency (s)", "Max Latency (s)", "Throughput (queries/sec)", "Success Rate (%)", "Failure Rate (%)", "Elapsed Time (s)"])
        for result in results:
            writer.writerow(result)
    logging.info(f"Results saved to {RESULTS_FILE}")

# Main function
if __name__ == "__main__":
    try_connection()

    all_results = []

    absolute_start_time = time.time()

    for table_name in TABLES:
        for config in QUERY_CONFIGS:
            num_queries = config["num_queries"]
            num_clients = config["num_clients"]

            exp_start_time = time.time()

            # Run benchmark
            avg_latency, min_latency, max_latency, throughput, success_rate, failure_rate = run_benchmark(table_name, num_queries, num_clients)
            
            exp_elapsed_time = time.time() - exp_start_time
            logging.info(f"Experiment on {table_name} with {num_queries} queries and {num_clients} clients took {exp_elapsed_time:.2f} seconds, or {exp_elapsed_time / 60:.2f} minutes")
            if avg_latency is not None:
                all_results.append([table_name, num_queries, num_clients, avg_latency, min_latency, max_latency, throughput, success_rate, failure_rate, exp_elapsed_time])

    total_elapsed_time = time.time() - absolute_start_time

    logging.info(f"Total benchmarking time: {total_elapsed_time:.2f} seconds, or {total_elapsed_time / 60:.2f} minutes")

    # Save results to CSV
    save_results_to_csv(all_results)
    print("Benchmarking completed. Check the log file for detailed results.")
