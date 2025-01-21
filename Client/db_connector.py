import psycopg2

class DBConnector:
    """Handles database connections and queries."""

    def __init__(self, db_config):
        self.conn = None
        self.config = db_config

    def connect(self):
        """Establish a database connection."""
        try:
            self.conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                dbname=self.config["dbname"],
                user=self.config["user"],
                password=self.config["password"],
            )
            print("Database connection established.")
        except psycopg2.Error as e:
            print("Error connecting to the database:", e)
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

    def get_cursor(self):
        """Get a cursor for executing queries."""
        if not self.conn:
            self.connect()
        return self.conn.cursor()
