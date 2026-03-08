# Tasks: YugabyteDB Read/Write Benchmark Tool

**Input**: Design documents from `/specs/001-yb-rw-benchmark/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Modify `docker-compose.yaml` to ensure YugabyteDB is confined to ~3GiB storage limits.
- [x] T002 [P] Create `src/read_bench.py` skeleton structure.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Update `src/main.py` CLI parser to include `--mode (read_standard, read_optimized)`, `--duration`.
- [x] T004 [P] Update `src/db_utils.py` to create the standard `test_data` schema (id, name, email, score, created_at).

---

## Phase 3: User Story 1 - Benchmark Write Performance (Priority: P1)

**Goal**: Execute and compare different CSV data import methods to evaluate throughput and latency.

**Independent Test**: Run parallel and single write benchmarks against the local DB and observe output metrics.

### Implementation for User Story 1

- [x] T005 [P] [US1] Update `src/baseline.py` to calculate and output specific metrics (QPS, TPS, Latency avg/p95/p99, IOPS).
- [x] T006 [P] [US1] Update `src/parallel.py` to calculate and output the identical specific metrics structure.

---

## Phase 4: User Story 2 - Benchmark Range Query Read Performance (Priority: P1)

**Goal**: Compare performance of standard range queries versus queries optimized for YugabyteDB's distributed architecture.

**Independent Test**: Pre-load data, run `read_standard` and `read_optimized` modes, and verify QPS/Latency outputs differences.

### Implementation for User Story 2

- [x] T007 [P] [US2] Update `src/db_utils.py` to create `test_data_optimized` table and the `idx_score_name` covering index.
- [x] T008 [US2] Implement thread pool continuous read execution logic in `src/read_bench.py` (for standard table).
- [x] T009 [US2] Implement optimized range query logic in `src/read_bench.py` (explicit ASC/DESC, Cover Index usage).
- [x] T010 [US2] Integrate `read_standard` and `read_optimized` routing into `src/main.py`.

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 [P] Documentation updates in `README.md` containing run commands.
- [x] T012 Code cleanup and verify safe concurrency thread joins.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: All depend on Foundational phase
- **Polish (Final Phase)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational
- **User Story 2 (P1)**: Can start after Foundational

### Parallel Opportunities

- Docker compose modifications (T001) and read_bench.py skeleton (T002).
- CLI args (T003) and standard schema details (T004).
- Write metrics updates across `baseline.py` (T005) and `parallel.py` (T006).

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup + Foundational
2. Implement US1 Write Benchmarks
3. Validate Output metrics

### Incremental Delivery

1. Deliver Write Benchmark metrics adjustments (US1).
2. Deliver Schema/Index configurations and basic Read loop (US2).
3. Validate explicit YugabyteDB Optimized Read Queries (US2).
