"""Chat interface component for Ra'd AI.

Provides enhanced chat input, message display, and response handling.
"""

import io
import os
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import logging

try:
    import streamlit as st
except ImportError:
    st = None  # Allow module to be imported for testing without streamlit

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from PIL import Image
except ImportError:
    Image = None

from components.error_display import format_api_error, render_error_banner

# Import formatting utilities with graceful fallback
try:
    from utils.data_processing import format_dataframe_for_display, CURRENCY_COLUMNS
    HAS_FORMATTING = True
except ImportError:
    HAS_FORMATTING = False
    CURRENCY_COLUMNS = []

# Import chart generation utilities
try:
    from utils.chart_generator import (
        detect_chart_intent,
        extract_chart_parameters,
        generate_chart_from_data,
        get_chart_suggestions,
    )
    HAS_CHART_GENERATOR = True
except ImportError:
    HAS_CHART_GENERATOR = False

# Import financial charts
try:
    from components.visualizations.financial_charts import (
        create_income_statement_waterfall,
        create_ratio_radar_chart,
        create_sector_sunburst,
        create_risk_return_scatter,
        create_sector_performance_heatmap,
        create_yoy_comparison_chart,
        FINANCIAL_COLORS,
    )
    HAS_FINANCIAL_CHARTS = True
except ImportError:
    HAS_FINANCIAL_CHARTS = False

logger = logging.getLogger(__name__)


def should_format_dataframe(df) -> bool:
    """Check if a DataFrame contains financial columns that should be formatted.

    Args:
        df: DataFrame to check

    Returns:
        True if DataFrame has financial columns
    """
    if df is None or not hasattr(df, 'columns'):
        return False

    if not HAS_FORMATTING:
        return False

    # Check for financial columns
    df_cols_lower = [c.lower() for c in df.columns]
    currency_cols_lower = [c.lower() for c in CURRENCY_COLUMNS]

    return any(col in currency_cols_lower for col in df_cols_lower)


def try_generate_enhanced_chart(
    query: str,
    df: Any,
    response_data: Dict[str, Any]
) -> Optional[Any]:
    """Attempt to generate an enhanced financial chart based on query.

    Args:
        query: User's original query
        df: Source DataFrame
        response_data: PandasAI response data

    Returns:
        Plotly figure or None
    """
    if not HAS_CHART_GENERATOR or not HAS_FINANCIAL_CHARTS:
        return None

    if df is None or not hasattr(df, 'columns'):
        return None

    try:
        # Detect chart intent
        intent = detect_chart_intent(query)

        if not intent.get("wants_chart") or intent.get("confidence", 0) < 0.5:
            return None

        chart_type = intent.get("chart_type")
        if not chart_type or chart_type == "auto":
            return None

        # Extract parameters
        params = extract_chart_parameters(query, df)

        # Generate chart
        fig = generate_chart_from_data(df, chart_type, params)

        return fig

    except Exception as e:
        logger.warning(f"Could not generate enhanced chart: {e}")
        return None


def render_chart_suggestions(df: Any) -> None:
    """Render chart suggestions based on available data.

    Args:
        df: Source DataFrame
    """
    if not HAS_CHART_GENERATOR or st is None:
        return

    try:
        suggestions = get_chart_suggestions(df)

        if suggestions:
            with st.expander("Chart Suggestions", expanded=False):
                st.caption("Based on your data, try these visualizations:")

                cols = st.columns(min(len(suggestions), 3))
                for i, suggestion in enumerate(suggestions[:6]):
                    with cols[i % 3]:
                        if st.button(
                            f"{suggestion['title']}",
                            key=f"chart_suggest_{i}",
                            help=suggestion['description']
                        ):
                            st.session_state.query = suggestion['query']
                            st.rerun()

    except Exception as e:
        logger.warning(f"Could not render chart suggestions: {e}")


