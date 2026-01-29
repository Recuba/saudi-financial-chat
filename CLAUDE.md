# CLAUDE.md - AI Assistant Guide for Saudi Financial Chat

## Project Overview

**Ra'd AI (رعد)** is a Streamlit-based natural language interface for querying Saudi XBRL financial data from Tadawul (Saudi Stock Exchange). Users can ask questions in plain English/Arabic about financial metrics, ratios, and company data, and receive tabular results, charts, or text responses.

**Key Technologies:**
- **Frontend/UI:** Streamlit
- **AI/NLP:** PandasAI 3.0 + LiteLLM
- **LLM Provider:** OpenRouter (Google Gemini 2.0 Flash)
- **Data Format:** Parquet files (pre-processed from Saudi XBRL reports)
- **Runtime:** Python 3.11

## Repository Structure

```
saudi-financial-chat/
├── app.py                    # Main application (single-file monolith)
├── requirements.txt          # Python dependencies
├── runtime.txt               # Python version (3.11) for Streamlit Cloud
├── README.md                 # User-facing documentation
├── CLAUDE.md                 # This file - AI assistant guide
├── .gitignore
│
├── data/                     # Financial datasets (~918 KB total)
│   ├── analytics_view.parquet   # Pre-joined analytics (361 KB)
│   ├── facts_numeric.parquet    # Individual financial metrics (295 KB)
│   ├── filings.parquet          # Company filing metadata (52 KB)
│   └── ratios.parquet           # Calculated financial ratios (210 KB)
│
├── .streamlit/
│   ├── config.toml           # Theme configuration (dark/gold)
│   └── secrets.toml.example  # Secrets template
│
├── .devcontainer/
│   └── devcontainer.json     # VS Code/Codespaces dev container
│
└── .github/
    └── workflows/
        └── claude.yml        # Claude Code GitHub Action
```

## Architecture

### Single-File Application (`app.py`)

The entire application is contained in `app.py` (~424 lines), organized into logical sections:

| Lines | Section | Description |
|-------|---------|-------------|
| 1-14 | Imports | Core dependencies |
| 16-25 | LLM Config | LiteLLM + OpenRouter setup |
| 27-32 | Page Config | Streamlit page settings |
| 34-269 | Custom CSS | CSS variables and Ra'd branding |
| 271-279 | Data Loading | Cached parquet file loading |
| 281-283 | Title | Brand header with Arabic |
| 285-323 | Sidebar | Dataset selection & info |
| 325-337 | Data Preview | Expandable data preview |
| 339-356 | Examples | Pre-built query buttons |
| 359-419 | Chat Logic | Main query processing |
| 421-423 | Footer | Branding footer |

### Data Flow

```
User Query → st.chat_input → PandasAI DataFrame.chat() → LLM (Gemini)
    → Generated Python/Pandas Code → Execute → Response (DataFrame/Chart/Text)
```

## Key Code Patterns

### Data Loading with Caching
```python
@st.cache_data
def load_data():
    base_path = Path(__file__).parent / "data"
    filings = pd.read_parquet(base_path / "filings.parquet")
    # ... load other datasets
    return filings, facts, ratios, analytics
```

### PandasAI Integration
```python
# LLM configuration
llm = LiteLLM(
    model="openrouter/google/gemini-2.0-flash-001",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)
pai.config.set({"llm": llm})

# Query execution
df = pai.DataFrame(selected_df)
response = df.chat(prompt)
```

### Response Type Handling
The app handles three response types from PandasAI:
- `response.type == 'dataframe'` → Display with `st.dataframe()`
- `response.type == 'chart'` → Display image with `st.image()`
- Other → Display as text with `st.write()`

### Session State for Button Queries
```python
if st.button("Top 10 companies by revenue 2024"):
    st.session_state.query = "What are the top 10 companies by revenue in 2024?"

if "query" in st.session_state and st.session_state.query:
    prompt = st.session_state.query
    st.session_state.query = None
```

## Development Workflows

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Create secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit secrets.toml and add your OPENROUTER_API_KEY

