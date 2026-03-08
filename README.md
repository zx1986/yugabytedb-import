# YugabyteDB CSV Importer & Read/Write Benchmark Tool

A Python CLI tool for benchmarking YugabyteDB write and read performance using a local Docker Compose cluster.

## Architecture

- **1 Master node** + **3 TServer nodes** running via Docker Compose
- Cluster storage confined to **~3 GiB** (tmpfs volumes)
- Write modes: standard `pg_copy` (single-thread) vs YugabyteDB Smart Driver parallel COPY
- Read modes: standard range queries vs queries on a YugabyteDB-optimized covering index

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- `psycopg2-yugabytedb-binary >= 2.9.9`

## Setup

```bash
# Start the cluster (wait ~15s for the cluster to elect a leader)
docker-compose up -d

# Install Python dependencies
python -m venv .venv && source .venv/bin/activate
pip install psycopg2-yugabytedb-binary
```

## Benchmark Modes

All modes report: **QPS, TPS, IOPS, Latency (avg/p95/p99)**

### Write Benchmarks

```bash
# Standard single-thread COPY (1M rows)
python src/main.py --mode single --file data.csv --generate 1000000

# Parallel COPY with Smart Driver (20 workers, reuse existing data)
python src/main.py --mode parallel --file data.csv --workers 20 --no-init
```

### Read Benchmarks

```bash
# Must have data loaded first (run a write benchmark or --generate above)

# Standard range queries (against unoptimized table)
python src/main.py --mode read_standard --file data.csv --no-init --workers 10 --duration 60

# Optimized range queries (covering index: score DESC, name ASC INCLUDE email, created_at)
python src/main.py --mode read_optimized --file data.csv --no-init --workers 10 --duration 60
```

### Full End-to-End Example

```bash
# 1. Generate data + standard write
python src/main.py --mode single --file bench.csv --generate 2000000

# 2. Parallel write (reuse same data, fresh table)
python src/main.py --mode parallel --file bench.csv --workers 20

# 3. Standard read benchmark (60s)
python src/main.py --mode read_standard --file bench.csv --no-init --duration 60

# 4. Optimized read benchmark (60s)
python src/main.py --mode read_optimized --file bench.csv --no-init --duration 60
```

## CLI Reference

| Argument       | Default    | Description                                           |
|----------------|------------|-------------------------------------------------------|
| `--mode`       | (required) | `single`, `parallel`, `read_standard`, `read_optimized` |
| `--file`       | (required) | Path to CSV file                                      |
| `--generate`   | —          | Generate N rows into `--file` before benchmark        |
| `--workers`    | 10         | Concurrent threads (parallel write or read clients)   |
| `--chunk-size` | 10000      | Rows per chunk (parallel write only)                  |
| `--duration`   | 60         | Seconds to run read benchmark                        |
| `--no-init`    | false      | Skip schema drop/recreate; truncate tables only       |

## Index Strategy (Read Benchmark)

| Mode | Table | Index |
|---|---|---|
| `read_standard` | `test_data` | Primary Key (id ASC) only |
| `read_optimized` | `test_data_optimized` | Covering: `score DESC, name ASC INCLUDE (email, created_at)` |

The optimized index avoids double lookups and in-memory sorts by matching the query's explicit `ORDER BY score DESC, name ASC` and covering all projected columns.
