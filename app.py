"""
Saudi Financial Database Chat UI
================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Set up OpenRouter API from Streamlit secrets
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]

from pandasai import SmartDataframe
from pandasai.llm import LiteLLM

# Page config
st.set_page_config(
    page_title="Saudi Financial Database",
    page_icon="📊",
    layout="wide"
)

# Initialize LLM
@st.cache_resource
def get_llm():
    return LiteLLM(model="openrouter/google/gemini-2.0-flash-001")

# Load data
@st.cache_data
def load_data():
    base_path = Path(__file__).parent / "data"
    filings = pd.read_parquet(base_path / "filings.parquet")
    facts = pd.read_parquet(base_path / "facts_numeric.parquet")
    ratios = pd.read_parquet(base_path / "ratios.parquet")
    analytics = pd.read_parquet(base_path / "analytics_view.parquet")
    return filings, facts, ratios, analytics

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_dataset" not in st.session_state:
    st.session_state.current_dataset = "analytics"

# Header
st.title("📊 Saudi Financial Database Chat")
st.markdown("Ask questions about Saudi listed companies' financial data in natural language.")

# Sidebar
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
    st.session_state.current_dataset = dataset_choice

    st.divider()

    st.header("📋 Available Data")

    if dataset_choice == "analytics":
        st.write("**Columns:**")
        cols = analytics.columns.tolist()
        st.code("\n".join(cols[:20]) + f"\n... ({len(cols)} total)")
    elif dataset_choice == "filings":
        st.write("**Columns:**")
        st.code("\n".join(filings.columns.tolist()))
    elif dataset_choice == "facts":
        st.write("**Metrics:**")
        st.code("\n".join(facts['metric'].unique().tolist()))
    else:
        st.write("**Ratios:**")
        st.code("\n".join(ratios['ratio'].unique().tolist()))

    st.divider()

    st.header("💡 Example Questions")
    examples = [
        "What are the top 10 companies by revenue in 2024?",
        "Show average ROE by sector in 2023",
        "Which companies have debt to equity > 2?",
        "Compare net profit margins across sectors",
        "List companies with negative net profit in 2024"
    ]
    for ex in examples:
        if st.button(ex, key=ex):
            st.session_state.messages.append({"role": "user", "content": ex})
            st.rerun()

    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.divider()

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Chat input
if prompt := st.chat_input("Ask a question about Saudi financial data..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing data..."):
            try:
                # Get selected dataset
                filings, facts, ratios, analytics = load_data()

                dataset_map = {
                    "analytics": analytics,
                    "filings": filings,
                    "facts": facts,
                    "ratios": ratios
                }

                selected_df = dataset_map[st.session_state.current_dataset]

                # Create SmartDataframe
                llm = get_llm()
                sdf = SmartDataframe(selected_df, config={"llm": llm, "verbose": False})

                # Execute query
                result = sdf.chat(prompt)

                # Display result
                if isinstance(result, pd.DataFrame):
                    st.dataframe(result, use_container_width=True)
                    response_content = f"DataFrame with {len(result)} rows"
                else:
                    st.write(result)
                    response_content = str(result)

                st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.caption("Powered by PandasAI + OpenRouter/Gemini | Data: Saudi Tadawul XBRL Financials")
