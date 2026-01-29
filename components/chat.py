"""Chat interface component for Ra'd AI.

Provides enhanced chat input, message display, and response handling.
"""

import io
import os
import html
from datetime import datetime
from typing import Any, Callable, Dict, Optional, List
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

logger = logging.getLogger(__name__)


def format_response(response: Any) -> Dict[str, Any]:
    """Format a PandasAI response for display.

    Args:
        response: PandasAI response object

    Returns:
        Dictionary with type, data, code, and optional message

    Example:
        response = df.chat("What is the average revenue?")
        formatted = format_response(response)
        # Returns: {"type": "text", "data": "42.5", "code": "...", "message": None}
    """
    if response is None:
        logger.warning("Received None response from PandasAI")
        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": "No response received from AI"
        }

    response_type = getattr(response, "type", "unknown")
    value = getattr(response, "value", None)
    code = getattr(response, "last_code_executed", "")

    logger.debug(f"Processing response type: {response_type}")

    if response_type == "dataframe":
        if pd is not None:
            try:
                df_value = value if isinstance(value, pd.DataFrame) else pd.DataFrame(value) if value else pd.DataFrame()
                return {
                    "type": "dataframe",
                    "data": df_value,
                    "code": code,
                    "message": None
                }
            except Exception as e:
                logger.error(f"Error converting response to DataFrame: {e}")
                return {
                    "type": "error",
                    "data": None,
                    "code": code,
                    "message": f"Failed to create DataFrame: {html.escape(str(e))}"
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
        logger.debug(f"Unknown response type '{response_type}', treating as text")
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


def _safe_remove_file(filepath: str) -> bool:
    """Safely remove a file with proper error handling.

    Args:
        filepath: Path to the file to remove

    Returns:
        True if file was removed, False otherwise
    """
    if not filepath:
        return False

    try:
        if os.path.exists(filepath) and os.path.isfile(filepath):
            os.remove(filepath)
            logger.debug(f"Removed temporary file: {filepath}")
            return True
        else:
            logger.debug(f"File does not exist or is not a file: {filepath}")
            return False
    except PermissionError as e:
        logger.warning(f"Permission denied removing file {filepath}: {e}")
        return False
    except OSError as e:
        logger.error(f"Error removing file {filepath}: {e}")
        return False


def render_ai_response(response_data: Dict[str, Any]) -> None:
    """Render an AI response in the chat.

    Args:
        response_data: Dictionary from format_response()
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render AI response")

    response_type = response_data.get("type", "unknown")
    data = response_data.get("data")
    code = response_data.get("code", "")

    if response_type == "error":
        error_msg = response_data.get("message", "An error occurred")
        st.error(html.escape(str(error_msg)))
        return

    tab_result, tab_code = st.tabs(["Result", "Code"])

    with tab_result:
        if response_type == "dataframe":
            try:
                st.dataframe(data, use_container_width=True, hide_index=True)
            except Exception as e:
                logger.error(f"Error displaying dataframe: {e}")
                st.error(f"Could not display data: {html.escape(str(e))}")

        elif response_type == "chart":
            try:
                if Image is not None and data:
                    # Chart data can be file path or bytes
                    if isinstance(data, bytes):
                        img = Image.open(io.BytesIO(data))
                    elif isinstance(data, str):
                        if os.path.exists(data):
                            with open(data, "rb") as f:
                                img_bytes = f.read()
                            img = Image.open(io.BytesIO(img_bytes))
                            # Clean up temp file safely
                            _safe_remove_file(data)
                        else:
                            st.error(f"Chart file not found: {html.escape(data)}")
                            return
                    else:
                        st.error("Invalid chart data format")
                        return

                    st.image(img, use_container_width=True)
                else:
                    if Image is None:
                        st.error("PIL/Pillow is required to display charts")
                    else:
                        st.warning("No chart data available")
            except Exception as e:
                logger.error(f"Error displaying chart: {e}")
                st.error(f"Failed to display chart: {html.escape(str(e))}")

        elif response_type == "text":
            st.write(data if data else "No response text")

        else:
            logger.warning(f"Unknown response type for display: {response_type}")
            st.write(str(data) if data else "No data")

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

    Example:
        response = process_query("What is the average revenue?", df)
        if response["type"] == "error":
            print(f"Error: {response['message']}")
        else:
            print(f"Result: {response['data']}")
    """
    if not query or not query.strip():
        logger.warning("Empty query received")
        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": "Please enter a query"
        }

    logger.info(f"Processing query: {query[:100]}...")

    try:
        import pandasai as pai
        df = pai.DataFrame(dataset)
        response = df.chat(query)
        response_data = format_response(response)

        # If chart, convert file path to bytes for history storage
        if response_data["type"] == "chart" and response_data["data"]:
            filepath = response_data["data"]
            if isinstance(filepath, str) and os.path.exists(filepath):
                try:
                    with open(filepath, "rb") as f:
                        chart_bytes = f.read()
                    _safe_remove_file(filepath)
                    response_data["data"] = chart_bytes
                    logger.debug("Converted chart file to bytes for storage")
                except IOError as e:
                    logger.warning(f"Could not read chart file {filepath}: {e}")
                    # Keep file path if conversion fails

        logger.info(f"Query processed successfully, response type: {response_data['type']}")
        return response_data

    except ImportError as e:
        error_msg = f"Missing required package: {e}"
        logger.error(error_msg)
        if on_error:
            try:
                on_error(error_msg)
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}")
        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": error_msg
        }

    except ValueError as e:
        error_msg = f"Invalid query or data: {html.escape(str(e))}"
        logger.error(f"Query validation error: {e}")
        if on_error:
            try:
                on_error(str(e))
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}")
        return {
            "type": "error",
            "data": None,
            "code": None,
            "message": error_msg
        }

    except Exception as e:
        error_msg = html.escape(str(e))
        logger.error(f"Query processing error: {e}", exc_info=True)

        if on_error:
            try:
                on_error(str(e))
            except Exception as callback_error:
                logger.error(f"Error callback failed: {callback_error}")

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

    # Get dataset name for more informative spinner
    dataset_name = getattr(dataset, 'name', 'data')

    with st.chat_message("ai"):
        with st.spinner(f"Analyzing {dataset_name}..."):
            response = process_query(query, dataset)

        if response is None:
            logger.error("process_query returned None unexpectedly")
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
                if st.button("Retry Query", key=f"retry_{hash(query)}"):
                    st.session_state.query = query
                    st.rerun()
        else:
            render_ai_response(response)
            # Show timestamp with timezone info
            st.caption(f"Response at {datetime.now().strftime('%H:%M:%S')} (local time)")


