# Phase 2: Query Routing Engine - Research

**Researched:** 2026-02-01
**Domain:** Query intent classification, entity resolution, LLM routing
**Confidence:** HIGH

## Summary

Phase 2 enhances the existing keyword-based query router with: (1) ticker/company name resolution using the ticker_index.parquet lookup table, (2) LLM-based intent classification for ambiguous queries, and (3) verification that keyword patterns cover all routing scenarios.

The current `query_router.py` implements basic keyword matching with priority order (ranking > sector > timeseries > latest > general). This research identifies the gaps: company/ticker extraction is not implemented, ambiguous queries fall through to general without LLM guidance, and the keyword patterns may miss common query formulations.

**Primary recommendation:** Extend QueryRouter with three layers: (1) keyword detection (fast, existing), (2) entity extraction with fuzzy matching (fast, new), (3) LLM classification fallback (slow, for ambiguous queries only).

## Current State Analysis

### Existing Implementation

**File:** `utils/query_router.py`

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
    "general": "tasi_financials",  # default fallback
}
```

**Working:** Keyword matching with priority order, returns `(view_name, reason)` tuple.
**Missing:** Entity extraction, LLM fallback, confidence scoring.

### Data Views Available

| View | Rows | Purpose | When to Route |
|------|------|---------|---------------|
| `tasi_financials` | 4,748 | Full dataset, all periods | Complex/unknown queries |
| `latest_financials` | 302 | Latest record per company | "latest", "current", specific company |
| `latest_annual` | 302 | Latest annual per company | Annual-only queries |
| `ticker_index` | 302 | Company metadata | Not for queries, for lookup |
| `company_annual_timeseries` | 1,155 | Annual data with YoY growth | Growth, trend, historical |
| `sector_benchmarks_latest` | 6 | Sector aggregates | Sector comparison |
| `top_bottom_performers` | 160 | Rankings by metric | Top/bottom N queries |

### ticker_index.parquet Structure

```
Columns: ['ticker', 'company_name', 'sector', 'size_category',
          'record_count', 'first_year', 'last_year', 'latest_roe', 'latest_assets']
Shape: (302, 9)

Sample:
ticker | company_name               | sector
1010   | Riyad Bank                 | Financials
1020   | Bank Aljazira              | Financials
2050   | Savola Group               | Other
4001   | Abdullah Al Othaim Markets | Consumer Staples
```

**Key insight:** Company names are full names (not abbreviated). Tickers are 4-digit numbers. Both need fuzzy matching since users may type partial names or misspell.

## Gap Analysis

| Requirement | Current State | Gap | Priority |
|-------------|---------------|-----|----------|
| ROUTE-01: Keyword pattern matching | Implemented | May need more patterns | LOW |
| ROUTE-02: LLM classification for ambiguous | Not implemented | Full implementation needed | HIGH |
| ROUTE-03: Fallback to full dataset | Implemented | Working correctly | DONE |
| ROUTE-04: Ticker/company resolution | Not implemented | Full implementation needed | HIGH |

### Missing Keyword Patterns

Current patterns may miss common query formulations:

| Intent | Missing Patterns |
|--------|------------------|
| ranking | "biggest", "smallest", "largest", "most", "least", "leader" |
| sector | "by sector", "per sector", "sector average", "industry average" |
| timeseries | "history", "historical", "years", "quarterly", "annual" |
| latest | "last quarter", "most recent", "Q1", "Q2", "Q3", "Q4" |

### Ambiguous Query Examples

Queries that need LLM classification:

| Query | Ambiguity |
|-------|-----------|
| "Show me SABIC financials" | Latest? Historical? All? |
| "How is Riyad Bank performing?" | Ranking? Timeseries? Latest metrics? |
| "Compare banks" | Sector benchmark? Specific companies? |
| "Revenue analysis" | Ranking? Timeseries? By company? |

## Standard Stack

### Core Libraries

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `rapidfuzz` | 3.x | Fast fuzzy string matching | 10x faster than fuzzywuzzy, pure C++ |
| `pandasai` | 3.x | LLM-to-code translation | Already in use |
| `pandasai-litellm` | latest | OpenRouter/LLM integration | Already in use |

### No New Dependencies Needed

The project already has everything needed:
- **LLM access:** `utils/llm_config.py` configures LiteLLM with OpenRouter
- **Data access:** `utils/data_loader.py` loads all parquet views including ticker_index
- **Session state:** Streamlit session state for caching

Only new dependency: `rapidfuzz` for fuzzy string matching (optional, can use Python stdlib for simpler approach).

**Installation (if using rapidfuzz):**
```bash
pip install rapidfuzz
```

## Architecture Patterns

### Recommended Routing Architecture

```
User Query
    │
    ▼
