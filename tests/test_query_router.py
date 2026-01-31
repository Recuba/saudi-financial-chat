"""Tests for query_router module.

Comprehensive test coverage for:
- Keyword pattern matching
- Priority order verification
- Entity extraction (tickers, companies, sectors)
- Backward compatibility
"""

import pytest
import pandas as pd

from utils.query_router import (
    QueryRouter,
    route_query,
    KEYWORD_PATTERNS,
    VIEW_MAPPING,
    ROUTE_REASONS,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_ticker_index():
    """Mock ticker_index DataFrame for testing entity extraction."""
    return pd.DataFrame({
        'ticker': ['1010', '1020', '2050', '4001'],
        'company_name': ['Riyad Bank', 'Bank Aljazira', 'Savola Group', 'Abdullah Al Othaim Markets'],
        'sector': ['Financials', 'Financials', 'Consumer Staples', 'Consumer Staples']
    })


@pytest.fixture
def router_without_index():
    """QueryRouter without ticker_index."""
    return QueryRouter()


@pytest.fixture
def router_with_index(mock_ticker_index):
    """QueryRouter with ticker_index for entity extraction."""
    return QueryRouter(ticker_index=mock_ticker_index)


# =============================================================================
# Test: Keyword Pattern Matching
# =============================================================================


class TestKeywordPatterns:
    """Test keyword pattern matching for each intent."""

    def test_ranking_keywords(self, router_without_index):
        """Test ranking intent keywords."""
        ranking_queries = [
            "top 10 companies",
            "bottom 5 by revenue",
            "best performers",
            "worst stocks",
            "highest profit margin",
            "lowest debt",
            "rank by ROE",
            "biggest companies",
            "smallest market cap",
            "largest revenue",
            "most profitable",
            "least efficient",
            "leader in sales",
        ]
        for query in ranking_queries:
            view_name, reason, _ = router_without_index.route(query)
            assert view_name == "top_bottom_performers", f"Failed for query: {query}"
            assert reason == "Ranking query detected"

    def test_sector_keywords(self, router_without_index):
        """Test sector intent keywords."""
        sector_queries = [
            "compare sectors",
            "industry overview",
            "benchmark against sector",
            "by sector analysis",
            "per sector breakdown",
            "sector average ROE",
            "industry average profit",
        ]
        for query in sector_queries:
            view_name, reason, _ = router_without_index.route(query)
            assert view_name == "sector_benchmarks_latest", f"Failed for query: {query}"
            assert reason == "Sector comparison query detected"

    def test_timeseries_keywords(self, router_without_index):
        """Test timeseries intent keywords."""
        timeseries_queries = [
            "revenue growth",
            "trend analysis",
            "yoy comparison",
            "year over year change",
            "change over time",
            "show history",
            "historical data",
            "last 5 years",
            "quarterly performance",
            "annual report",
        ]
        for query in timeseries_queries:
            view_name, reason, _ = router_without_index.route(query)
            assert view_name == "company_annual_timeseries", f"Failed for query: {query}"
            assert reason == "Time series/growth query detected"

    def test_latest_keywords(self, router_without_index):
        """Test latest intent keywords."""
        latest_queries = [
            "latest financials",
            "current ratio",
            "2024 results",
            "2025 forecast",
            "last quarter earnings",
            "Q1 revenue",
            "Q2 profit",
            "Q3 performance",
            "Q4 results",
            # Note: "most recent data" matches "most" (ranking) first due to priority
        ]
        for query in latest_queries:
            view_name, reason, _ = router_without_index.route(query)
            assert view_name == "latest_financials", f"Failed for query: {query}"
            assert reason == "Latest data query detected"

    def test_fallback_to_general(self, router_without_index):
        """Test queries with no keywords fall back to general view."""
        general_queries = [
            "show me data",
            "what is the revenue",
            "SABIC financials",
            "company information",
        ]
        for query in general_queries:
            view_name, reason, _ = router_without_index.route(query)
            assert view_name == "tasi_financials", f"Failed for query: {query}"
            assert reason == "General query - using full dataset"


# =============================================================================
# Test: Priority Order
# =============================================================================


class TestPriorityOrder:
    """Test that priority order is maintained (ranking > sector > timeseries > latest)."""

    def test_priority_ranking_over_latest(self, router_without_index):
        """Ranking keywords should take priority over latest keywords."""
        # "top" (ranking) should win over "latest"
        view_name, reason, _ = router_without_index.route("top 10 latest companies")
        assert view_name == "top_bottom_performers"

    def test_priority_ranking_over_sector(self, router_without_index):
        """Ranking keywords should take priority over sector keywords."""
        view_name, reason, _ = router_without_index.route("top sectors by revenue")
        assert view_name == "top_bottom_performers"

    def test_priority_ranking_over_timeseries(self, router_without_index):
        """Ranking keywords should take priority over timeseries keywords."""
        view_name, reason, _ = router_without_index.route("top growth companies")
        assert view_name == "top_bottom_performers"

    def test_priority_sector_over_timeseries(self, router_without_index):
        """Sector keywords should take priority over timeseries keywords."""
        view_name, reason, _ = router_without_index.route("sector growth comparison")
        assert view_name == "sector_benchmarks_latest"

    def test_priority_sector_over_latest(self, router_without_index):
        """Sector keywords should take priority over latest keywords."""
        view_name, reason, _ = router_without_index.route("sector latest data")
        assert view_name == "sector_benchmarks_latest"

    def test_priority_timeseries_over_latest(self, router_without_index):
        """Timeseries keywords should take priority over latest keywords."""
        view_name, reason, _ = router_without_index.route("growth in latest year")
        assert view_name == "company_annual_timeseries"


# =============================================================================
# Test: Entity Extraction
# =============================================================================


class TestEntityExtraction:
    """Test entity extraction from queries."""

    def test_extract_ticker(self, router_with_index):
        """Test extraction of ticker codes."""
        view_name, reason, entities = router_with_index.route("show 1010 data")
        assert "1010" in entities['tickers']
        assert "Riyad Bank" in entities['companies']

    def test_extract_company_name(self, router_with_index):
        """Test extraction of company names."""
        view_name, reason, entities = router_with_index.route("Riyad Bank revenue")
        assert "Riyad Bank" in entities['companies']

    def test_extract_sector(self, router_with_index):
        """Test extraction of sector names."""
        view_name, reason, entities = router_with_index.route("financials sector analysis")
        assert len(entities['sectors']) > 0
        assert any('Financials' in s for s in entities['sectors'])

    def test_extract_multiple_tickers(self, router_with_index):
        """Test extraction of multiple tickers."""
        view_name, reason, entities = router_with_index.route("compare 1010 and 1020")
        assert "1010" in entities['tickers']
        assert "1020" in entities['tickers']
        assert len(entities['tickers']) == 2

    def test_fuzzy_match_company(self, router_with_index):
        """Test fuzzy matching for company names."""
        # "savola" should match "Savola Group" (substring match)
        view_name, reason, entities = router_with_index.route("savola group revenue")
        assert "Savola Group" in entities['companies']

    def test_no_entities_found(self, router_with_index):
        """Test queries with no extractable entities."""
        view_name, reason, entities = router_with_index.route("show all data")
        assert len(entities['tickers']) == 0
        assert len(entities['companies']) == 0
        assert len(entities['sectors']) == 0

    def test_invalid_ticker_not_extracted(self, router_with_index):
        """Test that invalid 4-digit numbers are not extracted as tickers."""
        view_name, reason, entities = router_with_index.route("show 9999 data")
        assert "9999" not in entities['tickers']

    def test_ticker_resolves_to_company(self, router_with_index):
        """Test that ticker extraction also adds company name."""
        view_name, reason, entities = router_with_index.route("1020 financials")
        assert "1020" in entities['tickers']
        assert "Bank Aljazira" in entities['companies']

    def test_sector_alias_banking(self, router_with_index):
        """Test sector alias: 'banking' -> 'Financials'."""
        view_name, reason, entities = router_with_index.route("banking sector overview")
        assert len(entities['sectors']) > 0
        # Should match Financials sector
        assert any('Financials' in s for s in entities['sectors'])


# =============================================================================
# Test: Backward Compatibility
# =============================================================================


class TestBackwardCompatibility:
    """Test backward compatibility with route_query function."""

    def test_route_query_function_returns_tuple(self):
        """Test that route_query() returns (str, str) tuple."""
        result = route_query("top 10 companies")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], str)

    def test_route_query_function_routing(self):
        """Test that route_query() routes correctly."""
        view_name, reason = route_query("top 10")
        assert view_name == "top_bottom_performers"
        assert reason == "Ranking query detected"

        view_name, reason = route_query("sector comparison")
        assert view_name == "sector_benchmarks_latest"
        assert reason == "Sector comparison query detected"

    def test_router_without_ticker_index(self):
        """Test QueryRouter works without ticker_index."""
        router = QueryRouter()
        view_name, reason, entities = router.route("top 10 by revenue")
        assert view_name == "top_bottom_performers"
        assert entities == {'tickers': [], 'companies': [], 'sectors': []}

    def test_router_with_llm_disabled(self):
        """Test QueryRouter with llm_enabled=False (default)."""
        router = QueryRouter(llm_enabled=False)
        assert router.llm_enabled is False
        view_name, reason, entities = router.route("ambiguous query")
        # Should fall back to general without LLM
        assert view_name == "tasi_financials"


