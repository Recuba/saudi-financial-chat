# Requirements: Ra'd AI v2

**Defined:** 2026-01-31
**Core Value:** Users can ask financial questions naturally and get accurate answers without understanding database structure

## v1 Requirements

### Query Routing

- [ ] **ROUTE-01**: System detects query intent via keyword pattern matching
- [ ] **ROUTE-02**: Ambiguous queries classified by LLM before execution
- [ ] **ROUTE-03**: Unknown queries fall back to full dataset (`tasi_financials.parquet`)
- [ ] **ROUTE-04**: Company/ticker names resolved via `ticker_index.parquet` lookup

### Data Layer

- [ ] **DATA-01**: App loads data from `data/tasi_optimized/` directory
- [ ] **DATA-02**: Query routed to appropriate parquet view based on detected intent
- [ ] **DATA-03**: PandasAI v3 configured with routed DataFrame before query execution

### UI Simplification

- [ ] **UI-01**: Sidebar removed completely from interface
- [ ] **UI-02**: Chat interface is the primary interaction method
- [ ] **UI-03**: Comparison mode accessible via chat command or toggle (no sidebar)
- [ ] **UI-04**: LLM model defaulted to Gemini 2.0 Flash (no visible selector)

## v2 Requirements

### Enhanced Routing

- **ROUTE-05**: Multi-view queries that JOIN data from multiple parquet files
- **ROUTE-06**: Query caching for repeated questions
- **ROUTE-07**: Routing confidence scores displayed to user

### Advanced Features

- **ADV-01**: Voice input for queries
- **ADV-02**: Export results to Excel/PDF
- **ADV-03**: Scheduled query execution

## Out of Scope

| Feature | Reason |
|---------|--------|
| User authentication | Public financial data, no personalization needed |
| Persistent query history | Session-based is sufficient for v1 |
| Custom model fine-tuning | OpenRouter models are sufficient |
| Real-time data updates | XBRL filings are periodic, not real-time |
| Multiple language UI | English/Arabic queries work, UI stays English |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| ROUTE-01 | TBD | Pending |
| ROUTE-02 | TBD | Pending |
| ROUTE-03 | TBD | Pending |
| ROUTE-04 | TBD | Pending |
| DATA-01 | TBD | Pending |
| DATA-02 | TBD | Pending |
| DATA-03 | TBD | Pending |
| UI-01 | TBD | Pending |
| UI-02 | TBD | Pending |
| UI-03 | TBD | Pending |
| UI-04 | TBD | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 0
- Unmapped: 11

---
*Requirements defined: 2026-01-31*
*Last updated: 2026-01-31 after initial definition*
