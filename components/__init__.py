"""UI components for Ra'd AI."""

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
]
