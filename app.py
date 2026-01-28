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
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

    /* ===== GLOBAL OVERRIDES ===== */
    html, body, .stApp, [data-testid="stApp"] {
        background: #0A0A0A !important;
        color: #E8E8E8 !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(ellipse at 20% 0%, rgba(212,168,75,0.06) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 100%, rgba(212,168,75,0.04) 0%, transparent 50%),
                    #0A0A0A !important;
    }

    /* Hide default Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden !important;
        display: none !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111111 0%, #0A0A0A 100%) !important;
        border-right: 1px solid rgba(212,168,75,0.15) !important;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4 {
        color: #D4A84B !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: #C0C0C0 !important;
    }

    /* ===== METRIC CARDS ===== */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #151515, #1E1E1E) !important;
        border: 1px solid rgba(212,168,75,0.2) !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        transition: border-color 0.3s, box-shadow 0.3s !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: rgba(212,168,75,0.5) !important;
        box-shadow: 0 0 20px rgba(212,168,75,0.1) !important;
    }

    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"] {
        color: #999 !important;
        font-size: 0.85rem !important;
    }

    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #D4A84B !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
    }

    /* ===== BUTTONS ===== */
    .stButton > button,
    button[data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-secondary"] {
        background: linear-gradient(145deg, #1A1A1A, #222) !important;
        border: 1px solid rgba(212,168,75,0.25) !important;
        color: #E0E0E0 !important;
        border-radius: 10px !important;
        font-family: 'Tajawal', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }

    .stButton > button:hover,
    button[data-testid="stBaseButton-secondary"]:hover {
        background: linear-gradient(145deg, #222, #1A1A1A) !important;
        border-color: #D4A84B !important;
        color: #D4A84B !important;
        box-shadow: 0 4px 15px rgba(212,168,75,0.15) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
    }

    /* ===== CHAT INPUT ===== */
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] textarea,
    [data-testid="stChatInput"] > div {
        background: #151515 !important;
        border-color: rgba(212,168,75,0.25) !important;
        color: #E0E0E0 !important;
        border-radius: 12px !important;
    }

    [data-testid="stChatInput"]:focus-within {
        border-color: #D4A84B !important;
        box-shadow: 0 0 15px rgba(212,168,75,0.15) !important;
    }

    /* ===== CHAT MESSAGES ===== */
    [data-testid="stChatMessage"],
    .stChatMessage {
        background: #141414 !important;
        border: 1px solid rgba(212,168,75,0.1) !important;
        border-radius: 14px !important;
        padding: 1.2rem !important;
    }

    /* ===== EXPANDER ===== */
    [data-testid="stExpander"],
    .streamlit-expanderHeader {
        border: 1px solid rgba(212,168,75,0.15) !important;
        border-radius: 10px !important;
    }

    [data-testid="stExpander"] summary,
    .streamlit-expanderHeader {
        background: #151515 !important;
        color: #E0E0E0 !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    [data-testid="stExpander"] summary:hover {
        color: #D4A84B !important;
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"],
    .stDataFrame {
        border: 1px solid rgba(212,168,75,0.15) !important;
        border-radius: 10px !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        background: #141414 !important;
        border-radius: 10px !important;
        padding: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        color: #999 !important;
        font-family: 'Tajawal', sans-serif !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #D4A84B, #B8860B) !important;
        color: #0A0A0A !important;
        font-weight: 600 !important;
    }

    /* ===== SELECTBOX ===== */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background: #151515 !important;
        border-color: rgba(212,168,75,0.25) !important;
        color: #E0E0E0 !important;
    }

    /* ===== DIVIDERS ===== */
    hr, [data-testid="stSeparator"] {
        border-color: rgba(212,168,75,0.12) !important;
    }

    /* ===== CODE BLOCKS ===== */
    .stCodeBlock, [data-testid="stCodeBlock"], pre, code {
        border: 1px solid rgba(212,168,75,0.12) !important;
        border-radius: 8px !important;
    }

    /* ===== SPINNER ===== */
    .stSpinner > div {
        border-top-color: #D4A84B !important;
    }

    /* ===== ALERTS ===== */
    [data-testid="stAlert"] {
        border-radius: 10px !important;
    }

    /* ===== BRANDED HEADER ===== */
    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
        background: radial-gradient(ellipse at center top, rgba(212,168,75,0.12) 0%, transparent 60%) !important;
        border: 1px solid rgba(212,168,75,0.08);
        border-radius: 20px;
        margin-bottom: 2rem;
    }

    .brand-title {
        font-family: 'Tajawal', sans-serif;
        font-size: 4.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #C49A3C 0%, #F0D078 40%, #D4A84B 70%, #E8C872 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        line-height: 1.2;
        filter: drop-shadow(0 0 30px rgba(212,168,75,0.3));
    }

    .brand-subtitle {
        font-family: 'Tajawal', sans-serif;
        font-size: 1.1rem;
        color: #888 !important;
        margin-top: 0.5rem;
        letter-spacing: 4px;
        text-transform: uppercase;
    }

    .brand-tagline {
        font-family: 'Tajawal', sans-serif;
        font-size: 1.05rem;
        color: #D4A84B !important;
        margin-top: 1rem;
        font-weight: 500;
    }

    .early-access-badge {
        display: inline-block;
        background: linear-gradient(135deg, #D4A84B 0%, #B8860B 100%);
        color: #0A0A0A;
        padding: 0.35rem 1.5rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 3px;
        margin-top: 1.2rem;
        text-transform: uppercase;
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        color: #D4A84B !important;
        font-family: 'Tajawal', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }

    /* ===== FOOTER ===== */
    .custom-footer {
        text-align: center;
        padding: 2rem 0;
        color: #555 !important;
        font-size: 0.85rem;
        border-top: 1px solid rgba(212,168,75,0.1);
        margin-top: 2rem;
    }

    .custom-footer strong {
        color: #999 !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0A0A0A;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(212,168,75,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(212,168,75,0.5);
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
