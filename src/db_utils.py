import psycopg2
from psycopg2 import pool
import logging

logger = logging.getLogger(__name__)

DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "yugabyte"
DB_USER = "yugabyte"
DB_PASSWORD = "yugabyte"


def get_connection_string():
    return (
        f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} "
        f"user={DB_USER} password={DB_PASSWORD} "
        f"options='-c load_balance=true'"
    )


def tune_session(conn):
    """Apply per-session performance tuning suitable for bulk loading."""
    with conn.cursor() as cur:
        cur.execute("SET synchronous_commit = OFF")
        cur.execute("SET session_replication_role = 'replica'")


def init_db_schema():
    """Drop and recreate the test_data table."""
    with psycopg2.connect(get_connection_string()) as conn:
        with conn.cursor() as cur:
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
        logger.info("Schema initialized (test_data table created).")


def clear_test_data():
    """Truncate the test_data table."""
    with psycopg2.connect(get_connection_string()) as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE test_data;")
        conn.commit()
        logger.info("test_data table truncated.")


class SmartConnectionPool:
    """Thread-safe connection pool backed by YugabyteDB Smart Driver."""

    def __init__(self, minconn: int, maxconn: int):
        self.pool = pool.ThreadedConnectionPool(
            minconn, maxconn, dsn=get_connection_string()
        )
        logger.info(
            "ThreadedConnectionPool ready (min=%d, max=%d, load_balance=true).",
            minconn, maxconn,
        )

    def getconn(self):
        return self.pool.getconn()

    def putconn(self, conn):
        self.pool.putconn(conn)

    def closeall(self):
        self.pool.closeall()
        logger.info("Connection pool closed.")