┌──────────────────────┐
│ 1. Entity Extraction │  ← Fast: regex + fuzzy match
│    - Ticker lookup   │
│    - Company lookup  │
└──────────┬───────────┘
           │
    ▼ (entities found?)
    │
    ├─YES──► Filter data by entity, proceed to keyword check
    │
    ▼ NO
┌──────────────────────┐
│ 2. Keyword Matching  │  ← Fast: string contains
│    - Priority order  │
│    - Return if match │
└──────────┬───────────┘
           │
    ▼ (keywords found?)
    │
    ├─YES──► Return (view_name, reason)
    │
    ▼ NO (ambiguous)
┌──────────────────────┐
│ 3. LLM Classification│  ← Slow: API call
│    - Classify intent │
│    - Return view     │
└──────────┬───────────┘
           │
    ▼ (classification failed?)
    │
    ├─YES──► Return ("tasi_financials", "Fallback - uncertain classification")
    │
    ▼ NO
Return (classified_view, reason)
```

### Recommended Class Structure

```python
class QueryRouter:
    """Enhanced query router with entity extraction and LLM fallback."""

    def __init__(self, ticker_index: pd.DataFrame, llm_enabled: bool = True):
        self.ticker_index = ticker_index
        self.llm_enabled = llm_enabled
        self._build_lookup_index()

    def route(self, query: str) -> Tuple[str, str, float]:
        """Route query to optimal view.

        Returns:
            (view_name, reason, confidence)
            confidence: 1.0 for keyword match, 0.8 for LLM, 0.5 for fallback
        """
        # Step 1: Extract entities
        entities = self._extract_entities(query)

        # Step 2: Keyword matching
        view, reason = self._keyword_route(query)
        if view != "tasi_financials":
            return view, reason, 1.0

        # Step 3: LLM classification (if enabled and ambiguous)
        if self.llm_enabled:
            view, reason = self._llm_classify(query, entities)
            return view, reason, 0.8

        # Step 4: Fallback
        return "tasi_financials", "General query", 0.5

    def _extract_entities(self, query: str) -> dict:
        """Extract company names and tickers from query."""
        ...

    def _keyword_route(self, query: str) -> Tuple[str, str]:
        """Existing keyword matching logic."""
        ...

    def _llm_classify(self, query: str, entities: dict) -> Tuple[str, str]:
        """Use LLM to classify ambiguous query intent."""
        ...
```

### Pattern: Entity Extraction with Fuzzy Matching

```python
def _build_lookup_index(self):
    """Build lookup structures for fast entity matching."""
    # Ticker lookup (exact match)
    self.ticker_to_company = dict(zip(
        self.ticker_index['ticker'].astype(str),
        self.ticker_index['company_name']
    ))

    # Company name lookup (normalized for fuzzy matching)
    self.company_names = self.ticker_index['company_name'].str.lower().tolist()
    self.name_to_ticker = dict(zip(
        self.ticker_index['company_name'].str.lower(),
        self.ticker_index['ticker'].astype(str)
    ))

