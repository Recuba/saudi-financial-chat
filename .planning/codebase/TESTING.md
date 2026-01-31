# Testing Patterns

**Analysis Date:** 2025-01-31

## Test Framework

**Runner:**
- pytest (version not pinned in requirements.txt)
- Config: `pytest.ini`

**Configuration (`pytest.ini`):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

**Assertion Library:**
- Built-in `assert` statements (pytest style)

**Run Commands:**
```bash
pytest                           # Run all tests
pytest -v                        # Verbose output (default via addopts)
pytest tests/test_chat.py        # Run specific file
pytest -k "test_format"          # Run tests matching pattern
pytest --cov                     # Coverage (if pytest-cov installed)
```

## Test File Organization

**Location:**
- Separate `tests/` directory at project root
- Not co-located with source files

**Naming:**
- Files: `test_{module_name}.py`
- Functions: `test_{what_is_being_tested}_{expected_behavior}`

**Structure:**
```
tests/
├── __init__.py
├── test_app.py
├── test_chat.py
├── test_comparison_mode.py
├── test_data_loader.py
├── test_data_preview.py
├── test_data_processing.py
├── test_error_display.py
├── test_example_questions.py
├── test_export.py
├── test_integration.py
├── test_llm_config.py
├── test_loading.py
├── test_query_suggestions.py
├── test_session_manager.py
├── test_sidebar.py
├── test_styles.py
└── test_visualizations.py
```

## Test Structure

**Suite Organization:**
```python
"""Tests for chat component utilities."""

import pytest


def test_format_response_dataframe():
    """Test formatting DataFrame responses."""
    import pandas as pd
    from components.chat import format_response

    # Create mock response
    class MockResponse:
        type = "dataframe"
        value = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        last_code_executed = "df.head()"

    result = format_response(MockResponse())

    assert result["type"] == "dataframe"
    assert result["data"] is not None
    assert result["code"] == "df.head()"
```

**Patterns:**
- Module docstring at top of test file
- Imports inside test functions (allows tests to run independently)
- Each test has descriptive docstring
- Arrange-Act-Assert pattern (implicit)
- No fixtures used (simple test structure)

## Mocking

**Framework:** Inline mock classes (no pytest-mock or unittest.mock)

**Patterns:**
```python
# Define mock class inline
class MockResponse:
    type = "text"
    value = "The average is 42.5"
    last_code_executed = "df['col'].mean()"

result = format_response(MockResponse())
```

**Mock Missing Attributes:**
```python
class MockResponse:
    pass  # No attributes - tests graceful handling

result = format_response(MockResponse())
assert result["type"] == "text"  # Should handle with defaults
```

**What to Mock:**
- PandasAI response objects
- Session state structures
- External service responses

**What NOT to Mock:**
- Actual parquet data files (loaded in integration tests)
- Pure functions (test actual implementation)
- DataFrame operations

## Fixtures and Factories

**Test Data:**
```python
# Create test DataFrames inline
df = pd.DataFrame({
    "company_name": ["Test Corp"],
    "revenue": [1000000],
})

# Standard test data patterns
df = pd.DataFrame({
    "company": ["A", "B", "C"],
    "revenue": [100, 200, 150]
})
```

**Location:**
- No separate fixtures file
- Test data created inline in each test
- No `conftest.py` with shared fixtures

## Coverage

**Requirements:** Not enforced (no coverage thresholds configured)

**Coverage Tool:** pytest-cov (`.coverage` file present)

**View Coverage:**
```bash
pytest --cov=components --cov=utils --cov-report=html
# View htmlcov/index.html
```

**Coverage Directory:** `htmlcov/` (present in project)

## Test Types

**Unit Tests:**
- Test individual functions in isolation
- Most tests in codebase are unit tests
- Focus on single function behavior
- Example: `test_format_response_dataframe()`, `test_export_to_csv()`

**Integration Tests:**
- File: `tests/test_integration.py`
- Test data pipeline end-to-end
- Test actual parquet file loading
- Test filter application flow
- Organized with section headers:
```python
# =============================================================================
# Data Pipeline Integration Tests
# =============================================================================
```

**E2E Tests:**
- Not implemented
- No Streamlit testing framework (like streamlit-testing-library)

## Common Patterns

**Testing Return Types:**
```python
def test_load_data_returns_dict():
    """Test that load_data returns a dictionary of dataframes."""
    from utils.data_loader import load_data

    result = load_data()

    assert isinstance(result, dict)
    assert "filings" in result
    assert "facts" in result
```

**Testing Data Structures:**
```python
def test_session_defaults_have_required_keys():
    """Test that all required keys are in defaults."""
    from components.session_manager import SESSION_DEFAULTS

    required_keys = [
        "chat_history",
        "favorite_queries",
        "recent_queries",
    ]

    for key in required_keys:
        assert key in SESSION_DEFAULTS, f"Missing required key: {key}"
```

**Testing Error Handling:**
```python
def test_get_dataset_invalid_name():
    """Test that get_dataset raises error for invalid name."""
    from utils.data_loader import get_dataset

    with pytest.raises(ValueError) as exc_info:
        get_dataset("invalid_name")

    assert "invalid" in str(exc_info.value).lower()
```

**Testing Functions Are Callable:**
```python
def test_chat_functions_callable():
    """Test that chat functions are callable."""
    from components.chat import (
        format_response,
        get_chat_history,
        add_to_chat_history,
        clear_chat_history,
    )

    assert callable(format_response)
    assert callable(get_chat_history)
```

**Testing CSS/Styles:**
```python
def test_css_contains_theme_variables():
    """Test that CSS includes theme variables."""
    from styles.css import get_base_css

    css = get_base_css()

    assert "--gold-primary" in css
    assert "--bg-dark" in css
```

**Testing Visualization Functions:**
```python
def test_create_bar_chart_returns_figure():
    """Test creating a bar chart returns Plotly figure."""
    from components.visualizations.response_charts import create_bar_chart

    df = pd.DataFrame({
        "company": ["A", "B", "C"],
        "revenue": [100, 200, 150]
    })

    fig = create_bar_chart(df, x="company", y="revenue", title="Revenue")

    assert fig is not None
    assert hasattr(fig, "to_html")  # Plotly figure attribute
```

**Testing With Actual Data (Integration):**
```python
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
```

## Writing New Tests

**Template for New Test File:**
```python
"""Tests for {module_name}."""

import pytest
import pandas as pd  # if needed


def test_{function_name}_{expected_behavior}():
    """Test that {description of what is being tested}."""
    from {module}.{submodule} import {function}

    # Arrange
    input_data = ...

    # Act
    result = function(input_data)

    # Assert
    assert result == expected
```

**Checklist for New Tests:**
- [ ] Descriptive function name starting with `test_`
- [ ] Docstring explaining what is tested
- [ ] Imports inside test function
- [ ] Clear assertions with helpful messages
- [ ] No external dependencies (mock if needed)
- [ ] Test both success and error cases

---

*Testing analysis: 2025-01-31*
