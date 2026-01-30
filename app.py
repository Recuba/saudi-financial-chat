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
    render_chat_with_response,
    initialize_chat_history,
)
from components.error_display import render_api_key_setup_guide
from utils.data_loader import load_data, get_dataset_info
from utils.llm_config import initialize_llm, check_llm_ready
from utils.data_processing import (
    normalize_to_sar,
    format_dataframe_for_display,
    CURRENCY_COLUMNS,
)

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

        # Apply scale factor normalization for accurate financial values
        if 'scale_factor' in selected_df.columns:
            selected_df = normalize_to_sar(selected_df)
            normalization_applied = True
        else:
            normalization_applied = False

        # Store in session state for filters
        if 'filtered_df' not in st.session_state:
            st.session_state.filtered_df = selected_df

        # --- FILTERS SECTION ---
        with st.expander("Data Filters", expanded=False):
            filter_cols = st.columns([2, 2, 1])

            # Sector filter
            with filter_cols[0]:
                if 'sector' in selected_df.columns:
                    all_sectors = sorted(selected_df['sector'].dropna().unique().tolist())
                    selected_sectors = st.multiselect(
                        "Filter by Sector",
                        options=all_sectors,
                        default=all_sectors,
                        key="sector_filter",
                        help="Select one or more sectors to filter the data"
                    )
                else:
                    selected_sectors = None

            # Year filter
            with filter_cols[1]:
                if 'fiscal_year' in selected_df.columns:
                    years = sorted(selected_df['fiscal_year'].dropna().unique().tolist())
                    if len(years) > 1:
                        year_range = st.slider(
                            "Fiscal Year Range",
                            min_value=int(min(years)),
                            max_value=int(max(years)),
                            value=(int(min(years)), int(max(years))),
                            key="year_filter",
                            help="Select the fiscal year range"
                        )
                    else:
                        year_range = (int(years[0]), int(years[0])) if years else None
                else:
                    year_range = None

            # Reset filters button
            with filter_cols[2]:
                st.write("")  # Spacer
                st.write("")  # Spacer
                if st.button("Reset Filters", key="reset_filters"):
                    st.session_state.sector_filter = all_sectors if 'sector' in selected_df.columns else None
                    st.rerun()

        # Apply filters to DataFrame
        filtered_df = selected_df.copy()

        if selected_sectors is not None and len(selected_sectors) < len(all_sectors):
            filtered_df = filtered_df[filtered_df['sector'].isin(selected_sectors)]

        if year_range is not None:
            filtered_df = filtered_df[
                (filtered_df['fiscal_year'] >= year_range[0]) &
                (filtered_df['fiscal_year'] <= year_range[1])
            ]

        # Store filtered data
        st.session_state.filtered_df = filtered_df

        # Show filter status
        total_records = len(selected_df)
        filtered_records = len(filtered_df)
        if filtered_records < total_records:
            st.info(f"Showing {filtered_records:,} of {total_records:,} records (filtered)")

        # Data preview with formatting
        with st.expander("Data Preview", expanded=False):
            preview_df = filtered_df.head(10).copy()

            # Format for display
            display_df = format_dataframe_for_display(
                preview_df,
                normalize=False,  # Already normalized above
                format_values=True
            )

            st.dataframe(display_df, use_container_width=True, hide_index=True)

            # Data context info
            col1, col2, col3 = st.columns(3)
            with col1:
                if 'company_name' in filtered_df.columns:
                    st.caption(f"Companies: {filtered_df['company_name'].nunique():,}")
            with col2:
                if 'sector' in filtered_df.columns:
                    st.caption(f"Sectors: {filtered_df['sector'].nunique():,}")
            with col3:
                if normalization_applied:
                    st.caption("Values normalized to SAR")

        # Example questions
        example_query = render_example_questions(max_visible=3)
        if example_query:
            st.session_state.query = example_query

        st.divider()

        # Chat input
        prompt = render_chat_input()

        # Check for button-triggered query
        if "query" in st.session_state and st.session_state.query:
            prompt = st.session_state.query
            st.session_state.query = None

        # Process query using filtered data
        if prompt:
            render_chat_with_response(prompt, filtered_df)

    except FileNotFoundError as e:
        st.error("Data files not found. Please ensure data files are in the 'data' directory.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# --- FOOTER ---
st.divider()
st.caption("رعد | Ra'd AI | Powered by PandasAI + Gemini | Saudi Exchange XBRL Data | Early Access")