def _extract_entities(self, query: str) -> dict:
    """Extract entities from query.

    Returns:
        {
            'tickers': ['1010', '2050'],
            'companies': ['Riyad Bank', 'Savola'],
            'sectors': ['Financials']
        }
    """
    query_lower = query.lower()
    entities = {'tickers': [], 'companies': [], 'sectors': []}

    # Extract tickers (4-digit numbers)
    import re
    ticker_matches = re.findall(r'\b(\d{4})\b', query)
    for t in ticker_matches:
        if t in self.ticker_to_company:
            entities['tickers'].append(t)

    # Extract company names (fuzzy match)
    # Use threshold of 80% similarity
    for name in self.company_names:
        if name in query_lower or self._fuzzy_match(name, query_lower) > 0.8:
            entities['companies'].append(self.name_to_ticker[name])

    # Extract sectors
    sectors = ['financials', 'insurance', 'real estate', 'utilities',
               'consumer staples', 'other']
    for sector in sectors:
        if sector in query_lower:
            entities['sectors'].append(sector)

    return entities
```

### Pattern: LLM Intent Classification

```python
def _llm_classify(self, query: str, entities: dict) -> Tuple[str, str]:
    """Use LLM to classify query intent.

    Called only for ambiguous queries (no keyword match).
    """
    prompt = f"""Classify this financial query into ONE category:

Query: "{query}"

Categories:
- RANKING: Questions about top/bottom performers, comparisons, rankings
- SECTOR: Questions comparing sectors or industries
- TIMESERIES: Questions about trends, growth, changes over time
- LATEST: Questions about current/recent data, specific company metrics
- GENERAL: Complex queries needing full dataset

Respond with just the category name and a brief reason.
Format: CATEGORY: reason

Example:
Query: "How has SABIC's revenue changed over the years?"
Response: TIMESERIES: revenue change over years implies historical trend analysis
"""

    try:
        import pandasai as pai
        # Use existing LLM configuration
        response = pai.config.llm.chat(prompt)

        # Parse response
        if 'RANKING' in response.upper():
            return 'top_bottom_performers', 'LLM: ' + response
        elif 'SECTOR' in response.upper():
            return 'sector_benchmarks_latest', 'LLM: ' + response
        elif 'TIMESERIES' in response.upper():
            return 'company_annual_timeseries', 'LLM: ' + response
        elif 'LATEST' in response.upper():
            return 'latest_financials', 'LLM: ' + response
        else:
            return 'tasi_financials', 'LLM: general/complex query'

    except Exception as e:
        logger.warning(f"LLM classification failed: {e}")
        return 'tasi_financials', 'Fallback: LLM classification failed'
```

### Anti-Patterns to Avoid

1. **Calling LLM for every query:** Use keyword matching first, LLM only for ambiguous queries
2. **Hard-coded company names:** Use ticker_index as source of truth, not hardcoded lists
3. **Case-sensitive matching:** Always normalize to lowercase for comparison
4. **Ignoring LLM failures:** Always have fallback to tasi_financials

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fuzzy string matching | Custom edit distance | `rapidfuzz` or `difflib.SequenceMatcher` | Edge cases in Unicode, performance |
| LLM API calls | Direct HTTP requests | Existing `pandasai.config.llm` | Already configured with auth |
| Company lookup | Hardcoded dict | ticker_index.parquet | Single source of truth |

**Key insight:** All infrastructure exists. Focus on routing logic, not rebuilding LLM or data access.

## Common Pitfalls

### Pitfall 1: Entity Extraction Greediness

**What goes wrong:** Extracting partial matches like "Bank" matching multiple companies
**Why it happens:** Naive substring matching without word boundaries
**How to avoid:** Use word boundary regex, require minimum match length, prefer exact matches
**Warning signs:** Same query returning different entities on each run

### Pitfall 2: LLM Classification Latency

**What goes wrong:** Every query takes 1-2 seconds due to LLM call
**Why it happens:** Calling LLM even when keyword matching would suffice
**How to avoid:** Keyword matching first, LLM only for truly ambiguous queries
**Warning signs:** Average query latency > 500ms

### Pitfall 3: Sector Name Variants

**What goes wrong:** "Financial" doesn't match "Financials" sector
**Why it happens:** Exact string matching on sector names
**How to avoid:** Normalize sector names, handle plurals and common variants
**Warning signs:** Sector queries falling through to general view

### Pitfall 4: Year Extraction Conflicts

**What goes wrong:** "2024" triggers "latest" view but query is about full 2024 history
**Why it happens:** Year keyword overrides actual intent
**How to avoid:** Check context around year mentions, "in 2024" vs "latest 2024"
**Warning signs:** Historical queries for specific years returning only latest data

### Pitfall 5: Confidence Inflation

**What goes wrong:** Returning high confidence for uncertain routes
**Why it happens:** Not tracking routing decision quality
**How to avoid:** Return confidence scores with routes, log routing decisions
**Warning signs:** Users getting unexpected views with no explanation

## Code Examples

### Entity Extraction (Recommended)

```python
import re
from difflib import SequenceMatcher

