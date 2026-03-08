import time
import logging
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from db_utils import SmartConnectionPool

logger = logging.getLogger(__name__)

_RANGE_QUERY_STANDARD = """
SELECT id, name, email, score, created_at
FROM test_data
WHERE score BETWEEN %s AND %s
ORDER BY score DESC, name ASC
LIMIT 100;
"""

_RANGE_QUERY_OPTIMIZED = """
SELECT id, name, email, score, created_at
FROM test_data_optimized
WHERE score BETWEEN %s AND %s
ORDER BY score DESC, name ASC
LIMIT 100;
"""


def _execute_query(pool: SmartConnectionPool, query: str, latencies: list[float]) -> int:
    """Execute a single range query, appending latency to the shared list."""
    import random
    lo = random.uniform(0.0, 50.0)
    hi = lo + random.uniform(5.0, 50.0)

    conn = pool.getconn()
    try:
        t0 = time.perf_counter()
        with conn.cursor() as cur:
            cur.execute(query, (lo, hi))
            rows = cur.rowcount
        latencies.append((time.perf_counter() - t0) * 1000.0)  # ms
        return rows
    finally:
        pool.putconn(conn)


def _run_read_bench(query: str, workers: int, duration_sec: int, label: str):
    """
    Drive concurrent read queries for `duration_sec` seconds and report metrics.
    Uses a thread-pool with `workers` concurrent clients.
    """
    pool = SmartConnectionPool(minconn=workers, maxconn=workers)
    latencies: list[float] = []
    total_queries = 0
    start = time.time()
    deadline = start + duration_sec

    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            pending: set = set()
            while time.time() < deadline:
                # Keep the pool saturated
                while len(pending) < workers * 2 and time.time() < deadline:
                    f = executor.submit(_execute_query, pool, query, latencies)
                    pending.add(f)

                done = {f for f in pending if f.done()}
                for f in done:
                    f.result()  # raises on error
                    total_queries += 1
                    pending -= {f}

            # Drain remaining
            for f in as_completed(pending):
                f.result()
                total_queries += 1
    finally:
        pool.closeall()

    elapsed = time.time() - start

    if latencies:
        latencies.sort()
        avg_ms = statistics.mean(latencies)
        p95_ms = latencies[int(len(latencies) * 0.95)]
        p99_ms = latencies[int(len(latencies) * 0.99)]
    else:
        avg_ms = p95_ms = p99_ms = 0.0

    qps = total_queries / elapsed if elapsed > 0 else 0.0
    # TPS = 1 query = 1 auto-commit txn
    tps = qps
    # IOPS proxy: total rows read / elapsed (each query returns up to 100 rows)
    iops = (total_queries * 100) / elapsed if elapsed > 0 else 0.0

    logger.info("--- %s Read Results ---", label)
    logger.info("Workers:       %d", workers)
    logger.info("Duration:      %.2f seconds", elapsed)
    logger.info("Total queries: %d", total_queries)
    logger.info("QPS:           %.2f queries/sec", qps)
    logger.info("TPS:           %.2f txns/sec", tps)
    logger.info("IOPS (est.):   %.2f row-reads/sec", iops)
    logger.info("Latency avg:   %.2f ms", avg_ms)
    logger.info("Latency p95:   %.2f ms", p95_ms)
    logger.info("Latency p99:   %.2f ms", p99_ms)

    return {
        "label": label,
        "qps": qps,
        "tps": tps,
        "iops": iops,
        "latency_avg_ms": avg_ms,
        "latency_p95_ms": p95_ms,
        "latency_p99_ms": p99_ms,
        "total_queries": total_queries,
        "duration_sec": elapsed,
    }


def run_standard_read(workers: int, duration_sec: int):
    """Benchmark standard range queries against the unoptimized test_data table."""
    return _run_read_bench(_RANGE_QUERY_STANDARD, workers, duration_sec, "Standard Read")


def run_optimized_read(workers: int, duration_sec: int):
    """Benchmark optimized range queries against test_data_optimized (covering index)."""
    return _run_read_bench(_RANGE_QUERY_OPTIMIZED, workers, duration_sec, "Optimized Read")
