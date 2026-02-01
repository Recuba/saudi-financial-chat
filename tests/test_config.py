"""Tests for centralized configuration module."""

import os
import pytest
from config import (
    Config,
    AppSettings,
    DataViewConfig,
    QueryConfig,
    ExampleQueries,
    LoadingMessages,
)


class TestConfig:
    """Tests for Config class."""

    def test_default_model(self):
        """Test default model is set."""
        assert Config.DEFAULT_MODEL is not None
        assert "openrouter" in Config.DEFAULT_MODEL

    def test_api_timeout_default(self):
        """Test API timeout has sensible default."""
        assert Config.API_TIMEOUT == 30

    def test_cache_ttl_default(self):
        """Test cache TTL has sensible default."""
        assert Config.CACHE_TTL == 3600  # 1 hour

    def test_log_level_default(self):
        """Test log level defaults to INFO."""
        assert Config.LOG_LEVEL == "INFO"

    def test_debug_mode_default(self):
        """Test debug mode is off by default."""
        assert Config.DEBUG_MODE is False

    def test_is_production_default(self):
        """Test production check returns False by default."""
        # Clear any existing ENVIRONMENT variable
        old_env = os.environ.get("ENVIRONMENT")
        if "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

        # Should return False for non-production
        assert Config.is_production() is False

        # Restore
        if old_env:
            os.environ["ENVIRONMENT"] = old_env

    def test_get_log_level_returns_int(self):
        """Test get_log_level returns numeric level."""
        import logging
        level = Config.get_log_level()
        assert isinstance(level, int)
        assert level == logging.INFO


class TestAppSettings:
    """Tests for AppSettings class."""

    def test_max_query_length(self):
        """Test max query length is reasonable."""
        assert AppSettings.MAX_QUERY_LENGTH == 2000

    def test_min_query_length(self):
        """Test min query length is reasonable."""
        assert AppSettings.MIN_QUERY_LENGTH == 3

    def test_max_rows_display(self):
        """Test max rows display is reasonable."""
        assert AppSettings.MAX_ROWS_DISPLAY == 100

    def test_max_chat_history(self):
        """Test max chat history is reasonable."""
        assert AppSettings.MAX_CHAT_HISTORY == 100

    def test_theme_default(self):
        """Test default theme is dark."""
        assert AppSettings.THEME_DEFAULT == "dark"


class TestDataViewConfig:
    """Tests for DataViewConfig class."""

    def test_view_names_exist(self):
        """Test view names are defined."""
        assert len(DataViewConfig.VIEW_NAMES) == 7

    def test_required_views_present(self):
        """Test all required views are present."""
        required = [
            "tasi_financials",
            "latest_financials",
            "ticker_index",
        ]
        for view in required:
            assert view in DataViewConfig.VIEW_NAMES

    def test_view_descriptions_match_names(self):
        """Test all views have descriptions."""
        for view_name in DataViewConfig.VIEW_NAMES:
            assert view_name in DataViewConfig.VIEW_DESCRIPTIONS

    def test_view_routing_mapping(self):
        """Test view routing has all query types."""
        expected_types = ["ranking", "sector", "timeseries", "latest", "general"]
        for query_type in expected_types:
            assert query_type in DataViewConfig.VIEW_ROUTING


class TestQueryConfig:
    """Tests for QueryConfig class."""

    def test_ranking_keywords(self):
        """Test ranking keywords are defined."""
        assert len(QueryConfig.RANKING_KEYWORDS) > 0
        assert "top" in QueryConfig.RANKING_KEYWORDS
        assert "bottom" in QueryConfig.RANKING_KEYWORDS

    def test_sector_keywords(self):
        """Test sector keywords are defined."""
        assert len(QueryConfig.SECTOR_KEYWORDS) > 0
        assert "sector" in QueryConfig.SECTOR_KEYWORDS

    def test_timeseries_keywords(self):
        """Test timeseries keywords are defined."""
        assert len(QueryConfig.TIMESERIES_KEYWORDS) > 0
        assert "growth" in QueryConfig.TIMESERIES_KEYWORDS

    def test_latest_keywords(self):
        """Test latest keywords are defined."""
        assert len(QueryConfig.LATEST_KEYWORDS) > 0
        assert "latest" in QueryConfig.LATEST_KEYWORDS


class TestExampleQueries:
    """Tests for ExampleQueries class."""

    def test_ranking_examples_exist(self):
        """Test ranking examples are defined."""
        assert len(ExampleQueries.RANKING_EXAMPLES) > 0

    def test_sector_examples_exist(self):
        """Test sector examples are defined."""
        assert len(ExampleQueries.SECTOR_EXAMPLES) > 0

    def test_timeseries_examples_exist(self):
        """Test timeseries examples are defined."""
        assert len(ExampleQueries.TIMESERIES_EXAMPLES) > 0

    def test_general_examples_exist(self):
        """Test general examples are defined."""
        assert len(ExampleQueries.GENERAL_EXAMPLES) > 0

    def test_get_all_examples(self):
        """Test get_all_examples returns all examples."""
        all_examples = ExampleQueries.get_all_examples()
        expected_count = (
            len(ExampleQueries.RANKING_EXAMPLES) +
            len(ExampleQueries.SECTOR_EXAMPLES) +
            len(ExampleQueries.TIMESERIES_EXAMPLES) +
            len(ExampleQueries.GENERAL_EXAMPLES)
        )
        assert len(all_examples) == expected_count

    def test_example_structure(self):
        """Test examples have correct structure."""
        for example in ExampleQueries.get_all_examples():
            assert "query" in example
            assert "category" in example
            assert isinstance(example["query"], str)
            assert isinstance(example["category"], str)


class TestLoadingMessages:
    """Tests for LoadingMessages class."""

    def test_analyzing_messages_exist(self):
        """Test analyzing messages are defined."""
        assert len(LoadingMessages.ANALYZING) > 0

    def test_querying_messages_exist(self):
        """Test querying messages are defined."""
        assert len(LoadingMessages.QUERYING) > 0

    def test_generating_messages_exist(self):
        """Test generating messages are defined."""
        assert len(LoadingMessages.GENERATING) > 0

    def test_get_random_message(self):
        """Test get_random_message returns a string."""
        message = LoadingMessages.get_random_message("analyzing")
        assert isinstance(message, str)
        assert len(message) > 0

    def test_get_random_message_default(self):
        """Test get_random_message with invalid stage uses default."""
        message = LoadingMessages.get_random_message("invalid_stage")
        assert isinstance(message, str)
        assert message in LoadingMessages.ANALYZING
