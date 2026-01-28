"""
Saudi Financial Database Chat UI
================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
Deployed on Streamlit Cloud.
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path

# Set up OpenRouter API from Streamlit secrets
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]
else:
    os.environ["OPENROUTER_API_KEY"] = "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"

import pandasai as pai
from pandasai_litellm import LiteLLM

# Page config
st.set_page_config(
    page_title="Saudi Financial Database",
    page_icon="📊",
    layout="wide"
)

# Initialize LLM
@st.cache_resource
def get_llm():
    return LiteLLM(model="openrouter/google/gemini-3-flash-preview")

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
        "Plot total assets trend for Almarai",
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
        if message["role"] == "assistant" and "image" in message:
            st.image(message["image"])
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

                # Save to temp CSV and load with PandasAI
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                    selected_df.to_csv(f.name, index=False)
                    temp_csv = f.name

                df = pai.read_csv(temp_csv)

                # Configure LLM
                llm = get_llm()
                pai.config.set({"llm": llm})

                # Execute query
                result = df.chat(prompt)

                # Clean up temp file
                os.unlink(temp_csv)

                # Display result
                response_content = ""

                if hasattr(result, 'value'):
                    result_value = result.value
                else:
                    result_value = result

                # Check if it's a plot/image path
                if isinstance(result_value, str) and (result_value.endswith('.png') or 'chart' in result_value.lower()):
                    if os.path.exists(result_value):
                        st.image(result_value)
                        response_content = "Chart generated successfully"
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_content,
                            "image": result_value
                        })
                    else:
                        st.write(result_value)
                        response_content = str(result_value)
                        st.session_state.messages.append({"role": "assistant", "content": response_content})
                elif isinstance(result_value, pd.DataFrame):
                    st.dataframe(result_value, use_container_width=True)
                    response_content = f"DataFrame with {len(result_value)} rows"
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                else:
                    st.write(result_value)
                    response_content = str(result_value)
                    st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.caption("Powered by PandasAI + OpenRouter/Gemini | Data: Saudi Tadawul XBRL Financials")
