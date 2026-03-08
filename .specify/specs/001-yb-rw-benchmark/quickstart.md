# Quickstart: YugabyteDB Read/Write Benchmark

This tool evaluates the performance of different write strategies (Standard `pg_copy` vs YugabyteDB Smart Driver parallel) and read strategies (standard queries vs Optimized Schema Queries) against a local YugabyteDB cluster.

## 1. Prerequisites
- Docker & Docker Compose installed.
- Python 3.11+.

## 2. Environment Setup

Boot the customized 3GiB limited 1-node master, 3-node tserver cluster:

```bash
docker-compose up -d
```
*(Wait 10-15 seconds for the cluster logic and masters to initialize)*

Install the required Python binding (YugabyteDB Smart Driver):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt # or manually: pip install psycopg2-yugabytedb-binary>=2.9.9
```

## 3. Run Benchmarks

### Generate Data + Standard Write Benchmark
```bash
# Generates 5,000,000 rows (~300MB depending on strings) and imports using a single thread
python src/main.py --mode single --file test_data.csv --generate 5000000
```

### Parallel Write Benchmark
```bash
# Drops the table, recreates it, and imports using 20 concurrent threads
python src/main.py --mode parallel --file test_data.csv --workers 20
```

### Read Benchmarks
Run range query reads against the data for 60 seconds:
```bash
# Standard table structure read test
python src/main.py --mode read_standard --file test_data.csv --no-init --duration 60

# YugabyteDB Optimized index structure read test
python src/main.py --mode read_optimized --file test_data.csv --no-init --duration 60
```
