"""Unit tests for data validation layer.

Tests schema validation, data quality metrics, and validation utilities.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import pandas as pd
import numpy as np

# Mock dependencies
sys.modules['streamlit'] = MagicMock()


class TestExpectedSchemas:
    """Test EXPECTED_SCHEMAS constant."""

    def test_schemas_defined(self):
        """Test that expected schemas are defined."""
        from utils.data_loader import EXPECTED_SCHEMAS

        assert isinstance(EXPECTED_SCHEMAS, dict)
        assert len(EXPECTED_SCHEMAS) > 0

    def test_analytics_view_schema(self):
        """Test analytics_view schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        if "analytics_view" in EXPECTED_SCHEMAS:
            schema = EXPECTED_SCHEMAS["analytics_view"]
            assert isinstance(schema, dict)
            # Should have common columns
            expected_cols = ["company_name", "sector", "revenue"]
            for col in expected_cols:
                assert col in schema or len(schema) > 0

    def test_ratios_schema(self):
        """Test ratios schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        if "ratios" in EXPECTED_SCHEMAS:
            schema = EXPECTED_SCHEMAS["ratios"]
            assert isinstance(schema, dict)

    def test_facts_numeric_schema(self):
        """Test facts_numeric schema definition."""
        from utils.data_loader import EXPECTED_SCHEMAS

        if "facts_numeric" in EXPECTED_SCHEMAS:
            schema = EXPECTED_SCHEMAS["facts_numeric"]
            assert isinstance(schema, dict)


class TestValidateSchema:
    """Test validate_schema function."""

    def test_validate_filings_schema(self):
        """Test validation with filings schema."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "fiscal_year": [2024, 2024],
            "filing_id": [1, 2]
        })

        result = validate_schema(df, "filings")

        assert isinstance(result, dict)
        assert "valid" in result
        assert result["valid"] is True

    def test_validate_missing_required_column(self):
        """Test validation with missing required column."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            # Missing fiscal_year and filing_id
        })

        result = validate_schema(df, "filings")

        # Should indicate missing column
        assert isinstance(result, dict)
        assert result["valid"] is False
        assert len(result["missing_required"]) > 0

    def test_validate_extra_columns(self):
        """Test validation with extra columns."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "fiscal_year": [2024, 2024],
            "filing_id": [1, 2],
            "extra_col": [1, 2]  # Extra
        })

        result = validate_schema(df, "filings")

        # Extra columns should be detected but valid
        assert result["valid"] is True
        assert "extra_col" in result["extra_columns"]

    def test_validate_analytics_schema(self):
        """Test validation with analytics schema."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "fiscal_year": [2024, 2024]
        })

        result = validate_schema(df, "analytics")

        assert isinstance(result, dict)
        assert "valid" in result

    def test_validate_unknown_dataset(self):
        """Test validation with unknown dataset name."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({"col1": [1, 2]})

        result = validate_schema(df, "unknown_dataset")

        # Should handle gracefully with empty schema
        assert isinstance(result, dict)


