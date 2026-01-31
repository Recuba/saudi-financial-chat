"""Query Router for Ra'd AI.

Provides keyword-based routing with LLM fallback for ambiguous queries.
Uses pattern matching first, then LLM classification for uncertain intents.

Usage:
    from utils.query_router import QueryRouter

    # With LLM fallback (recommended)
    router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=True)
    view_name, reason, entities, confidence = router.route("analyze SABIC performance")
    # Returns: ('latest_financials', 'LLM: Company-specific query', {...}, 0.8)

    # Keyword-only (faster, no LLM calls)
    router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=False)
    view_name, reason, entities, confidence = router.route("top 10 companies")
    # Returns: ('top_bottom_performers', 'Ranking query detected', {...}, 1.0)

    # Backward compatible function (returns 2-tuple):
    from utils.query_router import route_query
    view_name, reason = route_query("top 10 companies by revenue")

Confidence scores:
    - 1.0: Keyword match (high confidence)
    - 0.8: LLM classification (medium confidence)
    - 0.5: Fallback to general (low confidence)
"""

import logging
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# Keyword patterns for query classification
# Checked in priority order: ranking > sector > timeseries > latest
KEYWORD_PATTERNS = {
    "ranking": [
        "top", "bottom", "best", "worst", "highest", "lowest", "rank",
        "biggest", "smallest", "largest", "most", "least", "leader"
    ],
    "sector": [
        "sector", "industry", "compare sector", "benchmark",
        "by sector", "per sector", "sector average", "industry average"
    ],
    "timeseries": [
        "growth", "trend", "yoy", "year over year", "change", "over time",
        "history", "historical", "years", "quarterly", "annual"
    ],
    "latest": [
        "latest", "current", "recent", "now", "today", "2024", "2025",
        "last quarter", "most recent", "q1", "q2", "q3", "q4"
    ],
}

# Mapping from query intent to optimal view name
VIEW_MAPPING = {
    "ranking": "top_bottom_performers",
    "sector": "sector_benchmarks_latest",
    "timeseries": "company_annual_timeseries",
    "latest": "latest_financials",
    "general": "tasi_financials",  # default fallback
}

# Human-readable reasons for routing decisions
ROUTE_REASONS = {
    "ranking": "Ranking query detected",
    "sector": "Sector comparison query detected",
    "timeseries": "Time series/growth query detected",
    "latest": "Latest data query detected",
    "general": "General query - using full dataset",
}

# Sector name aliases for entity extraction
SECTOR_ALIASES = {
    "financials": ["financial", "bank", "banking", "financials"],
    "insurance": ["insurance", "insurer"],
    "real estate": ["real estate", "property", "realestate"],
    "utilities": ["utility", "utilities", "power", "electric"],
    "consumer staples": ["consumer", "retail", "food", "consumer staples"],
    "other": ["other"],
}


def route_query(query: str) -> Tuple[str, str]:
    """Route a query to the optimal data view based on keyword patterns.

    Backward compatible function that returns 2-tuple.
    Uses keyword-only routing (no LLM) for fast, deterministic results.

    Args:
        query: Natural language query string

    Returns:
        Tuple of (view_name, reason) where:
        - view_name: Name of the optimal view to query
        - reason: Human-readable explanation for the routing decision

    Examples:
        >>> route_query("top 10 companies by revenue")
        ('top_bottom_performers', 'Ranking query detected')

        >>> route_query("what is the latest profit for SABIC")
        ('latest_financials', 'Latest data query detected')

        >>> route_query("show me all data")
        ('tasi_financials', 'General query - using full dataset')
    """
    router = QueryRouter(llm_enabled=False)  # Keyword-only for backward compat
    view_name, reason, _, _ = router.route(query)  # Ignore entities and confidence
    return view_name, reason


