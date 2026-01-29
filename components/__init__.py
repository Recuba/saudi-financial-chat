"""UI components for Ra'd AI.

This package provides reusable Streamlit UI components for the Ra'd AI application.

Available modules and exports:

error_display:
    - format_api_error: Format API errors for user-friendly display
    - render_error_banner: Display error messages as styled banners
    - render_api_key_setup_guide: Show API key configuration instructions

sidebar:
    - render_sidebar: Main sidebar with all controls
    - render_database_info: Display database statistics
    - render_dataset_selector: Dataset selection dropdown
    - render_column_reference: Expandable column documentation
    - render_llm_status: LLM connection status indicator

example_questions:
    - render_example_questions: Display clickable example question cards
    - render_example_questions_minimal: Compact example question display
    - EXAMPLE_QUESTIONS: Dictionary of categorized example questions

chat:
    - format_response: Format AI responses for display
    - render_chat_input: Chat input field component
    - render_user_message: Display user messages in chat
    - render_ai_response: Display AI responses with formatting
    - process_query: Process user queries through the AI
    - render_chat_with_response: Combined chat input and response
    - initialize_chat_history: Set up session state for chat
    - add_to_chat_history: Add messages to chat history
    - get_chat_history: Retrieve chat history from session
    - clear_chat_history: Clear all chat messages
    - render_chat_history: Display full chat history
    - render_clear_history_button: Button to clear chat

status_indicator:
    - render_loading_state: Display loading spinner with message
    - render_status_badge: Colored status badge component
    - render_dependency_status: Show dependency check results
    - check_optional_dependencies: Check for optional packages
"""

from .error_display import (
    format_api_error,
    render_error_banner,
    render_api_key_setup_guide,
)
from .sidebar import (
    render_sidebar,
    render_database_info,
    render_dataset_selector,
    render_column_reference,
    render_llm_status,
)
from .example_questions import (
    render_example_questions,
    render_example_questions_minimal,
    EXAMPLE_QUESTIONS,
)
from .chat import (
    format_response,
    render_chat_input,
    render_user_message,
    render_ai_response,
    process_query,
    render_chat_with_response,
    initialize_chat_history,
    add_to_chat_history,
    get_chat_history,
    clear_chat_history,
    render_chat_history,
    render_clear_history_button,
)
from .status_indicator import (
    render_loading_state,
    render_status_badge,
    render_dependency_status,
    check_optional_dependencies,
)

__all__ = [
    # Error display
    "format_api_error",
    "render_error_banner",
    "render_api_key_setup_guide",
    # Sidebar
    "render_sidebar",
    "render_database_info",
    "render_dataset_selector",
    "render_column_reference",
    "render_llm_status",
    # Example questions
    "render_example_questions",
    "render_example_questions_minimal",
    "EXAMPLE_QUESTIONS",
    # Chat
    "format_response",
    "render_chat_input",
    "render_user_message",
    "render_ai_response",
    "process_query",
    "render_chat_with_response",
    "initialize_chat_history",
    "add_to_chat_history",
    "get_chat_history",
    "clear_chat_history",
    "render_chat_history",
    "render_clear_history_button",
    # Status indicator
    "render_loading_state",
    "render_status_badge",
    "render_dependency_status",
    "check_optional_dependencies",
]
