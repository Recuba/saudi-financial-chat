"""
Saudi Financial Database Chat UI
================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
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
    page_title="Saudi Financial Database",
    page_icon="📊",
    layout="wide",
)

# --- SECRETS VALIDATION ---
if "OPENROUTER_API_KEY" not in st.secrets:
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

# --- TITLE ---
st.title("📊 Saudi Financial Database Chat")
st.markdown("Ask questions about Saudi listed companies' financial data in natural language.")

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
    st.dataframe(dataset_map[dataset_choice].head(10), use_container_width=True)

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
st.divider()
st.caption("Powered by PandasAI + OpenRouter/Gemini | Data: Saudi Tadawul XBRL Financials")
