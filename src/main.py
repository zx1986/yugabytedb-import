import argparse
import logging
import sys

from test_data_generator import generate_test_data
from db_utils import init_db_schema, clear_test_data
from baseline import run_baseline
from parallel import run_parallel

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def main():
    parser = argparse.ArgumentParser(description="YugabyteDB CSV Benchmark Tool")
    parser.add_argument('--mode', choices=['single', 'parallel'], required=True, help="Execution mode")
    parser.add_argument('--file', type=str, required=True, help="Path to the CSV file")
    parser.add_argument('--workers', type=int, default=10, help="Number of worker threads (only for parallel mode)")
    parser.add_argument('--chunk-size', type=int, default=10000, help="Number of rows per chunk (only for parallel mode)")
    parser.add_argument('--generate', type=int, default=None, help="Generate mock data with specified length before import (overwrites file if specified)")
    parser.add_argument('--no-init', action='store_true', help="Skip re-initializing the database table")

    args = parser.parse_args()
    setup_logging()
    
    logger = logging.getLogger("MAIN")

    if args.generate is not None:
        generate_test_data(args.file, args.generate)
        
    if not args.no_init:
        init_db_schema()
    else:
        # Just truncate the table to ensure a clean slate
        clear_test_data()
        
    logger.info(f"Running in '{args.mode}' mode with file '{args.file}'")
    
    if args.mode == 'single':
        run_baseline(args.file)
    elif args.mode == 'parallel':
        run_parallel(args.file, args.workers, args.chunk_size)

if __name__ == "__main__":
    main()
