#!/usr/bin/env python3

from db_config import *
import psycopg2

def try_connection():
    print(f"Trying to connect to the database at {DB_HOST}:{DB_PORT}...")

    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
        )
        print("Database connection successful!")
        conn.close()
    except Exception as e:
        print("Error connecting to the database:", e)

if __name__ == "__main__":
    try_connection()
