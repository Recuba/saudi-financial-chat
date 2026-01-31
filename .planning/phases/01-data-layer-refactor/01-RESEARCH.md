# Phase 1: Data Layer Refactor - Research

**Researched:** 2026-01-31
**Domain:** Parquet data loading, PandasAI v3, query routing
**Confidence:** HIGH

## Summary

This phase migrates the backend from the legacy 4-file parquet structure to the new `tasi_optimized` parquet views. The current implementation in `utils/data_loader.py` loads files from `data/` with manual dataset selection via sidebar. The new structure in `data/tasi_optimized/` provides 7 optimized views with pre-computed aggregations and query recommendations.

The migration requires: (1) refactoring data_loader.py to load from tasi_optimized, (2) implementing hybrid query routing to select the optimal view based on query intent, (3) updating PandasAI integration to use the routed DataFrame, and (4) removing the manual dataset selection from sidebar.

An existing `tasi_query_helper.py` provides routing recommendations and semantic query support that can be leveraged.

**Primary recommendation:** Implement a QueryRouter class that uses keyword matching (fast path) with optional LLM classification (fallback) to route queries to the optimal parquet view, defaulting to `tasi_financials.parquet` for uncertain queries.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pandas | >=2.0.0 | DataFrame operations | Already in use, required by PandasAI |
| pandasai | 3.0.0 | Natural language queries | Already configured with LiteLLM |
| pyarrow | (current) | Parquet I/O | Already in use, optimal for parquet |
| streamlit | >=1.30.0 | UI framework | Already in use with caching |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pandasai-litellm | (current) | LLM backend | Already configured for OpenRouter |
| pyyaml | (current) | Schema loading | For semantic schema (tasi_semantic_schema.yaml) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| pyarrow parquet | polars | Faster reads, but adds dependency and changes API |
| keyword routing | pure LLM routing | Slower, costs tokens, less deterministic |

**Installation:**
```bash
# No new packages needed - all already installed
pip install pandas>=2.0.0 pandasai>=3.0.0 pyarrow pyyaml
```

## Architecture Patterns

### Recommended Project Structure
```
utils/
    data_loader.py         # Refactor: load from tasi_optimized
    query_router.py        # NEW: route queries to optimal view
    llm_config.py          # Existing: LLM configuration

data/tasi_optimized/
    tasi_financials.parquet      # Full dataset (4,748 rows)
    latest_financials.parquet    # Latest per company (302 rows)
    latest_annual.parquet        # Latest annual (302 rows)
    ticker_index.parquet         # Ticker lookup (302 rows)
    views/
        company_annual_timeseries.parquet   # With YoY growth
        sector_benchmarks_latest.parquet    # Sector aggregates
        top_bottom_performers.parquet       # Rankings
```

### Pattern 1: Query Router with Hybrid Routing
**What:** Classify query intent using keywords first, LLM fallback for ambiguous cases
**When to use:** Every query before passing to PandasAI
**Example:**
```python
# Source: Prior decision - hybrid routing for speed/accuracy balance
class QueryRouter:
    KEYWORD_PATTERNS = {
        "latest": ["latest", "current", "recent", "now", "today"],
        "ranking": ["top", "bottom", "best", "worst", "highest", "lowest"],
        "sector": ["sector", "industry", "compare sector"],
        "timeseries": ["growth", "trend", "over time", "yoy", "year over year"],
    }

    def route(self, query: str) -> str:
        """Return view name based on query intent."""
        query_lower = query.lower()

        # Fast path: keyword matching
        if any(kw in query_lower for kw in self.KEYWORD_PATTERNS["ranking"]):
            return "top_bottom_performers"
        if any(kw in query_lower for kw in self.KEYWORD_PATTERNS["sector"]):
            return "sector_benchmarks_latest"
        # ... more patterns

        # Default: full dataset (per prior decision - better slow than wrong)
        return "tasi_financials"
```

