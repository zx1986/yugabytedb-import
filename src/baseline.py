import time
import logging
import psycopg2
from db_utils import get_connection_string, tune_session

logger = logging.getLogger(__name__)

# 8 MB read buffer for file I/O
_READ_BUFFER_SIZE = 8 * 1024 * 1024


def run_baseline(file_path: str):
    """Executes a standard single-threaded COPY command."""
    logger.info("Starting baseline single-threaded COPY...")

    start_time = time.time()

    try:
        with psycopg2.connect(get_connection_string()) as conn:
            tune_session(conn)
            with conn.cursor() as cur:
                with open(file_path, "r", buffering=_READ_BUFFER_SIZE) as f:
                    cur.copy_expert(
                        "COPY test_data FROM STDIN WITH (FORMAT CSV)", f,
                        size=_READ_BUFFER_SIZE,
                    )
                inserted_rows = cur.rowcount
            conn.commit()
    except Exception as e:
        logger.error("Baseline import failed: %s", e)
        raise

    duration = time.time() - start_time
    rows_per_sec = inserted_rows / duration if duration > 0 else 0

    logger.info("--- Baseline Mode Results ---")
    logger.info("Rows inserted: %d", inserted_rows)
    logger.info("Total time:    %.2f seconds", duration)
    logger.info("Throughput:    %.2f rows/sec", rows_per_sec)

    return inserted_rows, duration, rows_per_sec
