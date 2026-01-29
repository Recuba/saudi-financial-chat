"""Data loading utilities for Ra'd AI.

Provides cached data loading with error handling and dataset statistics.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def get_data_path() -> Path:
    """Get the path to the data directory."""
    return Path(__file__).parent.parent / "data"


@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, pd.DataFrame]:
    """Load all datasets from parquet files.

    Returns:
        Dictionary with keys: filings, facts, ratios, analytics

    Raises:
        FileNotFoundError: If data files are missing
    """
    base_path = get_data_path()

    try:
        data = {
            "filings": pd.read_parquet(base_path / "filings.parquet"),
            "facts": pd.read_parquet(base_path / "facts_numeric.parquet"),
            "ratios": pd.read_parquet(base_path / "ratios.parquet"),
            "analytics": pd.read_parquet(base_path / "analytics_view.parquet"),
        }
        logger.info(f"Loaded {len(data)} datasets successfully")
        return data
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise


def get_dataset(name: str) -> pd.DataFrame:
    """Get a specific dataset by name.

    Args:
        name: One of 'filings', 'facts', 'ratios', 'analytics'

    Returns:
        The requested DataFrame

    Raises:
        ValueError: If dataset name is invalid
    """
    valid_names = ["filings", "facts", "ratios", "analytics"]
    if name not in valid_names:
        raise ValueError(f"Invalid dataset name: {name}. Must be one of {valid_names}")

    data = load_data()
    return data[name]


def get_dataset_info() -> Dict[str, int]:
    """Get summary statistics about loaded datasets.

    Returns:
        Dictionary with counts for companies, periods, metrics, ratios
    """
    data = load_data()

    return {
        "companies": data["filings"]["company_name"].nunique(),
        "periods": len(data["filings"]),
        "metrics": data["facts"]["metric"].nunique(),
        "ratios": data["ratios"]["ratio"].nunique(),
    }


def get_column_info(dataset_name: str) -> Dict[str, list]:
    """Get column information for a dataset."""
    df = get_dataset(dataset_name)

    result = {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }

    if dataset_name == "facts":
        result["metrics"] = df["metric"].unique().tolist()
    elif dataset_name == "ratios":
        result["ratio_names"] = df["ratio"].unique().tolist()

    return result


# Dataset display names
DATASET_DISPLAY_NAMES = {
    "analytics": "Analytics View (Pre-joined)",
    "filings": "Company Filings (Metadata)",
    "facts": "Financial Facts (Metrics)",
    "ratios": "Financial Ratios",
}


def get_dataset_display_name(name: str) -> str:
    """Get the display name for a dataset."""
    return DATASET_DISPLAY_NAMES.get(name, name)
