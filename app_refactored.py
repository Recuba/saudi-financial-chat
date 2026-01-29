"""
Saudi Financial Database Chat UI - Refactored
==============================================
A Streamlit app for natural language querying of Saudi XBRL financial data.

This refactored version demonstrates the new component library with:
- Navigation: Option menu and tabbed layouts
- Tables: AG-Grid with SAR formatting
- Filters: Dynamic multi-select filters
- Visualizations: ECharts and Plotly charts
- Chat: Message history with feedback
- Advanced: Data profiling and visual explorer
"""

import pandas as pd
import streamlit as st
import io
from PIL import Image
import os
from pathlib import Path

# Import our component library
from components import (
    # Navigation
    render_sidebar_nav,
    NavItem,
    render_tabs,
    TabItem,
    render_metric_row,
    render_alert,
    AlertType,
    MAIN_NAV_AVAILABLE,
    # Tables
    FinancialGrid,
    create_financial_grid,
    AGGRID_AVAILABLE,
    create_financial_metrics,
    # Filters
    render_dynamic_filters,
    render_filter_summary,
    # Chat
    ChatMessage,
    render_message,
    render_chat_history,
    add_message_to_history,
    clear_chat_history,
    get_chat_history,
    render_star_rating,
    # Visualizations
    create_sector_treemap,
    create_correlation_heatmap,
    THEME_COLORS,
    # Advanced
    render_visual_explorer,
    render_data_profiler,
    PYGWALKER_AVAILABLE,
    YDATA_PROFILING_AVAILABLE,
    # Utilities
    check_all_dependencies,
    show_dependency_status,
)

from utils.theme import COLORS, apply_chart_theme_css, get_chart_colors
import requests
import math

# --- NUMBER FORMATTING HELPERS ---
def format_sr_value(value: float, decimals: int = 1) -> str:
    """
    Format a numeric value as SR currency with proper scaling.
    Scale factor is '000 (thousands).

    Examples:
        1,000,000 -> "SR 1,000MM" (1 million)
        1,500,000,000 -> "SR 1.5B" (1.5 billion)
        50,000 -> "SR 50.0K" (50 thousand)
    """
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"

    abs_value = abs(value)
    if abs_value >= 1e9:
        # Billions
        scaled = value / 1e9
        return f"SR {scaled:,.{decimals}f}B"
    elif abs_value >= 1e6:
        # Millions - show as thousands with MM suffix
        scaled = value / 1e3
        return f"SR {scaled:,.0f}MM"
    elif abs_value >= 1e3:
        # Thousands
        scaled = value / 1e3
        return f"SR {scaled:,.{decimals}f}K"
    else:
        return f"SR {value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a decimal value as percentage (0.538 -> 53.8%)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value * 100:.{decimals}f}%"