# =============================================================================
# Test: Edge Cases
# =============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query(self, router_without_index):
        """Test empty query handling."""
        view_name, reason, entities = router_without_index.route("")
        assert view_name == "tasi_financials"
        assert reason == "General query - using full dataset"

    def test_whitespace_query(self, router_without_index):
        """Test whitespace-only query handling."""
        view_name, reason, entities = router_without_index.route("   ")
        assert view_name == "tasi_financials"

    def test_none_query(self, router_without_index):
        """Test None query handling."""
        view_name, reason, entities = router_without_index.route(None)
        assert view_name == "tasi_financials"

    def test_case_insensitive_keywords(self, router_without_index):
        """Test that keyword matching is case-insensitive."""
        view_name, reason, _ = router_without_index.route("TOP 10 COMPANIES")
        assert view_name == "top_bottom_performers"

        view_name, reason, _ = router_without_index.route("SECTOR analysis")
        assert view_name == "sector_benchmarks_latest"

    def test_get_available_views(self, router_without_index):
        """Test get_available_views() method."""
        views = router_without_index.get_available_views()
        assert "tasi_financials" in views
        assert "top_bottom_performers" in views
        assert "sector_benchmarks_latest" in views
        assert "company_annual_timeseries" in views
        assert "latest_financials" in views

    def test_get_view_for_intent(self, router_without_index):
        """Test get_view_for_intent() method."""
        assert router_without_index.get_view_for_intent("ranking") == "top_bottom_performers"
        assert router_without_index.get_view_for_intent("sector") == "sector_benchmarks_latest"
        assert router_without_index.get_view_for_intent("timeseries") == "company_annual_timeseries"
        assert router_without_index.get_view_for_intent("latest") == "latest_financials"
        assert router_without_index.get_view_for_intent("general") == "tasi_financials"
        assert router_without_index.get_view_for_intent("unknown") == "tasi_financials"


# =============================================================================
# Test: Constants
# =============================================================================


class TestConstants:
    """Test module-level constants."""

    def test_keyword_patterns_has_all_intents(self):
        """Test KEYWORD_PATTERNS has all expected intents."""
        expected_intents = ["ranking", "sector", "timeseries", "latest"]
        for intent in expected_intents:
            assert intent in KEYWORD_PATTERNS

    def test_view_mapping_has_all_intents(self):
        """Test VIEW_MAPPING has all expected intents plus general."""
        expected_intents = ["ranking", "sector", "timeseries", "latest", "general"]
        for intent in expected_intents:
            assert intent in VIEW_MAPPING

    def test_route_reasons_has_all_intents(self):
        """Test ROUTE_REASONS has all expected intents plus general."""
        expected_intents = ["ranking", "sector", "timeseries", "latest", "general"]
        for intent in expected_intents:
            assert intent in ROUTE_REASONS