### Pattern 2: Cached Multi-View Data Loader
**What:** Load all views into memory at startup with Streamlit caching
**When to use:** App initialization
**Example:**
```python
# Source: Existing pattern in data_loader.py
@st.cache_data(show_spinner=False)
def load_tasi_data() -> Dict[str, pd.DataFrame]:
    """Load all tasi_optimized views."""
    base = Path(__file__).parent.parent / "data" / "tasi_optimized"

    return {
        "tasi_financials": pd.read_parquet(base / "tasi_financials.parquet"),
        "latest_financials": pd.read_parquet(base / "latest_financials.parquet"),
        "latest_annual": pd.read_parquet(base / "latest_annual.parquet"),
        "ticker_index": pd.read_parquet(base / "ticker_index.parquet"),
        "company_annual_timeseries": pd.read_parquet(base / "views/company_annual_timeseries.parquet"),
        "sector_benchmarks_latest": pd.read_parquet(base / "views/sector_benchmarks_latest.parquet"),
        "top_bottom_performers": pd.read_parquet(base / "views/top_bottom_performers.parquet"),
    }
```

### Pattern 3: PandasAI with Routed DataFrame
**What:** Process query with appropriate view selected by router
**When to use:** In chat.py process_query function
**Example:**
```python
# Source: Existing pattern in chat.py + new routing
def process_query(query: str, router: QueryRouter, data: Dict) -> Dict:
    view_name = router.route(query)
    df = data[view_name]

    pai_df = pai.DataFrame(df)
    response = pai_df.chat(query)
    return format_response(response)
```

### Anti-Patterns to Avoid
- **Manual dataset selection:** Users should not need to understand data structure (prior decision)
- **Always loading full dataset:** Wastes resources when smaller view suffices
- **Pure LLM routing:** Too slow and non-deterministic for simple cases
- **Hardcoded file paths:** Use Path() for cross-platform compatibility

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Query intent detection | Custom NLP | Keyword patterns + existing metadata.json query_recommendations | Simple, fast, deterministic |
| Arabic column resolution | Custom mapping | TASIQueryHelper from tasi_query_helper.py | Already has arabic_map, synonym_map |
| Sector aggregates | df.groupby() at query time | sector_benchmarks_latest.parquet | Pre-computed, faster |
| YoY growth calculation | Manual lag/pct_change | company_annual_timeseries.parquet | Pre-computed columns |
| Top/bottom rankings | df.nlargest/nsmallest | top_bottom_performers.parquet | Pre-computed per metric |

**Key insight:** The tasi_optimized structure already has pre-computed views for common query patterns. Route to these views instead of computing at query time.

## Common Pitfalls

### Pitfall 1: Breaking Existing Tests
**What goes wrong:** Changing data_loader.py signature breaks 20+ test imports
**Why it happens:** Tests import specific functions like `get_dataset("analytics")`
**How to avoid:**
- Maintain backward compatibility during transition OR
- Update all tests in same commit
- Run `pytest` before committing changes
**Warning signs:** Test failures mentioning missing keys or functions

### Pitfall 2: Sidebar Dataset Selection Conflicts
**What goes wrong:** Sidebar still shows old dataset names, causes confusion
**Why it happens:** Sidebar.py imports from data_loader and displays dataset choices
**How to avoid:**
- Remove dataset selector completely (prior decision)
- Update sidebar to show view metadata instead of selection
**Warning signs:** Mismatch between sidebar display and actual data loaded

### Pitfall 3: Comparison Mode Breaks
**What goes wrong:** Comparison mode expects `company_name` column
**Why it happens:** Different parquet views have different schemas
**How to avoid:**
- All routing logic must validate required columns exist
- `tasi_financials`, `latest_financials`, `latest_annual` all have `company_name`
- Route comparison queries to views with `company_name`
**Warning signs:** KeyError on company_name in comparison mode

