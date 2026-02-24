import time
import io
import logging
from itertools import islice
from concurrent.futures import ThreadPoolExecutor, as_completed
from db_utils import SmartConnectionPool, tune_session

logger = logging.getLogger(__name__)


def _copy_chunk(raw_lines: list[str], pool: SmartConnectionPool) -> int:
    """Copy a chunk of raw CSV lines into the database via COPY FROM STDIN."""
    conn = pool.getconn()
    try:
        tune_session(conn)
        buf = io.StringIO("".join(raw_lines))
        with conn.cursor() as cur:
            cur.copy_expert("COPY test_data FROM STDIN WITH (FORMAT CSV)", buf)
            inserted = cur.rowcount
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)
    return inserted


def run_parallel(file_path: str, workers: int, chunk_size: int):
    """
    Stream-reads a CSV file and distributes raw-line chunks to a thread pool
    for parallel COPY into YugabyteDB.
    """
    logger.info(
        "Starting parallel COPY with %d workers, chunk_size=%d ...",
        workers, chunk_size,
    )

    conn_pool = SmartConnectionPool(minconn=workers, maxconn=workers)

    start_time = time.time()
    total_inserted = 0

    try:
        with open(file_path, "r") as fh:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = []

                while True:
                    chunk = list(islice(fh, chunk_size))
                    if not chunk:
                        break
                    futures.append(executor.submit(_copy_chunk, chunk, conn_pool))

                    # Bounded submission: if we have twice as many pending futures
                    # as workers, drain some before submitting more.
                    if len(futures) >= workers * 2:
                        done = [f for f in futures if f.done()]
                        for f in done:
                            total_inserted += f.result()
                            futures.remove(f)

                for f in as_completed(futures):
                    total_inserted += f.result()

    except Exception as e:
        logger.error("Parallel import failed: %s", e)
        raise
    finally:
        conn_pool.closeall()

    duration = time.time() - start_time
    rows_per_sec = total_inserted / duration if duration > 0 else 0

    logger.info("--- Parallel Mode Results ---")
    logger.info("Workers:       %d", workers)
    logger.info("Chunk Size:    %d", chunk_size)
    logger.info("Rows inserted: %d", total_inserted)
    logger.info("Total time:    %.2f seconds", duration)
    logger.info("Throughput:    %.2f rows/sec", rows_per_sec)

    return total_inserted, duration, rows_per_sec
