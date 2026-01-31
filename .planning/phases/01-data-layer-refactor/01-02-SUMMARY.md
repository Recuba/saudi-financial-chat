---
phase: 01-data-layer-refactor
plan: 02
subsystem: data-layer
tags: [query-routing, keyword-matching, auto-routing, sidebar-refactor]

dependency_graph:
  requires:
    - phase: 01-01
      provides: load_tasi_data function with 7 views, get_view function, VIEW_NAMES
  provides:
    - route_query function for keyword-based view selection
    - QueryRouter class for extensibility
    - Automatic query routing in app.py
    - Simplified sidebar without dataset selector
  affects:
    - 01-03 (PandasAI integration will use routed views)
    - Phase 2 (LLM fallback routing)

tech_stack:
  added: []
  patterns:
    - Keyword-based query routing with priority order
    - View routing with reason tracking
    - Extensible router class for future LLM integration

key_files:
  created:
    - utils/query_router.py
  modified:
    - app.py
    - components/sidebar.py
    - components/__init__.py

key_decisions:
  - "Priority order: ranking > sector > timeseries > latest > general"
  - "Return (view_name, reason) tuple for transparency"
  - "Default to tasi_financials for unmatched queries"

patterns_established:
  - "Query routing pattern: route_query(prompt) returns (view, reason)"
  - "Routing transparency: show routed view name via st.caption"

metrics:
  duration: 5min
  completed: 2026-02-01
---

# Phase 1 Plan 2: Query Router Implementation Summary

**Keyword-based query routing to optimal views with automatic integration in app.py and simplified sidebar**

## Performance

- **Duration:** 5 min
- **Started:** 2026-02-01T00:18:00Z
- **Completed:** 2026-02-01T00:23:00Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Created query router with keyword pattern matching for ranking/sector/timeseries/latest queries
- Integrated automatic routing in app.py before PandasAI processing
- Removed dataset selector from sidebar (users no longer need to choose)
- Added view info section showing available views and their purposes

## Task Commits

Each task was committed atomically:

1. **Task 1: Create query_router.py** - `35f01b2` (feat)
2. **Task 2: Integrate router in app.py** - `595aaa7` (feat)
3. **Task 3: Simplify sidebar.py** - `ab09d43` (refactor)

## Files Created/Modified

- `utils/query_router.py` - New module with route_query() and QueryRouter class
- `app.py` - Integrated routing before PandasAI, uses load_tasi_data()
- `components/sidebar.py` - Removed dataset selector, added view info section
- `components/__init__.py` - Updated exports to reflect sidebar changes

## Key Components

### Query Router (utils/query_router.py)

```python
KEYWORD_PATTERNS = {
    "ranking": ["top", "bottom", "best", "worst", "highest", "lowest", "rank"],
    "sector": ["sector", "industry", "compare sector", "benchmark"],
    "timeseries": ["growth", "trend", "yoy", "year over year", "change", "over time"],
    "latest": ["latest", "current", "recent", "now", "today", "2024", "2025"],
}

VIEW_MAPPING = {
    "ranking": "top_bottom_performers",
    "sector": "sector_benchmarks_latest",
    "timeseries": "company_annual_timeseries",
    "latest": "latest_financials",
    "general": "tasi_financials",
}

def route_query(query: str) -> Tuple[str, str]:
    """Returns (view_name, reason) based on keyword matching"""
```

### Routing Integration (app.py)

```python
if prompt:
    view_name, route_reason = route_query(prompt)
    selected_df = data[view_name]
    st.caption(f"Using: {view_name}")
    response = process_query(prompt, selected_df)
```

## Decisions Made

1. **Priority order for keyword matching:** ranking > sector > timeseries > latest > general
   - Rationale: Ranking queries are most specific, general fallback ensures queries always work

2. **Return (view_name, reason) tuple:** Provides transparency for debugging and user feedback
   - Rationale: Users and developers can understand why a view was selected

3. **Default to tasi_financials:** Unmatched queries get full dataset
   - Rationale: Better to be slow than wrong; full dataset has all data

4. **QueryRouter class for extensibility:** Allows adding LLM fallback in Phase 2
   - Rationale: Future-proofing without over-engineering Phase 1

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**components/__init__.py needed updating** - When removing render_dataset_selector() from sidebar.py, the package __init__.py still tried to import it. Fixed by updating the imports and __all__ list. This was expected maintenance for the refactoring task.

## Verification Results

```
PASS: top 10 by revenue -> top_bottom_performers
PASS: compare sectors -> sector_benchmarks_latest
PASS: revenue growth trend -> company_annual_timeseries
PASS: latest profit for SABIC -> latest_financials
PASS: show all companies -> tasi_financials

ALL TESTS PASSED
```

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**For manual verification:**
- Run `streamlit run app.py` and test queries
- Verify routing displays "Using: {view_name}" caption
- Verify no dataset selector in sidebar

**Phase 1 complete after this plan:**
- Data loader refactored (01-01)
- Query router implemented (01-02)
- Ready for Phase 2 (PandasAI enhancements)

---
*Phase: 01-data-layer-refactor*
*Completed: 2026-02-01*
