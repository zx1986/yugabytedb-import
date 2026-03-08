# Data Model: YugabyteDB Read/Write Benchmark Tool

## 1. Entities

### `test_data` (Standard Benchmark Table)
- **Purpose**: Baseline table for traditional batch loading and unoptimized range queries.
- **Fields**:
  - `id` (INT): Primary Key
  - `name` (VARCHAR): Arbitrary string data
  - `email` (VARCHAR): Arbitrary string data
  - `score` (FLOAT): Numeric value for sorting/filtering
  - `created_at` (TIMESTAMP): Time-series data simulation
- **Indexes**:
  - Default Primary Key (ASC)

### `test_data_optimized` (Optimized Benchmark Table)
- **Purpose**: Target table for YugabyteDB specific read query optimizations.
- **Fields**: identical to `test_data`.
- **Indexes**:
  - Primary Key (ASC)
  - Secondary Index: `idx_score_name`
    - **Keys**: `score DESC`, `name ASC`
    - **Type**: Covering Index
    - **INCLUDE**: `(email, created_at)`
    - **Note**: Avoids double lookups (index -> main table) by covering the SELECT projection. Explicit ASC/DESC matches the test query order to prevent DISTINCT or in-memory sorts.

## 2. Validation Rules & Constraints

- No specific business validations are necessary. The benchmark requires deterministic mock data containing varying distributions to test index performance adequately.
- The `id` must be sequential or strictly uniformly distributed to test range splits in YugabyteDB effectively.

## 3. Storage Considerations

- YugabyteDB automatically handles sharding. 
- Generating up to 3GiB of data equates roughly to ~30-50 million rows of the above schema, which will be distributed across the 3 tablet servers.
