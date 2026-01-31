# External Integrations

**Analysis Date:** 2026-01-31

## APIs & External Services

**LLM Provider (OpenRouter):**
- Service: OpenRouter (LLM API gateway)
- SDK/Client: `pandasai-litellm` via `LiteLLM` class
- Auth: `OPENROUTER_API_KEY` (Streamlit secrets)
- Base URL: `https://openrouter.ai/api/v1/models`
- Implementation: `utils/llm_config.py`

**Default Model:**
- ID: `openrouter/google/gemini-2.0-flash-001`
- Display: "Gemini 2.0 Flash"
- Configurable via sidebar model selector

**API Calls:**
```python
# Model list fetching (utils/llm_config.py:21-58)
requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {api_key}"},
    timeout=10
)

# LLM initialization (utils/llm_config.py:198-210)
from pandasai_litellm.litellm import LiteLLM
llm = LiteLLM(model=selected_model, api_key=api_key)
pai.config.set({"llm": llm})
```

## Data Storage

**Databases:**
- Type: File-based (Parquet files)
- No external database connection
- Data loaded from local `data/` directory

**Data Files:**
| File | Purpose |
|------|---------|
| `data/filings.parquet` | Company metadata |
| `data/facts_numeric.parquet` | Financial metrics |
| `data/ratios.parquet` | Calculated ratios |
| `data/analytics_view.parquet` | Pre-joined view |

**Data Loading:**
```python
# utils/data_loader.py:20-46
@st.cache_data(show_spinner=False)
def load_data() -> Dict[str, pd.DataFrame]:
    data = {
        "filings": pd.read_parquet(base_path / "filings.parquet"),
        "facts": pd.read_parquet(base_path / "facts_numeric.parquet"),
        "ratios": pd.read_parquet(base_path / "ratios.parquet"),
        "analytics": pd.read_parquet(base_path / "analytics_view.parquet"),
    }
```

**File Storage:**
- Local filesystem only
- Export outputs to user downloads (CSV, TXT, Markdown)
- Temporary chart images stored in OS temp directory

**Caching:**
- Streamlit in-memory cache (`@st.cache_data`)
- No external cache (Redis, Memcached)

## Authentication & Identity

**Auth Provider:**
- Optional: `streamlit-authenticator` package
- Implementation: `components/advanced/auth.py`
- Falls back to demo mode when not configured

**Demo Mode:**
- Default behavior when auth not configured
- Accepts any non-empty username
- No password validation
- Full feature access

**Session Storage:**
- Streamlit session state only
- No persistent auth tokens
- Cookie name: `saudi_financial_chat_auth` (when auth configured)

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Rollbar, etc.)
- Python `logging` module for internal logs
- PandasAI logs to `pandasai.log`

**Logs:**
- Standard Python logging
- Logger per module: `logging.getLogger(__name__)`
- Log file: `pandasai.log` (PandasAI operations)

**Usage Analytics:**
- Disabled: `.streamlit/config.toml` sets `gatherUsageStats = false`

## CI/CD & Deployment

**Hosting:**
- Primary: Streamlit Cloud
- Alternative: Any Python hosting (Heroku, etc.)
- Dev: VS Code Dev Containers / GitHub Codespaces

**CI Pipeline:**
- GitHub Actions: `.github/workflows/claude.yml`
  - Purpose: Claude Code integration for PR automation
  - Trigger: @claude mentions in issues/PRs
  - Not a traditional CI/CD pipeline

**No automated testing/deployment pipeline detected.**

## Environment Configuration

**Required env vars:**
| Variable | Purpose | Location |
|----------|---------|----------|
| `OPENROUTER_API_KEY` | LLM API authentication | `.streamlit/secrets.toml` |

**Secrets location:**
- Local: `.streamlit/secrets.toml` (gitignored)
- Production: Streamlit Cloud secrets dashboard
- Example: `.streamlit/secrets.toml.example`

**Configuration Files:**
| File | Purpose |
|------|---------|
| `.streamlit/config.toml` | Streamlit theme/settings |
| `.streamlit/secrets.toml` | API keys (local) |
| `runtime.txt` | Python version |
| `pytest.ini` | Test configuration |
| `.devcontainer/devcontainer.json` | VS Code dev container |

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Third-Party SDKs Summary

| SDK | Version | Purpose | Import Location |
|-----|---------|---------|-----------------|
| PandasAI | >=3.0.0 | NL queries | `components/chat.py` |
| LiteLLM | via pandasai-litellm | LLM routing | `utils/llm_config.py` |
| Plotly | >=5.0.0 | Charts | `components/visualizations/` |
| Pillow | latest | Image handling | `components/chat.py` |

## Rate Limits & Quotas

**OpenRouter:**
- Rate limits depend on API key tier
- No client-side rate limiting implemented
- Request timeout: 10 seconds for model list

**Streamlit:**
- Session state limits apply
- No explicit memory management

## Graceful Degradation

The application handles missing optional dependencies:

```python
# Pattern used throughout codebase
try:
    import streamlit_plotly_events
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
```

**Degradation behavior:**
| Missing Dependency | Fallback |
|-------------------|----------|
| `streamlit-authenticator` | Demo mode auth |
| `streamlit-plotly-events` | Charts without click events |
| `openpyxl` | No Excel export (CSV only) |

---

*Integration audit: 2026-01-31*
