"""Error display component with pattern-based error classification and user-friendly handling."""

from typing import Any, Callable, Dict, List, Optional

try:
    import streamlit as st
except ImportError:
    st = None  # Allow module to be imported for testing without streamlit


# Error patterns mapping error types to their patterns, titles, descriptions, steps, and action labels
ERROR_PATTERNS: Dict[str, Dict[str, Any]] = {
    "auth": {
        "patterns": ["authentication", "api key", "unauthorized", "401", "invalid key"],
        "title": "API Key Issue",
        "description": "There's a problem with your API key configuration.",
        "steps": [
            "Check that your API key is correctly entered in the sidebar",
            "Verify your API key is valid and not expired",
            "Ensure your API key has the required permissions",
            "Try generating a new API key from the Google AI Studio",
        ],
        "action_label": "Check Settings",
    },
    "rate_limit": {
        "patterns": ["rate limit", "too many requests", "429", "quota"],
        "title": "Rate Limit Exceeded",
        "description": "You've made too many requests in a short period.",
        "steps": [
            "Wait a few minutes before trying again",
            "Reduce the frequency of your requests",
            "Consider upgrading your API plan for higher limits",
        ],
        "action_label": "Retry Later",
    },
    "timeout": {
        "patterns": ["timeout", "timed out", "connection", "network"],
        "title": "Connection Timeout",
        "description": "The request took too long or couldn't connect to the server.",
        "steps": [
            "Check your internet connection",
            "Try again in a few moments",
            "The server might be experiencing high load",
        ],
        "action_label": "Retry",
    },
    "data": {
        "patterns": ["column", "not found", "keyerror", "indexerror", "no data"],
        "title": "Data Error",
        "description": "There was an issue processing the data.",
        "steps": [
            "Verify the data file is correctly formatted",
            "Check that all required columns are present",
            "Ensure the data is not empty",
        ],
        "action_label": "Check Data",
    },
    "model": {
        "patterns": ["model", "gemini", "llm", "generation"],
        "title": "Model Error",
        "description": "There was an issue with the AI model.",
        "steps": [
            "Try a different query or question",
            "The model might be temporarily unavailable",
            "Check if the model name is correctly configured",
        ],
        "action_label": "Retry",
    },
}

# Generic error fallback
GENERIC_ERROR: Dict[str, Any] = {
    "title": "An Error Occurred",
    "description": "Something went wrong while processing your request.",
    "steps": [
        "Try refreshing the page",
        "Check your input and try again",
        "If the problem persists, please contact support",
    ],
    "action_label": "Retry",
}


def format_api_error(error_message: str) -> Dict[str, Any]:
    """
    Format an API error message into a user-friendly structure.

    Matches the error message against known patterns and returns
    a formatted error info dictionary with type, title, description,
    resolution steps, and action label.

    Args:
        error_message: The raw error message string

    Returns:
        Dictionary containing:
            - type: Error type (auth, rate_limit, timeout, data, model, or generic)
            - title: User-friendly error title
            - description: Description of what went wrong
            - steps: List of resolution steps
            - action_label: Label for the action button
            - original_message: The original error message
    """
    error_lower = error_message.lower()

    # Try to match against known error patterns
    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern in error_lower:
                return {
                    "type": error_type,
                    "title": config["title"],
                    "description": config["description"],
                    "steps": config["steps"],
                    "action_label": config["action_label"],
                    "original_message": error_message,
                }

    # Return generic error if no pattern matched
    return {
        "type": "generic",
        "title": GENERIC_ERROR["title"],
        "description": GENERIC_ERROR["description"],
        "steps": GENERIC_ERROR["steps"],
        "action_label": GENERIC_ERROR["action_label"],
        "original_message": error_message,
    }


def render_error_banner(
    error_info: Dict[str, Any],
    show_details: bool = False,
    on_retry: Optional[Callable[[], None]] = None,
) -> None:
    """
    Render a Streamlit error banner with user-friendly formatting.

    Displays the error with title, description, resolution steps,
    and an optional retry button. Technical details can be shown
    in a collapsible section.

    Args:
        error_info: Dictionary from format_api_error()
        show_details: Whether to show technical details by default
        on_retry: Optional callback function for the retry button
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render error banner")

    # Error icon based on type
    icon_map = {
        "auth": ":key:",
        "rate_limit": ":hourglass:",
        "timeout": ":electric_plug:",
        "data": ":card_file_box:",
        "model": ":robot_face:",
        "generic": ":warning:",
    }
    icon = icon_map.get(error_info["type"], ":warning:")

    # Main error container
    with st.container():
        st.error(f"{icon} **{error_info['title']}**")

        st.markdown(error_info["description"])

        # Resolution steps
        if error_info.get("steps"):
            st.markdown("**What you can do:**")
            for step in error_info["steps"]:
                st.markdown(f"- {step}")

        # Action button
        col1, col2 = st.columns([1, 3])
        with col1:
            if on_retry and st.button(error_info["action_label"], type="primary"):
                on_retry()

        # Collapsible technical details
        with st.expander("Technical Details", expanded=show_details):
            st.code(error_info["original_message"], language=None)


def render_api_key_setup_guide() -> None:
    """
    Render a guide for setting up the API key.

    Shows step-by-step instructions for obtaining and configuring
    the Google Gemini API key.
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render API key setup guide")

    st.info(":key: **API Key Setup Required**")

    st.markdown("""
    To use this application, you need a Google Gemini API key. Follow these steps:

    ### Step 1: Get Your API Key
    1. Visit [Google AI Studio](https://aistudio.google.com/)
    2. Sign in with your Google account
    3. Click "Get API Key" in the left sidebar
    4. Create a new API key or use an existing one

    ### Step 2: Configure the App
    1. Enter your API key in the sidebar
    2. The key will be stored securely in your session

    ### Step 3: Start Analyzing
    Once configured, you can start asking questions about your financial data!

    ---
    :lock: **Security Note:** Your API key is only stored in your browser session
    and is never saved to the server.
    """)