def extract_entities(query: str, ticker_index: pd.DataFrame) -> dict:
    """Extract entities from query.

    Args:
        query: User's natural language query
        ticker_index: DataFrame with ticker, company_name, sector columns

    Returns:
        dict with keys: tickers, companies, sectors
    """
    query_lower = query.lower()
    entities = {'tickers': [], 'companies': [], 'sectors': []}

    # Build lookup structures
    ticker_set = set(ticker_index['ticker'].astype(str))
    company_names = ticker_index['company_name'].tolist()

    # 1. Extract tickers (4-digit numbers that exist in index)
    for match in re.finditer(r'\b(\d{4})\b', query):
        ticker = match.group(1)
        if ticker in ticker_set:
            entities['tickers'].append(ticker)

    # 2. Extract company names (fuzzy match with threshold)
    words = query_lower.split()
    for company in company_names:
        company_lower = company.lower()

        # Exact substring match
        if company_lower in query_lower:
            entities['companies'].append(company)
            continue

        # Fuzzy match for longer company names (>5 chars)
        if len(company_lower) > 5:
            ratio = SequenceMatcher(None, company_lower, query_lower).ratio()
            if ratio > 0.6:
                entities['companies'].append(company)

    # 3. Extract sectors
    sector_map = {
        'financials': ['financial', 'bank', 'banking'],
        'insurance': ['insurance', 'insurer'],
        'real estate': ['real estate', 'property', 'realestate'],
        'utilities': ['utility', 'utilities', 'power', 'electric'],
        'consumer staples': ['consumer', 'retail', 'food'],
    }

    for sector, keywords in sector_map.items():
        if any(kw in query_lower for kw in keywords):
            entities['sectors'].append(sector)

    return entities
```

### LLM Intent Classification Prompt

```python
CLASSIFICATION_PROMPT = """You are a query classifier for a Saudi financial data system.

Classify this query into exactly ONE category:

Query: "{query}"

Categories (choose ONE):
- RANKING: Comparing companies, top/bottom N, best/worst performers
- SECTOR: Sector-level analysis, industry comparisons, sector averages
- TIMESERIES: Trends over time, growth rates, historical analysis, YoY changes
- LATEST: Current metrics, most recent data, specific company's latest numbers
- GENERAL: Complex multi-dimensional queries, unclear intent

Detected entities: {entities}

Respond in this exact format:
CATEGORY|reason

Example: TIMESERIES|Query asks about revenue change over years
"""
```

### Integration with app.py (Recommended Pattern)

```python
# In app.py query processing section
if prompt:
    # Enhanced routing with entity extraction
    from utils.query_router import QueryRouter
    from utils.data_loader import load_tasi_data

    data = load_tasi_data()
    router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=True)

    view_name, route_reason, confidence = router.route(prompt)
    selected_df = data[view_name]

    # Show routing info with confidence
    confidence_label = "HIGH" if confidence > 0.9 else "MEDIUM" if confidence > 0.7 else "LOW"
    st.caption(f"Using: {view_name} ({confidence_label} confidence)")

    # Proceed with PandasAI
    response = process_query(prompt, selected_df)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Rule-based NLU | Hybrid keyword + LLM | 2024 | Better accuracy, acceptable latency |
