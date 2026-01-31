"""Query Router for Ra'd AI.

Provides keyword-based routing to select optimal data views for user queries.
Uses simple pattern matching for Phase 1; LLM fallback added in Phase 2.

Usage:
    from utils.query_router import QueryRouter

    router = QueryRouter(ticker_index=data['ticker_index'])
    view_name, reason, entities = router.route("top 10 companies by revenue")
    # Returns: ('top_bottom_performers', 'Ranking query detected', {'tickers': [], 'companies': [], 'sectors': []})

    # Backward compatible function (returns 2-tuple):
    from utils.query_router import route_query
    view_name, reason = route_query("top 10 companies by revenue")
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
    router = QueryRouter()
    view_name, reason, _ = router.route(query)
    return view_name, reason


class QueryRouter:
    """Query router with entity extraction and extensibility for future LLM fallback.

    Provides keyword-based routing with optional entity extraction when
    ticker_index is provided. Can be extended with LLM classification in Phase 2.

    Usage:
        # Basic usage (no entity extraction)
        router = QueryRouter()
        view_name, reason, entities = router.route("top 10 by revenue")

        # With entity extraction
        router = QueryRouter(ticker_index=data['ticker_index'])
        view_name, reason, entities = router.route("show 1010 financials")
        # entities = {'tickers': ['1010'], 'companies': ['Riyad Bank'], 'sectors': []}
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

    def route(self, query: str) -> Tuple[str, str, Dict[str, List[str]]]:
        """Route a query to the optimal data view.

        Args:
            query: Natural language query string

        Returns:
            Tuple of (view_name, reason, entities) where:
            - view_name: Name of the optimal view to query
            - reason: Human-readable explanation for the routing decision
            - entities: Dict with extracted tickers, companies, sectors
        """
        # Handle empty query
        if not query or not query.strip():
            logger.info("Empty query - routing to tasi_financials")
            return VIEW_MAPPING["general"], ROUTE_REASONS["general"], {
                'tickers': [], 'companies': [], 'sectors': []
            }

        # Extract entities (informational for now, routing logic unchanged)
        entities = self._extract_entities(query)

        query_lower = query.lower()

        # Check patterns in priority order
        for intent in ["ranking", "sector", "timeseries", "latest"]:
            keywords = self.keyword_patterns[intent]
            for keyword in keywords:
                if keyword in query_lower:
                    view_name = self.view_mapping[intent]
                    reason = self.route_reasons[intent]
                    logger.info(f"Routed query to {view_name}: {reason}")
                    return view_name, reason, entities

        # Default fallback
        view_name = self.view_mapping["general"]
        reason = self.route_reasons["general"]
        logger.info(f"Routed query to {view_name}: {reason}")
        return view_name, reason, entities

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
