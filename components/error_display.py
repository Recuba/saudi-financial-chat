"""Error display component with pattern-based error classification and user-friendly handling."""

import html
import logging
from typing import Any, Callable, Dict, List, Optional

try:
    import streamlit as st
except ImportError:
    st = None  # Allow module to be imported for testing without streamlit

logger = logging.getLogger(__name__)


def _sanitize_message(message: str) -> str:
    """Sanitize a message for safe HTML display.

    Args:
        message: The raw message string

    Returns:
        HTML-escaped message string
    """
    if not message:
        return ""
    return html.escape(str(message))


# Error patterns mapping error types to their patterns, titles, descriptions, steps, and action labels
ERROR_PATTERNS: Dict[str, Dict[str, Any]] = {
    "auth": {
        "patterns": ["authentication", "api key", "unauthorized", "401", "invalid key", "api_key"],
        "title": "API Key Issue",
        "description": "There's a problem with your API key configuration.",
        "steps": [
            "Check that your API key is correctly entered in the sidebar",
            "Verify your API key is valid and not expired",
            "Ensure your API key has the required permissions",
            "Try generating a new API key from OpenRouter",
        ],
        "action_label": "Check Settings",
    },
    "rate_limit": {
        "patterns": ["rate limit", "too many requests", "429", "quota", "exceeded"],
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
        "patterns": ["timeout", "timed out", "connection", "network", "unreachable"],
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
        "patterns": ["column", "not found", "keyerror", "indexerror", "no data", "empty"],
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
        "patterns": ["model", "gemini", "llm", "generation", "openrouter"],
        "title": "Model Error",
        "description": "There was an issue with the AI model.",
        "steps": [
            "Try a different query or question",
            "The model might be temporarily unavailable",
            "Try selecting a different model from the sidebar",
        ],
        "action_label": "Retry",
    },
    "response_format": {
        "patterns": ["result must be in the format", "dictionary of type and value", "result =", "parsing"],
        "title": "Query Processing Error",
        "description": "The AI had trouble formatting the response for your question.",
        "steps": [
            "Try rephrasing your question with more specific terms",
            "Ask for a specific metric or comparison (e.g., 'What is the total revenue for SABIC in 2023?')",
            "Try asking for data in a different format (e.g., 'Show me a table of...' instead of 'List...')",
            "Break complex questions into simpler parts",
        ],
        "action_label": "Try Again",
    },
    "ssl": {
        "patterns": ["ssl", "certificate", "https", "verify"],
        "title": "SSL/Security Error",
        "description": "There was a security issue with the connection.",
        "steps": [
            "Check your network connection",
            "Ensure you're not behind a restrictive firewall",
            "Try again in a few moments",
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
            - original_message: The original error message (sanitized)
    """
    if not error_message:
        error_message = "Unknown error"

    error_lower = str(error_message).lower()

    # Try to match against known error patterns
    for error_type, config in ERROR_PATTERNS.items():
        for pattern in config["patterns"]:
            if pattern in error_lower:
                logger.debug(f"Matched error pattern '{pattern}' -> type '{error_type}'")
                return {
                    "type": error_type,
                    "title": config["title"],
                    "description": config["description"],
                    "steps": config["steps"],
                    "action_label": config["action_label"],
                    "original_message": _sanitize_message(error_message),
                }

    # Return generic error if no pattern matched
    logger.debug(f"No error pattern matched for: {error_message[:100]}")
    return {
        "type": "generic",
        "title": GENERIC_ERROR["title"],
        "description": GENERIC_ERROR["description"],
        "steps": GENERIC_ERROR["steps"],
        "action_label": GENERIC_ERROR["action_label"],
        "original_message": _sanitize_message(error_message),
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
        "response_format": ":speech_balloon:",
        "ssl": ":lock:",
        "generic": ":warning:",
    }
    error_type = error_info.get("type", "generic")
    icon = icon_map.get(error_type, ":warning:")

    # Sanitize title and description for safe display
    title = _sanitize_message(error_info.get("title", "Error"))
    description = _sanitize_message(error_info.get("description", "An error occurred"))

    # Main error container
    try:
        with st.container():
            st.error(f"{icon} **{title}**")

            st.markdown(description)

            # Resolution steps
            steps = error_info.get("steps", [])
            if steps:
                st.markdown("**What you can do:**")
                for step in steps:
                    st.markdown(f"- {_sanitize_message(step)}")

            # Action button
            col1, col2 = st.columns([1, 3])
            with col1:
                action_label = _sanitize_message(error_info.get("action_label", "Retry"))
                if on_retry and st.button(action_label, type="primary"):
                    try:
                        on_retry()
                    except Exception as e:
                        logger.error(f"Error in retry callback: {e}")
                        st.error("Failed to retry. Please refresh the page.")

            # Collapsible technical details
            with st.expander("Technical Details", expanded=show_details):
                # Display original message (already sanitized in format_api_error)
                original_msg = error_info.get("original_message", "No details available")
                st.text(original_msg)  # Use st.text instead of st.code for safer display

    except Exception as e:
        logger.error(f"Error rendering error banner: {e}")
        st.error("An error occurred while displaying the error message.")


def render_api_key_setup_guide() -> None:
    """
    Render a guide for setting up the API key.

    Shows step-by-step instructions for obtaining and configuring
    the OpenRouter API key.
    """
    if st is None:
        raise RuntimeError("Streamlit is required to render API key setup guide")

    st.info(":key: **API Key Setup Required**")

    st.markdown("""
    To use this application, you need an OpenRouter API key. Follow these steps:

    ### Step 1: Get Your API Key
    1. Visit [OpenRouter](https://openrouter.ai/)
    2. Sign in or create an account
    3. Go to "Keys" in your dashboard
    4. Create a new API key

    ### Step 2: Configure the App

    **For Local Development:**
    Create a file at `.streamlit/secrets.toml`:
    ```toml
    OPENROUTER_API_KEY = "sk-or-v1-your-api-key-here"
    ```

    **For Streamlit Cloud:**
    1. Go to your app settings
    2. Click "Secrets"
    3. Add your API key

    ### Step 3: Start Analyzing
    Once configured, you can start asking questions about your financial data!

    ---
    :lock: **Security Note:** Your API key is stored securely in Streamlit secrets
    and is never exposed to the client.
    """)
