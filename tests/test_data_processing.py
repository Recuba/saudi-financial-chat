# tests/test_data_processing.py
import pytest
import pandas as pd
from utils.data_processing import (
    normalize_to_sar,
    format_sar_abbreviated,
    format_percentage,
    format_ratio,
    get_column_type,
    create_styled_dataframe
)

def test_normalize_scale_1():
    """Values with scale_factor=1 should remain unchanged."""
    df = pd.DataFrame({
        'revenue': [1000000.0],
        'scale_factor': [1]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_scale_1000():
    """Values with scale_factor=1000 should be multiplied by 1000."""
    df = pd.DataFrame({
        'revenue': [1000.0],
        'scale_factor': [1000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_scale_1000000():
    """Values with scale_factor=1000000 should be multiplied by 1000000."""
    df = pd.DataFrame({
        'revenue': [1.0],
        'scale_factor': [1000000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert result['revenue'].iloc[0] == 1000000.0

def test_normalize_handles_null():
    """Null values should remain null after normalization."""
    df = pd.DataFrame({
        'revenue': [None],
        'scale_factor': [1000]
    })
    result = normalize_to_sar(df, ['revenue'])
    assert pd.isna(result['revenue'].iloc[0])


class TestFormatSarAbbreviated:
    def test_billions(self):
        assert format_sar_abbreviated(1_500_000_000) == 'SAR 1.5B'

    def test_millions(self):
        assert format_sar_abbreviated(2_500_000) == 'SAR 2.5M'

    def test_thousands(self):
        assert format_sar_abbreviated(5_500) == 'SAR 5.5K'

    def test_small_values(self):
        assert format_sar_abbreviated(500) == 'SAR 500'

    def test_negative(self):
        assert format_sar_abbreviated(-1_500_000_000) == 'SAR -1.5B'

    def test_null(self):
        assert format_sar_abbreviated(None) == '-'


class TestFormatPercentage:
    def test_positive(self):
        assert format_percentage(0.25) == '25.0%'

    def test_negative(self):
        assert format_percentage(-0.10) == '-10.0%'

    def test_null(self):
        assert format_percentage(None) == '-'


class TestFormatRatio:
    def test_normal(self):
        assert format_ratio(2.15) == '2.15x'

    def test_null(self):
        assert format_ratio(None) == '-'


class TestGetColumnType:
    def test_currency_column(self):
        assert get_column_type('revenue') == 'currency'
        assert get_column_type('net_profit') == 'currency'

    def test_percentage_column(self):
        assert get_column_type('roe') == 'percentage'
        assert get_column_type('gross_margin') == 'percentage'

    def test_ratio_column(self):
        assert get_column_type('current_ratio') == 'ratio'
        assert get_column_type('debt_to_equity') == 'ratio'

    def test_ratio_not_currency(self):
        # These should be ratio, not currency (bug fix verification)
        assert get_column_type('cash_conversion') == 'ratio'
        assert get_column_type('ocf_to_current_liabilities') == 'ratio'

    def test_unknown_column(self):
        assert get_column_type('company_name') == 'text'


def test_create_styled_dataframe():
    """Styled dataframe should return Styler object."""
    df = pd.DataFrame({
        'revenue': [1_000_000_000],
        'roe': [0.25],
        'current_ratio': [1.5]
    })
    styled = create_styled_dataframe(df)
    assert isinstance(styled, pd.io.formats.style.Styler)
