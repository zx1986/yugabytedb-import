<!-- 
Sync Impact Report
- Version change: 0.0.0 -> 1.0.0 (Initial)
- Modified principles: Setup initial principles based on yb-csv-importer existing structure
- Added sections: Core Principles, Development Standards, Development Workflow, Governance
- Removed sections: Template placeholders
- Templates requiring updates:
  ✅ .specify/templates/plan-template.md
  ✅ .specify/templates/spec-template.md
  ✅ .specify/templates/tasks-template.md
- Follow-up TODOs: 
  - TODO(RATIFICATION_DATE): Confirm exact ratification date.
-->
# YugabyteDB CSV Importer Constitution

## Core Principles

### I. CLI First
The tool MUST be a command-line utility. All configuration (mode, workers, chunk size) MUST be provided via CLI arguments. Standard input/output streams SHOULD be used for generic text interfaces, and structured logging MUST handle execution details.

### II. Performance Observability
Given this is a benchmarking tool, it MUST emit clear, structured logs detailing performance metrics. Operations MUST log total rows inserted, duration in seconds, and throughput (rows/sec) to enable accurate comparison between single and parallel modes.

### III. Reliable Reproducibility
The application MUST provide mechanisms to ensure benchmarks are reproducible. This includes generating consistent test data deterministically and ensuring the database schema is freshly initialized or truncated before each benchmark run.

### IV. Safe Concurrency
When operating in parallel mode, database connections MUST be managed through a connection pool (e.g., `SmartConnectionPool`). ThreadPool execution MUST be bounded to prevent unbounded memory growth and connection exhaustion. Every database interaction MUST be safely wrapped in `try/except/finally` blocks to ensure connections are returned.

## Development Standards

- **Language Specs**: Python 3.11+. Use type hints for all public functions to improve clarity.
- **Dependencies**: Keep external dependencies minimal. `psycopg2-yugabytedb-binary` represents the core driver.
- **Testing**: Maintain test coverage for core utilities (`db_utils`), data generation (`test_data_generator`), and parallel execution logic (`parallel`).

## Development Workflow

- **Formatting & Linting**: Code MUST be formatted using standard Python tools prior to commit.
- **Pull Requests**: Pull requests MUST pass all tests and be verified in both single and parallel modes against a local YugabyteDB instance.
- **Benchmarking Changes**: Any code modification touching the `COPY` logic MUST include a before-and-after benchmark comparison in the PR description.

## Governance

- The principles in this document supersede ad-hoc development practices.
- Amendments to this constitution MUST bump the version number according to Semantic Versioning and require documented rationale via a Sync Impact Report.
- All code reviews MUST enforce compliance with the Core Principles.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2026-03-08