### Pitfall 4: PandasAI Config Reset
**What goes wrong:** LLM not configured error after data layer changes
**Why it happens:** `pai.config.set({"llm": llm})` state is global, may be cleared
**How to avoid:**
- LLM initialization in llm_config.py is separate from data loading
- Verify LLM config persists across data layer changes
- Keep LLM config initialization in app.py startup
**Warning signs:** "LLM not configured" errors after refactor

### Pitfall 5: Caching Stale Data
**What goes wrong:** Old data served after parquet files updated
**Why it happens:** `@st.cache_data` caches indefinitely by default
**How to avoid:**
- Add TTL to cache: `@st.cache_data(ttl=3600)`
- Clear cache on app restart for development
- Consider file modification time in cache key
**Warning signs:** Data doesn't update after file changes

## Code Examples

Verified patterns from official sources and existing codebase:

### Loading Parquet with Streamlit Caching
```python
# Source: Existing pattern in utils/data_loader.py
@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, pd.DataFrame]:
    base_path = get_data_path() / "tasi_optimized"
    try:
        data = {
            "tasi_financials": pd.read_parquet(base_path / "tasi_financials.parquet"),
            # ... more views
        }
        logger.info(f"Loaded {len(data)} datasets successfully")
        return data
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
```

### PandasAI v3 Configuration
```python
# Source: Existing utils/llm_config.py + PandasAI docs
import pandasai as pai
from pandasai_litellm.litellm import LiteLLM

def initialize_llm(model_id: Optional[str] = None):
    llm = LiteLLM(
        model=selected_model,
        api_key=api_key,
    )
    pai.config.set({"llm": llm})
    return llm, None
```

### PandasAI Query Execution
```python
# Source: Existing components/chat.py
import pandasai as pai

def process_query(query: str, dataset: pd.DataFrame) -> Dict:
    df = pai.DataFrame(dataset)
    response = df.chat(query)
    return format_response(response)
```

