import psycopg2
import random
import time
from tqdm import tqdm
import logging
import signal
import sys
import os
from threading import Event

class DataGenerator:
    def __init__(self, config):
        self.generator_config = config["generator"]
        self.db_config = config["db"]
        self.stop_event = Event()
        self.conn = None
        self.cursor = None
        self.setup_logger()

    def setup_logger(self):
        """Set up structured logging."""
        current_time = time.strftime("%Y%m%d-%H%M%S")

        if not os.path.exists("logs"):
            os.makedirs("logs")

        log_path = os.path.join("logs", f"data_generator_{current_time}.log")

        # Remove existing handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_path)
            ]
        )

    def connect_to_db(self):
        """Establish a connection to the database using the configuration."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                dbname=self.db_config["dbname"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            self.cursor = self.conn.cursor()
            logging.info("Connected to PostgreSQL database.")

        except KeyError as e:
            logging.error(f"Missing configuration for: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Failed to connect to the database: {e}")
            sys.exit(1)

    def configure_session(self):
        """Configure database session settings."""
        try:
            maintenance_work_mem = self.generator_config["maintenance_work_mem"]
            # self.cursor.execute(f"SET maintenance_work_mem = '{maintenance_work_mem}';")
            self.cursor.execute("SET maintenance_work_mem = '4GB';")
            self.cursor.execute("SET work_mem = '128MB';")
            # self.cursor.execute("SET shared_buffers = '8GB';")
            self.cursor.execute("SET effective_cache_size = '24GB';")
            self.cursor.execute("SET max_parallel_workers_per_gather = 6;")
            self.cursor.execute("SET parallel_tuple_cost = 0.1;")
            self.cursor.execute("SET parallel_setup_cost = 50;")
            self.cursor.execute("SET force_parallel_mode = 'off';")
            logging.info("PostgreSQL settings optimized for index building and benchmarking.")

            logging.info(f"Set maintenance_work_mem to {maintenance_work_mem}.")
        except KeyError as e:
            logging.error(f"Missing configuration for: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Failed to configure the database session: {e}")
            sys.exit(1)


    def recreate_tables(self):
        """Drop and recreate tables."""
        logging.info("Recreating tables...")
        for table_name, index_type in self.generator_config["tables"].items():
            self.cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            self.cursor.execute(f"""
                CREATE TABLE {table_name} (
                    id SERIAL PRIMARY KEY,
                    embedding VECTOR({self.generator_config['dimensions']})
                );
            """)
            logging.info(f"Table {table_name} recreated successfully.")

    def populate_table(self, table_name):
        """Populate the no_index table with random embeddings."""
        num_rows = self.generator_config["num_rows"]
        batch_size = self.generator_config["batch_size"]
        dimensions = self.generator_config["dimensions"]

        logging.info(f"Populating table {table_name} with {num_rows} embeddings...")

        total_batches = (num_rows + batch_size - 1) // batch_size
        with tqdm(total=num_rows, desc=f"Populating {table_name}", unit="rows") as pbar:
            batch = []
            for i in range(num_rows):
                if self.stop_event.is_set():
                    logging.warning("Data generation interrupted.")
                    break

                embedding = [round(random.uniform(0, 1), 2) for _ in range(dimensions)]
                batch.append((embedding,))

                if len(batch) == batch_size:
                    self.cursor.executemany(
                        f"INSERT INTO {table_name} (embedding) VALUES (%s)", batch
                    )
                    self.conn.commit()
                    pbar.update(len(batch))
                    batch = []

            if batch:
                self.cursor.executemany(
                    f"INSERT INTO {table_name} (embedding) VALUES (%s)", batch
                )
                self.conn.commit()
                pbar.update(len(batch))
        logging.info(f"Table {table_name} populated successfully.")

    def copy_data_to_other_tables(self, source_table):
        """Copy data from source table to other tables."""
        for target_table, index_type in self.generator_config["tables"].items():
            if target_table != source_table:
                logging.info(f"Copying data from {source_table} to {target_table}...")
                self.cursor.execute(f"INSERT INTO {target_table} (embedding) SELECT embedding FROM {source_table};")
                self.conn.commit()
                logging.info(f"Data copied to {target_table}.")

    def create_indexes(self):
        """Create indexes for the indexed tables."""
        for table_name, index_type in self.generator_config["tables"].items():
            if index_type:
                index_creation_start = time.time()

                logging.info(f"Creating {index_type} index on {table_name}...")
                index_config = self.generator_config["index_configs"][index_type]
                self.cursor.execute(f"""
                    CREATE INDEX {table_name}_{index_type}_idx 
                    ON {table_name} USING {index_type} (embedding vector_l2_ops) 
                    {index_config};
                """)
                self.conn.commit()

                # smallcase, remove () and replace , with and
                log_config = index_config.lower().replace("(", "").replace(")", "").replace(",", " and").replace(" = ", "=")

                index_creation_time = round(time.time() - index_creation_start, 2)
                
                logging.info(f"{index_type} {log_config} index created for {table_name} in {index_creation_time} seconds or {index_creation_time/60:.2f} minutes.")

    def shutdown(self):
        """Close database connections and clean up resources."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.info("Database connection closed.")

    def start(self):
        """Run the data generation process."""
        try:
            random.seed(self.generator_config["seed"])
    
            self.connect_to_db()
            self.configure_session()

            if self.generator_config["recreate_tables"]:
                self.recreate_tables()

            no_index_name = None
            for table_name, indexing in self.generator_config["tables"].items():
                if indexing == None:
                    no_index_name = table_name
            if not no_index_name:
                raise Exception("Table to be copied cannot be found.")            

            self.populate_table(no_index_name)
            self.copy_data_to_other_tables(no_index_name)
            self.create_indexes()

            logging.info("Data generation completed successfully.")
        except Exception as e:
            logging.error(f"An error occurred during data generation: {e}")
        finally:
            self.shutdown()
