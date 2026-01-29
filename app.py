"""
Saudi Financial Database Chat UI
================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
"""

import pandasai as pai
from pandasai_litellm.litellm import LiteLLM
import pandas as pd
import streamlit as st
import io
from PIL import Image
import os
from pathlib import Path
from utils.data_processing import normalize_to_sar, format_dataframe_for_display

# --- LLM CONFIGURATION ---
llm = LiteLLM(
    model="openrouter/google/gemini-2.0-flash-001",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

# --- PANDASAI CONFIGURATION ---
pai.config.set({
    "llm": llm,
})

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="رعد | Saudi Financial AI",
    page_icon="⚡",
    layout="wide",
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
</style>
""", unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    """Load and normalize financial data from parquet files."""
    base_path = Path(__file__).parent / "data"

    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")

    # Note: Scale factor normalization disabled - original data has inconsistent
    # scale relationships that require investigation of source XBRL data.
    # The formatting functions will still improve display readability.
    # if 'scale_factor' in analytics.columns and (analytics['scale_factor'] != 1).any():
    #     analytics = normalize_to_sar(analytics)

    return filings, facts, ratios, analytics

# --- TITLE ---
st.markdown('<h1 class="brand-title">⚡ رعد | Ra\'d AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="brand-subtitle">Saudi Exchange Market Analysis | حلل السوق - Facts بدون فلسفة</p>', unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Database Info")

    filings, facts, ratios, analytics = load_data()

    st.metric("Companies", filings['company_name'].nunique())
    st.metric("Fiscal Periods", len(filings))
    st.metric("Financial Metrics", facts['metric'].nunique())
    st.metric("Financial Ratios", ratios['ratio'].nunique())

    st.divider()

    st.header("🎯 Dataset Selection")
    dataset_choice = st.selectbox(
        "Choose dataset to query:",
        ["analytics", "filings", "facts", "ratios"],
        format_func=lambda x: {
            "analytics": "📈 Analytics View (Pre-joined)",
            "filings": "🏢 Company Filings (Metadata)",
            "facts": "💰 Financial Facts (Metrics)",
            "ratios": "📊 Financial Ratios"
        }[x]
    )

    st.divider()

    st.header("📋 Available Columns")
    if dataset_choice == "analytics":
        cols = analytics.columns.tolist()
        st.code("\n".join(cols[:15]) + f"\n... ({len(cols)} total)")
    elif dataset_choice == "filings":
        st.code("\n".join(filings.columns.tolist()))
    elif dataset_choice == "facts":
        st.write("**Metrics:**")
        st.code("\n".join(facts['metric'].unique().tolist()))
    else:
        st.write("**Ratios:**")
        st.code("\n".join(ratios['ratio'].unique().tolist()))

# --- MAIN AREA ---
st.divider()

# Show data preview
with st.expander("📄 Data Preview", expanded=False):
    filings, facts, ratios, analytics = load_data()
    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }

    # Format for display
    preview_df = format_dataframe_for_display(
        dataset_map[dataset_choice].head(10),
        normalize=False,  # Data loaded as-is
        format_values=True
    )

    st.dataframe(
        preview_df,
        use_container_width=True,
        height=400
    )

# --- EXAMPLE QUESTIONS ---
st.subheader("💡 Example Questions")
col1, col2 = st.columns(2)
with col1:
    if st.button("Top 10 companies by revenue 2024"):
        st.session_state.query = "What are the top 10 companies by revenue in 2024?"
    if st.button("Average ROE by sector 2023"):
        st.session_state.query = "Show average ROE by sector in 2023"
    if st.button("Companies with debt to equity > 2"):
        st.session_state.query = "Which companies have debt to equity ratio greater than 2?"
with col2:
    if st.button("Net profit margins by sector"):
        st.session_state.query = "Compare net profit margins across sectors"
    if st.button("Negative net profit 2024"):
        st.session_state.query = "List companies with negative net profit in 2024"
    if st.button("Create bar chart of top 5 by assets"):
        st.session_state.query = "Create a bar chart showing top 5 companies by total assets"

st.divider()

# --- CHAT INPUT ---
prompt = st.chat_input("Ask a question about Saudi financial data...")

# Check for button-triggered query
if "query" in st.session_state and st.session_state.query:
    prompt = st.session_state.query
    st.session_state.query = None

if prompt:
    # Get selected dataset
    filings, facts, ratios, analytics = load_data()
    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }
    selected_df = dataset_map[dataset_choice]

    # Create PandasAI DataFrame
    df = pai.DataFrame(selected_df)

    # Show user message
    with st.chat_message("human"):
        st.write(prompt)

    # Get AI response
    with st.chat_message("ai"):
        with st.spinner("Analyzing data..."):
            try:
                response = df.chat(prompt)

                if response.type == 'dataframe':
                    tabResult, tabCode = st.tabs(["Result", "Code"])
                    with tabResult:
                        # Format the dataframe for display
                        display_df = format_dataframe_for_display(
                            response.value,
                            normalize=False,  # Already normalized at load
                            format_values=True
                        )
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    with tabCode:
                        st.code(response.last_code_executed, language='python')

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

                else:
                    tabResult, tabCode = st.tabs(["Result", "Code"])
                    with tabResult:
                        st.write(response.value)
                    with tabCode:
                        st.code(response.last_code_executed, language='python')

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- FOOTER ---
st.divider()
st.caption("⚡ رعد AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | Early Access")
