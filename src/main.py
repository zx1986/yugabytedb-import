import argparse
import logging
import sys

from test_data_generator import generate_test_data
from db_utils import (
    init_db_schema,
    clear_test_data,
    populate_optimized_from_standard,
    init_optimized_schema_only,
)
from baseline import run_baseline
from parallel import run_parallel
from read_bench import run_standard_read, run_optimized_read


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    parser = argparse.ArgumentParser(description="YugabyteDB Read/Write Benchmark Tool")
    parser.add_argument(
        '--mode',
        choices=['single', 'parallel', 'read_standard', 'read_optimized'],
        required=True,
        help="Benchmark mode: write (single/parallel) or read (read_standard/read_optimized)",
    )
    parser.add_argument('--file', type=str, required=True, help="Path to the CSV file")
    parser.add_argument(
        '--workers', type=int, default=10,
        help="Concurrent threads (parallel write or read clients)",
    )
    parser.add_argument(
        '--chunk-size', type=int, default=10_000,
        help="Rows per chunk (parallel write only)",
    )
    parser.add_argument(
        '--generate', type=int, default=None,
        help="Generate N rows of mock data into --file before benchmarking",
    )
    parser.add_argument(
        '--no-init', action='store_true',
        help="Skip schema re-creation; truncate tables only",
    )
    parser.add_argument(
        '--duration', type=int, default=60,
        help="Duration in seconds to run read benchmarks",
    )

    args = parser.parse_args()
    setup_logging()

    logger = logging.getLogger("MAIN")

    if args.generate is not None:
        generate_test_data(args.file, args.generate)

    # Schema initialisation
    if not args.no_init:
        init_db_schema()
    else:
        clear_test_data()

    logger.info("Running in '%s' mode with file '%s'", args.mode, args.file)

    if args.mode == 'single':
        run_baseline(args.file)

    elif args.mode == 'parallel':
        run_parallel(args.file, args.workers, args.chunk_size)

    elif args.mode == 'read_standard':
        # Ensure standard table is populated
        run_standard_read(args.workers, args.duration)

    elif args.mode == 'read_optimized':
        # Populate the covering-index table from the base table, then benchmark
        init_optimized_schema_only()
        populate_optimized_from_standard()
        run_optimized_read(args.workers, args.duration)


if __name__ == "__main__":
    main()
