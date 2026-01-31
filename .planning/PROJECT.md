# Ra'd AI v2 - Smart Query Routing

## What This Is

Ra'd AI is a financial analytics chatbot for querying Saudi Tadawul stock exchange data using natural language. Users ask questions in plain English/Arabic, and the system translates queries to Python via PandasAI, executes them against optimized parquet views, and returns formatted results with optional visualizations.

## Core Value

Users can ask financial questions naturally and get accurate answers without understanding database structure or query languages.

## Requirements

### Validated

- User can enter natural language queries about Saudi company financials — existing
- System translates queries to Python via PandasAI and executes against data — existing
- Results displayed as tables, charts, or text based on response type — existing
- Chat history preserved during session — existing
- Error messages provide guidance on query refinement — existing
- Comparison mode for side-by-side entity analysis — existing
- Dark theme with gold accent styling — existing

### Active

- [ ] Remove sidebar completely — clean chatbox-only interface
- [ ] Smart query routing via keyword pattern matching
- [ ] LLM-based intent classification for ambiguous queries
- [ ] Fallback to full dataset when routing uncertain
- [ ] Backend uses new `tasi_optimized` database structure
- [ ] Ticker/company name resolution via `ticker_index.parquet`
- [ ] Comparison mode preserved with streamlined UI

### Out of Scope

- User authentication — not needed for public financial data
- Query history persistence across sessions — complexity vs value
- Custom model fine-tuning — OpenRouter provides sufficient models
- Real-time data updates — XBRL filings are periodic, not real-time

## Context

**Existing Codebase:**
- Streamlit-based web app with component architecture
- PandasAI v3 for natural language to Python translation
- OpenRouter API for LLM access (Gemini 2.0 Flash default)
- Currently requires users to select dataset manually

**New Database Structure (`data/tasi_optimized/`):**
- `tasi_financials.parquet` — Full dataset (4,748 records, 44 columns)
- `latest_financials.parquet` — Most recent per company (302 records)
- `latest_annual.parquet` — Most recent annual per company (288 records)
- `company_annual_timeseries.parquet` — YoY growth data (1,155 records)
- `sector_benchmarks_latest.parquet` — Sector statistics (6 sectors)
- `top_bottom_performers.parquet` — Rankings (160 records)
- `ticker_index.parquet` — Company lookup (302 companies)
- `metadata.json` — Schema and optimization details

**Query Routing Logic:**
| Pattern | Target View |
|---------|-------------|
| "latest", "current", "now" | `latest_financials.parquet` |
| "annual", "yearly", "FY" | `latest_annual.parquet` |
| "trend", "growth", "YoY", "over time" | `company_annual_timeseries.parquet` |
| "sector", "industry", "average" | `sector_benchmarks_latest.parquet` |
| "top", "best", "worst", "ranking" | `top_bottom_performers.parquet` |
| Company name/ticker mentioned | Resolve via `ticker_index.parquet` |
| Ambiguous | LLM classification |
| Unknown/complex | `tasi_financials.parquet` (full) |

## Constraints

- **Tech stack**: Streamlit + PandasAI v3 + OpenRouter — existing infrastructure
- **Data format**: Parquet files only — no database server
- **UI framework**: Must remain Streamlit — no React/Vue migration
- **Deployment**: Streamlit Cloud compatible

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hybrid routing (keywords + LLM) | Balance speed and accuracy | — Pending |
| Remove sidebar completely | Simplify UX, users shouldn't care about data structure | — Pending |
| Keep comparison mode | Users find side-by-side analysis valuable | — Pending |
| Fallback to full dataset | Better to be slow than wrong | — Pending |

---
*Last updated: 2026-01-31 after initialization*
