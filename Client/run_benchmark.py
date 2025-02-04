#!/usr/bin/env python3

import json
import signal
import sys
import logging
from benchmark_runner import BenchmarkRunner
from utils import setup_logger

# Global variable to manage cleanup
benchmark_runner = None

def cleanup(signum, frame):
    """Cleans up resources before exiting."""
    global benchmark_runner
    logging.info(f"Received termination signal ({signum}). Cleaning up...")

    if benchmark_runner:
        benchmark_runner.shutdown()

    logging.info("Cleanup complete. Exiting.")
    sys.exit(0)

if __name__ == "__main__":
    # Optional: You can still use a simple or advanced logger setup.
    setup_logger("benchmark.log")  # from your existing utils.py

    # Attach signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        # Load configuration
        with open("config.json", "r") as file:
            config = json.load(file)

        db_config = config["db"]
        benchmark_config = config["benchmark"]

        tables = benchmark_config["tables"]
        query_configs = benchmark_config["query_configs"]
        dimensions = benchmark_config["dimensions"]

        host_ip = db_config["hosts"][str(dimensions)]
        db_config["host"] = host_ip

        # Initialize and start benchmark
        benchmark_runner = BenchmarkRunner(
            tables=tables,
            query_configs=query_configs,
            dimensions=dimensions,
            db_config=db_config
        )
        benchmark_runner.start()

    except Exception as e:
        logging.error(f"Error during benchmarking: {e}")
        cleanup(signal.SIGTERM, None)
