"""Centralized configuration for Ra'd AI.

This module provides a single source of truth for all configuration values,
environment variables, and application constants.

Usage:
    from config import Config, AppSettings

    api_timeout = Config.API_TIMEOUT
    max_query_length = AppSettings.MAX_QUERY_LENGTH
"""

import os
from typing import List, Optional


class Config:
    """Environment-based configuration with sensible defaults."""

    # API Configuration
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_MAX_RETRIES: int = int(os.getenv("API_MAX_RETRIES", "3"))
    API_RETRY_BACKOFF: float = float(os.getenv("API_RETRY_BACKOFF", "0.5"))

    # Model Configuration
    DEFAULT_MODEL: str = os.getenv(
        "DEFAULT_MODEL",
        "openrouter/google/gemini-3-flash-preview"
    )
    MODEL_DISPLAY_NAME: str = os.getenv("MODEL_DISPLAY_NAME", "Gemini 3 Flash")

    # Cache Configuration
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Feature Flags
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    SHOW_CODE_BY_DEFAULT: bool = os.getenv("SHOW_CODE_BY_DEFAULT", "false").lower() == "true"
    ENABLE_QUERY_ROUTING: bool = os.getenv("ENABLE_QUERY_ROUTING", "true").lower() == "true"

    # Data Paths
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    TASI_OPTIMIZED_DIR: str = os.getenv("TASI_OPTIMIZED_DIR", "data/tasi_optimized")

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"

    @classmethod
    def get_log_level(cls) -> int:
        """Get numeric log level."""
        import logging
        return getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)


class AppSettings:
    """Application-level settings and constants."""

    # Query Settings
    MAX_QUERY_LENGTH: int = 2000
    MIN_QUERY_LENGTH: int = 3
    MAX_QUERIES_PER_MINUTE: int = 10

    # Display Settings
    MAX_ROWS_DISPLAY: int = 100
    MAX_COLUMNS_DISPLAY: int = 50
    ROWS_PER_PAGE: int = 25

    # Session Settings
    MAX_CHAT_HISTORY: int = 100
    MAX_RECENT_QUERIES: int = 10
    MAX_FAVORITE_QUERIES: int = 20

    # Export Settings
    EXPORT_TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"
    EXPORT_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

    # UI Settings
    THEME_DEFAULT: str = "dark"
    SIDEBAR_WIDTH: int = 300


class DataViewConfig:
    """Configuration for data views and datasets."""

    # Available tasi_optimized views
    VIEW_NAMES: List[str] = [
        "tasi_financials",
        "latest_financials",
        "latest_annual",
        "ticker_index",
        "company_annual_timeseries",
        "sector_benchmarks_latest",
        "top_bottom_performers",
    ]

    # View descriptions for UI
    VIEW_DESCRIPTIONS: dict = {
        "tasi_financials": "Full dataset with all financial metrics (4,748 rows)",
        "latest_financials": "Latest record per company (302 rows)",
        "latest_annual": "Latest annual record per company (302 rows)",
        "ticker_index": "Ticker metadata and lookup table (302 rows)",
        "company_annual_timeseries": "Annual data with YoY growth calculations (1,155 rows)",
        "sector_benchmarks_latest": "Sector-level aggregates and benchmarks (6 rows)",
        "top_bottom_performers": "Top/bottom 20 companies per metric (160 rows)",
    }

    # Query routing view mapping
    VIEW_ROUTING: dict = {
        "ranking": "top_bottom_performers",
        "sector": "sector_benchmarks_latest",
        "timeseries": "company_annual_timeseries",
        "latest": "latest_financials",
        "general": "tasi_financials",
    }


class QueryConfig:
    """Configuration for query processing and routing."""

    # Keywords for query classification
    RANKING_KEYWORDS: List[str] = [
        "top", "bottom", "best", "worst", "highest", "lowest",
        "leading", "trailing", "rank", "ranking"
    ]

    SECTOR_KEYWORDS: List[str] = [
        "sector", "industry", "segment", "benchmark", "average",
        "compare sectors", "sector performance"
    ]

    TIMESERIES_KEYWORDS: List[str] = [
        "growth", "trend", "yoy", "year over year", "change",
        "historical", "over time", "progression"
    ]

    LATEST_KEYWORDS: List[str] = [
        "latest", "current", "recent", "now", "today",
        "most recent", "up to date"
    ]


class ExampleQueries:
    """Pre-defined example queries for user guidance."""

    RANKING_EXAMPLES: List[dict] = [
        {
            "query": "What are the top 10 companies by revenue?",
            "category": "Ranking",
        },
        {
            "query": "Which companies have the highest profit margins?",
            "category": "Ranking",
        },
    ]

    SECTOR_EXAMPLES: List[dict] = [
        {
            "query": "Compare average ROE across all sectors",
            "category": "Sector Analysis",
        },
        {
            "query": "Which sector has the highest average revenue?",
            "category": "Sector Analysis",
        },
    ]

    TIMESERIES_EXAMPLES: List[dict] = [
        {
            "query": "Show revenue growth trend for ARAMCO",
            "category": "Time Series",
        },
        {
            "query": "Which companies had the highest YoY profit growth?",
            "category": "Time Series",
        },
    ]

    GENERAL_EXAMPLES: List[dict] = [
        {
            "query": "List all banks in the dataset",
            "category": "General",
        },
        {
            "query": "What is the total market cap of all companies?",
            "category": "General",
        },
    ]

    @classmethod
    def get_all_examples(cls) -> List[dict]:
        """Get all example queries."""
        return (
            cls.RANKING_EXAMPLES +
            cls.SECTOR_EXAMPLES +
            cls.TIMESERIES_EXAMPLES +
            cls.GENERAL_EXAMPLES
        )


class LoadingMessages:
    """Loading state messages for UI feedback."""

    ANALYZING: List[str] = [
        "Analyzing your question...",
        "Understanding your request...",
        "Processing query...",
    ]

    QUERYING: List[str] = [
        "Querying financial data...",
        "Fetching results...",
        "Searching the database...",
    ]

    GENERATING: List[str] = [
        "Generating response...",
        "Preparing results...",
        "Formatting output...",
    ]

    @classmethod
    def get_random_message(cls, stage: str = "analyzing") -> str:
        """Get a random loading message for the given stage."""
        import random
        messages = getattr(cls, stage.upper(), cls.ANALYZING)
        return random.choice(messages)
