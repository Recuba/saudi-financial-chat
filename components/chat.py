"""Chat interface component for Ra'd AI.

Provides enhanced chat input, message display, and response handling.
"""

import hashlib
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
from components.export import (
    export_to_csv,
    export_response_to_text,
    generate_export_filename,
)

logger = logging.getLogger(__name__)


def _get_response_key(response_data: Dict[str, Any]) -> str:
    """Generate a stable key from response data.

    Uses a hash of the content to ensure consistent keys across Streamlit reruns,
    unlike id() which changes between reruns.

    Args:
        response_data: Dictionary from format_response()

    Returns:
        8-character hex string suitable for widget keys
    """
    content = str(response_data.get("data", ""))[:100]  # First 100 chars
    return hashlib.md5(content.encode()).hexdigest()[:8]


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


def format_response_for_copy(response_data: Dict[str, Any]) -> str:
    """Format response data for clipboard copy.

    Args:
        response_data: Dictionary from format_response()

    Returns:
        String suitable for clipboard
    """
    response_type = response_data.get("type", "text")
    data = response_data.get("data")

    if data is None:
        return ""

    if response_type == "dataframe":
        if pd is not None and isinstance(data, pd.DataFrame):
            return data.to_string(index=False)
        return str(data)

    elif response_type == "chart":
        return "[Chart - cannot copy image to clipboard]"

    else:
        return str(data)


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

    # Copy button and export buttons
    if response_type != "chart":
        copy_text = format_response_for_copy(response_data)
        if copy_text:
            response_key = _get_response_key(response_data)
            col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
            with col2:
                if st.button("📋", key=f"copy_{response_key}", help="Copy to clipboard"):
                    st.session_state[f"copied_{response_key}"] = True

            # Export buttons
            with col3:
                text_export = export_response_to_text(response_data)
                st.download_button(
                    label="📄",
                    data=text_export,
                    file_name=generate_export_filename("response", "txt"),
                    mime="text/plain",
                    key=f"export_txt_{response_key}",
                    help="Export as text"
                )

            with col4:
                # CSV export (only for dataframes)
                if response_type == "dataframe" and pd is not None and isinstance(data, pd.DataFrame):
                    csv_export = export_to_csv(data)
                    st.download_button(
                        label="📊",
                        data=csv_export,
                        file_name=generate_export_filename("data", "csv"),
                        mime="text/csv",
                        key=f"export_csv_{response_key}",
                        help="Export as CSV"
                    )

            # Show copyable text area when clicked
            if st.session_state.get(f"copied_{response_key}"):
                st.code(copy_text, language=None)
                st.caption("Select text above and press Ctrl+C (Cmd+C on Mac) to copy")

    tab_result, tab_code = st.tabs(["Result", "Code"])

    with tab_result:
        if response_type == "dataframe":
            st.dataframe(data, use_container_width=True, hide_index=True)

            # Auto-visualize if query suggests chart
            from components.visualizations.response_charts import should_render_chart, auto_visualize
            last_query = st.session_state.get("last_query", "")
            if should_render_chart(last_query) and len(data) <= 50:
                fig = auto_visualize(data, last_query)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)

        elif response_type == "chart":
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