def format_response(response: Any) -> Dict[str, Any]:
    """Format a PandasAI response for display.

    Args:
        response: PandasAI response object

    Returns:
        Dictionary with type, data, code, and optional message
    """
    if response is None:
        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": "No response received from AI"
        }

    response_type = getattr(response, "type", "unknown")
    value = getattr(response, "value", None)
    code = getattr(response, "last_code_executed", "")

    if response_type == "dataframe":
        if pd is not None:
            return {
                "type": "dataframe",
                "data": value if isinstance(value, pd.DataFrame) else pd.DataFrame(value) if value else pd.DataFrame(),
                "code": code,
                "message": None
            }
        else:
            return {
                "type": "dataframe",
                "data": value,
                "code": code,
                "message": None
            }

    elif response_type == "chart":
        return {
            "type": "chart",
            "data": value,  # File path
            "code": code,
            "message": None
        }

    elif response_type == "text" or response_type == "string":
        return {
            "type": "text",
            "data": str(value) if value else "",
            "code": code,
            "message": None
        }

    else:
        return {
            "type": "text",
            "data": str(value) if value else "No data returned",
            "code": code,
            "message": None
        }


def render_chat_input(placeholder: str = "Ask a question about Saudi financial data...") -> Optional[str]:
    """Render the chat input with keyboard hints.

    Args:
        placeholder: Placeholder text for the input

    Returns:
        User's query or None
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render chat input")

    st.markdown(
        '<p style="text-align: right; color: var(--text-muted); font-size: 12px; margin-bottom: 4px;">'
        '<span class="kbd-hint">Enter</span> to send'
        '</p>',
        unsafe_allow_html=True
    )

    return st.chat_input(placeholder)


def render_user_message(query: str) -> None:
    """Render a user's message in the chat.

    Args:
        query: The user's query string
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render user message")

    with st.chat_message("human"):
        st.write(query)


