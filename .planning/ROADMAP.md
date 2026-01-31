# Roadmap: Ra'd AI v2

## Overview

Ra'd AI v2 transforms the chatbot from a manual dataset-selection model to an intelligent query-routing system. Phase 1 migrates the backend to the new optimized parquet structure. Phase 2 implements smart query routing via keyword matching and LLM classification. Phase 3 removes the sidebar and delivers a clean chatbox-only interface where users simply ask questions without understanding the underlying data structure.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Data Layer Refactor** - Migrate backend to tasi_optimized parquet views
- [x] **Phase 2: Query Routing Engine** - Implement keyword + LLM-based query routing
- [x] **Phase 3: UI Simplification** - Remove sidebar, streamline to chatbox-only interface

## Phase Details

### Phase 1: Data Layer Refactor
**Goal**: Backend loads and serves data from the new `tasi_optimized` parquet structure
**Depends on**: Nothing (first phase)
**Requirements**: DATA-01, DATA-02, DATA-03
**Success Criteria** (what must be TRUE):
  1. App loads data from `data/tasi_optimized/` directory without errors
  2. All 7 parquet views accessible (tasi_financials, latest_financials, latest_annual, company_annual_timeseries, sector_benchmarks_latest, top_bottom_performers, ticker_index)
  3. PandasAI receives DataFrame and can execute queries successfully
  4. Query results render correctly (no regression from current behavior)
**Plans:** 2 plans

Plans:
- [x] 01-01-PLAN.md - Data layer foundation (refactor data_loader.py, update tests)
- [x] 01-02-PLAN.md - Router and integration (create query_router.py, update app.py, simplify sidebar)

### Phase 2: Query Routing Engine
**Goal**: System automatically routes queries to the optimal data view based on intent
**Depends on**: Phase 1
**Requirements**: ROUTE-01, ROUTE-02, ROUTE-03, ROUTE-04
**Success Criteria** (what must be TRUE):
  1. Query with "latest" or "current" keyword routes to latest_financials.parquet
  2. Query mentioning company name or ticker resolves via ticker_index lookup
  3. Ambiguous queries trigger LLM intent classification before routing
  4. Complex or unknown queries fall back to full tasi_financials.parquet
  5. Generated PandasAI code operates on the routed DataFrame
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md - Entity extraction and enhanced keywords (expand patterns, add ticker/company detection, tests)
- [x] 02-02-PLAN.md - LLM intent classification (add LLM fallback for ambiguous queries, confidence scoring)

### Phase 3: UI Simplification
**Goal**: Clean chatbox-only interface with no visible configuration complexity
**Depends on**: Phase 2
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria** (what must be TRUE):
  1. No sidebar visible on any screen size
  2. User can enter query and receive response without any prior configuration
  3. Comparison mode accessible via chat command or inline toggle (not sidebar)
  4. LLM defaults to Gemini 2.0 Flash with no visible model selector
**Plans:** 1 plan

Plans:
- [x] 03-01-PLAN.md - Remove sidebar and simplify interface (CSS hiding, remove sidebar code, update tests)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Layer Refactor | 2/2 | Complete | 2026-02-01 |
| 2. Query Routing Engine | 2/2 | Complete | 2026-02-01 |
| 3. UI Simplification | 1/1 | Complete | 2026-02-01 |

---
*Roadmap created: 2026-01-31*
*Depth: quick (3 phases)*
*Coverage: 11/11 v1 requirements mapped*
*Phase 1 planned: 2026-02-01*
*Phase 2 planned: 2026-02-01*
*Phase 3 planned: 2026-02-01*
