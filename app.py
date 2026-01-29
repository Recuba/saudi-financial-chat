"""
Ra'd AI - Saudi Financial Analytics Platform
=============================================
A Streamlit app for natural language querying of Saudi XBRL financial data.
"""

import streamlit as st
import logging
import html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    render_chat_with_response,
    initialize_chat_history,
)
from components.error_display import render_api_key_setup_guide
from utils.data_loader import load_data
from utils.llm_config import initialize_llm, check_llm_ready, clear_model_cache
from utils.chart_config import apply_matplotlib_config

# --- ASSETS ---
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

# --- APPLY STYLES ---
st.markdown(get_base_css(), unsafe_allow_html=True)
st.markdown(get_error_css(), unsafe_allow_html=True)

# --- APPLY MATPLOTLIB CONFIGURATION ---
# This sets professional chart styling globally
apply_matplotlib_config()

# --- INITIALIZE LLM ---
llm, llm_error = initialize_llm()
if llm_error:
    logger.warning(f"LLM initialization warning: {llm_error}")

# --- INITIALIZE CHAT HISTORY ---
try:
    initialize_chat_history()
except Exception as e:
    logger.error(f"Failed to initialize chat history: {e}")

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
    logger.info("Model changed, reinitializing LLM")
    clear_model_cache()  # Clear cache to ensure fresh model list
    llm, llm_error = initialize_llm()
    if llm_error:
        st.error(f"Failed to initialize model: {html.escape(llm_error)}")
    else:
        st.success("Model updated successfully!", icon="✅")
        st.rerun()

# --- MAIN CONTENT ---
st.divider()

# Check if LLM is configured
if not check_llm_ready():
    render_api_key_setup_guide()
else:
    # Load data
    try:
        data = load_data()

        # Safe dataset access
        selected_df = data.get(dataset_choice)
        if selected_df is None:
            st.error(f"Dataset '{dataset_choice}' not found. Available: {list(data.keys())}")
            logger.error(f"Dataset '{dataset_choice}' not found in loaded data")
        else:
            # Data preview
            with st.expander("Data Preview", expanded=False):
                st.dataframe(selected_df.head(10), use_container_width=True)
                st.caption(f"Showing 10 of {len(selected_df):,} rows")

            # Example questions
            example_query = render_example_questions(max_visible=3)
            if example_query:
                # Store query for processing
                st.session_state.query = example_query
                st.rerun()  # Rerun to process the query

            st.divider()

            # Chat input
            prompt = render_chat_input()

            # Check for button-triggered query (from example or retry)
            if "query" in st.session_state and st.session_state.query:
                prompt = st.session_state.query
                st.session_state.query = None  # Clear to prevent re-processing

            # Process query
            if prompt:
                logger.info(f"Processing user query: {prompt[:50]}...")
                render_chat_with_response(prompt, selected_df)

    except FileNotFoundError as e:
        logger.error(f"Data files not found: {e}")
        st.error("Data files not found. Please ensure data files are in the 'data' directory.")
        with st.expander("Technical Details"):
            st.code(str(e))

    except PermissionError as e:
        logger.error(f"Permission error accessing data: {e}")
        st.error("Permission denied accessing data files.")

    except ValueError as e:
        logger.error(f"Data validation error: {e}")
        st.error(f"Data error: {html.escape(str(e))}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        st.error(f"An unexpected error occurred: {html.escape(str(e))}")
        with st.expander("Technical Details"):
            st.code(str(e))

# --- FOOTER ---
st.divider()
st.caption("رعد | Ra'd AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | Early Access")
