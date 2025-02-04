from db_connector import DBConnector
import random
import time
import logging
import csv
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor
import statistics

class BenchmarkRunner:
    """Manages the benchmarking process."""

    def __init__(self, tables, query_configs, dimensions, db_config):
        self.tables = tables
        self.query_configs = query_configs
        self.dimensions = dimensions
        self.results = []
        self.db = DBConnector(db_config)
        self.executor = None

        # Create a folder to store logs and results
        if not os.path.exists("results"):
            os.makedirs("results")

        current_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        self.benchmark_result_folder = os.path.join("results", f"benchmark_{current_time}")

        if not os.path.exists(self.benchmark_result_folder):
            os.makedirs(self.benchmark_result_folder)

        # Set up logging
        log_file_path = os.path.join(self.benchmark_result_folder, f"query_benchmark_{current_time}.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file_path),
                logging.StreamHandler()
            ]
        )
        self.results_file = os.path.join(self.benchmark_result_folder, f"benchmark_results_{current_time}.csv")

    def generate_query_vector(self):
        """Generate a random query vector."""
        return [round(random.uniform(0, 1), 2) for _ in range(self.dimensions)]

    def run_query(self, table_name):
        """Execute a single query and measure elapsed time."""
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
            return elapsed_time, True  # (latency, success_boolean)
        except Exception as e:
            logging.error(f"Error running query on {table_name}: {e}")
            return None, False  # Failure

    def compute_latency_stats(self, latencies):
        """Compute extended latency stats from a list of latencies."""
        if not latencies:
            return {
                "avg_latency": None,
                "min_latency": None,
                "max_latency": None,
                "p50_latency": None,
                "p90_latency": None,
                "p95_latency": None,
                "p99_latency": None,
                "stddev_latency": None,
                "throughput": None
            }

        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        # Use Python's built-in statistics module to get stdev
        stddev_latency = statistics.pstdev(latencies)  # population stdev

        # For percentiles, you can use statistics.quantiles in Python 3.8+
        sorted_lats = sorted(latencies)
        def percentile(p):
            # position of percentile in sorted array
            idx = (len(sorted_lats) - 1) * (p / 100)
            lower = int(idx)
            upper = min(lower + 1, len(sorted_lats) - 1)
            weight = idx - lower
            return sorted_lats[lower] * (1 - weight) + sorted_lats[upper] * weight

        p50_latency = percentile(50)
        p90_latency = percentile(90)
        p95_latency = percentile(95)
        p99_latency = percentile(99)

        throughput = len(latencies) / sum(latencies) if sum(latencies) > 0 else 0

        return {
            "avg_latency": avg_latency,
            "min_latency": min_latency,
            "max_latency": max_latency,
            "p50_latency": p50_latency,
            "p90_latency": p90_latency,
            "p95_latency": p95_latency,
            "p99_latency": p99_latency,
            "stddev_latency": stddev_latency,
            "throughput": throughput
        }

    def run_benchmark(self, table_name, num_queries, num_clients, warm_up=False):
        """
        Run the benchmark for a single table with the given concurrency.
        If warm_up=True, we'll do these queries but won't store final stats in self.results.
        """
        label = "Warm-up" if warm_up else "Benchmark"
        logging.info(f"{label} for {table_name} with {num_queries} queries and {num_clients} clients...")

        start_time = time.time()

        latencies = []
        success_count = 0
        failure_count = 0

        # Create or reuse executor
        # We'll create a new one for each run_benchmark to isolate concurrency
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(self.run_query, table_name) for _ in range(num_queries)]
            for future in futures:
                elapsed, success = future.result()
                if success:
                    success_count += 1
                    latencies.append(elapsed)
                else:
                    failure_count += 1

        success_rate = (success_count / num_queries) * 100 if num_queries else 0
        failure_rate = (failure_count / num_queries) * 100 if num_queries else 0
        elapsed_time = time.time() - start_time

        # Log basic stats
        if warm_up:
            # For a warm-up, we can just log and not save to CSV results
            logging.info(f"Finished warm-up for {table_name}, ignoring results in CSV.")
            return None

        # Compute extended stats
        stats = self.compute_latency_stats(latencies)

        # Log results
        logging.info(
            f"Results for {table_name}: avg_latency={stats['avg_latency']:.4f}s, "
            f"p50={stats['p50_latency']:.4f}s, p90={stats['p90_latency']:.4f}s, "
            f"throughput={stats['throughput']:.2f} q/s, "
            f"success_rate={success_rate:.2f}%, failure_rate={failure_rate:.2f}%, elapsed={elapsed_time:.2f}s"
        )

        # Return a dict that will be appended to self.results
        result_entry = {
            "table_name": table_name,
            "num_queries": num_queries,
            "num_clients": num_clients,
            "avg_latency": stats["avg_latency"],
            "min_latency": stats["min_latency"],
            "max_latency": stats["max_latency"],
            "p50_latency": stats["p50_latency"],
            "p90_latency": stats["p90_latency"],
            "p95_latency": stats["p95_latency"],
            "p99_latency": stats["p99_latency"],
            "stddev_latency": stats["stddev_latency"],
            "throughput": stats["throughput"],
            "success_rate": success_rate,
            "failure_rate": failure_rate,
            "elapsed_time": elapsed_time
        }
        return result_entry

    def save_results(self):
        """Save results to a CSV file."""
        if not self.results:
            logging.info("No results to save (maybe only warm-up runs?).")
            return

        # Dynamically gather all keys from the first result
        fieldnames = list(self.results[0].keys())
        with open(self.results_file, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        logging.info(f"Results saved to {self.results_file}.")

    def shutdown(self):
        """Close DB connection and log final message."""
        self.db.close()
        logging.info("Database connection closed.")

    def start(self):
        """Run the benchmarks for all configurations."""
        try:
            self.db.connect()
            for config in self.query_configs:
                # Some users put "warm_up" in the config, default to False if missing
                warm_up = config.get("warm_up", False)
                num_queries = config["num_queries"]
                num_clients = config["num_clients"]

                for table_name in self.tables:
                    result = self.run_benchmark(
                        table_name=table_name,
                        num_queries=num_queries,
                        num_clients=num_clients,
                        warm_up=warm_up
                    )
                    if result:  # will be None if warm_up==True
                        self.results.append(result)

            self.save_results()

        finally:
            self.shutdown()
