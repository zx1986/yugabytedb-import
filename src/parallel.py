import time
import logging
import io
import csv
from itertools import islice
from concurrent.futures import ThreadPoolExecutor, as_completed
from db_utils import get_connection_string, SmartConnectionPool

logger = logging.getLogger(__name__)

def copy_chunk(chunk_data, pool: SmartConnectionPool):
    """
    Worker function to execute COPY for a specific chunk using a connection from the pool.
    """
    conn = pool.getconn()
    if conn is None:
        raise Exception("Failed to get connection from pool.")

    # Convert the chunk back into a file-like object so copy_expert can read it.
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerows(chunk_data)
    buffer.seek(0)
    
    inserted_rows = 0
    try:
        with conn.cursor() as cur:
            sql = "COPY test_data FROM STDIN WITH (FORMAT CSV)"
            cur.copy_expert(sql, buffer)
            inserted_rows = cur.rowcount
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to copy chunk: {e}")
        raise
    finally:
        pool.putconn(conn)
        
    return inserted_rows

def run_parallel(file_path: str, workers: int, chunk_size: int):
    """
    Reads a CSV file line-by-line using streaming and distributes 
    chunks of data to multiple workers using a thread pool.
    """
    logger.info(f"Starting parallel chunked COPY with {workers} workers and chunk size {chunk_size}...")
    
    # Initialize connection pool containing enough connections to map to workers
    # Using Smart Driver, it's recommended to have pool min=max for uniform connections
    conn_pool = SmartConnectionPool(minconn=workers, maxconn=workers)
    
    start_time = time.time()
    total_inserted = 0
    
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = []
                
                while True:
                    # islice consumes the iterator efficiently without loading the whole file into RAM
                    chunk_data = list(islice(reader, chunk_size))
                    if not chunk_data:
                        break # EOF
                        
                    future = executor.submit(copy_chunk, chunk_data, conn_pool)
                    futures.append(future)

                # Wait for all futures to complete
                for f_task in as_completed(futures):
                    # Gather rowcount
                    total_inserted += f_task.result()
                    
    except Exception as e:
        logger.error(f"Parallel import failed: {e}")
        raise
    finally:
        conn_pool.closeall()
        
    duration = time.time() - start_time
    rows_per_sec = total_inserted / duration if duration > 0 else 0
    
    logger.info(f"--- Parallel Mode Results ---")
    logger.info(f"Workers:       {workers}")
    logger.info(f"Chunk Size:    {chunk_size}")
    logger.info(f"Rows inserted: {total_inserted}")
    logger.info(f"Total time:    {duration:.2f} seconds")
    logger.info(f"Throughput:    {rows_per_sec:.2f} rows/sec")

    return total_inserted, duration, rows_per_sec
