# Technology Stack

**Analysis Date:** 2026-01-31

## Languages

**Primary:**
- Python 3.11 - Core application language (specified in `runtime.txt`)

**Secondary:**
- CSS3 - Custom styling via `styles/css.py` and `styles/variables.py`
- TOML - Configuration files (`.streamlit/config.toml`, `.streamlit/secrets.toml`)

## Runtime

**Environment:**
- Python 3.11 (Heroku/Streamlit Cloud compatible)
- Dev container: `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`

**Package Manager:**
- pip
- Lockfile: Not present (uses `requirements.txt` with version constraints)

## Frameworks

**Core:**
- Streamlit >=1.30.0 - Web application framework
  - Entry point: `app.py`
  - Config: `.streamlit/config.toml`
  - Secrets: `.streamlit/secrets.toml`

**AI/ML:**
- PandasAI >=3.0.0 - Natural language to DataFrame queries
  - Config in `utils/llm_config.py`
  - Uses `pai.DataFrame(dataset).chat(query)` pattern

- pandasai-litellm - LLM adapter for PandasAI
  - Enables OpenRouter/LiteLLM backend

**Data Processing:**
- pandas >=2.0.0,<3.0.0 - DataFrame operations
- numpy <2.0.0 - Numerical computations
- pyarrow - Parquet file I/O

**Visualization:**
- Plotly >=5.0.0 - Interactive charts
  - Components in `components/visualizations/`
  - Theme colors defined in `components/visualizations/plotly_interactive.py`

- Pillow - Image processing for PandasAI chart outputs

**Testing:**
- pytest - Test runner
  - Config: `pytest.ini`
  - Tests: `tests/` directory

## Key Dependencies

**Critical:**
- `pandasai` >=3.0.0 - Core NL-to-code engine
- `streamlit` >=1.30.0 - Web framework
- `pandas` >=2.0.0 - Data manipulation
- `pyarrow` - Parquet file support (required for data loading)

**Infrastructure:**
- `requests` - HTTP client for OpenRouter API calls
- `pandasai-litellm` - LLM provider adapter

**Optional (graceful degradation):**
- `streamlit-plotly-events` - Click handling in charts (checked at runtime)
- `streamlit-authenticator` - Authentication (falls back to demo mode)
- `openpyxl` - Excel export (optional feature)

## Configuration

**Environment:**
- Single required env var: `OPENROUTER_API_KEY`
  - Set via `.streamlit/secrets.toml` locally
  - Set via Streamlit Cloud secrets in production
  - Example in `.streamlit/secrets.toml.example`

**Build:**
- `.streamlit/config.toml` - Streamlit theme and settings:
  - Dark theme with gold (#D4A84B) primary color
  - Background: #0E0E0E
  - Usage stats disabled

**Runtime configuration:**
- `runtime.txt` - Python version for Heroku/Streamlit Cloud

## Platform Requirements

**Development:**
- Python 3.11
- pip for package management
- ~500MB disk for dependencies
- OpenRouter API key for LLM features

**Production:**
- Streamlit Cloud (primary deployment target)
- Port 8501 (Streamlit default)
- Parquet data files in `data/` directory

**Dev Containers:**
- VS Code devcontainer support via `.devcontainer/devcontainer.json`
- Auto-runs `streamlit run app.py` on attach

## Data Format

**Storage:**
- Parquet files (columnar, compressed)
- Located in `data/` directory:
  - `filings.parquet` - Company metadata
  - `facts_numeric.parquet` - Financial metrics
  - `ratios.parquet` - Calculated ratios
  - `analytics_view.parquet` - Pre-joined view

**Caching:**
- Streamlit `@st.cache_data` decorator for data loading
- Model list cached 1 hour (`ttl=3600`)

## Version Constraints

| Package | Constraint | Reason |
|---------|------------|--------|
| numpy | <2.0.0 | PandasAI compatibility |
| pandas | >=2.0.0,<3.0.0 | Stable API, pyarrow integration |
| streamlit | >=1.30.0 | chat_input, modern widgets |
| pandasai | >=3.0.0 | Latest architecture |
| plotly | >=5.0.0 | Modern API |

---

*Stack analysis: 2026-01-31*
