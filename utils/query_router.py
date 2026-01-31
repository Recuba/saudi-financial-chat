"""Query Router for Ra'd AI.

Provides keyword-based routing to select optimal data views for user queries.
Uses simple pattern matching for Phase 1; LLM fallback added in Phase 2.

Usage:
    from utils.query_router import route_query

    view_name, reason = route_query("top 10 companies by revenue")
    # Returns: ('top_bottom_performers', 'Ranking query detected')
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Keyword patterns for query classification
# Checked in priority order: ranking > sector > timeseries > latest
KEYWORD_PATTERNS = {
    "ranking": ["top", "bottom", "best", "worst", "highest", "lowest", "rank"],
    "sector": ["sector", "industry", "compare sector", "benchmark"],
    "timeseries": ["growth", "trend", "yoy", "year over year", "change", "over time"],
    "latest": ["latest", "current", "recent", "now", "today", "2024", "2025"],
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


def route_query(query: str) -> Tuple[str, str]:
    """Route a query to the optimal data view based on keyword patterns.

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
    # Handle empty query
    if not query or not query.strip():
        logger.info("Empty query - routing to tasi_financials")
        return VIEW_MAPPING["general"], ROUTE_REASONS["general"]

    query_lower = query.lower()

    # Check patterns in priority order
    for intent in ["ranking", "sector", "timeseries", "latest"]:
        keywords = KEYWORD_PATTERNS[intent]
        for keyword in keywords:
            if keyword in query_lower:
                view_name = VIEW_MAPPING[intent]
                reason = ROUTE_REASONS[intent]
                logger.info(f"Routed query to {view_name}: {reason}")
                return view_name, reason

    # Default fallback
    view_name = VIEW_MAPPING["general"]
    reason = ROUTE_REASONS["general"]
    logger.info(f"Routed query to {view_name}: {reason}")
    return view_name, reason


class QueryRouter:
    """Query router with extensibility for future LLM fallback.

    Provides the same routing logic as route_query() but as a class
    that can be extended with additional routing strategies in Phase 2.

    Usage:
        router = QueryRouter()
        view_name, reason = router.route("top 10 by revenue")
    """

    def __init__(self):
        """Initialize the query router."""
        self.keyword_patterns = KEYWORD_PATTERNS
        self.view_mapping = VIEW_MAPPING
        self.route_reasons = ROUTE_REASONS

    def route(self, query: str) -> Tuple[str, str]:
        """Route a query to the optimal data view.

        Args:
            query: Natural language query string

        Returns:
            Tuple of (view_name, reason)
        """
        return route_query(query)

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