class QueryRouter:
    """Query router with entity extraction and LLM fallback for ambiguous queries.

    Provides keyword-based routing with optional entity extraction when
    ticker_index is provided. Uses LLM classification when keywords don't match.

    Usage:
        # With LLM fallback (recommended for production)
        router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=True)
        view_name, reason, entities, confidence = router.route("analyze SABIC")
        # Returns: ('latest_financials', 'LLM: Company analysis query', {...}, 0.8)

        # Keyword-only (faster, deterministic)
        router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=False)
        view_name, reason, entities, confidence = router.route("top 10 by revenue")
        # Returns: ('top_bottom_performers', 'Ranking query detected', {...}, 1.0)

    Confidence levels:
        - 1.0: High (keyword match)
        - 0.8: Medium (LLM classification)
        - 0.5: Low (fallback to general)
    """

    def __init__(self, ticker_index: Optional[pd.DataFrame] = None, llm_enabled: bool = False):
        """Initialize the query router.

        Args:
            ticker_index: DataFrame with ticker, company_name, sector columns.
                         If provided, enables entity extraction.
            llm_enabled: Whether to use LLM for ambiguous queries (Phase 2).
        """
        self.ticker_index = ticker_index
        self.llm_enabled = llm_enabled
        self.keyword_patterns = KEYWORD_PATTERNS
        self.view_mapping = VIEW_MAPPING
        self.route_reasons = ROUTE_REASONS

        # Build lookup structures if ticker_index provided
        self.ticker_to_company: Dict[str, str] = {}
        self.company_names: List[str] = []
        self.name_to_ticker: Dict[str, str] = {}
        self.sectors: List[str] = []

        if ticker_index is not None:
            self._build_lookup_index()

    def _build_lookup_index(self) -> None:
        """Build lookup structures for fast entity matching."""
        if self.ticker_index is None:
            return

        # Ticker to company name lookup (exact match)
        self.ticker_to_company = dict(zip(
            self.ticker_index['ticker'].astype(str),
            self.ticker_index['company_name']
        ))

        # Company name list (lowercase for matching)
        self.company_names = self.ticker_index['company_name'].tolist()

        # Company name to ticker lookup (lowercase keys)
        self.name_to_ticker = dict(zip(
            self.ticker_index['company_name'].str.lower(),
            self.ticker_index['ticker'].astype(str)
        ))

        # Unique sectors
        self.sectors = self.ticker_index['sector'].unique().tolist()

        logger.debug(f"Built lookup index: {len(self.ticker_to_company)} tickers, "
                     f"{len(self.company_names)} companies, {len(self.sectors)} sectors")

    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract tickers, company names, and sectors from query.

        Args:
            query: Natural language query string

        Returns:
            Dictionary with keys:
            - 'tickers': list of matched ticker codes (4-digit numbers found in ticker_index)
            - 'companies': list of matched company names
            - 'sectors': list of detected sector names
        """
        entities: Dict[str, List[str]] = {
            'tickers': [],
            'companies': [],
            'sectors': []
        }

        if self.ticker_index is None:
            return entities

        query_lower = query.lower()

        # 1. Extract tickers (4-digit numbers that exist in index)
        ticker_matches = re.findall(r'\b(\d{4})\b', query)
        for ticker in ticker_matches:
            if ticker in self.ticker_to_company:
                entities['tickers'].append(ticker)
                # Also add the company name for the ticker
                company_name = self.ticker_to_company[ticker]
                if company_name not in entities['companies']:
                    entities['companies'].append(company_name)

        # 2. Extract company names
        for company_name in self.company_names:
            company_lower = company_name.lower()

            # Skip if already added via ticker
            if company_name in entities['companies']:
                continue

            # Exact substring match
            if company_lower in query_lower:
                entities['companies'].append(company_name)
                continue

            # Fuzzy match for longer names (>5 chars)
            if len(company_lower) > 5:
                # Check if any significant part of the company name matches
                ratio = SequenceMatcher(None, company_lower, query_lower).ratio()
                if ratio > 0.6:
                    entities['companies'].append(company_name)

        # 3. Extract sectors using aliases
        for sector, aliases in SECTOR_ALIASES.items():
            for alias in aliases:
                if alias in query_lower:
                    # Map to actual sector name from data if possible
                    for actual_sector in self.sectors:
                        if actual_sector.lower() == sector or sector in actual_sector.lower():
                            if actual_sector not in entities['sectors']:
                                entities['sectors'].append(actual_sector)
                            break
                    else:
                        # Use the sector key if no match found
                        if sector.title() not in entities['sectors']:
                            entities['sectors'].append(sector.title())
                    break

        return entities

    def route(self, query: str) -> Tuple[str, str, Dict[str, List[str]], float]:
        """Route a query to the optimal data view.

        Args:
            query: Natural language query string

        Returns:
            Tuple of (view_name, reason, entities, confidence) where:
            - view_name: Name of the optimal view to query
            - reason: Human-readable explanation for the routing decision
            - entities: Dict with extracted tickers, companies, sectors
            - confidence: Routing confidence (1.0=keyword, 0.8=LLM, 0.5=fallback)
        """
        # Handle empty query
        if not query or not query.strip():
            logger.info("Empty query - routing to tasi_financials")
            return VIEW_MAPPING["general"], ROUTE_REASONS["general"], {
                'tickers': [], 'companies': [], 'sectors': []
            }, 0.5

        # Step 1: Extract entities
        entities = self._extract_entities(query) if self.ticker_index is not None else {
            'tickers': [], 'companies': [], 'sectors': []
        }

        # Step 2: Keyword matching (high confidence)
        view, reason = self._keyword_route(query)
        if view != "tasi_financials":
            logger.info(f"Keyword routed to {view}: {reason}")
            return view, reason, entities, 1.0

        # Step 3: LLM classification (medium confidence)
        if self.llm_enabled:
            view, reason = self._llm_classify(query, entities)
            if view != "tasi_financials":
                logger.info(f"LLM routed to {view}: {reason}")
                return view, reason, entities, 0.8

        # Step 4: Fallback (low confidence)
        logger.info("Fallback to tasi_financials: No keyword or LLM match")
        return "tasi_financials", "General query - using full dataset", entities, 0.5

    def _keyword_route(self, query: str) -> Tuple[str, str]:
        """Route query using keyword pattern matching.

        Args:
            query: Natural language query string

        Returns:
            Tuple of (view_name, reason)
        """
        query_lower = query.lower()

        # Check patterns in priority order: ranking > sector > timeseries > latest
        for intent in ["ranking", "sector", "timeseries", "latest"]:
            keywords = self.keyword_patterns[intent]
            for keyword in keywords:
                if keyword in query_lower:
                    return self.view_mapping[intent], self.route_reasons[intent]

        # No keyword match
        return self.view_mapping["general"], self.route_reasons["general"]

    def _llm_classify(self, query: str, entities: Dict[str, List[str]]) -> Tuple[str, str]:
        """Use LLM to classify ambiguous query intent.

        Args:
            query: Natural language query string
            entities: Extracted entities from query

        Returns:
            Tuple of (view_name, reason)
        """
        prompt = f'''Classify this Saudi financial query into ONE category:

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

Example: TIMESERIES|Query asks about revenue change over years'''

        try:
            import pandasai as pai
            response = pai.config.llm.chat(prompt)

            # Parse response (CATEGORY|reason format)
            if '|' in response:
                category, reason = response.split('|', 1)
                category = category.strip().upper()
            else:
                category = response.strip().upper()
                reason = "LLM classification"

            # Map category to view
            category_to_view = {
                'RANKING': 'top_bottom_performers',
                'SECTOR': 'sector_benchmarks_latest',
                'TIMESERIES': 'company_annual_timeseries',
                'LATEST': 'latest_financials',
                'GENERAL': 'tasi_financials'
            }

            view = category_to_view.get(category, 'tasi_financials')
            return view, f"LLM: {reason.strip()}"

        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            return 'tasi_financials', 'Fallback: LLM classification failed'

    def get_available_views(self) -> list:
        """Get list of available view names."""
        return list(self.view_mapping.values())

    def get_view_for_intent(self, intent: str) -> str:
        """Get the view name for a specific intent.

        Args:
            intent: Query intent (ranking, sector, timeseries, latest, general)

        Returns:
            View name for the intent, or tasi_financials if intent unknown
        """
        return self.view_mapping.get(intent, self.view_mapping["general"])
