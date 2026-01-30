"""Tests for data loader utility."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import MagicMock


def test_load_data_function_callable():
    """Test that load_data function is callable."""
    from utils.data_loader import load_data

    assert callable(load_data)


def test_data_loader_constants():
    """Test that data loader constants are defined."""
    from utils.data_loader import EXPECTED_SCHEMAS, DATASET_DISPLAY_NAMES

    assert isinstance(EXPECTED_SCHEMAS, dict)
    assert isinstance(DATASET_DISPLAY_NAMES, dict)
    assert len(EXPECTED_SCHEMAS) >= 4
    assert len(DATASET_DISPLAY_NAMES) >= 4


def test_get_data_path():
    """Test that get_data_path returns valid path."""
    from utils.data_loader import get_data_path

    path = get_data_path()
    assert isinstance(path, Path)


def test_get_dataset_info_function_callable():
    """Test that get_dataset_info function is callable."""
    from utils.data_loader import get_dataset_info

    assert callable(get_dataset_info)


def test_get_dataset_invalid_name():
    """Test that get_dataset raises error for invalid name."""
    from utils.data_loader import get_dataset

    with pytest.raises(ValueError):
        get_dataset("invalid_name")


def test_get_data_path():
    """Test that get_data_path returns valid path."""
    from utils.data_loader import get_data_path

    path = get_data_path()
    assert isinstance(path, Path)
    assert path.exists()


def test_get_dataset_display_name():
    """Test dataset display names."""
    from utils.data_loader import get_dataset_display_name

    assert get_dataset_display_name("analytics") == "Analytics View (Pre-joined)"
    assert get_dataset_display_name("filings") == "Company Filings (Metadata)"
    assert get_dataset_display_name("unknown") == "unknown"


class TestExpectedSchemas:
    """Test EXPECTED_SCHEMAS constant."""

    def test_schemas_defined(self):
        """Test that expected schemas are defined."""
        from utils.data_loader import EXPECTED_SCHEMAS

        assert isinstance(EXPECTED_SCHEMAS, dict)
        assert len(EXPECTED_SCHEMAS) >= 4

    def test_filings_schema(self):
        """Test filings schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        schema = EXPECTED_SCHEMAS["filings"]
        assert "required_columns" in schema
        assert "company_name" in schema["required_columns"]
        assert "fiscal_year" in schema["required_columns"]

    def test_facts_schema(self):
        """Test facts schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        schema = EXPECTED_SCHEMAS["facts"]
        assert "required_columns" in schema
        assert "filing_id" in schema["required_columns"]

    def test_ratios_schema(self):
        """Test ratios schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        schema = EXPECTED_SCHEMAS["ratios"]
        assert "required_columns" in schema

    def test_analytics_schema(self):
        """Test analytics schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        schema = EXPECTED_SCHEMAS["analytics"]
        assert "required_columns" in schema
        assert "company_name" in schema["required_columns"]


class TestValidateSchema:
    """Test validate_schema function."""

    def test_valid_schema(self):
        """Test validation with matching schema."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "fiscal_year": [2024, 2024],
            "filing_id": [1, 2]
        })

        result = validate_schema(df, "filings")

        assert result["valid"] is True
        assert len(result["missing_required"]) == 0

    def test_missing_required_column(self):
        """Test validation with missing required column."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            # Missing fiscal_year and filing_id
        })

        result = validate_schema(df, "filings")

        assert result["valid"] is False
        assert "fiscal_year" in result["missing_required"]
        assert "filing_id" in result["missing_required"]

    def test_extra_columns(self):
        """Test that extra columns are detected."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A"],
            "fiscal_year": [2024],
            "filing_id": [1],
            "extra_column": ["value"]  # Extra
        })

        result = validate_schema(df, "filings")

        assert "extra_column" in result["extra_columns"]

    def test_optional_columns_missing(self):
        """Test that missing optional columns are tracked."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A"],
            "fiscal_year": [2024],
            "filing_id": [1]
            # Missing optional columns like sector, symbol
        })

        result = validate_schema(df, "filings")

        assert len(result["missing_optional"]) > 0

    def test_unknown_dataset(self):
        """Test validation with unknown dataset name."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({"col1": [1]})

        result = validate_schema(df, "unknown_dataset")

        # Should handle gracefully
        assert isinstance(result, dict)


class TestGetDataQualityMetrics:
    """Test get_data_quality_metrics function."""

    def test_basic_metrics(self):
        """Test basic quality metrics calculation."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": ["a", "b", "c"]
        })

        metrics = get_data_quality_metrics(df)

        assert metrics["row_count"] == 3
        assert metrics["column_count"] == 2
        assert metrics["total_cells"] == 6
        assert metrics["null_cells"] == 0
        assert metrics["completeness_pct"] == 100.0

    def test_metrics_with_nulls(self):
        """Test metrics with null values."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": [1, None, 3],
            "col2": [None, None, "c"]
        })

        metrics = get_data_quality_metrics(df)

        assert metrics["null_cells"] == 3
        assert metrics["completeness_pct"] == 50.0

    def test_column_null_counts(self):
        """Test per-column null counts."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": [1, None, 3],
            "col2": [None, None, None]
        })

        metrics = get_data_quality_metrics(df)

        assert metrics["column_null_counts"]["col1"] == 1
        assert metrics["column_null_counts"]["col2"] == 3

    def test_low_quality_columns(self):
        """Test detection of low quality columns."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "good_col": [1, 2, 3, 4, 5],
            "bad_col": [None, None, None, None, 1]  # 80% null
        })

        metrics = get_data_quality_metrics(df)

        assert "bad_col" in metrics["low_quality_columns"]
        assert "good_col" not in metrics["low_quality_columns"]

    def test_empty_dataframe(self):
        """Test metrics with empty DataFrame."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame()

        metrics = get_data_quality_metrics(df)

        assert metrics["row_count"] == 0
        assert metrics["column_count"] == 0


class TestValidateAllDatasets:
    """Test validate_all_datasets function."""

    def test_validate_all_callable(self):
        """Test that validate_all_datasets is callable."""
        from utils.data_loader import validate_all_datasets

        assert callable(validate_all_datasets)


class TestGetDataSummary:
    """Test get_data_summary function."""

    def test_summary_callable(self):
        """Test that get_data_summary is callable."""
        from utils.data_loader import get_data_summary

        assert callable(get_data_summary)


class TestGetColumnInfo:
    """Test get_column_info function."""

    def test_column_info_callable(self):
        """Test that get_column_info is callable."""
        from utils.data_loader import get_column_info

        assert callable(get_column_info)