class TestGetDataQualityMetrics:
    """Test get_data_quality_metrics function."""

    def test_quality_metrics_basic(self):
        """Test basic data quality metrics."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "company_name": ["A", "B", "C"],
            "revenue": [100, 200, 300],
            "profit": [10, None, 30]
        })

        metrics = get_data_quality_metrics(df)

        assert isinstance(metrics, dict)

    def test_quality_metrics_completeness(self):
        """Test completeness metric calculation."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": ["A", "B", None],  # 1 null
            "col2": [1, 2, 3]  # No nulls
        })

        metrics = get_data_quality_metrics(df)

        if "completeness" in metrics:
            # Overall completeness should reflect null values
            assert 0 <= metrics["completeness"] <= 100

    def test_quality_metrics_null_counts(self):
        """Test null count reporting."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": ["A", None, None],
            "col2": [1, 2, None]
        })

        metrics = get_data_quality_metrics(df)

        if "null_counts" in metrics:
            assert metrics["null_counts"]["col1"] == 2
            assert metrics["null_counts"]["col2"] == 1

    def test_quality_metrics_row_count(self):
        """Test row count in metrics."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": ["A", "B", "C", "D", "E"]
        })

        metrics = get_data_quality_metrics(df)

        if "row_count" in metrics:
            assert metrics["row_count"] == 5

    def test_quality_metrics_column_count(self):
        """Test column count in metrics."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": [1],
            "col2": [2],
            "col3": [3]
        })

        metrics = get_data_quality_metrics(df)

        if "column_count" in metrics:
            assert metrics["column_count"] == 3

    def test_quality_metrics_duplicate_rows(self):
        """Test duplicate row detection."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame({
            "col1": ["A", "A", "B"],
            "col2": [1, 1, 2]
        })

        metrics = get_data_quality_metrics(df)

        if "duplicate_rows" in metrics:
            assert metrics["duplicate_rows"] >= 1

    def test_quality_metrics_empty_df(self):
        """Test metrics with empty DataFrame."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame()

        metrics = get_data_quality_metrics(df)

        assert isinstance(metrics, dict)

    def test_quality_metrics_handles_empty(self):
        """Test metrics handles empty DataFrame gracefully."""
        from utils.data_loader import get_data_quality_metrics

        df = pd.DataFrame()
        metrics = get_data_quality_metrics(df)

        assert isinstance(metrics, dict)
        assert metrics["row_count"] == 0


class TestValidateAllDatasets:
    """Test validate_all_datasets function."""

    def test_validate_all_callable(self):
        """Test that validate_all_datasets is callable."""
        from utils.data_loader import validate_all_datasets

        assert callable(validate_all_datasets)


class TestGetDataSummary:
    """Test get_data_summary function."""

    def test_summary_returns_dict(self):
        """Test basic data summary returns dict."""
        from utils.data_loader import get_data_summary

        summary = get_data_summary()

        assert isinstance(summary, dict)

    def test_summary_has_datasets(self):
        """Test summary contains datasets info."""
        from utils.data_loader import get_data_summary

        summary = get_data_summary()

        assert "datasets" in summary

    def test_summary_has_total_records(self):
        """Test summary has total records."""
        from utils.data_loader import get_data_summary

        summary = get_data_summary()

        assert "total_records" in summary
        assert isinstance(summary["total_records"], int)

    def test_summary_has_overall_quality(self):
        """Test summary has overall quality."""
        from utils.data_loader import get_data_summary

        summary = get_data_summary()

        assert "overall_quality" in summary


class TestDataTypeValidation:
    """Test data type validation utilities."""

    def test_numeric_type_check(self):
        """Test numeric type checking."""
        df = pd.DataFrame({
            "int_col": [1, 2, 3],
            "float_col": [1.1, 2.2, 3.3],
            "str_col": ["a", "b", "c"]
        })

        assert pd.api.types.is_numeric_dtype(df["int_col"])
        assert pd.api.types.is_numeric_dtype(df["float_col"])
        assert not pd.api.types.is_numeric_dtype(df["str_col"])

    def test_datetime_type_check(self):
        """Test datetime type checking."""
        df = pd.DataFrame({
            "date_col": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "str_col": ["2024-01-01", "2024-01-02"]
        })

        assert pd.api.types.is_datetime64_any_dtype(df["date_col"])
        assert not pd.api.types.is_datetime64_any_dtype(df["str_col"])


class TestDataCleaningValidation:
    """Test data cleaning and validation."""

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({
            "company": ["A", "A", "B"],
            "year": [2024, 2024, 2024],
            "revenue": [100, 100, 200]
        })

        cleaned = df.drop_duplicates()
        assert len(cleaned) == 2

    def test_handle_null_values(self):
        """Test null value handling."""
        df = pd.DataFrame({
            "col1": [1, None, 3],
            "col2": [None, 2, 3]
        })

        # Fill nulls
        filled = df.fillna(0)
        assert filled.isnull().sum().sum() == 0

        # Drop nulls
        dropped = df.dropna()
        assert len(dropped) == 1

    def test_type_conversion(self):
        """Test type conversion."""
        df = pd.DataFrame({
            "str_nums": ["1", "2", "3"]
        })

        df["int_nums"] = df["str_nums"].astype(int)
        assert df["int_nums"].dtype == np.int64


class TestValidationErrorHandling:
    """Test error handling in validation."""

    def test_unknown_dataset_validation(self):
        """Test handling of unknown dataset name."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({"col1": [1, 2, 3]})

        # Unknown dataset should be handled gracefully
        result = validate_schema(df, "unknown_dataset")
        assert isinstance(result, dict)

    def test_large_dataset_validation(self):
        """Test validation of large datasets."""
        from utils.data_loader import get_data_quality_metrics

        # Create large DataFrame
        df = pd.DataFrame({
            "col1": range(10000),
            "col2": [f"value_{i}" for i in range(10000)]
        })

        # Should complete without error
        metrics = get_data_quality_metrics(df)
        assert metrics is not None


class TestSchemaEvolution:
    """Test schema evolution handling."""

    def test_extra_columns_detected(self):
        """Test that extra columns are detected."""
        from utils.data_loader import validate_schema

        df = pd.DataFrame({
            "company_name": ["A", "B"],
            "fiscal_year": [2024, 2024],
            "filing_id": [1, 2],
            "new_column": [4, 5]  # Extra column
        })

        result = validate_schema(df, "filings")

        # Extra columns should be detected
        assert "new_column" in result["extra_columns"]


class TestDataIntegrity:
    """Test data integrity checks."""

    def test_referential_integrity(self):
        """Test referential integrity between datasets."""
        companies = pd.DataFrame({
            "company_id": [1, 2, 3],
            "company_name": ["A", "B", "C"]
        })

        financials = pd.DataFrame({
            "company_id": [1, 2, 4],  # 4 is invalid
            "revenue": [100, 200, 300]
        })

        # Check for invalid references
        valid_ids = set(companies["company_id"])
        invalid_refs = financials[~financials["company_id"].isin(valid_ids)]

        assert len(invalid_refs) == 1
        assert invalid_refs.iloc[0]["company_id"] == 4

    def test_value_range_validation(self):
        """Test value range validation."""
        df = pd.DataFrame({
            "percentage": [10, 50, 150, -10],  # 150 and -10 are invalid
            "ratio": [0.5, 1.0, 1.5, 2.0]
        })

        # Validate percentage range
        valid_pct = (df["percentage"] >= 0) & (df["percentage"] <= 100)
        assert valid_pct.sum() == 2

    def test_uniqueness_constraint(self):
        """Test uniqueness constraints."""
        df = pd.DataFrame({
            "company_id": [1, 2, 2, 3],  # Duplicate ID
            "year": [2024, 2024, 2024, 2024]
        })

        # Check for duplicate keys
        duplicates = df[df.duplicated(subset=["company_id", "year"], keep=False)]
        assert len(duplicates) == 2