def format_ratio(value: float, decimals: int = 2) -> str:
    """Format a numeric value as ratio (1.77 -> 1.77x)."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "-"
    return f"{value:.{decimals}f}x"


# --- DEFAULT MODEL ---
DEFAULT_MODEL = "google/gemini-3-flash-preview"

# --- FETCH OPENROUTER MODELS ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_openrouter_models(api_key: str) -> list:
    """Fetch available models from OpenRouter API."""
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            models = []
            for model in data.get("data", []):
                model_id = model.get("id", "")
                model_name = model.get("name", model_id)
                # Get pricing info
                pricing = model.get("pricing", {})
                prompt_price = float(pricing.get("prompt", 0)) * 1000000  # per 1M tokens
                # Filter to text models only
                arch = model.get("architecture", {})
                if "text" in arch.get("output_modalities", []):
                    models.append({
                        "id": model_id,
                        "name": model_name,
                        "context_length": model.get("context_length", 0),
                        "price_per_1m": prompt_price
                    })
            # Sort by name
            models.sort(key=lambda x: x["name"].lower())
            return models
    except Exception as e:
        st.warning(f"Could not fetch models: {e}")
    return []

# --- LLM CONFIGURATION (with graceful fallback) ---
PANDASAI_AVAILABLE = False
OPENROUTER_API_KEY = None
pai = None

try:
    import pandasai as pai
    from pandasai_litellm.litellm import LiteLLM

    if "OPENROUTER_API_KEY" in st.secrets:
        OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
        PANDASAI_AVAILABLE = True
except ImportError:
    pass
except Exception:
    pass

def get_llm(model_id: str):
    """Create LiteLLM instance with specified model."""
    from pandasai_litellm.litellm import LiteLLM
    return LiteLLM(
        model=f"openrouter/{model_id}",
        api_key=OPENROUTER_API_KEY,
    )

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Ra'd AI | Saudi Financial",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS WITH VARIABLES ---
st.markdown("""
<style>
/* Import Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

/* CSS Custom Properties (Variables) */
:root {
    /* Gold Palette */
    --gold-primary: #D4A84B;
    --gold-light: #E8C872;
    --gold-dark: #B8860B;
    --gold-gradient: linear-gradient(135deg, #D4A84B 0%, #E8C872 50%, #B8860B 100%);

    /* Background Colors */
    --bg-dark: #0E0E0E;
    --bg-card: #1A1A1A;
    --bg-card-hover: #252525;
    --bg-input: #2A2A2A;

    /* Text Colors */
    --text-primary: #FFFFFF;
    --text-secondary: #B0B0B0;
    --text-muted: #707070;

    /* Accent Colors */
    --accent-green: #4CAF50;
    --accent-red: #F44336;

    /* Spacing */
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;

    /* Shadows */
    --shadow-gold: 0 4px 20px rgba(212, 168, 75, 0.3);
    --shadow-card: 0 4px 12px rgba(0, 0, 0, 0.4);
}

/* Global Background */
.stApp {
    background: radial-gradient(ellipse at top, #1a1a1a 0%, var(--bg-dark) 50%) !important;
}

/* Main Container */
[data-testid="stAppViewContainer"] {
    background: transparent !important;
}

[data-testid="stMain"] {
    background: transparent !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-card) 0%, var(--bg-dark) 100%) !important;
    border-right: 1px solid rgba(212, 168, 75, 0.2) !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdown"] {
    color: var(--text-primary) !important;
}

/* Headers */
h1, h2, h3 {
    color: var(--text-primary) !important;
    font-family: 'Tajawal', sans-serif !important;
}

/* Brand Title with Gold Gradient */
.brand-title {
    background: var(--gold-gradient);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    filter: drop-shadow(0 2px 4px rgba(212, 168, 75, 0.4));
}

.brand-subtitle {
    color: var(--text-secondary);
    text-align: center;
    font-size: 1.1rem;
    margin-bottom: 1rem;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid rgba(212, 168, 75, 0.3) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: var(--gold-primary) !important;
    box-shadow: var(--shadow-gold) !important;
    transform: translateY(-2px);
}

[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: var(--gold-light) !important;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dark) 0%, var(--gold-primary) 100%) !important;
    color: var(--bg-dark) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, var(--gold-primary) 0%, var(--gold-light) 100%) !important;
    box-shadow: var(--shadow-gold) !important;
    transform: translateY(-2px) !important;
}

/* Chat Input */
[data-testid="stChatInput"] textarea {
    background: var(--bg-input) !important;
    border: 1px solid rgba(212, 168, 75, 0.3) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: var(--gold-primary) !important;
    box-shadow: 0 0 0 2px rgba(212, 168, 75, 0.2) !important;
}

/* Chat Messages */
[data-testid="stChatMessage"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}

[data-testid="stDataFrame"] table {
    background: var(--bg-card) !important;
}

[data-testid="stDataFrame"] th {
    background: var(--gold-dark) !important;
    color: var(--text-primary) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid rgba(212, 168, 75, 0.2) !important;
    border-radius: var(--radius-md) !important;
}

[data-testid="stExpander"] summary {
    color: var(--gold-light) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-input) !important;
    border: 1px solid rgba(212, 168, 75, 0.3) !important;
    border-radius: var(--radius-sm) !important;
}

/* Divider */
hr {
    border-color: rgba(212, 168, 75, 0.2) !important;
}

/* Tabs */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-radius: var(--radius-sm) !important;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--gold-primary) !important;
    color: var(--bg-dark) !important;
}

