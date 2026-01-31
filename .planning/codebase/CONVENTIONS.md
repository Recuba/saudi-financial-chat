# Coding Conventions

**Analysis Date:** 2025-01-31

## Naming Patterns

**Files:**
- Use `snake_case.py` for all Python files
- Component files named after their primary function: `chat.py`, `sidebar.py`, `export.py`
- Test files prefixed with `test_`: `test_chat.py`, `test_export.py`
- Module constants in dedicated files: `variables.py` for design tokens

**Functions:**
- Use `snake_case` for all functions
- Prefix with `render_` for Streamlit UI functions: `render_sidebar()`, `render_chat_input()`
- Prefix with `get_` for retrieval functions: `get_dataset()`, `get_chat_history()`
- Prefix with `format_` for transformation functions: `format_response()`, `format_api_error()`
- Prefix with `export_` for export functions: `export_to_csv()`, `export_response_to_text()`
- Prefix with `add_`/`remove_`/`clear_` for state mutations: `add_to_chat_history()`, `clear_chat_history()`

**Variables:**
- Use `snake_case` for local variables and parameters
- Use descriptive names: `response_data`, `dataset_choice`, `model_changed`

**Constants:**
- Use `UPPER_SNAKE_CASE` for module-level constants
- Group related constants: `CURRENCY_COLUMNS`, `RATIO_COLUMNS`
- Define at module top after imports
- Examples from `utils/data_processing.py`:
```python
CURRENCY_COLUMNS = [
    'revenue', 'net_profit', 'gross_profit', 'operating_profit',
    'total_assets', 'total_equity', ...
]
```

**Types/Classes:**
- Use `PascalCase` for classes (rare in codebase)
- Type hints use standard library types: `Dict`, `List`, `Optional`, `Any`, `Tuple`
- Import from `typing` module

## Code Style

**Formatting:**
- 4-space indentation
- No explicit formatter configuration detected
- Max line length approximately 100 characters (informal)
- Blank line between function definitions
- Two blank lines before top-level definitions

**Linting:**
- No explicit linter configuration detected (no `.flake8`, `ruff.toml`, etc.)
- Code follows PEP 8 conventions informally

## Import Organization

**Order:**
1. Standard library imports
2. Try/except blocks for optional dependencies
3. Third-party imports
4. Local imports (relative or absolute)

**Pattern for Optional Dependencies:**
```python
try:
    import streamlit as st
except ImportError:
    st = None  # Allow module to be imported for testing without streamlit

try:
    import pandas as pd
except ImportError:
    pd = None
```

**Path Aliases:**
- No path aliases configured
- Use relative imports within packages: `from .variables import GOLD_PRIMARY`
- Use absolute imports for cross-package: `from utils.data_loader import load_data`

## Error Handling

**Patterns:**
- Guard clauses for optional dependencies:
```python
if st is None:
    raise RuntimeError("Streamlit is required to render chat input")
```

- Try/except with logging for data operations:
```python
try:
    data = load_data()
except FileNotFoundError as e:
    logger.error(f"Data file not found: {e}")
    raise
except Exception as e:
    logger.error(f"Error loading data: {e}")
    raise
```

- Return error dictionaries instead of raising exceptions for API responses:
```python
return {
    "type": "error",
    "data": None,
    "code": None,
    "message": error_msg
}
```

- Pattern-based error classification in `components/error_display.py`:
```python
ERROR_PATTERNS: Dict[str, Dict[str, Any]] = {
    "auth": {
        "patterns": ["authentication", "api key", "unauthorized", "401"],
        "title": "API Key Issue",
        "description": "...",
        "steps": [...],
    },
}
```

## Logging

**Framework:** Standard library `logging`

**Patterns:**
- Create logger at module level:
```python
import logging
logger = logging.getLogger(__name__)
```

- Use appropriate log levels:
  - `logger.info()` for successful operations
  - `logger.error()` for errors with context
```python
logger.info(f"Loaded {len(data)} datasets successfully")
logger.error(f"Query processing error: {error_msg}")
```

## Comments

**When to Comment:**
- Module-level docstrings describing purpose
- Function docstrings with Args/Returns sections
- Inline comments for complex logic (sparingly used)
- Section separators in `__init__.py` files:
```python
# ============================================================================
# Core Components (always available - used by app.py)
# ============================================================================
```

**Docstring Format (Google style):**
```python
def format_response(response: Any) -> Dict[str, Any]:
    """Format a PandasAI response for display.

    Args:
        response: PandasAI response object

    Returns:
        Dictionary with type, data, code, and optional message
    """
```

## Function Design

**Size:** Functions are typically 10-50 lines, focused on single responsibility

**Parameters:**
- Use type hints for all parameters
- Optional parameters use `Optional[Type]` with default `None`
- Use keyword arguments for clarity in complex functions:
```python
def format_dataframe_for_display(
    df: pd.DataFrame,
    normalize: bool = True,
    format_values: bool = True,
    currency_column: str = 'currency'
) -> pd.DataFrame:
```

**Return Values:**
- Always specify return type
- Return `None` explicitly when appropriate
- Use `Dict[str, Any]` for structured responses
- Use `Tuple` for multiple return values: `-> Tuple[str, bool]`

## Module Design

**Exports:**
- Define `__all__` list in `__init__.py` for explicit exports
- Re-export commonly used functions at package level
- Use lazy loading for optional components:
```python
def _try_import_tables():
    """Lazily import tables components."""
    global TABLES_AVAILABLE
    try:
        from .tables import (...)
        TABLES_AVAILABLE = True
        return True
    except ImportError:
        return False
```

**Barrel Files:**
- Each package has `__init__.py` that re-exports public API
- `components/__init__.py`: ~200 lines, exports all component functions
- `styles/__init__.py`: Re-exports variables and CSS functions
- `utils/__init__.py`: Re-exports data and LLM utilities

## Streamlit Patterns

**Session State:**
- Initialize with defaults:
```python
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
```

- Use session manager for complex state: `components/session_manager.py`
- Access via getter/setter functions for consistency

**Component Structure:**
- Separate render functions from logic
- Return values from components for parent coordination:
```python
def render_sidebar() -> Tuple[str, bool]:
    """Render the complete sidebar.

    Returns:
        Tuple of (selected dataset name, model_changed boolean)
    """
```

**Caching:**
- Use `@st.cache_data` for data loading:
```python
@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, pd.DataFrame]:
```

---

*Convention analysis: 2025-01-31*
