import os
import random
import string
import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

_LETTERS = string.ascii_letters


def _random_name(length: int = 15) -> str:
    return "".join(random.choices(_LETTERS, k=length))


def generate_test_data(file_path: str, num_rows: int = 1_000_000):
    """Generate a headerless CSV file with mock data suitable for COPY."""
    if os.path.exists(file_path):
        logger.info("File '%s' already exists, skipping generation.", file_path)
        return

    logger.info("Generating %d rows into '%s' ...", num_rows, file_path)
    start = time.time()
    now = datetime.now()

    batch_size = 50_000
    with open(file_path, "w", buffering=8 * 1024 * 1024) as fh:
        batch: list[str] = []
        for i in range(1, num_rows + 1):
            name = _random_name()
            ts = (now - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d %H:%M:%S")
            batch.append(
                f"{i},{name},{name.lower()}@example.com,"
                f"{random.uniform(0.0, 100.0):.2f},{ts}\n"
            )
            if i % batch_size == 0:
                fh.writelines(batch)
                batch.clear()
        if batch:
            fh.writelines(batch)

    logger.info("Generated %d rows in %.2f s.", num_rows, time.time() - start)
