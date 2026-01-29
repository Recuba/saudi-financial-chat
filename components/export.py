"""Export functionality for Ra'd AI responses."""

from datetime import datetime
from typing import Any, Dict, List, Optional
import io

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import streamlit as st
except ImportError:
    st = None


def generate_export_filename(base_name: str, extension: str) -> str:
    """Generate filename with timestamp.

    Args:
        base_name: Base name for file
        extension: File extension (without dot)

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}.{extension}"


def export_to_csv(df: "pd.DataFrame") -> str:
    """Export dataframe to CSV string.

    Args:
        df: DataFrame to export

    Returns:
        CSV string
    """
    if pd is None:
        raise ImportError("pandas required")

    return df.to_csv(index=False)


def export_to_excel(df: "pd.DataFrame") -> bytes:
    """Export dataframe to Excel bytes.

    Args:
        df: DataFrame to export

    Returns:
        Excel file as bytes
    """
    if pd is None:
        raise ImportError("pandas required")

    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def export_response_to_text(response_data: Dict[str, Any]) -> str:
    """Export response data to plain text.

    Args:
        response_data: Response dictionary

    Returns:
        Text representation
    """
    response_type = response_data.get("type", "text")
    data = response_data.get("data")
    code = response_data.get("code", "")

    lines = []
    lines.append("=" * 50)
    lines.append(f"Response Type: {response_type}")
    lines.append("=" * 50)
    lines.append("")

    if response_type == "dataframe" and pd is not None:
        if isinstance(data, pd.DataFrame):
            lines.append(data.to_string(index=False))
        else:
            lines.append(str(data))
    elif response_type == "chart":
        lines.append("[Chart - exported separately]")
    else:
        lines.append(str(data) if data else "No data")

    if code:
        lines.append("")
        lines.append("-" * 30)
        lines.append("Generated Code:")
        lines.append(code)

    return "\n".join(lines)


def export_chat_history_to_markdown(history: List[Dict[str, Any]]) -> str:
    """Export chat history to Markdown format.

    Args:
        history: List of chat entries

    Returns:
        Markdown string
    """
    lines = []
    lines.append("# Ra'd AI Chat History")
    lines.append(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for entry in history:
        role = entry.get("role", "unknown")
        content = entry.get("content", "")
        timestamp = entry.get("timestamp", "")

        if role == "user":
            lines.append(f"## User")
            lines.append(f"> {content}")
        else:
            lines.append(f"## Ra'd AI")
            response_data = entry.get("response_data", {})
            if response_data:
                lines.append(export_response_to_text(response_data))
            else:
                lines.append(content)

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_export_buttons(
    response_data: Dict[str, Any],
    key_prefix: str = "export"
) -> None:
    """Render export buttons for a response.

    Args:
        response_data: Response data to export
        key_prefix: Unique key prefix for buttons
    """
    if st is None:
        raise RuntimeError("Streamlit required")

    response_type = response_data.get("type", "text")
    data = response_data.get("data")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        # Text export
        text = export_response_to_text(response_data)
        st.download_button(
            label="TXT",
            data=text,
            file_name=generate_export_filename("response", "txt"),
            mime="text/plain",
            key=f"{key_prefix}_txt"
        )

    with col2:
        # CSV export (only for dataframes)
        if response_type == "dataframe" and pd is not None and isinstance(data, pd.DataFrame):
            csv = export_to_csv(data)
            st.download_button(
                label="CSV",
                data=csv,
                file_name=generate_export_filename("data", "csv"),
                mime="text/csv",
                key=f"{key_prefix}_csv"
            )


def render_history_export_button() -> None:
    """Render button to export full chat history."""
    if st is None:
        raise RuntimeError("Streamlit required")

    from components.chat import get_chat_history

    history = get_chat_history()

    if history:
        md = export_chat_history_to_markdown(history)
        st.download_button(
            label="Export Chat History",
            data=md,
            file_name=generate_export_filename("chat_history", "md"),
            mime="text/markdown",
            key="export_history"
        )