# Run the app
streamlit run app.py
```

### Dev Container (VS Code/Codespaces)
- Opens in Python 3.11 container
- Auto-installs dependencies
- Auto-launches Streamlit on port 8501
- Opens README.md and app.py automatically

### Deployment (Streamlit Cloud)
1. Push to GitHub (public repo required for free tier)
2. Connect to Streamlit Cloud
3. Set main file: `app.py`
4. Add secret: `OPENROUTER_API_KEY`

## Code Conventions

### Styling
- **Theme:** Dark background with gold accents (Ra'd branding)
- **Primary Color:** `#D4A84B` (gold)
- **Background:** `#0E0E0E` (near-black)
- **CSS Variables:** Defined in `:root` block for consistency
- **Font:** Tajawal (Arabic-friendly Google Font)

### CSS Variable System
```css
:root {
    --gold-primary: #D4A84B;
    --gold-light: #E8C872;
    --gold-dark: #B8860B;
    --bg-dark: #0E0E0E;
    --bg-card: #1A1A1A;
    --text-primary: #FFFFFF;
    /* ... more variables */
}
```

### Naming Conventions
- Dataset names: lowercase (`analytics`, `filings`, `facts`, `ratios`)
- Variables: snake_case
- CSS classes: kebab-case (`brand-title`, `brand-subtitle`)

### Error Handling
```python
try:
    response = df.chat(prompt)
    # ... process response
except Exception as e:
    st.error(f"Error: {str(e)}")
```

## Datasets

### analytics_view.parquet
Pre-joined analytical data combining company info with financial metrics. Best for most queries.

### filings.parquet
Company filing metadata including:
- Company names and identifiers
- Filing dates and fiscal periods
- Sector classifications

### facts_numeric.parquet
Individual financial metrics with columns:
- `metric` - Name of the financial metric
- `value` - Numerical value
- Related company/period identifiers

### ratios.parquet
Calculated financial ratios:
- ROE, ROA, debt ratios
- Profit margins
- Liquidity ratios

## Common Tasks for AI Assistants

### Adding a New Example Question
In `app.py`, find the "Example Questions" section (around line 340) and add a new button:
```python
if st.button("Your question label"):
    st.session_state.query = "Your full question text?"
```

### Modifying the Theme
1. Update CSS variables in `app.py` (lines 41-71)
2. Update `.streamlit/config.toml` for base theme colors

### Adding a New Dataset
1. Add parquet file to `data/` directory
2. Update `load_data()` function to load new file
3. Add to `dataset_map` dictionary
4. Update sidebar selectbox options

### Changing the LLM Model
In `app.py` line 18, modify the model string:
```python
llm = LiteLLM(
    model="openrouter/your-model-here",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)
```

## Dependencies

```
numpy           # Numerical operations
pandas          # Data manipulation
pandasai>=3.0.0 # Natural language to pandas
pandasai_litellm # LLM provider bridge
Pillow          # Image processing for charts
streamlit       # Web UI framework
pyarrow         # Parquet file support
```

## Environment Variables / Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | API key for OpenRouter (provides access to Gemini) |

## GitHub Actions

The repository includes a Claude Code GitHub Action (`.github/workflows/claude.yml`) that:
- Triggers on `@claude` mentions in issues/PRs
- Uses Claude Opus 4 model
- Has read-only permissions

## Important Notes for AI Assistants

1. **Single-file architecture:** All application logic is in `app.py`. Keep it that way unless there's a strong reason to split.

2. **CSS in Python:** Custom styling is embedded as a string in `app.py`. Use CSS variables for consistency.

3. **Arabic support:** The app supports Arabic text. Use the Tajawal font for Arabic content.

4. **No backend:** This is a pure Streamlit app with no separate API server.

5. **Data is static:** The parquet files contain pre-processed data. To update data, replace the parquet files.

6. **Secrets management:** Never commit API keys. Use `.streamlit/secrets.toml` locally and Streamlit Cloud secrets in production.

7. **PandasAI 3.0:** The app uses PandasAI >= 3.0.0 which has different API patterns than 2.x versions. Use `pai.DataFrame()` and `df.chat()`.

8. **Response cleanup:** Chart images are temporary files that get deleted after display (`os.remove(response.value)`).

## Testing

There are no automated tests in this repository. Manual testing workflow:
1. Run `streamlit run app.py`
2. Test each example question button
3. Test custom queries across different datasets
4. Verify chart generation works
5. Check error handling with invalid queries

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key error | Check `OPENROUTER_API_KEY` in secrets |
| Import errors | Ensure `pandasai>=3.0.0` is installed |
| Chart not displaying | Check Pillow is installed |
| Data not loading | Verify parquet files exist in `data/` |
