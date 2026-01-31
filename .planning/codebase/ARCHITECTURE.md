# Architecture

**Analysis Date:** 2026-01-31

## Pattern Overview

**Overall:** Component-Based Monolith with Layered Separation

**Key Characteristics:**
- Single-page Streamlit application with component composition
- Clear separation between UI components, utilities, and data access
- Session state-driven reactivity (Streamlit's execution model)
- Lazy loading for optional visualization dependencies
- PandasAI as the core NLP-to-code translation engine

## Layers

**Presentation Layer:**
- Purpose: Renders UI elements, handles user interactions
- Location: `components/`
- Contains: Reusable Streamlit components (chat, sidebar, filters, visualizations)
- Depends on: Utils layer, Streamlit, session state
- Used by: Main application (`app.py`)

**Business Logic Layer:**
- Purpose: Data processing, LLM configuration, response formatting
- Location: `utils/`
- Contains: Data loading, LLM initialization, data transformations
- Depends on: External APIs (OpenRouter), pandas, PandasAI
- Used by: Components, main application

**Styling Layer:**
- Purpose: Centralized design system and CSS generation
- Location: `styles/`
- Contains: CSS variables, color palette, typography tokens
- Depends on: None (pure Python constants and functions)
- Used by: Main application (injected as `<style>` tags)

**Data Layer:**
- Purpose: Financial data storage (parquet files)
- Location: `data/`
- Contains: Pre-processed Tadawul XBRL financial data
- Depends on: None (static files)
- Used by: `utils/data_loader.py`

## Data Flow

**Query Processing Flow:**

1. User enters natural language query in chat input (`components/chat.py:render_chat_input`)
2. Query passed to `process_query()` which wraps DataFrame with PandasAI
3. PandasAI generates Python code using LLM via LiteLLM/OpenRouter
4. Generated code executed against pandas DataFrame
5. Response formatted by `format_response()` into structured dict
6. Response rendered via `render_ai_response()` with tabs (Result/Code)
7. Auto-visualization triggered if query contains chart keywords

**State Management:**
- All state stored in `st.session_state` (Streamlit's built-in)
- Session defaults defined in `components/session_manager.py:SESSION_DEFAULTS`
- Chat history, filters, favorites, and preferences persisted in session
- No external database - all state is ephemeral per browser session

**LLM Integration Flow:**

1. API key retrieved from Streamlit secrets (`st.secrets["OPENROUTER_API_KEY"]`)
2. LiteLLM wrapper configured with selected model (`utils/llm_config.py:initialize_llm`)
3. PandasAI config updated with LLM instance (`pai.config.set({"llm": llm})`)
4. All queries routed through OpenRouter to Gemini (default model)

## Key Abstractions

**Component Pattern:**
- Purpose: Encapsulate UI rendering and related logic
- Examples: `components/chat.py`, `components/sidebar.py`, `components/data_preview.py`
- Pattern: Functions prefixed with `render_` return None and produce Streamlit output

**Response Data Dictionary:**
- Purpose: Standardized format for PandasAI responses
- Examples: Created in `components/chat.py:format_response`
- Pattern: Dict with keys `type`, `data`, `code`, `message`
- Types: "dataframe", "chart", "text", "error"

**Session State Helpers:**
- Purpose: Type-safe session state access
- Examples: `get_session_value()`, `set_session_value()`, `initialize_session()`
- Pattern: Functions in `components/session_manager.py` wrap `st.session_state`

**Lazy Import Pattern:**
- Purpose: Graceful degradation for optional dependencies
- Examples: `components/__init__.py`, `components/visualizations/__init__.py`
- Pattern: Try/except imports with fallback stub functions

## Entry Points

**Main Application:**
- Location: `app.py`
- Triggers: `streamlit run app.py`
- Responsibilities: Page config, session init, LLM init, layout composition, query handling

**Refactored Application (Legacy):**
- Location: `app_refactored.py`
- Triggers: Not actively used
- Responsibilities: Alternative implementation, kept for reference

**Streamlit Config:**
- Location: `.streamlit/config.toml`
- Triggers: Auto-loaded by Streamlit
- Responsibilities: Theme configuration (dark mode, gold primary color)

## Error Handling

**Strategy:** Graceful degradation with user-friendly messages

**Patterns:**
- API errors caught in `process_query()`, formatted via `format_api_error()`
- Import errors caught at module level, stub functions provided
- Data loading errors surface via `st.error()` with recovery suggestions
- LLM validation errors return dict with `valid: False` and `error` message

**Error Display:**
- `components/error_display.py` provides `render_error_banner()` and `render_api_key_setup_guide()`
- Errors styled via `styles/css.py:get_error_css()`
- Retry buttons offered for transient failures

## Cross-Cutting Concerns

**Logging:**
- Standard Python logging (`logging.getLogger(__name__)`)
- Used in `utils/data_loader.py`, `utils/llm_config.py`, `components/chat.py`
- Log levels: INFO for success, WARNING for degraded, ERROR for failures

**Validation:**
- API key validation in `utils/llm_config.py:validate_api_key()`
- Dataset name validation in `utils/data_loader.py:get_dataset()`
- Filter validation in `components/filters/advanced_filters.py`

**Caching:**
- Data loading cached via `@st.cache_data` (Streamlit decorator)
- Model list fetched with TTL cache (1 hour) in `utils/llm_config.py`
- No persistent cache - reloads on app restart

**Theming:**
- Design tokens in `styles/variables.py` (colors, spacing, typography)
- CSS generated by `styles/css.py:get_base_css()` and `get_error_css()`
- Streamlit theme in `.streamlit/config.toml` synced with CSS variables

---

*Architecture analysis: 2026-01-31*