/* Code Blocks */
[data-testid="stCode"] {
    background: var(--bg-input) !important;
    border: 1px solid rgba(212, 168, 75, 0.2) !important;
    border-radius: var(--radius-sm) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--bg-dark);
}

::-webkit-scrollbar-thumb {
    background: var(--gold-dark);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gold-primary);
}

/* Caption/Footer */
.stCaption, [data-testid="stCaption"] {
    color: var(--text-muted) !important;
}

/* Spinner */
[data-testid="stSpinner"] {
    color: var(--gold-primary) !important;
}

/* Navigation Cards */
.nav-card {
    background: var(--bg-card);
    border: 1px solid rgba(212, 168, 75, 0.2);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.nav-card:hover {
    border-color: var(--gold-primary);
    box-shadow: var(--shadow-gold);
}
</style>
""", unsafe_allow_html=True)

# Apply chart theme CSS
apply_chart_theme_css()


# --- LOAD DATA ---
@st.cache_data
def load_data():
    base_path = Path(__file__).parent / "data"
    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")
    return filings, facts, ratios, analytics


# --- NAVIGATION ---
NAV_ITEMS = [
    NavItem(label="Dashboard", icon="house"),
    NavItem(label="Data Explorer", icon="table"),
    NavItem(label="Chat AI", icon="chat-dots"),
    NavItem(label="Analytics", icon="graph-up"),
    NavItem(label="Settings", icon="gear"),
]


def render_sidebar():
    """Render the sidebar with navigation and filters."""
    with st.sidebar:
        st.markdown('<h1 class="brand-title">⚡ Ra\'d AI</h1>', unsafe_allow_html=True)
        st.markdown('<p class="brand-subtitle">Saudi Financial Analytics</p>', unsafe_allow_html=True)

        st.divider()

        # Navigation
        if MAIN_NAV_AVAILABLE:
            selected = render_sidebar_nav(
                items=NAV_ITEMS,
                key="main_nav",
            )
        else:
            # Fallback navigation
            nav_options = [item.label for item in NAV_ITEMS]
            selected = st.radio("Navigation", nav_options, label_visibility="collapsed")

        st.divider()

        # Database info
        st.subheader("📁 Database Info")
        filings, facts, ratios, analytics = load_data()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Companies", filings['company_name'].nunique())
            st.metric("Periods", len(filings))
        with col2:
            st.metric("Metrics", facts['metric'].nunique())
            st.metric("Ratios", ratios['ratio'].nunique())

        return selected


# --- PAGE: DASHBOARD ---
def render_dashboard():
    """Render the main dashboard page."""
    st.header("📊 Financial Dashboard")

    filings, facts, ratios, analytics = load_data()

    # Key Metrics Row
    st.subheader("Key Market Indicators")

    # Calculate some metrics
    total_companies = filings['company_name'].nunique()
    latest_year = analytics['fiscal_year'].max() if 'fiscal_year' in analytics.columns else 2024

    # Filter to latest year
    latest_data = analytics[analytics['fiscal_year'] == latest_year] if 'fiscal_year' in analytics.columns else analytics

    # Display metrics in columns
    cols = st.columns(4)
    with cols[0]:
        st.metric("🏢 Total Companies", f"{total_companies:,}")
    with cols[1]:
        st.metric("📅 Latest Year", latest_year)
    with cols[2]:
        st.metric("📊 Total Records", f"{len(analytics):,}")
    with cols[3]:
        sectors = analytics['sector'].nunique() if 'sector' in analytics.columns else 0
        st.metric("🏭 Unique Sectors", sectors)

    st.divider()

    # Two column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Sector Distribution")
        if 'sector' in analytics.columns and 'revenue' in analytics.columns:
            try:
                # Prepare data for treemap
                sector_data = latest_data.groupby('sector').agg({
                    'revenue': 'sum',
                    'company_name': 'count'
                }).reset_index()
                sector_data.columns = ['sector', 'total_revenue', 'company_count']

                create_sector_treemap(
                    data=sector_data,
                    value_column='total_revenue',
                    name_column='sector',
                    sector_column='sector',
                    title=f"Sector by Revenue ({latest_year})",
                    height=400,
                )
            except Exception as e:
                st.info(f"Treemap requires streamlit-echarts. Using fallback.")
                st.bar_chart(analytics.groupby('sector').size())
        else:
            st.info("Sector data not available")

    with col2:
        st.subheader("Quick Stats")
        if 'revenue' in analytics.columns:
            rev = analytics['revenue'].sum()
            st.metric("Total Revenue", format_sr_value(rev))
        if 'net_profit' in analytics.columns:
            profit = analytics['net_profit'].sum()
            st.metric("Total Net Profit", format_sr_value(profit))
        if 'total_assets' in analytics.columns:
            assets = analytics['total_assets'].sum()
            st.metric("Total Assets", format_sr_value(assets))


# --- PAGE: DATA EXPLORER ---
def render_data_explorer():
    """Render the data explorer page with AG-Grid."""
    st.header("🔍 Data Explorer")

    filings, facts, ratios, analytics = load_data()

    # Dataset selection
    dataset_choice = st.selectbox(
        "Select Dataset",
        ["analytics", "filings", "facts", "ratios"],
        format_func=lambda x: {
            "analytics": "📈 Analytics View (Pre-joined)",
            "filings": "🏢 Company Filings (Metadata)",
            "facts": "💰 Financial Facts (Metrics)",
            "ratios": "📊 Financial Ratios"
        }[x]
    )

    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }
    selected_df = dataset_map[dataset_choice]

    # Dynamic filters
    filter_columns = []
    if 'sector' in selected_df.columns:
        filter_columns.append('sector')
    if 'industry' in selected_df.columns:
        filter_columns.append('industry')
    if 'fiscal_year' in selected_df.columns:
        filter_columns.append('fiscal_year')
    if 'company_name' in selected_df.columns:
        filter_columns.append('company_name')

    if filter_columns:
        st.subheader("Filters")
        filtered_df, active_filters = render_dynamic_filters(
            df=selected_df,
            filter_columns=filter_columns[:4],  # Limit to 4 filters
            location="columns",
            show_summary=True,
        )
    else:
        filtered_df = selected_df

    st.subheader(f"Data ({len(filtered_df):,} rows)")

    # Use AG-Grid if available
    if AGGRID_AVAILABLE:
        selected_rows, _ = create_financial_grid(
            data=filtered_df.head(500),  # Limit for performance
            selection_mode="multiple",
            enable_pagination=True,
            page_size=25,
            enable_export=True,
            key="explorer_grid",
        )

        if not selected_rows.empty:
            st.success(f"Selected {len(selected_rows)} rows")
            with st.expander("View Selected Data"):
                st.dataframe(selected_rows, use_container_width=True)
    else:
        st.dataframe(filtered_df.head(500), use_container_width=True, hide_index=True)
        st.caption("Install streamlit-aggrid for enhanced grid features")


# --- PAGE: CHAT AI ---
def render_chat_page():
    """Render the AI chat interface."""
    st.header("💬 Chat with Ra'd AI")

    # Check if PandasAI is configured
    if not PANDASAI_AVAILABLE:
        st.warning("⚠️ **AI Chat requires configuration**")
        st.markdown("""
        To enable AI-powered chat, create a secrets file:

        **1. Create the file:** `.streamlit/secrets.toml`

        **2. Add your API key:**
        ```toml
        OPENROUTER_API_KEY = "sk-or-v1-your-key-here"
        ```

        **3. Get an API key from:** [OpenRouter](https://openrouter.ai/keys)

        **4. Restart the app**
        """)
        return

    filings, facts, ratios, analytics = load_data()

    # Fetch available models
    available_models = fetch_openrouter_models(OPENROUTER_API_KEY)

    # Model and Dataset selection
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        dataset_choice = st.selectbox(
            "Query Dataset",
            ["analytics", "filings", "facts", "ratios"],
            format_func=lambda x: {
                "analytics": "📈 Analytics View",
                "filings": "🏢 Company Filings",
                "facts": "💰 Financial Facts",
                "ratios": "📊 Financial Ratios"
            }[x],
            key="chat_dataset"
        )

    with col2:
        # Model dropdown
        if available_models:
            model_options = [m["id"] for m in available_models]
            model_names = {m["id"]: f"{m['name']} ({m['context_length']//1000}K)" for m in available_models}

            # Find default model index
            default_idx = 0
            for i, m in enumerate(model_options):
                if m == DEFAULT_MODEL:
                    default_idx = i
                    break

            selected_model = st.selectbox(
                "AI Model",
                model_options,
                index=default_idx,
                format_func=lambda x: model_names.get(x, x),
                key="chat_model"
            )
        else:
            selected_model = DEFAULT_MODEL
            st.text_input("AI Model", value=DEFAULT_MODEL, disabled=True)

    with col3:
        if st.button("Clear History", type="secondary"):
            clear_chat_history()
            st.rerun()

    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }
    selected_df = dataset_map[dataset_choice]

    # Example questions
    with st.expander("💡 Example Questions", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Top 10 by revenue 2024"):
                st.session_state.query = "What are the top 10 companies by revenue in 2024?"
            if st.button("Average ROE by sector"):
                st.session_state.query = "Show average ROE by sector"
        with col2:
            if st.button("Companies with D/E > 2"):
                st.session_state.query = "Which companies have debt to equity ratio greater than 2?"
            if st.button("Top 5 by assets chart"):
                st.session_state.query = "Create a bar chart showing top 5 companies by total assets"

    st.divider()

    # Render chat history
    render_chat_history(show_timestamps=True, show_code=True)

    # Chat input
    prompt = st.chat_input("Ask a question about Saudi financial data...")

    # Check for button-triggered query
    if "query" in st.session_state and st.session_state.query:
        prompt = st.session_state.query
        st.session_state.query = None

    if prompt:
        # Add user message
        user_msg = ChatMessage(role="user", content=prompt)
        add_message_to_history(user_msg)
        render_message(user_msg)

        # Configure LLM with selected model
        llm = get_llm(selected_model)
        pai.config.set({"llm": llm})

        # Create PandasAI DataFrame
        df = pai.DataFrame(selected_df)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner(f"Analyzing with {selected_model}..."):
                try:
                    response = df.chat(prompt)

                    if response.type == 'dataframe':
                        tabResult, tabCode = st.tabs(["Result", "Code"])
                        with tabResult:
                            st.dataframe(response.value, use_container_width=True, hide_index=True)
                        with tabCode:
                            st.code(response.last_code_executed, language='python')

                        # Save to history
                        assistant_msg = ChatMessage(
                            role="assistant",
                            content=f"Found {len(response.value)} results",
                            code=response.last_code_executed,
                            metadata={"response_type": "dataframe"}
                        )

                    elif response.type == "chart":
                        with open(response.value, "rb") as f:
                            img_bytes = f.read()
                        img = Image.open(io.BytesIO(img_bytes))

                        tabResult, tabCode = st.tabs(["Result", "Code"])
                        with tabResult:
                            st.image(img)
                        with tabCode:
                            st.code(response.last_code_executed, language='python')

                        os.remove(response.value)

                        assistant_msg = ChatMessage(
                            role="assistant",
                            content="Generated chart",
                            code=response.last_code_executed,
                            metadata={"response_type": "chart"}
                        )

                    else:
                        tabResult, tabCode = st.tabs(["Result", "Code"])
                        with tabResult:
                            st.write(response.value)
                        with tabCode:
                            st.code(response.last_code_executed, language='python')

                        assistant_msg = ChatMessage(
                            role="assistant",
                            content=str(response.value),
                            code=response.last_code_executed,
                        )

                    add_message_to_history(assistant_msg)

                    # Feedback widget
                    st.divider()
                    import uuid
                    msg_id = str(uuid.uuid4())[:8]
                    render_star_rating(
                        message_id=msg_id,
                        query=prompt,
                        response_summary=assistant_msg.content[:100] if assistant_msg.content else "Response",
                        key=f"feedback_{msg_id}"
                    )

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    error_msg = ChatMessage(
                        role="assistant",
                        content=f"Error: {str(e)}",
                        metadata={"error": True}
                    )
                    add_message_to_history(error_msg)


# --- PAGE: ANALYTICS ---
def render_analytics_page():
    """Render advanced analytics page."""
    st.header("📈 Advanced Analytics")

    filings, facts, ratios, analytics = load_data()

    # Tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["Visual Explorer", "Data Profiler", "Correlation"])

    with tab1:
        st.subheader("Interactive Visual Explorer")
        if PYGWALKER_AVAILABLE:
            render_visual_explorer(analytics.head(1000), key="pygwalker_main")
        else:
            st.info("Install pygwalker for interactive exploration: `pip install pygwalker`")
            st.write("Showing basic charts instead:")

            # Fallback visualization
            if 'sector' in analytics.columns and 'revenue' in analytics.columns:
                chart_data = analytics.groupby('sector')['revenue'].sum().reset_index()
                st.bar_chart(chart_data.set_index('sector'))

    with tab2:
        st.subheader("Automated Data Profiling")
        if YDATA_PROFILING_AVAILABLE:
            if st.button("Generate Profile Report"):
                with st.spinner("Generating profile report..."):
                    render_data_profiler(analytics.head(500))
        else:
            st.info("Install ydata-profiling for automated reports: `pip install ydata-profiling`")

            # Show basic stats
            st.write("**Basic Statistics:**")
            st.dataframe(analytics.describe(), use_container_width=True)

    with tab3:
        st.subheader("Correlation Analysis")

        # Select numeric columns
        numeric_cols = analytics.select_dtypes(include=['float64', 'int64']).columns.tolist()

        if len(numeric_cols) >= 2:
            selected_cols = st.multiselect(
                "Select columns for correlation",
                numeric_cols,
                default=numeric_cols[:5] if len(numeric_cols) >= 5 else numeric_cols
            )

            if len(selected_cols) >= 2:
                corr_matrix = analytics[selected_cols].corr()

                try:
                    create_correlation_heatmap(
                        data=corr_matrix,
                        title="Financial Metrics Correlation",
                        height=500,
                    )
                except ImportError:
                    st.write("**Correlation Matrix:**")
                    st.dataframe(corr_matrix.style.background_gradient(cmap='RdYlGn'), use_container_width=True)
        else:
            st.info("Not enough numeric columns for correlation analysis")


# --- PAGE: SETTINGS ---
def render_settings_page():
    """Render settings and dependency info page."""
    st.header("⚙️ Settings & Info")

    # Dependency status
    st.subheader("📦 Component Dependencies")
    show_dependency_status()

    st.divider()

    # App info
    st.subheader("ℹ️ About")
    st.markdown("""
    **Ra'd AI** (⚡ رعد) is an AI-powered Saudi financial data analysis platform.

    **Features:**
    - Natural language queries using PandasAI + Gemini
    - Interactive data grids with AG-Grid
    - Dynamic filtering and selection
    - Advanced visualizations with ECharts/Plotly
    - Data profiling and exploration

    **Data Source:** Saudi Exchange XBRL Filings

    **Version:** 2.0.0 (Refactored with Component Library)
    """)

    st.divider()

    # Available columns reference
    st.subheader("📋 Data Schema Reference")

    filings, facts, ratios, analytics = load_data()

    with st.expander("Analytics View Columns"):
        st.code("\n".join(analytics.columns.tolist()))

    with st.expander("Filings Columns"):
        st.code("\n".join(filings.columns.tolist()))

    with st.expander("Available Metrics"):
        if 'metric' in facts.columns:
            st.code("\n".join(facts['metric'].unique().tolist()))

    with st.expander("Available Ratios"):
        if 'ratio' in ratios.columns:
            st.code("\n".join(ratios['ratio'].unique().tolist()))


# --- MAIN ---
def main():
    """Main application entry point."""
    # Render sidebar and get selected page
    selected_page = render_sidebar()

    # Route to selected page
    if selected_page == "Dashboard":
        render_dashboard()
    elif selected_page == "Data Explorer":
        render_data_explorer()
    elif selected_page == "Chat AI":
        render_chat_page()
    elif selected_page == "Analytics":
        render_analytics_page()
    elif selected_page == "Settings":
        render_settings_page()
    else:
        render_dashboard()

    # Footer
    st.divider()
    st.caption("⚡ Ra'd AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | v2.0")


if __name__ == "__main__":
    main()
