"""Data loading utilities for Ra'd AI.

Provides cached data loading from tasi_optimized parquet views with error handling
and dataset statistics.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


# All available view names in tasi_optimized
VIEW_NAMES = [
    "tasi_financials",
    "latest_financials",
    "latest_annual",
    "ticker_index",
    "company_annual_timeseries",
    "sector_benchmarks_latest",
    "top_bottom_performers",
]


def get_data_path() -> Path:
    """Get the path to the data directory."""
    return Path(__file__).parent.parent / "data"


@st.cache_data(show_spinner=False, ttl=3600)
def load_tasi_data() -> Dict[str, pd.DataFrame]:
    """Load all tasi_optimized views from parquet files.

    Returns:
        Dictionary with 7 views:
        - tasi_financials: Full dataset (4,748 rows)
        - latest_financials: Latest record per company (302 rows)
        - latest_annual: Latest annual record per company (302 rows)
        - ticker_index: Ticker metadata lookup (302 rows)
        - company_annual_timeseries: Annual data with YoY growth (1,155 rows)
        - sector_benchmarks_latest: Sector-level aggregates (6 rows)
        - top_bottom_performers: Top/bottom 20 per metric (160 rows)

    Raises:
        FileNotFoundError: If data files are missing
    """
    base_path = get_data_path() / "tasi_optimized"

    try:
        data = {
            "tasi_financials": pd.read_parquet(base_path / "tasi_financials.parquet"),
            "latest_financials": pd.read_parquet(base_path / "latest_financials.parquet"),
            "latest_annual": pd.read_parquet(base_path / "latest_annual.parquet"),
            "ticker_index": pd.read_parquet(base_path / "ticker_index.parquet"),
            "company_annual_timeseries": pd.read_parquet(base_path / "views" / "company_annual_timeseries.parquet"),
            "sector_benchmarks_latest": pd.read_parquet(base_path / "views" / "sector_benchmarks_latest.parquet"),
            "top_bottom_performers": pd.read_parquet(base_path / "views" / "top_bottom_performers.parquet"),
        }
        logger.info(f"Loaded {len(data)} tasi_optimized views successfully")
        return data
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def get_view(name: str) -> pd.DataFrame:
    """Get a specific view by name.

    Args:
        name: One of VIEW_NAMES

    Returns:
        The requested DataFrame

    Raises:
        ValueError: If view name is invalid
    """
    if name not in VIEW_NAMES:
        raise ValueError(f"Invalid view name: {name}. Must be one of {VIEW_NAMES}")

    data = load_tasi_data()
    return data[name]


def get_view_info() -> Dict[str, int]:
    """Get summary statistics about loaded tasi_optimized views.

    Returns:
        Dictionary with:
        - total_companies: Number of unique companies (from ticker_index)
        - total_records: Total records in main dataset (from tasi_financials)
        - views_available: Number of available views (7)
    """
    data = load_tasi_data()

    return {
        "total_companies": len(data["ticker_index"]),
        "total_records": len(data["tasi_financials"]),
        "views_available": len(VIEW_NAMES),
    }


# =============================================================================
# Deprecated functions - kept for backward compatibility during transition
# =============================================================================

@st.cache_data(show_spinner=False, ttl=3600)
def load_data() -> Dict[str, pd.DataFrame]:
    """DEPRECATED: Use load_tasi_data() instead.

    Maps old dataset names to new tasi_optimized views for backward compatibility.
    """
    logger.warning("load_data() is deprecated. Use load_tasi_data() instead.")
    tasi_data = load_tasi_data()

    # Map old names to new views for backward compatibility
    return {
        "filings": tasi_data["ticker_index"],  # Closest equivalent for metadata
        "facts": tasi_data["tasi_financials"],  # Full dataset has all metrics
        "ratios": tasi_data["tasi_financials"],  # Full dataset includes ratios
        "analytics": tasi_data["tasi_financials"],  # Full pre-joined dataset
    }


def get_dataset(name: str) -> pd.DataFrame:
    """DEPRECATED: Use get_view() instead.

    Maps old dataset names to new tasi_optimized views for backward compatibility.
    """
    logger.warning(f"get_dataset('{name}') is deprecated. Use get_view() instead.")
    old_to_new = {
        "filings": "ticker_index",
        "facts": "tasi_financials",
        "ratios": "tasi_financials",
        "analytics": "tasi_financials",
    }

    if name not in old_to_new:
        raise ValueError(f"Invalid dataset name: {name}. Must be one of {list(old_to_new.keys())}")

    return get_view(old_to_new[name])


def get_dataset_info() -> Dict[str, int]:
    """DEPRECATED: Use get_view_info() instead."""
    logger.warning("get_dataset_info() is deprecated. Use get_view_info() instead.")
    info = get_view_info()
    data = load_tasi_data()

    # Return in old format for backward compatibility
    return {
        "companies": info["total_companies"],
        "periods": info["total_records"],
        "metrics": len(data["tasi_financials"].columns),  # Approximate
        "ratios": 12,  # Known from metadata.json
    }


def get_column_info(dataset_name: str) -> Dict[str, list]:
    """DEPRECATED: Column info from tasi_financials view.

    Maps old dataset names to tasi_financials for column info.
    """
    logger.warning(f"get_column_info('{dataset_name}') is deprecated.")
    df = get_view("tasi_financials")

    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


# DEPRECATED: Old dataset display names - no longer needed with auto-routing
DATASET_DISPLAY_NAMES = {
    "analytics": "Analytics View (Pre-joined)",
    "filings": "Company Filings (Metadata)",
    "facts": "Financial Facts (Metrics)",
    "ratios": "Financial Ratios",
}


def get_dataset_display_name(name: str) -> str:
    """DEPRECATED: Get the display name for a dataset."""
    logger.warning(f"get_dataset_display_name('{name}') is deprecated.")
    return DATASET_DISPLAY_NAMES.get(name, name)
