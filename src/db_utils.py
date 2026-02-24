import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

# Default connection parameters
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "yugabyte"
DB_USER = "yugabyte"
DB_PASSWORD = "yugabyte"  # default pass is usually empty or yugabyte

def get_connection_string():
    # Adding load_balance=true ensures Yugabyte Smart Driver balances connections across T-Servers
    return f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} options='-c load_balance=true'"

def init_db_schema():
    """Initializes the database schema for the test_data table."""
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Create a simple table for benchmarking
                cur.execute("DROP TABLE IF EXISTS test_data;")
                cur.execute("""
                    CREATE TABLE test_data (
                        id int,
                        name varchar,
                        email varchar,
                        score float,
                        created_at timestamp,
                        PRIMARY KEY(id ASC)
                    );
                """)
            conn.commit()
            logger.info("Database schema initialized successfully (test_data table created).")
    except Exception as e:
        logger.error(f"Failed to initialize schema: {e}")
        raise

def clear_test_data():
    """Truncates the test_data table."""
    conn_str = get_connection_string()
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE test_data;")
            conn.commit()
            logger.info("test_data table truncated successfully.")
    except Exception as e:
        logger.error(f"Failed to truncate table: {e}")
        raise

class SmartConnectionPool:
    def __init__(self, minconn, maxconn):
        self.pool = psycopg2.pool.ThreadedConnectionPool(
            minconn, maxconn, dsn=get_connection_string()
        )
        logger.info(f"Initialized ThreadedConnectionPool (min={minconn}, max={maxconn}) with load balancing.")
        
    def getconn(self):
        return self.pool.getconn()

    def putconn(self, conn):
        self.pool.putconn(conn)

    def closeall(self):
        self.pool.closeall()
        logger.info("Connection pool closed.")