def render_ai_response(response_data: Dict[str, Any]) -> None:
    """Render an AI response in the chat.

    Args:
        response_data: Dictionary from format_response()
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render AI response")

    response_type = response_data["type"]
    data = response_data["data"]
    code = response_data.get("code", "")

    if response_type == "error":
        st.error(response_data.get("message", "An error occurred"))
        return

    # Create tabs - add Chart tab if enhanced charts available
    if HAS_FINANCIAL_CHARTS and response_type == "dataframe":
        tab_result, tab_chart, tab_code = st.tabs(["Result", "Charts", "Code"])
    else:
        tab_result, tab_code = st.tabs(["Result", "Code"])
        tab_chart = None

    with tab_result:
        if response_type == "dataframe":
            # Format DataFrame for display if it contains financial columns
            display_data = data
            if should_format_dataframe(data):
                try:
                    display_data = format_dataframe_for_display(
                        data,
                        normalize=False,  # Data should already be normalized
                        format_values=True
                    )
                except Exception as e:
                    logger.warning(f"Could not format DataFrame: {e}")
                    display_data = data

            st.dataframe(display_data, use_container_width=True, hide_index=True)

            # Add export button for query results
            if pd is not None and isinstance(data, pd.DataFrame) and len(data) > 0:
                csv_data = data.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="query_result.csv",
                    mime="text/csv",
                    key=f"download_{datetime.now().timestamp()}"
                )

    # Chart tab for enhanced visualizations
    if tab_chart is not None and response_type == "dataframe":
        with tab_chart:
            if pd is not None and isinstance(data, pd.DataFrame) and len(data) > 0:
                st.caption("Generate advanced financial charts from your data:")

                # Quick chart options
                chart_cols = st.columns(4)

                with chart_cols[0]:
                    if st.button("Bar Chart", key=f"quick_bar_{datetime.now().timestamp()}"):
                        try:
                            import plotly.express as px
                            # Get first numeric column for values
                            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                            cat_cols = data.select_dtypes(include=['object']).columns.tolist()

                            if numeric_cols and cat_cols:
                                fig = px.bar(
                                    data.head(15),
                                    x=cat_cols[0],
                                    y=numeric_cols[0],
                                    color=cat_cols[0] if len(cat_cols) > 0 else None,
                                    title=f"{numeric_cols[0].replace('_', ' ').title()} by {cat_cols[0].replace('_', ' ').title()}"
                                )
                                fig.update_layout(
                                    paper_bgcolor="#0E0E0E",
                                    plot_bgcolor="#0E0E0E",
                                    font_color="#FFFFFF"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not create bar chart: {e}")

                with chart_cols[1]:
                    if st.button("Pie Chart", key=f"quick_pie_{datetime.now().timestamp()}"):
                        try:
                            import plotly.express as px
                            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                            cat_cols = data.select_dtypes(include=['object']).columns.tolist()

                            if numeric_cols and cat_cols:
                                fig = px.pie(
                                    data.head(10),
                                    values=numeric_cols[0],
                                    names=cat_cols[0],
                                    title=f"{numeric_cols[0].replace('_', ' ').title()} Distribution"
                                )
                                fig.update_layout(
                                    paper_bgcolor="#0E0E0E",
                                    plot_bgcolor="#0E0E0E",
                                    font_color="#FFFFFF"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not create pie chart: {e}")

                with chart_cols[2]:
                    if st.button("Line Trend", key=f"quick_line_{datetime.now().timestamp()}"):
                        try:
                            import plotly.express as px
                            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()

                            if 'fiscal_year' in data.columns and numeric_cols:
                                fig = px.line(
                                    data.sort_values('fiscal_year'),
                                    x='fiscal_year',
                                    y=numeric_cols[0],
                                    title=f"{numeric_cols[0].replace('_', ' ').title()} Over Time"
                                )
                                fig.update_layout(
                                    paper_bgcolor="#0E0E0E",
                                    plot_bgcolor="#0E0E0E",
                                    font_color="#FFFFFF"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Need fiscal_year column for trend chart")
                        except Exception as e:
                            st.error(f"Could not create line chart: {e}")

                with chart_cols[3]:
                    if st.button("Scatter Plot", key=f"quick_scatter_{datetime.now().timestamp()}"):
                        try:
                            import plotly.express as px
                            numeric_cols = data.select_dtypes(include=['number']).columns.tolist()

                            if len(numeric_cols) >= 2:
                                fig = px.scatter(
                                    data,
                                    x=numeric_cols[0],
                                    y=numeric_cols[1],
                                    title=f"{numeric_cols[0]} vs {numeric_cols[1]}"
                                )
                                fig.update_layout(
                                    paper_bgcolor="#0E0E0E",
                                    plot_bgcolor="#0E0E0E",
                                    font_color="#FFFFFF"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Need at least 2 numeric columns for scatter plot")
                        except Exception as e:
                            st.error(f"Could not create scatter plot: {e}")

                # Advanced chart options
                with st.expander("Advanced Financial Charts", expanded=False):
                    adv_cols = st.columns(3)

                    with adv_cols[0]:
                        if 'sector' in data.columns and st.button("Sector Sunburst", key=f"adv_sunburst_{datetime.now().timestamp()}"):
                            try:
                                from components.visualizations.financial_charts import create_sector_sunburst
                                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
                                if numeric_cols:
                                    fig = create_sector_sunburst(data, value_column=numeric_cols[0])
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not create sunburst: {e}")

                    with adv_cols[1]:
                        if 'sector' in data.columns and st.button("Sector Heatmap", key=f"adv_heatmap_{datetime.now().timestamp()}"):
                            try:
                                from components.visualizations.financial_charts import create_sector_performance_heatmap
                                numeric_cols = data.select_dtypes(include=['number']).columns.tolist()[:5]
                                if numeric_cols:
                                    fig = create_sector_performance_heatmap(data, metrics=numeric_cols)
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.error(f"Could not create heatmap: {e}")

                    with adv_cols[2]:
                        if st.button("Risk-Return", key=f"adv_riskret_{datetime.now().timestamp()}"):
                            try:
                                from components.visualizations.financial_charts import create_risk_return_scatter
                                if 'roe' in data.columns or 'roa' in data.columns:
                                    fig = create_risk_return_scatter(data)
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True)
                                else:
                                    st.info("Need ROE or ROA columns for risk-return chart")
                            except Exception as e:
                                st.error(f"Could not create risk-return chart: {e}")
            else:
                st.info("No data available for charting")

    # Handle non-dataframe responses in tab_result
    with tab_result:
        if response_type == "chart":
            try:
                if Image is not None and data:
                    # Chart data can be file path or bytes
                    if isinstance(data, bytes):
                        img = Image.open(io.BytesIO(data))
                    else:
                        with open(data, "rb") as f:
                            img_bytes = f.read()
                        img = Image.open(io.BytesIO(img_bytes))
                        # Clean up temp file
                        os.remove(data)
                    st.image(img, use_container_width=True)
                else:
                    st.error("Unable to display chart: PIL not available")
            except Exception as e:
                st.error(f"Failed to display chart: {e}")

        elif response_type == "text":
            st.write(data)

    with tab_code:
        if code:
            st.code(code, language="python")
        else:
            st.info("No code was generated for this response.")


def process_query(
    query: str,
    dataset: Any,
    on_error: Optional[Callable[[str], None]] = None
) -> Optional[Dict[str, Any]]:
    """Process a user query using PandasAI.

    Args:
        query: The user's natural language query
        dataset: The DataFrame to query
        on_error: Optional callback for error handling

    Returns:
        Formatted response dict or None on error
    """
    try:
        import pandasai as pai
        df = pai.DataFrame(dataset)
        response = df.chat(query)
        response_data = format_response(response)

        # If chart, convert file path to bytes for history storage
        if response_data["type"] == "chart" and response_data["data"]:
            try:
                with open(response_data["data"], "rb") as f:
                    chart_bytes = f.read()
                os.remove(response_data["data"])  # Clean up temp file
                response_data["data"] = chart_bytes
            except Exception:
                pass  # Keep file path if conversion fails

        return response_data

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Query processing error: {error_msg}")

        if on_error:
            on_error(error_msg)

        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": error_msg
        }


def render_chat_with_response(
    query: str,
    dataset: Any,
    show_retry: bool = True
) -> None:
    """Render a complete chat turn with query and response.

    Args:
        query: The user's query
        dataset: The DataFrame to query
        show_retry: Whether to show a retry button on error
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render chat with response")

    render_user_message(query)

    with st.chat_message("ai"):
        with st.spinner("Analyzing data..."):
            response = process_query(query, dataset)

        if response is None:
            response = {
                "type": "error",
                "data": None,
                "code": None,
                "message": "No response received"
            }

        if response["type"] == "error":
            error_info = format_api_error(response["message"])
            render_error_banner(error_info, show_details=True)

            if show_retry:
                if st.button("Retry Query", key="retry_query"):
                    st.session_state.query = query
                    st.rerun()
        else:
            render_ai_response(response)
            st.caption(f"Response at {datetime.now().strftime('%H:%M:%S')}")


