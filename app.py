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
    initial_sidebar_state="collapsed",
)

# --- IMPORTS ---
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
from styles.css import get_base_css, get_error_css, get_no_sidebar_css
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
from components.session_manager import initialize_session, add_recent_query
from utils.data_loader import load_tasi_data
from utils.query_router import QueryRouter
from utils.llm_config import initialize_llm, check_llm_ready

# --- ASSETS ---
LOGO_PATH = Path(__file__).parent / "assets" / "logo.png"

# --- APPLY STYLES ---
st.markdown(get_base_css(), unsafe_allow_html=True)
st.markdown(get_error_css(), unsafe_allow_html=True)
st.markdown(get_no_sidebar_css(), unsafe_allow_html=True)

# --- INITIALIZE SESSION STATE ---
initialize_session()

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
model_changed = render_sidebar()

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
        data = load_tasi_data()

        # Initialize query router with ticker_index for entity extraction and LLM fallback
        router = QueryRouter(ticker_index=data['ticker_index'], llm_enabled=True)

        # Advanced filters (applied to main view for filtering)
        from components.filters.advanced_filters import render_advanced_filters, apply_filters
        with st.sidebar:
            filters = render_advanced_filters(data["tasi_financials"])

        # Base filter state for query-time filtering
        base_filters = filters if filters else None

        # Initialize active tab in session state
        if "active_tab" not in st.session_state:
            st.session_state.active_tab = "Chat"

        # Mode selection (radio buttons instead of tabs for better chat_input compatibility)
        mode = st.radio(
            "Mode",
            ["Chat", "Compare"],
            horizontal=True,
            label_visibility="collapsed",
            key="mode_selector"
        )
        st.session_state.active_tab = mode

        if mode == "Chat":
            # Data preview (show main dataset)
            from components.data_preview import render_data_preview
            render_data_preview(data["tasi_financials"], expanded=True, max_rows=5)

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

            # Chat input (now outside of tabs, will render properly)
            prompt = render_chat_input()

            # Query suggestions
            from components.query_suggestions import render_suggestions_dropdown

            # Show suggestions based on recent queries or default
            suggestion = render_suggestions_dropdown(prompt or "")
            if suggestion:
                st.session_state.query = suggestion
                st.rerun()

            # Check for button-triggered query
            if "query" in st.session_state and st.session_state.query:
                prompt = st.session_state.query
                st.session_state.query = None

            # Process query and add to history
            if prompt:
                # Route query to optimal view with entity extraction and confidence
                view_name, route_reason, entities, confidence = router.route(prompt)
                logger.info(f"Routed '{prompt[:50]}...' to {view_name}: {route_reason} (confidence={confidence})")
                selected_df = data[view_name]

                # Apply advanced filters if set
                if base_filters:
                    selected_df = apply_filters(selected_df, base_filters)
                    st.sidebar.caption(f"Filtered: {len(selected_df):,} rows")

                # Confidence label with color coding
                if confidence >= 0.9:
                    confidence_label = "HIGH"
                    confidence_color = "green"
                elif confidence >= 0.7:
                    confidence_label = "MEDIUM"
                    confidence_color = "orange"
                else:
                    confidence_label = "LOW"
                    confidence_color = "red"

                # Build routing caption with entity info
                entity_info = ""
                if entities.get('tickers'):
                    entity_info = f" | Detected: {', '.join(entities['tickers'])}"
                elif entities.get('companies'):
                    entity_info = f" | Detected: {', '.join(entities['companies'][:2])}"

                st.caption(f"Using: {view_name} (:{confidence_color}[{confidence_label}]){entity_info}")

                st.session_state.last_query = prompt  # Store for chart visualization
                add_recent_query(prompt, view_name)  # Track in recent queries
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

        else:  # Compare mode
            from components.comparison_mode import render_comparison_mode
            render_comparison_mode(data["latest_financials"])

    except FileNotFoundError as e:
        st.error("Data files not found. Please ensure tasi_optimized files are in the 'data/tasi_optimized' directory.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# --- FOOTER ---
st.divider()
st.caption("رعد | Ra'd AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | Early Access")