def initialize_chat_history() -> None:
    """Initialize the chat history in session state."""
    if st is None:
        raise RuntimeError("Streamlit is required to initialize chat history")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        logger.debug("Initialized empty chat history")


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
    logger.debug(f"Added {role} message to chat history")


def get_chat_history() -> List[Dict[str, Any]]:
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
    logger.info("Chat history cleared")


def export_chat_history() -> Optional[str]:
    """Export chat history as JSON string.

    Returns:
        JSON string of chat history or None if empty
    """
    import json

    history = get_chat_history()
    if not history:
        return None

    # Filter out binary data (charts) for export
    exportable_history = []
    for entry in history:
        export_entry = entry.copy()
        if "response_data" in export_entry:
            response_copy = export_entry["response_data"].copy()
            if response_copy.get("type") == "chart":
                response_copy["data"] = "[chart data not exported]"
            export_entry["response_data"] = response_copy
        exportable_history.append(export_entry)

    return json.dumps(exportable_history, indent=2, default=str)


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
                    clear_chat_history()
                    st.session_state.confirm_clear = False
                    st.rerun()  # Refresh UI after clearing
                    return True
            with subcol2:
                if st.button("No", key="confirm_no"):
                    st.session_state.confirm_clear = False
                    st.rerun()
        else:
            if st.button("Clear", key="clear_history"):
                st.session_state.confirm_clear = True
                st.rerun()

    return False