def initialize_chat_history() -> None:
    """Initialize the chat history in session state."""
    if st is None:
        raise RuntimeError("Streamlit is required to initialize chat history")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def add_to_chat_history(role: str, content: Any, response_data: Optional[Dict[str, Any]] = None) -> None:
    """Add a message to the chat history.

    Args:
        role: The role ("user" or "assistant")
        content: The message content
        response_data: Optional formatted response data for assistant messages
    """
    if st is None:
        raise RuntimeError("Streamlit is required to add to chat history")

    initialize_chat_history()

    entry = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }

    if response_data is not None:
        entry["response_data"] = response_data

    st.session_state.chat_history.append(entry)


def get_chat_history() -> list:
    """Get the current chat history.

    Returns:
        List of chat history entries
    """
    if st is None:
        return []

    initialize_chat_history()
    return st.session_state.chat_history


def clear_chat_history() -> None:
    """Clear the chat history."""
    if st is None:
        raise RuntimeError("Streamlit is required to clear chat history")

    st.session_state.chat_history = []


def render_chat_history() -> None:
    """Render the full chat history."""
    if st is None:
        raise RuntimeError("Streamlit is required to render chat history")

    history = get_chat_history()

    for entry in history:
        role = entry["role"]
        content = entry["content"]

        if role == "user":
            with st.chat_message("human"):
                st.write(content)
        else:
            with st.chat_message("ai"):
                if "response_data" in entry:
                    render_ai_response(entry["response_data"])
                else:
                    st.write(content)


def render_clear_history_button() -> bool:
    """Render a clear history button with confirmation.

    Returns:
        True if history was cleared, False otherwise
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render clear history button")

    col1, col2 = st.columns([3, 1])

    with col2:
        if "confirm_clear" not in st.session_state:
            st.session_state.confirm_clear = False

        if st.session_state.confirm_clear:
            subcol1, subcol2 = st.columns(2)
            with subcol1:
                if st.button("Yes", key="confirm_yes", type="primary"):
                    clear_chat_history()  # Use the function instead of direct assignment
                    st.session_state.confirm_clear = False
                    return True
            with subcol2:
                if st.button("No", key="confirm_no"):
                    st.session_state.confirm_clear = False
        else:
            if st.button("Clear", key="clear_history"):
                st.session_state.confirm_clear = True

    return False
