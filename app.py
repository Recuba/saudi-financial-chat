"""
Ra'd AI - Saudi Financial Database Chat
=======================================
A premium Streamlit app for natural language querying of Saudi XBRL financial data.
"""

import pandasai as pai
from pandasai_litellm import LiteLLM
import pandas as pd
import streamlit as st
import io
from PIL import Image
import os
from pathlib import Path

# --- PAGE CONFIG (must be first Streamlit command) ---
st.set_page_config(
    page_title="Ra'd AI | رعد",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CUSTOM CSS FOR PREMIUM DARK/GOLD THEME ---
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');

    /* Root variables */
    :root {
        --gold-primary: #D4A84B;
        --gold-light: #E8C872;
        --gold-dark: #B8860B;
        --bg-dark: #0E0E0E;
        --bg-card: #1A1A1A;
        --bg-card-hover: #252525;
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
    }

    /* Main container */
    .stApp {
        background: linear-gradient(180deg, #0E0E0E 0%, #1A1A1A 100%);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, rgba(212, 168, 75, 0.1) 0%, rgba(14, 14, 14, 0) 50%);
        border-radius: 20px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at 20% 80%, rgba(212, 168, 75, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(212, 168, 75, 0.1) 0%, transparent 50%);
        pointer-events: none;
    }

    .brand-title {
        font-family: 'Tajawal', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #D4A84B 0%, #E8C872 50%, #D4A84B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        text-shadow: 0 0 40px rgba(212, 168, 75, 0.3);
    }

    .brand-subtitle {
        font-family: 'Tajawal', sans-serif;
        font-size: 1.2rem;
        color: #B0B0B0;
        margin-top: 0.5rem;
        letter-spacing: 2px;
    }

    .brand-tagline {
        font-family: 'Tajawal', sans-serif;
        font-size: 1rem;
        color: #D4A84B;
        margin-top: 1rem;
        font-weight: 500;
    }

    .early-access-badge {
        display: inline-block;
        background: linear-gradient(135deg, #D4A84B 0%, #B8860B 100%);
        color: #0E0E0E;
        padding: 0.4rem 1.5rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 1rem;
        text-transform: uppercase;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141414 0%, #0E0E0E 100%);
        border-right: 1px solid rgba(212, 168, 75, 0.2);
    }

    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #D4A84B !important;
        font-family: 'Tajawal', sans-serif;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
        border: 1px solid rgba(212, 168, 75, 0.2);
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.3s ease;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(212, 168, 75, 0.5);
        box-shadow: 0 4px 20px rgba(212, 168, 75, 0.15);
    }

    [data-testid="stMetric"] label {
        color: #B0B0B0 !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #D4A84B !important;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #1A1A1A 0%, #252525 100%);
        border: 1px solid rgba(212, 168, 75, 0.3);
        color: #FFFFFF;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
        width: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #252525 0%, #1A1A1A 100%);
        border-color: #D4A84B;
        color: #D4A84B;
        box-shadow: 0 4px 15px rgba(212, 168, 75, 0.2);
        transform: translateY(-2px);
    }

    /* Chat input */
    [data-testid="stChatInput"] {
        border-color: rgba(212, 168, 75, 0.3) !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #D4A84B !important;
        box-shadow: 0 0 10px rgba(212, 168, 75, 0.2);
    }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: #1A1A1A;
        border: 1px solid rgba(212, 168, 75, 0.1);
        border-radius: 15px;
        padding: 1rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #1A1A1A;
        border: 1px solid rgba(212, 168, 75, 0.2);
        border-radius: 10px;
        color: #FFFFFF;
    }

    .streamlit-expanderHeader:hover {
        border-color: #D4A84B;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid rgba(212, 168, 75, 0.2);
        border-radius: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #1A1A1A;
        border-radius: 10px;
        padding: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #B0B0B0;
        padding: 0.5rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4A84B 0%, #B8860B 100%);
        color: #0E0E0E !important;
    }

    /* Selectbox */
    [data-testid="stSelectbox"] > div > div {
        background: #1A1A1A;
        border-color: rgba(212, 168, 75, 0.3);
    }

    /* Divider */
    hr {
        border-color: rgba(212, 168, 75, 0.2);
    }

    /* Code blocks */
    .stCodeBlock {
        background: #141414 !important;
        border: 1px solid rgba(212, 168, 75, 0.2);
    }

    /* Section headers */
    .section-header {
        color: #D4A84B;
        font-family: 'Tajawal', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Footer */
    .custom-footer {
        text-align: center;
        padding: 2rem 0;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid rgba(212, 168, 75, 0.1);
        margin-top: 2rem;
    }

    .custom-footer a {
        color: #D4A84B;
        text-decoration: none;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #D4A84B !important;
    }

    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SECRETS VALIDATION ---
if "OPENROUTER_API_KEY" not in st.secrets:
    st.markdown("""
    <div class="main-header">
        <h1 class="brand-title">رعد AI</h1>
        <p class="brand-subtitle">SAUDI FINANCIAL INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)
    st.error("Missing OPENROUTER_API_KEY in Streamlit secrets. Please configure it in your Streamlit Cloud app settings.")
    st.stop()

# --- LLM CONFIGURATION ---
llm = LiteLLM(
    model="openrouter/google/gemini-2.0-flash-001",
    api_key=st.secrets["OPENROUTER_API_KEY"],
)

# --- PANDASAI CONFIGURATION ---
pai.config.set({
    "llm": llm,
})

# --- LOAD DATA ---
@st.cache_data
def load_data():
    base_path = Path(__file__).parent / "data"
    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")
    return filings, facts, ratios, analytics

# --- HEADER ---
st.markdown("""
<div class="main-header">
    <h1 class="brand-title">رعد AI</h1>
    <p class="brand-subtitle">SAUDI FINANCIAL INTELLIGENCE</p>
    <p class="brand-tagline">Facts - بدُون فلسفة | حلل السوق</p>
    <span class="early-access-badge">Early Access</span>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚡ Ra'd AI")
    st.markdown("---")

    st.markdown("#### Database Overview")

    filings, facts, ratios, analytics = load_data()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Companies", filings['company_name'].nunique())
        st.metric("Periods", len(filings))
    with col2:
        st.metric("Metrics", facts['metric'].nunique())
        st.metric("Ratios", ratios['ratio'].nunique())

    st.markdown("---")

    st.markdown("#### Dataset Selection")
    dataset_choice = st.selectbox(
        "Choose dataset to query:",
        ["analytics", "filings", "facts", "ratios"],
        format_func=lambda x: {
            "analytics": "Analytics View",
            "filings": "Company Filings",
            "facts": "Financial Facts",
            "ratios": "Financial Ratios"
        }[x],
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.markdown("#### Available Columns")
    if dataset_choice == "analytics":
        cols = analytics.columns.tolist()
        st.code("\n".join(cols[:12]) + f"\n... ({len(cols)} total)", language=None)
    elif dataset_choice == "filings":
        st.code("\n".join(filings.columns.tolist()), language=None)
    elif dataset_choice == "facts":
        st.markdown("**Metrics:**")
        st.code("\n".join(facts['metric'].unique().tolist()), language=None)
    else:
        st.markdown("**Ratios:**")
        st.code("\n".join(ratios['ratio'].unique().tolist()), language=None)

# --- MAIN AREA ---

# Data Preview
with st.expander("Preview Data", expanded=False):
    filings, facts, ratios, analytics = load_data()
    dataset_map = {
        "analytics": analytics,
        "filings": filings,
        "facts": facts,
        "ratios": ratios
    }
    st.dataframe(dataset_map[dataset_choice].head(10), use_container_width=True)

# Example Questions
st.markdown('<p class="section-header">Quick Queries</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Top 10 by Revenue 2024"):
        st.session_state.query = "What are the top 10 companies by revenue in 2024?"
    if st.button("Debt to Equity > 2"):
        st.session_state.query = "Which companies have debt to equity ratio greater than 2?"
with col2:
    if st.button("Average ROE by Sector"):
        st.session_state.query = "Show average ROE by sector in 2023"
    if st.button("Negative Net Profit"):
        st.session_state.query = "List companies with negative net profit in 2024"
with col3:
    if st.button("Profit Margins by Sector"):
        st.session_state.query = "Compare net profit margins across sectors"
    if st.button("Top 5 by Assets (Chart)"):
        st.session_state.query = "Create a bar chart showing top 5 companies by total assets"

st.markdown("---")

# --- CHAT INPUT ---
prompt = st.chat_input("Ask about Saudi financial data in English or Arabic...")

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
        with st.spinner("Analyzing..."):
            try:
                response = df.chat(prompt)

                if response.type == 'dataframe':
                    tabResult, tabCode = st.tabs(["Result", "Code"])
                    with tabResult:
                        st.dataframe(response.value, use_container_width=True, hide_index=True)
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
st.markdown("""
<div class="custom-footer">
    <p>Powered by <strong>PandasAI</strong> + <strong>Gemini</strong> | Saudi Exchange Data</p>
    <p style="margin-top: 0.5rem; color: #D4A84B;">رعد AI - حلل السوق</p>
</div>
""", unsafe_allow_html=True)
