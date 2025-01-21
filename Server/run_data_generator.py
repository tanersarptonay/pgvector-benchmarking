#!/usr/bin/env python3

import json
import signal
import logging
from data_generator import DataGenerator

def signal_handler(signum, frame):
    """Handle termination signals."""
    logging.info(f"Received termination signal ({signum}). Cleaning up...")
    generator.stop_event.set()

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

    # Load configuration
    try:
        with open("generator_config.json", "r") as file:
            config = json.load(file)
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        exit(1)

    # Initialize data generator
    generator = DataGenerator(config)

    # Attach signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start data generation
    generator.start()
