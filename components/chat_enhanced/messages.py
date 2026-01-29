"""
Chat Message Components
=======================
Handles chat message rendering, history management, and display
with fallback support for streamlit-chat package.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import streamlit as st

# --- OPTIONAL DEPENDENCY IMPORTS ---
try:
    from streamlit_chat import message as st_chat_message
    STREAMLIT_CHAT_AVAILABLE = True
except ImportError:
    STREAMLIT_CHAT_AVAILABLE = False


# --- THEME COLORS (matching app theme) ---
THEME = {
    "gold_primary": "#D4A84B",
    "gold_light": "#E8C872",
    "gold_dark": "#B8860B",
    "bg_dark": "#0E0E0E",
    "bg_card": "#1A1A1A",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0B0",
}


@dataclass
class ChatMessage:
    """
    Represents a chat message in the conversation.

    Attributes:
        role: The role of the message sender ('user', 'assistant', 'system')
        content: The text content of the message
        timestamp: When the message was created
        code: Optional code snippet associated with the message
        metadata: Additional metadata (e.g., response type, execution time)
    """
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    code: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize message data."""
        valid_roles = {"user", "assistant", "system"}
        if self.role not in valid_roles:
            raise ValueError(f"Invalid role '{self.role}'. Must be one of {valid_roles}")

        # Ensure metadata is a dict
        if self.metadata is None:
            self.metadata = {}

    @property
    def is_user(self) -> bool:
        """Check if message is from user."""
        return self.role == "user"

    @property
    def is_assistant(self) -> bool:
        """Check if message is from assistant."""
        return self.role == "assistant"

    @property
    def has_code(self) -> bool:
        """Check if message has associated code."""
        return self.code is not None and len(self.code.strip()) > 0

    @property
    def formatted_timestamp(self) -> str:
        """Return human-readable timestamp."""
        return self.timestamp.strftime("%H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "code": self.code,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Create ChatMessage from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            code=data.get("code"),
            metadata=data.get("metadata", {}),
        )


def _init_chat_history() -> None:
    """Initialize chat history in session state if not present."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []


def get_chat_history() -> List[ChatMessage]:
    """
    Retrieve the current chat history from session state.

    Returns:
        List of ChatMessage objects representing the conversation.
    """
    _init_chat_history()
    return st.session_state.chat_history


def add_message_to_history(message: ChatMessage) -> None:
    """
    Add a new message to the chat history.

    Args:
        message: ChatMessage object to add to history.
    """
    _init_chat_history()
    st.session_state.chat_history.append(message)


def clear_chat_history() -> None:
    """Clear all messages from the chat history."""
    st.session_state.chat_history = []


def render_message(
    message: ChatMessage,
    key: Optional[str] = None,
    show_timestamp: bool = False,
    show_code: bool = True,
) -> None:
    """
    Render a single chat message with appropriate styling.

    Uses streamlit-chat if available, otherwise falls back to st.chat_message.

    Args:
        message: ChatMessage object to render.
        key: Unique key for the message component.
        show_timestamp: Whether to display the message timestamp.
        show_code: Whether to display associated code (if any).
    """
    # Generate unique key if not provided
    if key is None:
        key = f"msg_{message.timestamp.timestamp()}_{message.role}"

    # Map roles to display names and avatars
    role_config = {
        "user": {
            "name": "You",
            "avatar": None,  # Use default
            "is_user": True,
        },
        "assistant": {
            "name": "Ra'd AI",
            "avatar": None,
            "is_user": False,
        },
        "system": {
            "name": "System",
            "avatar": None,
            "is_user": False,
        },
    }

    config = role_config.get(message.role, role_config["assistant"])

    if STREAMLIT_CHAT_AVAILABLE:
        # Use streamlit-chat for enhanced display
        st_chat_message(
            message.content,
            is_user=config["is_user"],
            key=key,
            avatar_style="initials" if config["is_user"] else "bottts",
            seed=config["name"],
        )

        # Show timestamp if requested
        if show_timestamp:
            st.caption(f"_{message.formatted_timestamp}_")

        # Show code block if present and requested
        if show_code and message.has_code:
            with st.expander("View Generated Code", expanded=False):
                st.code(message.code, language="python")
    else:
        # Fallback to native Streamlit chat_message
        avatar = "user" if message.is_user else "assistant"

        with st.chat_message(avatar):
            st.write(message.content)

            # Show timestamp if requested
            if show_timestamp:
                st.caption(f"_{message.formatted_timestamp}_")

            # Show code block if present and requested
            if show_code and message.has_code:
                with st.expander("View Generated Code", expanded=False):
                    st.code(message.code, language="python")


def render_chat_history(
    show_timestamps: bool = False,
    show_code: bool = True,
    max_messages: Optional[int] = None,
) -> None:
    """
    Render the entire chat history.

    Args:
        show_timestamps: Whether to display timestamps for each message.
        show_code: Whether to display associated code blocks.
        max_messages: Maximum number of recent messages to show (None for all).
    """
    history = get_chat_history()

    # Apply message limit if specified
    if max_messages is not None and len(history) > max_messages:
        history = history[-max_messages:]
        st.caption(f"_Showing last {max_messages} messages_")

    # Render each message
    for idx, message in enumerate(history):
        render_message(
            message,
            key=f"history_{idx}_{message.role}",
            show_timestamp=show_timestamps,
            show_code=show_code,
        )


def create_user_message(content: str, metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
    """
    Convenience function to create a user message.

    Args:
        content: The message text.
        metadata: Optional metadata dict.

    Returns:
        ChatMessage configured as user message.
    """
    return ChatMessage(
        role="user",
        content=content,
        metadata=metadata or {},
    )


def create_assistant_message(
    content: str,
    code: Optional[str] = None,
    response_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ChatMessage:
    """
    Convenience function to create an assistant message.

    Args:
        content: The message text.
        code: Optional generated code (e.g., from PandasAI).
        response_type: Type of response ('dataframe', 'chart', 'text').
        metadata: Optional additional metadata.

    Returns:
        ChatMessage configured as assistant message.
    """
    meta = metadata or {}
    if response_type:
        meta["response_type"] = response_type

    return ChatMessage(
        role="assistant",
        content=content,
        code=code,
        metadata=meta,
    )


def render_typing_indicator() -> None:
    """Display a typing indicator while assistant is processing."""
    with st.chat_message("assistant"):
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 8px;">
                <div style="
                    width: 8px;
                    height: 8px;
                    background: {THEME['gold_primary']};
                    border-radius: 50%;
                    animation: pulse 1s infinite;
                "></div>
                <div style="
                    width: 8px;
                    height: 8px;
                    background: {THEME['gold_primary']};
                    border-radius: 50%;
                    animation: pulse 1s infinite 0.2s;
                "></div>
                <div style="
                    width: 8px;
                    height: 8px;
                    background: {THEME['gold_primary']};
                    border-radius: 50%;
                    animation: pulse 1s infinite 0.4s;
                "></div>
                <span style="color: {THEME['text_secondary']}; margin-left: 8px;">
                    Analyzing data...
                </span>
            </div>
            <style>
                @keyframes pulse {{
                    0%, 100% {{ opacity: 0.3; transform: scale(0.8); }}
                    50% {{ opacity: 1; transform: scale(1); }}
                }}
            </style>
            """,
            unsafe_allow_html=True,
        )
