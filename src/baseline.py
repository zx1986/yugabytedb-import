import time
import logging
import psycopg2
from db_utils import get_connection_string

logger = logging.getLogger(__name__)

def run_baseline(file_path: str):
    """
    Executes a standard single-threaded COPY command.
    """
    logger.info("Starting baseline single-threaded COPY...")
    
    conn_str = get_connection_string()
    
    start_time = time.time()
    
    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                with open(file_path, 'r') as f:
                    # Using copy_expert to read from the file directly.
                    # We assume our test data has no header and is formatted as CSV.
                    sql = "COPY test_data FROM STDIN WITH (FORMAT CSV)"
                    cur.copy_expert(sql, f)
                    
                inserted_rows = cur.rowcount
            conn.commit()
            
    except Exception as e:
        logger.error(f"Baseline import failed: {e}")
        raise
        
    duration = time.time() - start_time
    rows_per_sec = inserted_rows / duration if duration > 0 else 0
    
    logger.info(f"--- Baseline Mode Results ---")
    logger.info(f"Rows inserted: {inserted_rows}")
    logger.info(f"Total time:    {duration:.2f} seconds")
    logger.info(f"Throughput:    {rows_per_sec:.2f} rows/sec")
    
    return inserted_rows, duration, rows_per_sec