### Query Router Implementation
```python
# Source: Adapted from data/files2/tasi_query_helper.py
class QueryRouter:
    VIEW_MAPPING = {
        "latest": "latest_financials",
        "latest_annual": "latest_annual",
        "ranking": "top_bottom_performers",
        "sector": "sector_benchmarks_latest",
        "timeseries": "company_annual_timeseries",
        "general": "tasi_financials",
    }

    def route(self, query: str) -> Tuple[str, str]:
        """Return (view_name, reason) based on query."""
        query_lower = query.lower()

        # Ranking queries
        if any(w in query_lower for w in ["top", "bottom", "best", "worst", "highest", "lowest"]):
            return "top_bottom_performers", "Ranking query detected"

        # Sector comparison
        if "sector" in query_lower and any(w in query_lower for w in ["compare", "average", "benchmark"]):
            return "sector_benchmarks_latest", "Sector comparison detected"

        # Time series / growth
        if any(w in query_lower for w in ["growth", "trend", "yoy", "year over year", "change"]):
            return "company_annual_timeseries", "Time series query detected"

        # Latest data
        if any(w in query_lower for w in ["latest", "current", "recent", "2024", "2025"]):
            return "latest_financials", "Latest data query detected"

        # Default: full dataset (per decision - better slow than wrong)
        return "tasi_financials", "General query - using full dataset"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual dataset selection | Auto-routing based on query | This phase | Users don't need to understand data |
| Single monolithic parquet | Optimized views | Pre-existing in tasi_optimized | Faster queries for common patterns |
| Separate filings/facts/ratios | Unified wide format | Pre-existing | Simpler queries, no joins needed |

**Deprecated/outdated:**
- `data/filings.parquet`, `data/facts_numeric.parquet`, `data/ratios.parquet`, `data/analytics_view.parquet`: Replaced by tasi_optimized structure

## Open Questions

Things that couldn't be fully resolved:

1. **LLM fallback for routing - when to trigger?**
   - What we know: Prior decision says hybrid (keywords + LLM)
   - What's unclear: Exact threshold for "uncertain" to trigger LLM
   - Recommendation: Start with keyword-only, add LLM fallback in future phase if needed

2. **Cache invalidation strategy**
   - What we know: Streamlit cache_data works, can add TTL
   - What's unclear: How often parquet files will be updated
   - Recommendation: Use TTL=3600 (1 hour), sufficient for most use cases

3. **Arabic query support**
   - What we know: TASIQueryHelper has Arabic mappings
   - What's unclear: Should router also handle Arabic keywords?
   - Recommendation: Integrate TASIQueryHelper's translate_query() in router

## Sources

### Primary (HIGH confidence)
- `utils/data_loader.py` - Current implementation analyzed
- `components/chat.py` - PandasAI integration pattern
- `data/tasi_optimized/metadata.json` - Query recommendations from data creator
- `data/files2/tasi_query_helper.py` - Existing routing logic

### Secondary (MEDIUM confidence)
- [PandasAI LLM Setup Docs](https://docs.pandas-ai.com/v3/large-language-models) - Configuration API
- `requirements.txt` - Version constraints (pandasai>=3.0.0)

### Tertiary (LOW confidence)
- WebSearch results for PandasAI v3 best practices - General patterns

## New Data Structure Reference

### View Schemas

| View | Rows | Columns | Key Columns | Best For |
|------|------|---------|-------------|----------|
| tasi_financials | 4,748 | 44 | All financials + ratios | General queries, fallback |
| latest_financials | 302 | 44 | Same schema, latest per company | "Current", "latest" queries |
| latest_annual | 302 | 44 | Same schema, latest annual | Annual comparisons |
| ticker_index | 302 | 9 | ticker, company_name, sector, stats | Company lookup |
| company_annual_timeseries | 1,155 | 16 | Core metrics + *_yoy columns | Growth, trends |
| sector_benchmarks_latest | 6 | 25 | sector, *_mean, *_median, *_std | Sector comparison |
| top_bottom_performers | 160 | 8 | ticker, value, rank, metric, category | Rankings |

### metadata.json Query Recommendations
```json
{
  "query_recommendations": {
    "year_filter": "Use by_year/ partitioned dataset",
    "latest_data": "Use latest_financials.parquet or latest_annual.parquet",
    "sector_comparison": "Use views/sector_benchmarks_latest.parquet",
    "single_company": "Query main file with ticker filter",
    "time_series": "Use views/company_annual_timeseries.parquet"
  }
}
```

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Using existing libraries, no changes needed
- Architecture: HIGH - Follows existing patterns, clear migration path
- Pitfalls: HIGH - Based on direct codebase analysis

**Research date:** 2026-01-31
**Valid until:** 2026-03-01 (stable domain, existing patterns)

---

## RESEARCH COMPLETE

**Phase:** 1 - Data Layer Refactor
**Confidence:** HIGH

### Key Findings

1. Current data loading is in `utils/data_loader.py`, serving 4 legacy parquet files with manual sidebar selection
2. New `tasi_optimized/` has 7 pre-optimized views with query recommendations in metadata.json
3. Existing `tasi_query_helper.py` has routing logic that can be adapted
4. PandasAI v3 is already configured correctly via LiteLLM in `llm_config.py`
5. Main dependencies: `app.py`, `sidebar.py`, `test_data_loader.py` - all need updates

### Files Created

`C:\Users\User\saudi-financial-chat\.planning\phases\01-data-layer-refactor\01-RESEARCH.md`

### Confidence Assessment

| Area | Level | Reason |
|------|-------|--------|
| Standard Stack | HIGH | No new packages, using existing |
| Architecture | HIGH | Clear patterns from existing code |
| Pitfalls | HIGH | Direct codebase analysis |
| Migration Path | HIGH | Existing query helper provides foundation |

### Open Questions

- LLM fallback threshold (recommendation: start without, add later if needed)
- Cache TTL strategy (recommendation: 1 hour)
- Arabic keyword routing (recommendation: use existing TASIQueryHelper)

### Ready for Planning

Research complete. Planner can now create PLAN.md files.