| FuzzyWuzzy | RapidFuzz | 2022 | 10x faster fuzzy matching |
| Single classifier | Cascading classifiers | 2024 | Cost reduction, latency optimization |

**Industry trend:** Semantic routing (embedding-based) is gaining traction for known intents, with LLM fallback for edge cases. For this project, keyword + fuzzy matching + LLM fallback is appropriate given the limited scope (5 intents, 302 companies).

## Open Questions

### 1. Company Abbreviation Handling

**What we know:** Users may type "SABIC" but full name is "Saudi Basic Industries Corporation"
**What's unclear:** Whether to maintain a separate abbreviation mapping or rely on fuzzy match
**Recommendation:** Start with fuzzy matching, add explicit abbreviation map if needed based on user feedback

### 2. Arabic Query Support

**What we know:** Company names in ticker_index are English only
**What's unclear:** Whether users will query in Arabic
**Recommendation:** Out of scope for Phase 2. Add Arabic support in future phase if needed.

### 3. Multi-Company Queries

**What we know:** User might ask "Compare SABIC and Riyad Bank revenue"
**What's unclear:** Which view best serves multi-company comparisons
**Recommendation:** Route to `latest_financials` for company comparisons (contains all companies)

## Sources

### Primary (HIGH confidence)
- **Codebase analysis:** `utils/query_router.py`, `utils/data_loader.py`, `app.py`
- **Data inspection:** `ticker_index.parquet`, all 7 views schema verified via pandas

### Secondary (MEDIUM confidence)
- [Intent Recognition and Auto-Routing in Multi-Agent Systems](https://gist.github.com/mkbctrl/a35764e99fe0c8e8c00b2358f55cd7fa)
- [AI Agent Routing Best Practices](https://www.patronus.ai/ai-agent-development/ai-agent-routing)
- [Hybrid LLM + Intent Classification Approach](https://medium.com/data-science-collective/intent-driven-natural-language-interface-a-hybrid-llm-intent-classification-approach-e1d96ad6f35d)
- [CompanyMatching on GitHub](https://github.com/Gawaboumga/CompanyMatching)
- [RapidFuzz for fuzzy matching](https://github.com/maxbachmann/RapidFuzz)

### Tertiary (LOW confidence)
- WebSearch patterns for fuzzy matching - validated against Python standard library options

## Metadata

**Confidence breakdown:**
- Current state analysis: HIGH - Direct codebase inspection
- Gap analysis: HIGH - Requirements vs implementation comparison
- Architecture patterns: MEDIUM - Based on industry best practices
- Code examples: HIGH - Tested patterns from codebase context

**Research date:** 2026-02-01
**Valid until:** 2026-03-01 (stable domain, low change rate)

## Implementation Recommendations

### Plan Structure

**Plan 02-01: Entity Extraction & Enhanced Keywords**
- Add entity extraction to QueryRouter
- Expand keyword patterns with missing terms
- Unit tests for entity extraction

**Plan 02-02: LLM Intent Classification**
- Implement LLM fallback for ambiguous queries
- Add confidence scoring to route() return
- Integration tests for LLM classification

### Estimated Effort

| Task | Complexity | Estimate |
|------|------------|----------|
| Entity extraction | Medium | 1-2 hours |
| Enhanced keywords | Low | 30 minutes |
| LLM classification | Medium | 1-2 hours |
| Testing | Medium | 1-2 hours |
| Integration | Low | 30 minutes |

**Total:** 4-7 hours of implementation work
