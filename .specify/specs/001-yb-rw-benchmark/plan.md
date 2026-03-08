# Implementation Plan: YugabyteDB Read/Write Benchmark Tool

**Branch**: `001-yb-rw-benchmark` | **Date**: 2026-03-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/001-yb-rw-benchmark/spec.md`

## Summary

The goal is to expand the existing YugabyteDB CSV importer to a complete Read/Write benchmark tool. 
- Expand `docker-compose.yaml` to explicitly support 1 master, 3 tservers with a footprint targeted under 3GiB limit for local rapid testing.
- Implement read benchmarking that compares traditional range queries versus YugabyteDB-optimized range queries using Sorted Partial Indexes, Covering Indexes, and explicitly directed ASC/DESC ordering to avoid DISTINCT overhead.
- Track QPS, TPS, Latency (avg, p95, p99), and IOPS using a cohesive benchmarking output structure.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: `psycopg2-yugabytedb-binary`, `argparse`, YugabyteDB Docker images.  
**Storage**: Local Docker Compose (1 master, 3 tservers) limited to 3GiB storage.  
**Testing**: Docker Compose local run and manual script validation.  
**Target Platform**: Local developer workstation (macOS).  
**Project Type**: CLI Data Benchmarking Tool.  
**Performance Goals**: N/A for the tool itself, but the tool captures up to 50k+ rows/sec.  
**Constraints**: Must use Python standard library threads for parallel copy, and standard `psycopg2` driver logic. Wait times must not block the main thread excessively.  
**Scale/Scope**: ~3GiB data generation and testing locally.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. CLI First**: Configuration strictly via CLI arguments.
- [x] **II. Performance Observability**: The tool will emit distinct read metrics (QPS, TPS, Latency, IOPS).
- [x] **III. Reliable Reproducibility**: Setup includes clearing data and explicit schema drops prior to tests.
- [x] **IV. Safe Concurrency**: Connection pool dictates max concurrency limits for reads/writes via bounded `ThreadPoolExecutor`.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-yb-rw-benchmark/
├── plan.md              # This file
├── spec.md              # The specification
├── data-model.md        # Database schema details and indexes
└── quickstart.md        # Quickstart instructions
```

### Source Code (repository root)

```text
/
├── docker-compose.yaml  # [MODIFY] Adjust resource limits to 3GiB storage
├── src/
│   ├── main.py          # [MODIFY] Add read benchmarking arguments and dispatch logic
│   ├── db_utils.py      # [MODIFY] Add read architectures (indexes/schemas)
│   ├── baseline.py      # [MODIFY] Ensure metrics match required format
│   ├── parallel.py      # [MODIFY] Ensure metrics match required format
│   ├── read_bench.py    # [NEW] Contains read thread pool execution and metrics tracking
│   └── test_data_generator.py # [MODIFY] Generate target ~3GiB data profile if requested
└── README.md            # [MODIFY] Update instructions for Read benchmarks
```

**Structure Decision**: Continue with the existing Flat Python CLI module layout inside `src/`. Added `read_bench.py` for read test encapsulation to avoid bloating `main.py` or `db_utils.py`.

## Proposed Changes

### 1. Docker Compose Adjustments
- Update `docker-compose.yaml` to ensure YugabyteDB node configurations use a confined `fs_data_dirs` or memory limitations (`--memory_limit_hard_bytes`) to approximate a lightweight 3GiB local environment.

### 2. Database Schema and Indexes (`db_utils.py`)
- Standard Table: Provide basic primary key structure.
- Optimized Table/Indexes: Include a `CREATE INDEX` statement using Covering attributes (e.g., `INCLUDE (email, score)`), a specific sort order (`name ASC, score DESC`), and Partial Index restrictions if applicable to the test queries.

### 3. Read Benchmarking (`read_bench.py` & `main.py`)
- Introduce thread pool execution for running `SELECT` statements continuously over a fixed duration (e.g., 60 seconds).
- Capture execution timestamps to calculate Average, P95, and P99 queries per second (QPS) and Latency.
- TPS mapping (1 query = 1 transaction in auto-commit mode).

## Verification Plan

### Automated Tests
- N/A - The testing relies on the system successfully executing the load against the Docker containers and outputting the log summary.

### Manual Verification
1. Boot the YugabyteDB cluster: `docker-compose up -d`
2. Generate base data (~3GiB footprint proxy/row count): `python src/main.py --mode parallel --file test.csv --generate 5000000`
3. Execute standard read test: `python src/main.py --mode read_standard`
4. Execute optimized read test: `python src/main.py --mode read_optimized`
5. Verify that the output lists QPS, Latency (Avg, P95, P99), and IOPS metrics.
6. Verify standard log stream errors do not exist.
