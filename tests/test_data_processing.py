# tests/test_data_processing.py
import pytest
import pandas as pd
from utils.data_processing import normalize_to_sar

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
