from db_connector import DBConnector
import random
import time
from concurrent.futures import ThreadPoolExecutor
import logging
import csv
from datetime import datetime
import os

class BenchmarkRunner:
    """Manages the benchmarking process."""
    def __init__(self, tables, query_configs, dimensions, db_config):
        self.tables = tables
        self.query_configs = query_configs
        self.dimensions = dimensions
        self.results = []
        self.executor = None
        self.db = DBConnector(db_config)

        # Create a folder to store logs and results
        if not os.path.exists("results"):
            os.makedirs("results")
        
        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        benchmark_result_folder = os.path.join("results", "benchmark_"+current_time)

        if not os.path.exists(benchmark_result_folder):
            os.makedirs(benchmark_result_folder)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(benchmark_result_folder, f"query_benchmark_{current_time}.log")),
                logging.StreamHandler()
            ]
        )
        self.results_file = os.path.join(benchmark_result_folder, f"benchmark_results_{current_time}.csv") 

    def generate_query_vector(self):
        """Generate a random query vector."""
        return [round(random.uniform(0, 1), 2) for _ in range(self.dimensions)]

    def run_query(self, table_name):
        """Execute a single query."""
        query_vector = self.generate_query_vector()
        query_vector_str = "[" + ",".join(map(str, query_vector)) + "]"

        try:
            cursor = self.db.get_cursor()
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
            cursor.fetchall()
            elapsed_time = time.time() - start_time
            return elapsed_time, True  # Success
        except Exception as e:
            logging.error(f"Error running query on {table_name}: {e}")
            return None, False  # Failure

    def run_benchmark(self, table_name, num_queries, num_clients):
        """Run the benchmark for a table."""
        single_benchmark_start_time = time.time()

        latencies = []
        success_count = 0
        failure_count = 0

        logging.info(f"Starting benchmark for {table_name} with {num_queries} queries and {num_clients} clients.")

        self.executor = ThreadPoolExecutor(max_workers=num_clients)
        futures = [self.executor.submit(self.run_query, table_name) for _ in range(num_queries)]
        for future in futures:
            result = future.result()
            if result:
                latency, success = result
                if success:
                    success_count += 1
                    latencies.append(latency)
                else:
                    failure_count += 1

        success_rate = (success_count / num_queries) * 100 if num_queries > 0 else 0
        failure_rate = (failure_count / num_queries) * 100 if num_queries > 0 else 0

        avg_latency = sum(latencies) / len(latencies) if latencies else None
        max_latency = max(latencies) if latencies else None
        min_latency = min(latencies) if latencies else None
        throughput = len(latencies) / sum(latencies) if latencies else None

        single_benchmark_elapsed_time = time.time() - single_benchmark_start_time


        logging.info(f"Results for {table_name}: "
                     f"Avg Latency: {avg_latency:.4f}s, Throughput: {throughput:.2f} q/s, "
                     f"Success Rate: {success_rate:.2f}%, Failure Rate: {failure_rate:.2f}%, Elapsed Time: {single_benchmark_elapsed_time:.2f}s")

        return {
            "table_name": table_name,
            "num_queries": num_queries,
            "num_clients": num_clients,
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "throughput": throughput,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "elapsed_time": single_benchmark_elapsed_time,
        }

    def save_results(self):
        """Save results to a CSV file."""
        with open(self.results_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=self.results[0].keys())
            writer.writeheader()
            writer.writerows(self.results)
        logging.info(f"Results saved to {self.results_file}.")

    def shutdown(self):
        """Shut down resources."""
        if self.executor:
            self.executor.shutdown(wait=False)
            logging.info("Thread pool executor shut down.")
        self.db.close()
        logging.info("Database connection closed.")

    def start(self):
        """Run the benchmarks for all configurations."""
        try:
            self.db.connect()
            for config in self.query_configs:
                for table in self.tables:
                    result = self.run_benchmark(
                        table_name=table,
                        num_queries=config["num_queries"],
                        num_clients=config["num_clients"],
                    )
                    self.results.append(result)

            self.save_results()
        finally:
            self.shutdown()
