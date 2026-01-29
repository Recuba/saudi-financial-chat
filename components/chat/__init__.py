"""
Chat & AI Interface Components
==============================
Provides chat message display, code rendering, and feedback collection
for the Saudi Financial Chat application.

Components:
    - ChatMessage: Dataclass for message representation
    - render_message: Display chat messages with streamlit-chat
    - render_chat_history: Display full conversation history
    - CodeDisplay: Monaco editor for syntax-highlighted code
    - FeedbackWidget: Star rating feedback collection
"""

from components.chat.messages import (
    ChatMessage,
    render_message,
    render_chat_history,
    add_message_to_history,
    clear_chat_history,
    get_chat_history,
)

from components.chat.code_display import (
    CodeDisplay,
    render_code,
    detect_language,
    copy_code_button,
)

from components.chat.feedback import (
    FeedbackRecord,
    FeedbackWidget,
    render_star_rating,
    get_feedback_history,
    save_feedback,
)

__all__ = [
    # Messages
    "ChatMessage",
    "render_message",
    "render_chat_history",
    "add_message_to_history",
    "clear_chat_history",
    "get_chat_history",
    # Code Display
    "CodeDisplay",
    "render_code",
    "detect_language",
    "copy_code_button",
    # Feedback
    "FeedbackRecord",
    "FeedbackWidget",
    "render_star_rating",
    "get_feedback_history",
    "save_feedback",
]
