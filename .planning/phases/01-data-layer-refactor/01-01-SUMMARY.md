---
phase: 01-data-layer-refactor
plan: 01
subsystem: data-layer
tags: [parquet, data-loading, tasi-optimized, caching]

dependency_graph:
  requires: []
  provides:
    - load_tasi_data function with 7 views
    - get_view function for individual view access
    - VIEW_NAMES constant
    - Streamlit caching with TTL=3600
  affects:
    - 01-02 (query router will use get_view)
    - 01-03 (PandasAI integration will use routed views)

tech_stack:
  added: []
  patterns:
    - Multi-view parquet loading
    - Streamlit cache_data with TTL
    - Deprecated function wrappers for backward compat

key_files:
  created: []
  modified:
    - utils/data_loader.py
    - tests/test_data_loader.py

decisions:
  - id: 01-01-1
    decision: Keep deprecated wrappers for backward compatibility
    rationale: Avoid breaking existing code during transition
    alternatives: Remove old functions (would break imports)

metrics:
  duration: 3 minutes
  completed: 2026-01-31
---

# Phase 1 Plan 1: Data Loader Refactor Summary

Refactored data loading to use the new tasi_optimized parquet structure with 7 pre-optimized views.

## One-liner

Multi-view parquet loading from tasi_optimized with Streamlit caching (TTL=3600) and deprecated wrappers for backward compatibility.

## What Was Built

### Core Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `load_tasi_data()` | Load all 7 optimized views | Dict[str, DataFrame] |
| `get_view(name)` | Get single view by name | DataFrame |
| `get_view_info()` | Get statistics about views | Dict with counts |

### VIEW_NAMES Constant

```python
VIEW_NAMES = [
    "tasi_financials",        # 4,748 rows - full dataset
    "latest_financials",      # 302 rows - latest per company
    "latest_annual",          # 302 rows - latest annual per company
    "ticker_index",           # 302 rows - company metadata
    "company_annual_timeseries",  # 1,155 rows - with YoY growth
    "sector_benchmarks_latest",   # 6 rows - sector aggregates
    "top_bottom_performers",      # 160 rows - rankings
]
```

### Caching Configuration

- Decorator: `@st.cache_data(show_spinner=False, ttl=3600)`
- TTL: 1 hour (3600 seconds) per research recommendation

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing imports in utils/__init__.py**
- **Found during:** Task 1 verification
- **Issue:** `get_column_info`, `get_dataset_display_name`, `DATASET_DISPLAY_NAMES` were imported by utils/__init__.py but removed
- **Fix:** Added deprecated wrappers for all three
- **Files modified:** utils/data_loader.py

## API Changes

### New API (Primary)

```python
from utils.data_loader import load_tasi_data, get_view, VIEW_NAMES

# Load all views
data = load_tasi_data()

# Access specific view
df = get_view("latest_financials")
```

### Deprecated API (Backward Compatible)

```python
# These still work but log deprecation warnings
from utils.data_loader import load_data, get_dataset

data = load_data()  # Maps to tasi_optimized views
df = get_dataset("analytics")  # Maps to tasi_financials
```

## Test Coverage

16 tests covering:
- `load_tasi_data()` returns dict with 7 views
- Each view is a DataFrame
- `get_view()` returns correct data
- `get_view()` raises ValueError for invalid names
- `VIEW_NAMES` contains all 7 names
- Key columns exist in views
- Row counts match expected (302 companies, 4748 total records)
- Backward compatibility for deprecated functions

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 69f317a | feat | Refactor data_loader for tasi_optimized views |
| fea9fad | test | Update tests for tasi_optimized view structure |

## Verification Results

```
Loaded 7 views: ['tasi_financials', 'latest_financials', 'latest_annual',
                  'ticker_index', 'company_annual_timeseries',
                  'sector_benchmarks_latest', 'top_bottom_performers']

pytest tests/test_data_loader.py: 16 passed in 0.84s
```

## Next Phase Readiness

**For 01-02 (Query Router):**
- `get_view(name)` function ready for routing decisions
- `VIEW_NAMES` constant available for validation
- All 7 views loadable and accessible

**No blockers identified.**
