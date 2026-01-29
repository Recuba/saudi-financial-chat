"""Integration tests for Ra'd AI."""

import pytest
import pandas as pd
from pathlib import Path


# =============================================================================
# Data Pipeline Integration Tests
# =============================================================================


def test_parquet_files_exist():
    """All required parquet files should exist."""
    data_dir = Path(__file__).parent.parent / "data"

    required_files = [
        "analytics_view.parquet",
        "facts_numeric.parquet",
        "filings.parquet",
        "ratios.parquet"
    ]

    for f in required_files:
        assert (data_dir / f).exists(), f"Missing file: {f}"


def test_analytics_view_has_required_columns():
    """Analytics view should have required columns."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "analytics_view.parquet")

    required_columns = [
        'company_name', 'fiscal_year', 'revenue', 'net_profit',
        'total_assets', 'roe', 'current_ratio'
    ]

    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"


def test_ratios_have_expected_structure():
    """Ratios file should have expected structure."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "ratios.parquet")

    required_columns = ['filing_id', 'ratio', 'value']
    for col in required_columns:
        assert col in df.columns, f"Missing column: {col}"


# =============================================================================
# Query Flow Integration Tests
# =============================================================================


def test_full_query_flow():
    """Test the complete query processing flow."""
    from components.chat import format_response

    # Test with mock data
    df = pd.DataFrame({
        "company_name": ["Test Corp"],
        "revenue": [1000000],
    })

    # format_response handles mock responses
    class MockResponse:
        type = "dataframe"
        value = df
        last_code_executed = "df"

    result = format_response(MockResponse())

    assert result["type"] == "dataframe"
    assert result["data"] is not None


# =============================================================================
# Filter Integration Tests
# =============================================================================


def test_filters_apply_correctly():
    """Test that filters modify data correctly."""
    from components.filters.advanced_filters import apply_filters

    df = pd.DataFrame({
        "sector": ["Tech", "Finance", "Tech"],
        "company_name": ["A", "B", "C"],
        "fiscal_year": [2023, 2023, 2022],
    })

    filters = {"sectors": ["Tech"]}
    filtered = apply_filters(df, filters)

    assert len(filtered) == 2
    assert all(filtered["sector"] == "Tech")


# =============================================================================
# Export Integration Tests
# =============================================================================


def test_export_produces_valid_output():
    """Test that exports produce valid files."""
    from components.export import export_to_csv, export_response_to_text

    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

    csv = export_to_csv(df)
    assert "a,b" in csv

    text = export_response_to_text({
        "type": "dataframe",
        "data": df,
        "code": "df",
    })
    assert "dataframe" in text.lower()


# =============================================================================
# Comparison Mode Integration Tests
# =============================================================================


def test_comparison_entities():
    """Test entity comparison works correctly."""
    from components.comparison_mode import compare_entities

    df = pd.DataFrame({
        "company_name": ["A", "A", "B", "B"],
        "fiscal_year": [2023, 2022, 2023, 2022],
        "revenue": [100, 90, 200, 180],
    })

    result = compare_entities(
        df,
        entity_col="company_name",
        entities=["A", "B"],
        metrics=["revenue"],
        year=2023
    )

    assert len(result) == 2
    assert set(result["company_name"].tolist()) == {"A", "B"}


# =============================================================================
# Query Suggestions Integration Tests
# =============================================================================


def test_query_suggestions_integration():
    """Test query suggestions work with partial input."""
    from components.query_suggestions import get_suggestions, COMMON_QUERIES

    # Test with partial input
    suggestions = get_suggestions("top", limit=5)

    assert isinstance(suggestions, list)
    assert len(suggestions) <= 5
    assert all("top" in s.lower() for s in suggestions)


# =============================================================================
# Session Manager Integration Tests
# =============================================================================


def test_session_defaults_integration():
    """Test session defaults are properly structured."""
    from components.session_manager import SESSION_DEFAULTS, get_session_defaults

    defaults = get_session_defaults()

    # Verify all expected keys exist
    assert "chat_history" in defaults
    assert "filters" in defaults
    assert "favorite_queries" in defaults

    # Verify types
    assert isinstance(defaults["chat_history"], list)
    assert isinstance(defaults["filters"], dict)


# =============================================================================
# Data Loader Integration Tests
# =============================================================================


def test_data_loader_integration():
    """Test data loading returns proper structures."""
    from utils.data_loader import DATASET_DISPLAY_NAMES, get_dataset_display_name

    # Verify display names exist
    assert "analytics" in DATASET_DISPLAY_NAMES
    assert "filings" in DATASET_DISPLAY_NAMES

    # Verify getter works
    name = get_dataset_display_name("analytics")
    assert len(name) > 0


# =============================================================================
# CSS Integration Tests
# =============================================================================


def test_css_integration():
    """Test CSS modules work together."""
    from styles.css import get_base_css, get_error_css
    from styles.variables import GOLD_PRIMARY, BG_DARK

    base_css = get_base_css()
    error_css = get_error_css()

    # Both should produce valid CSS
    assert "<style>" in base_css
    assert "</style>" in base_css
    assert "error" in error_css.lower()

    # Variables should be hex colors
    assert GOLD_PRIMARY.startswith("#")
    assert BG_DARK.startswith("#")


# =============================================================================
# Data Processing Integration Tests
# =============================================================================


def test_no_scientific_notation_in_formatted():
    """Formatted values should not contain scientific notation."""
    from utils.data_processing import format_sar_abbreviated

    test_values = [1e12, 1e9, 1e6, 1e3, 100]

    for val in test_values:
        formatted = format_sar_abbreviated(val)
        assert 'e+' not in formatted.lower(), f"Scientific notation found in {formatted}"


def test_format_dataframe_preserves_row_count():
    """Formatting should not change row count."""
    from utils.data_processing import format_dataframe_for_display

    df = pd.DataFrame({
        'revenue': [1e9, 2e9, 3e9],
        'roe': [0.1, 0.2, 0.3],
        'company': ['A', 'B', 'C']
    })

    formatted = format_dataframe_for_display(df, normalize=False, format_values=True)

    assert len(formatted) == len(df), "Formatting changed row count"


def test_format_dataframe_formats_currency():
    """Currency columns should be formatted with SAR prefix."""
    from utils.data_processing import format_dataframe_for_display

    df = pd.DataFrame({
        'revenue': [1_500_000_000],
        'company': ['Test Co']
    })

    formatted = format_dataframe_for_display(df, normalize=False, format_values=True)

    # Revenue should contain SAR
    assert 'SAR' in str(formatted['revenue'].iloc[0])
