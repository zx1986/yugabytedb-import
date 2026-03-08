import time
import logging
import psycopg2
from db_utils import get_connection_string, tune_session

logger = logging.getLogger(__name__)

# 8 MB read buffer for file I/O
_READ_BUFFER_SIZE = 8 * 1024 * 1024


def _calc_metrics(inserted_rows: int, duration: float, label: str = "Baseline") -> dict:
    """
    Derive QPS, TPS, Latency (single bulk op treated as 1 transaction), and IOPS.
    For a single-connection bulk COPY:
      - TPS  = 1  (one commit)
      - QPS  = rows / duration  (rows effectively queued per second)
      - IOPS = rows / duration  (each row = 1 logical write I/O)
      - Latency = duration in ms (wall-clock of the single txn)
    """
    qps = inserted_rows / duration if duration > 0 else 0.0
    tps = 1.0 / duration if duration > 0 else 0.0          # 1 txn total
    iops = inserted_rows / duration if duration > 0 else 0.0
    latency_ms = duration * 1000.0

    logger.info("--- %s Mode Results ---", label)
    logger.info("Rows inserted:  %d", inserted_rows)
    logger.info("Total time:     %.2f seconds", duration)
    logger.info("QPS:            %.2f rows/sec", qps)
    logger.info("TPS:            %.2f txns/sec", tps)
    logger.info("IOPS:           %.2f row-writes/sec", iops)
    logger.info("Latency (txn):  %.2f ms", latency_ms)

    return {
        "label": label,
        "rows_inserted": inserted_rows,
        "duration_sec": duration,
        "qps": qps,
        "tps": tps,
        "iops": iops,
        "latency_ms": latency_ms,
    }


def run_baseline(file_path: str) -> dict:
    """Executes a standard single-threaded COPY command and reports metrics."""
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
    return _calc_metrics(inserted_rows, duration, "Baseline Single-Thread")
