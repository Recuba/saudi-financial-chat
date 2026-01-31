---
phase: 02-query-routing-engine
plan: 01
subsystem: query-routing
tags: [entity-extraction, keyword-matching, routing, testing]
dependency-graph:
  requires: [01-data-layer-refactor]
  provides: [enhanced-query-router, entity-extraction, expanded-keywords]
  affects: [02-02-llm-classification]
tech-stack:
  added: []
  patterns: [dependency-injection, fuzzy-matching, lookup-index]
key-files:
  created:
    - tests/test_query_router.py
  modified:
    - utils/query_router.py
    - app.py
decisions:
  - id: D-0201-01
    summary: Use difflib.SequenceMatcher for fuzzy matching
    rationale: Standard library, no new dependencies required
metrics:
  duration: 4 minutes
  completed: 2026-02-01
---

# Phase 02 Plan 01: Entity Extraction & Enhanced Keywords Summary

Enhanced QueryRouter with entity extraction capability (tickers, company names, sectors) using ticker_index lookup and difflib fuzzy matching. Expanded keyword patterns for better routing coverage.

## What Changed

### Enhanced QueryRouter (utils/query_router.py)

1. **Expanded KEYWORD_PATTERNS** with additional terms:
   - ranking: added "biggest", "smallest", "largest", "most", "least", "leader"
   - sector: added "by sector", "per sector", "sector average", "industry average"
   - timeseries: added "history", "historical", "years", "quarterly", "annual"
   - latest: added "last quarter", "most recent", "q1", "q2", "q3", "q4"

2. **Constructor accepts ticker_index** for entity extraction:
   ```python
   router = QueryRouter(ticker_index=data['ticker_index'])
   ```

3. **New _build_lookup_index() method** creates fast lookup structures:
   - ticker_to_company: dict mapping ticker string to company name
   - company_names: list of company names for matching
   - name_to_ticker: dict mapping lowercase company name to ticker
   - sectors: list of unique sectors

4. **New _extract_entities() method** extracts:
   - Tickers: 4-digit numbers validated against ticker_index
   - Companies: Substring match + fuzzy match (>0.6 ratio for names >5 chars)
   - Sectors: Alias mapping (e.g., "bank" -> "Financials")

5. **Updated route() signature** returns 3-tuple:
   ```python
   view_name, reason, entities = router.route(query)
   # entities = {'tickers': [], 'companies': [], 'sectors': []}
   ```

6. **Backward compatibility** maintained via route_query() function

### Comprehensive Test Suite (tests/test_query_router.py)

Created 33 test cases in 6 test classes:
- TestKeywordPatterns: Verifies all keyword intents
- TestPriorityOrder: Verifies ranking > sector > timeseries > latest
- TestEntityExtraction: Verifies ticker, company, sector extraction
- TestBackwardCompatibility: Verifies route_query() and router without index
- TestEdgeCases: Empty query, None, case insensitivity
- TestConstants: Module constants completeness

### App Integration (app.py)

- QueryRouter instantiated with ticker_index after data load
- Entity detection displayed in routing caption: "Using: view_name | Detected: 1010"

## Commits

| Hash | Type | Description |
|------|------|-------------|
| 159e84f | feat | Enhance QueryRouter with entity extraction and expanded keywords |
| 4d62a6f | test | Add comprehensive query router test suite (33 tests) |
| 30608f1 | feat | Integrate enhanced router with entity display in app |

## Verification Results

- All 33 tests pass
- QueryRouter.route() returns correct 3-tuple
- Entity extraction correctly identifies tickers, company names, sectors
- Backward compatibility verified with route_query()

## Deviations from Plan

None - plan executed exactly as written.

## Decisions Made

| ID | Decision | Rationale |
|----|----------|-----------|
| D-0201-01 | Use difflib.SequenceMatcher for fuzzy matching | Standard library, no new dependencies, adequate accuracy for company name matching |

## Next Phase Readiness

**Ready for 02-02 (LLM Intent Classification):**
- QueryRouter has llm_enabled parameter (currently unused, defaults to False)
- Entity extraction provides context for LLM classification prompt
- Routing architecture supports adding _llm_classify() method

**No blockers identified.**
