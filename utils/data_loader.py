"""Data loading utilities for Ra'd AI.

Provides cached data loading with error handling, dataset statistics,
and data validation layer.
"""

import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, Optional, List, Any
import logging

logger = logging.getLogger(__name__)


# Expected schema definitions for validation
EXPECTED_SCHEMAS = {
    "filings": {
        "required_columns": ["company_name", "fiscal_year", "filing_id"],
        "optional_columns": ["sector", "symbol", "ticker", "isin", "currency", "scale_factor"],
    },
    "facts": {
        "required_columns": ["filing_id", "metric", "value_sar"],
        "optional_columns": ["company_name", "fiscal_year", "period_end"],
    },
    "ratios": {
        "required_columns": ["filing_id", "ratio", "value"],
        "optional_columns": ["company_name", "fiscal_year"],
    },
    "analytics": {
        "required_columns": ["company_name", "fiscal_year"],
        "optional_columns": ["sector", "revenue", "net_profit", "total_assets", "roe", "roa"],
    },
}


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


# --- DATA VALIDATION LAYER ---

def validate_schema(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """Validate DataFrame against expected schema.

    Args:
        df: DataFrame to validate
        dataset_name: Name of dataset for schema lookup

    Returns:
        Dictionary with validation results
    """
    schema = EXPECTED_SCHEMAS.get(dataset_name, {})
    required_cols = schema.get("required_columns", [])
    optional_cols = schema.get("optional_columns", [])

    results = {
        "valid": True,
        "missing_required": [],
        "missing_optional": [],
        "extra_columns": [],
        "warnings": [],
    }

    df_cols = set(df.columns.tolist())
    expected_cols = set(required_cols + optional_cols)

    # Check required columns
    for col in required_cols:
        if col not in df_cols:
            results["missing_required"].append(col)
            results["valid"] = False

    # Check optional columns
    for col in optional_cols:
        if col not in df_cols:
            results["missing_optional"].append(col)

    # Check for extra columns (informational)
    results["extra_columns"] = list(df_cols - expected_cols)

    if results["missing_required"]:
        results["warnings"].append(
            f"Missing required columns: {', '.join(results['missing_required'])}"
        )

    return results


def get_data_quality_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate data quality metrics for a DataFrame.

    Args:
        df: DataFrame to analyze

    Returns:
        Dictionary with quality metrics
    """
    total_cells = df.shape[0] * df.shape[1]
    null_cells = df.isnull().sum().sum()

    metrics = {
        "row_count": len(df),
        "column_count": len(df.columns),
        "total_cells": total_cells,
        "null_cells": int(null_cells),
        "completeness_pct": round((1 - null_cells / total_cells) * 100, 2) if total_cells > 0 else 0,
        "column_null_counts": {},
        "column_completeness": {},
    }

    # Per-column null analysis
    for col in df.columns:
        null_count = int(df[col].isnull().sum())
        metrics["column_null_counts"][col] = null_count
        completeness = round((1 - null_count / len(df)) * 100, 2) if len(df) > 0 else 0
        metrics["column_completeness"][col] = completeness

    # Identify problematic columns (>50% null)
    metrics["low_quality_columns"] = [
        col for col, pct in metrics["column_completeness"].items()
        if pct < 50
    ]

    return metrics


def validate_all_datasets() -> Dict[str, Dict[str, Any]]:
    """Validate all loaded datasets.

    Returns:
        Dictionary mapping dataset names to validation results
    """
    data = load_data()
    results = {}

    for name, df in data.items():
        schema_valid = validate_schema(df, name)
        quality = get_data_quality_metrics(df)

        results[name] = {
            "schema_validation": schema_valid,
            "quality_metrics": quality,
            "overall_status": "valid" if schema_valid["valid"] and quality["completeness_pct"] > 80 else "warning"
        }

    return results


def get_data_summary() -> Dict[str, Any]:
    """Get a comprehensive data summary for display.

    Returns:
        Dictionary with summary statistics
    """
    data = load_data()
    validation = validate_all_datasets()

    summary = {
        "datasets": {},
        "overall_quality": "good",
        "total_records": 0,
        "warnings": [],
    }

    warning_count = 0

    for name, df in data.items():
        summary["datasets"][name] = {
            "rows": len(df),
            "columns": len(df.columns),
            "quality": validation[name]["quality_metrics"]["completeness_pct"],
            "status": validation[name]["overall_status"],
        }
        summary["total_records"] += len(df)

        if validation[name]["overall_status"] == "warning":
            warning_count += 1
            summary["warnings"].extend(validation[name]["schema_validation"]["warnings"])

    if warning_count > 0:
        summary["overall_quality"] = "warning"
    if warning_count > 2:
        summary["overall_quality"] = "poor"

    return summary
