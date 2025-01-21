from db_config import *
import psycopg2
import random
import time
from tqdm import tqdm  # Progress bar library

# Configuration
NUM_ROWS = 1000000  # Number of embeddings to generate
DIMENSIONS = 128  # Number of dimensions for the embeddings
BATCH_SIZE = 2000  # Number of rows to insert per batch
SEED = 23  # Fixed seed for reproducibility
RECREATE_TABLES = True  # Set to True to delete and recreate tables

TABLES = {
    "items_no_index": None,  # No index
    "items_ivfflat": "ivfflat",  # IVFFlat indexing
    "items_hnsw": "hnsw"  # HNSW indexing
}

# Index configuration
INDEX_CONFIGS = {
    "ivfflat": "WITH (lists = 100)",  # Adjust the 'lists' parameter as needed
    "hnsw": "WITH (m = 8, ef_construction = 100)"  # Adjust 'm' and 'ef_construction' as needed
}

# Set the random seed
random.seed(SEED)

def recreate_tables(cursor):
    """Drop and recreate tables."""
    print("Recreating tables...")
    for table_name, index_type in TABLES.items():
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        cursor.execute(f"""
            CREATE TABLE {table_name} (
                id SERIAL PRIMARY KEY,
                embedding VECTOR({DIMENSIONS})
            );
        """)
        print(f"Table {table_name} recreated successfully.")
    print("All tables recreated.")

def populate_no_index_table(cursor, conn, table_name):
    """Populate the no_index table with random embeddings."""
    print(f"Populating table {table_name} with {NUM_ROWS} embeddings...")

    # Initialize progress bar
    total_batches = (NUM_ROWS + BATCH_SIZE - 1) // BATCH_SIZE  # Calculate total number of batches
    with tqdm(total=NUM_ROWS, desc="Inserting rows", unit="rows") as pbar:
        batch = []
        total_start_time = time.time()

        for i in range(NUM_ROWS):
            embedding = [round(random.uniform(0, 1), 2) for _ in range(DIMENSIONS)]
            batch.append((embedding,))

            if len(batch) == BATCH_SIZE:
                batch_start_time = time.time()  # Start timing this batch
                cursor.executemany(
                    f"INSERT INTO {table_name} (embedding) VALUES (%s)", batch
                )
                conn.commit()
                batch_end_time = time.time()  # End timing this batch

                # Update progress bar
                pbar.update(len(batch))
                pbar.set_postfix(batch_time=f"{batch_end_time - batch_start_time:.2f}s")

                batch = []  # Clear the batch

        # Insert remaining rows
        if batch:
            batch_start_time = time.time()
            cursor.executemany(
                f"INSERT INTO {table_name} (embedding) VALUES (%s)", batch
            )
            conn.commit()
            batch_end_time = time.time()

            # Update progress bar for the final batch
            pbar.update(len(batch))
            pbar.set_postfix(batch_time=f"{batch_end_time - batch_start_time:.2f}s")

        total_end_time = time.time()
        print(f"Inserted {NUM_ROWS} embeddings into {table_name} successfully.")
        print(f"Total time for {table_name}: {total_end_time - total_start_time:.2f} seconds")

def copy_data_to_other_tables(cursor, conn, source_table, target_table):
    """Copy data from the source table to the target table."""
    print(f"Copying data from {source_table} to {target_table}...")
    copy_start_time = time.time()
    cursor.execute(f"INSERT INTO {target_table} (embedding) SELECT embedding FROM {source_table};")
    conn.commit()
    copy_end_time = time.time()
    print(f"Data copied to {target_table} in {copy_end_time - copy_start_time:.2f} seconds.")

def create_index(cursor, conn, table_name, index_type):
    """Create the specified index on the table."""
    print(f"Creating {index_type} index on {table_name}...")
    if index_type == "ivfflat":
        cursor.execute(f"""
            CREATE INDEX {table_name}_{index_type}_idx 
            ON {table_name} USING ivfflat (embedding vector_l2_ops) 
            {INDEX_CONFIGS[index_type]};
        """)
    elif index_type == "hnsw":
        cursor.execute(f"""
            CREATE INDEX {table_name}_{index_type}_idx 
            ON {table_name} USING hnsw (embedding vector_l2_ops) 
            {INDEX_CONFIGS[index_type]};
        """)
    conn.commit()
    print(f"{index_type} index created successfully for {table_name}.")

try:
    print("Connecting to PostgreSQL...")
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # Step 1: Recreate tables if the flag is set
    if RECREATE_TABLES:
        recreate_tables(cursor)

    # Step 2: Populate items_no_index
    populate_no_index_table(cursor, conn, "items_no_index")

    # Step 3: Copy data to other tables
    for target_table, index_type in TABLES.items():
        if target_table != "items_no_index":
            copy_data_to_other_tables(cursor, conn, "items_no_index", target_table)

    # Step 4: Create indexes on the indexed tables
    for target_table, index_type in TABLES.items():
        if index_type:
            create_index(cursor, conn, target_table, index_type)

    print("Data generation, copying, and indexing completed successfully.")

finally:
    # Ensure connection is closed
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
    print("Connection closed.")
