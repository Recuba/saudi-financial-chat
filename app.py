"""
Ra'd AI - Saudi Financial Analytics Platform
=============================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
"""

import streamlit as st

# --- PAGE CONFIG (must be first Streamlit command) ---
st.set_page_config(
    page_title="Ra'd | Saudi Financial AI",
    page_icon="⚡",
    layout="wide",
)

# --- IMPORTS ---
from pathlib import Path
from styles.css import get_base_css, get_error_css
from components.sidebar import render_sidebar
from components.example_questions import render_example_questions
from components.chat import (
    render_chat_input,
    initialize_chat_history,
    render_chat_history,
    render_clear_history_button,
    add_to_chat_history,
    get_chat_history,
    process_query,
    render_ai_response,
)
from components.error_display import render_api_key_setup_guide
from utils.data_loader import load_data
from utils.llm_config import initialize_llm, check_llm_ready

# --- ASSETS ---
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

# --- APPLY STYLES ---
st.markdown(get_base_css(), unsafe_allow_html=True)
st.markdown(get_error_css(), unsafe_allow_html=True)

# --- INITIALIZE LLM ---
llm, llm_error = initialize_llm()

# --- INITIALIZE CHAT HISTORY ---
initialize_chat_history()

# --- LOGO ---
col1, col2, col3 = st.columns([1, 6, 1])
with col2:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
    else:
        st.markdown('<h1 class="brand-title">Ra\'d AI</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="brand-subtitle">Facts | بدون فلسفة</p>',
            unsafe_allow_html=True
        )

# --- SIDEBAR ---
dataset_choice, model_changed = render_sidebar()

# --- RE-INITIALIZE LLM IF MODEL CHANGED ---
if model_changed:
    llm, llm_error = initialize_llm()

# --- MAIN CONTENT ---
st.divider()

# Check if LLM is configured
if not check_llm_ready():
    render_api_key_setup_guide()
else:
    # Load data
    try:
        data = load_data()
        selected_df = data[dataset_choice]

        # Data preview (expanded by default with 5 rows)
        from components.data_preview import render_data_preview
        render_data_preview(selected_df, expanded=True, max_rows=5)

        # Example questions
        example_query = render_example_questions(max_visible=3)
        if example_query:
            st.session_state.query = example_query

        # Render chat history first
        render_chat_history()

        # Clear history button
        if get_chat_history():
            render_clear_history_button()

        st.divider()

        # Chat input
        prompt = render_chat_input()

        # Check for button-triggered query
        if "query" in st.session_state and st.session_state.query:
            prompt = st.session_state.query
            st.session_state.query = None

        # Process query and add to history
        if prompt:
            st.session_state.last_query = prompt  # Store for chart visualization
            add_to_chat_history("user", prompt)
            with st.chat_message("ai"):
                with st.spinner("Analyzing data..."):
                    response = process_query(prompt, selected_df)

                if response is None:
                    response = {
                        "type": "error",
                        "data": None,
                        "code": None,
                        "message": "No response received"
                    }

                add_to_chat_history("assistant", "", response)  # content is in response_data

                if response["type"] == "error":
                    from components.error_display import format_api_error, render_error_banner
                    error_info = format_api_error(response.get("message", "Unknown error"))
                    render_error_banner(error_info, show_details=True)
                    if st.button("Retry Query", key="retry_query"):
                        st.session_state.query = prompt
                        st.rerun()
                else:
                    render_ai_response(response)

    except FileNotFoundError as e:
        st.error("Data files not found. Please ensure data files are in the 'data' directory.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# --- FOOTER ---
st.divider()
st.caption("رعد | Ra'd AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | Early Access")
