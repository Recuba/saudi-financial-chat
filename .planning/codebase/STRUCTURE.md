# Codebase Structure

**Analysis Date:** 2026-01-31

## Directory Layout

```
saudi-financial-chat/
├── .github/                # GitHub workflows (CI/CD)
├── .planning/              # GSD planning documents
│   └── codebase/           # Architecture and convention docs
├── .streamlit/             # Streamlit configuration
├── assets/                 # Static assets (logo)
├── components/             # UI components (main feature modules)
│   ├── advanced/           # Advanced features (auth, profiler)
│   ├── chat_enhanced/      # Enhanced chat features
│   ├── filters/            # Data filtering components
│   ├── navigation/         # Navigation components
│   ├── tables/             # Table display components
│   └── visualizations/     # Chart and graph components
├── data/                   # Financial data (parquet files)
│   ├── archive/            # Old data versions
│   ├── files2/             # Additional data processing
│   └── xlsx_companies/     # Source XLSX files
├── docs/                   # Documentation
│   └── plans/              # Planning documents
├── exports/                # Generated export files
├── scripts/                # Data processing scripts
├── styles/                 # CSS and design tokens
├── tests/                  # Test suite
├── utils/                  # Utility modules
├── app.py                  # Main application entry point
├── app_refactored.py       # Alternative implementation (legacy)
├── requirements.txt        # Python dependencies
└── pytest.ini              # Test configuration
```

## Directory Purposes

**components/:**
- Purpose: All reusable UI components for the Streamlit app
- Contains: Python modules with `render_*` functions, component classes
- Key files: `chat.py`, `sidebar.py`, `session_manager.py`, `example_questions.py`
- Sub-packages have `__init__.py` with public exports

**components/filters/:**
- Purpose: Data filtering and selection UI
- Contains: Dynamic filters, tree selectors, date pickers, advanced filters
- Key files: `advanced_filters.py` (used in main app), `dynamic_filters.py`

**components/visualizations/:**
- Purpose: Charting and visualization components
- Contains: Plotly, ECharts, sparklines, relationship graphs
- Key files: `response_charts.py` (auto-visualization), `plotly_interactive.py`

**utils/:**
- Purpose: Non-UI business logic and helpers
- Contains: Data loading, LLM configuration, data processing
- Key files: `data_loader.py`, `llm_config.py`, `data_processing.py`

**styles/:**
- Purpose: Centralized design system
- Contains: CSS variables, color palette, spacing tokens, CSS generators
- Key files: `variables.py` (design tokens), `css.py` (CSS generators)

**data/:**
- Purpose: Financial data storage
- Contains: Parquet files with Tadawul company financials
- Key files: `filings.parquet`, `facts_numeric.parquet`, `ratios.parquet`, `analytics_view.parquet`

**tests/:**
- Purpose: Test suite with pytest
- Contains: Unit tests, integration tests
- Key files: `test_chat.py`, `test_data_loader.py`, `test_integration.py`

## Key File Locations

**Entry Points:**
- `app.py`: Main Streamlit application (run with `streamlit run app.py`)
- `.streamlit/config.toml`: Streamlit theme and browser config

**Configuration:**
- `.streamlit/config.toml`: Streamlit theme (dark mode, gold colors)
- `requirements.txt`: Python package dependencies
- `pytest.ini`: Test runner configuration
- `runtime.txt`: Python version for deployment

**Core Logic:**
- `components/chat.py`: Chat interface, query processing, response rendering
- `components/sidebar.py`: Dataset selection, model selector, column reference
- `utils/data_loader.py`: Parquet loading with caching
- `utils/llm_config.py`: OpenRouter/LiteLLM configuration

**Session Management:**
- `components/session_manager.py`: Session state helpers, defaults, favorites

**Styling:**
- `styles/variables.py`: Design tokens (colors, spacing, typography)
- `styles/css.py`: CSS generator functions

**Data Files:**
- `data/analytics_view.parquet`: Pre-joined view (recommended for queries)
- `data/filings.parquet`: Company metadata
- `data/facts_numeric.parquet`: Financial metrics
- `data/ratios.parquet`: Calculated financial ratios

**Testing:**
- `tests/test_app.py`: Main app tests
- `tests/test_chat.py`: Chat component tests
- `tests/test_integration.py`: End-to-end integration tests

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `data_loader.py`, `session_manager.py`)
- Test files: `test_<module>.py` (e.g., `test_chat.py`, `test_sidebar.py`)
- Config files: lowercase (e.g., `config.toml`, `requirements.txt`)

**Directories:**
- Packages: `lowercase` (e.g., `components`, `utils`, `filters`)
- Sub-packages: `snake_case` (e.g., `chat_enhanced`)

**Functions:**
- Render functions: `render_<element>()` (e.g., `render_sidebar()`, `render_chat_input()`)
- Getters: `get_<item>()` (e.g., `get_chat_history()`, `get_session_value()`)
- Setters: `set_<item>()` (e.g., `set_session_value()`, `set_selected_model()`)
- Validators: `validate_<item>()` or `check_<item>()` (e.g., `validate_api_key()`)
- Formatters: `format_<item>()` (e.g., `format_response()`, `format_api_error()`)
- Creators: `create_<item>()` (e.g., `create_bar_chart()`, `create_comparison_chart()`)

**Variables/Constants:**
- Module constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_MODEL`, `SESSION_DEFAULTS`)
- Design tokens: `UPPER_SNAKE_CASE` (e.g., `GOLD_PRIMARY`, `BG_DARK`)

## Where to Add New Code

**New Feature (Full Component):**
- Primary code: `components/<feature_name>.py`
- Tests: `tests/test_<feature_name>.py`
- Import in: `components/__init__.py` if public API
- Use in: `app.py` with appropriate render call

**New Visualization Type:**
- Implementation: `components/visualizations/<chart_type>.py`
- Export in: `components/visualizations/__init__.py`
- Use lazy import pattern for optional dependencies

**New Filter Type:**
- Implementation: `components/filters/<filter_name>.py`
- Export in: `components/filters/__init__.py`

**New Utility Function:**
- Shared helpers: `utils/<category>.py` (existing or new module)
- Export in: `utils/__init__.py`

**New CSS/Styling:**
- Design tokens: Add to `styles/variables.py`
- CSS rules: Add function in `styles/css.py` or extend `get_base_css()`

**New Data Processing:**
- Scripts: `scripts/<action>_<target>.py`
- Runtime utilities: `utils/data_processing.py`

## Special Directories

**.streamlit/:**
- Purpose: Streamlit configuration and secrets
- Generated: No (manually maintained)
- Committed: `config.toml` yes, `secrets.toml` no (gitignored)

**exports/:**
- Purpose: User-generated export files (CSV, MD)
- Generated: Yes (at runtime)
- Committed: No (transient)

**htmlcov/:**
- Purpose: Test coverage reports
- Generated: Yes (by pytest-cov)
- Committed: No

**data/archive/:**
- Purpose: Historical/backup data files
- Generated: Partially (manual backups)
- Committed: Varies

**.planning/:**
- Purpose: GSD planning and codebase analysis
- Generated: By GSD commands
- Committed: Yes

---

*Structure analysis: 2026-01-31*
