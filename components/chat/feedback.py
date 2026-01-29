"""
Feedback Components
===================
Star rating feedback collection and storage for
tracking user satisfaction with AI responses.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import streamlit as st

# --- OPTIONAL DEPENDENCY IMPORTS ---
try:
    from streamlit_star_rating import st_star_rating
    STAR_RATING_AVAILABLE = True
except ImportError:
    STAR_RATING_AVAILABLE = False


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

# Session state key for feedback storage
FEEDBACK_STORAGE_KEY = "feedback_history"


@dataclass
class FeedbackRecord:
    """
    Represents a feedback submission from a user.

    Attributes:
        rating: Star rating from 1-5.
        message_id: ID of the message being rated.
        query: The user's original query.
        response_summary: Brief summary of the AI response.
        comment: Optional user comment.
        timestamp: When the feedback was submitted.
        metadata: Additional metadata (e.g., response type, model used).
    """
    rating: int
    message_id: str
    query: str
    response_summary: str
    comment: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate feedback data."""
        if not 1 <= self.rating <= 5:
            raise ValueError(f"Rating must be between 1 and 5, got {self.rating}")

        if self.metadata is None:
            self.metadata = {}

    @property
    def is_positive(self) -> bool:
        """Check if feedback is positive (4-5 stars)."""
        return self.rating >= 4

    @property
    def is_negative(self) -> bool:
        """Check if feedback is negative (1-2 stars)."""
        return self.rating <= 2

    @property
    def is_neutral(self) -> bool:
        """Check if feedback is neutral (3 stars)."""
        return self.rating == 3

    @property
    def formatted_timestamp(self) -> str:
        """Return human-readable timestamp."""
        return self.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    @property
    def rating_label(self) -> str:
        """Return human-readable rating label."""
        labels = {
            1: "Very Poor",
            2: "Poor",
            3: "Average",
            4: "Good",
            5: "Excellent",
        }
        return labels.get(self.rating, "Unknown")

    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback to dictionary for serialization."""
        return {
            "rating": self.rating,
            "message_id": self.message_id,
            "query": self.query,
            "response_summary": self.response_summary,
            "comment": self.comment,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackRecord":
        """Create FeedbackRecord from dictionary."""
        return cls(
            rating=data["rating"],
            message_id=data["message_id"],
            query=data["query"],
            response_summary=data["response_summary"],
            comment=data.get("comment"),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            metadata=data.get("metadata", {}),
        )


def _init_feedback_storage() -> None:
    """Initialize feedback storage in session state if not present."""
    if FEEDBACK_STORAGE_KEY not in st.session_state:
        st.session_state[FEEDBACK_STORAGE_KEY] = []


def get_feedback_history() -> List[FeedbackRecord]:
    """
    Retrieve all feedback records from session state.

    Returns:
        List of FeedbackRecord objects.
    """
    _init_feedback_storage()
    return st.session_state[FEEDBACK_STORAGE_KEY]


def save_feedback(feedback: FeedbackRecord) -> None:
    """
    Save a feedback record to session state.

    Args:
        feedback: FeedbackRecord to save.
    """
    _init_feedback_storage()
    st.session_state[FEEDBACK_STORAGE_KEY].append(feedback)


def clear_feedback_history() -> None:
    """Clear all feedback records from session state."""
    st.session_state[FEEDBACK_STORAGE_KEY] = []


def get_feedback_stats() -> Dict[str, Any]:
    """
    Calculate feedback statistics.

    Returns:
        Dictionary with feedback statistics.
    """
    history = get_feedback_history()

    if not history:
        return {
            "total": 0,
            "average_rating": 0.0,
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "rating_distribution": {i: 0 for i in range(1, 6)},
        }

    ratings = [f.rating for f in history]

    return {
        "total": len(history),
        "average_rating": sum(ratings) / len(ratings),
        "positive_count": sum(1 for f in history if f.is_positive),
        "negative_count": sum(1 for f in history if f.is_negative),
        "neutral_count": sum(1 for f in history if f.is_neutral),
        "rating_distribution": {
            i: sum(1 for r in ratings if r == i) for i in range(1, 6)
        },
    }


def render_star_rating(
    message_id: str,
    query: str,
    response_summary: str,
    key: Optional[str] = None,
    on_submit: Optional[Callable[[FeedbackRecord], None]] = None,
    show_comment_box: bool = True,
    size: int = 24,
    default_value: int = 0,
) -> Optional[FeedbackRecord]:
    """
    Render a star rating feedback widget.

    Uses streamlit-star-rating if available, otherwise falls back
    to a custom implementation.

    Args:
        message_id: Unique ID for the message being rated.
        query: The user's original query.
        response_summary: Brief summary of the response.
        key: Unique key for the component.
        on_submit: Callback function when feedback is submitted.
        show_comment_box: Whether to show optional comment input.
        size: Size of star icons in pixels.
        default_value: Default rating value (0 = no selection).

    Returns:
        FeedbackRecord if submitted, None otherwise.
    """
    if key is None:
        key = f"feedback_{message_id}"

    # Container for feedback UI
    feedback_container = st.container()

    with feedback_container:
        st.markdown(
            f"""
            <div style="
                background: {THEME['bg_card']};
                border: 1px solid rgba(212, 168, 75, 0.2);
                border-radius: 8px;
                padding: 12px 16px;
                margin: 8px 0;
            ">
                <p style="
                    color: {THEME['text_secondary']};
                    font-size: 13px;
                    margin-bottom: 8px;
                ">How helpful was this response?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rating = None

        if STAR_RATING_AVAILABLE:
            # Use streamlit-star-rating
            rating = st_star_rating(
                label="",
                maxValue=5,
                defaultValue=default_value,
                key=f"{key}_stars",
                size=size,
                customCSS=f"""
                    .star-rating svg {{
                        fill: {THEME['gold_primary']};
                    }}
                    .star-rating svg.empty {{
                        fill: {THEME['bg_input']};
                        stroke: {THEME['gold_dark']};
                    }}
                """,
            )
        else:
            # Fallback: Custom star rating with buttons
            rating = _render_fallback_stars(
                key=f"{key}_fallback",
                default_value=default_value,
            )

        # Comment box
        comment = None
        if show_comment_box and rating and rating > 0:
            comment = st.text_area(
                "Additional comments (optional)",
                key=f"{key}_comment",
                height=80,
                placeholder="Tell us more about your experience...",
            )

        # Submit button
        if rating and rating > 0:
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("Submit Feedback", key=f"{key}_submit", type="primary"):
                    feedback = FeedbackRecord(
                        rating=rating,
                        message_id=message_id,
                        query=query,
                        response_summary=response_summary,
                        comment=comment if comment else None,
                    )

                    # Save to session state
                    save_feedback(feedback)

                    # Call callback if provided
                    if on_submit:
                        on_submit(feedback)

                    st.success(f"Thank you for your feedback! ({feedback.rating_label})")
                    return feedback

    return None


def _render_fallback_stars(
    key: str,
    default_value: int = 0,
) -> int:
    """
    Render fallback star rating using native Streamlit components.

    Args:
        key: Unique key for the component.
        default_value: Default rating value.

    Returns:
        Selected rating (1-5) or 0 if none selected.
    """
    # Initialize session state for rating
    state_key = f"{key}_rating"
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value

    cols = st.columns(5)

    for i, col in enumerate(cols):
        star_num = i + 1
        with col:
            # Determine if star should be filled
            is_filled = star_num <= st.session_state[state_key]

            # Star character and color
            star_char = "\u2605" if is_filled else "\u2606"  # Filled vs empty star
            star_color = THEME["gold_primary"] if is_filled else THEME["text_secondary"]

            # Custom button styling with HTML
            button_html = f"""
            <button onclick="
                var inputs = parent.document.querySelectorAll('input[data-testid]');
                inputs.forEach(function(input) {{
                    if (input.getAttribute('data-testid').includes('{key}_star_{star_num}')) {{
                        input.click();
                    }}
                }});
            " style="
                background: transparent;
                border: none;
                color: {star_color};
                font-size: 28px;
                cursor: pointer;
                padding: 4px 8px;
                transition: transform 0.15s ease;
            " onmouseover="this.style.transform='scale(1.2)'"
               onmouseout="this.style.transform='scale(1)'">
                {star_char}
            </button>
            """

            # Hidden button to capture clicks
            if st.button(
                star_char,
                key=f"{key}_star_{star_num}",
                help=f"Rate {star_num} star{'s' if star_num > 1 else ''}",
            ):
                st.session_state[state_key] = star_num
                st.rerun()

    return st.session_state[state_key]


class FeedbackWidget:
    """
    Encapsulates feedback widget state and rendering.

    Provides a reusable feedback collection component.
    """

    def __init__(
        self,
        message_id: str,
        query: str,
        response_summary: str,
        show_comment: bool = True,
    ):
        """
        Initialize feedback widget.

        Args:
            message_id: Unique ID for the message.
            query: User's original query.
            response_summary: Brief summary of the response.
            show_comment: Whether to show comment input.
        """
        self.message_id = message_id
        self.query = query
        self.response_summary = response_summary
        self.show_comment = show_comment
        self._submitted = False
        self._feedback: Optional[FeedbackRecord] = None

    @property
    def submitted(self) -> bool:
        """Check if feedback has been submitted."""
        return self._submitted

    @property
    def feedback(self) -> Optional[FeedbackRecord]:
        """Get submitted feedback record."""
        return self._feedback

    def render(
        self,
        key: Optional[str] = None,
        on_submit: Optional[Callable[[FeedbackRecord], None]] = None,
    ) -> Optional[FeedbackRecord]:
        """
        Render the feedback widget.

        Args:
            key: Unique key for the component.
            on_submit: Callback when feedback is submitted.

        Returns:
            FeedbackRecord if submitted, None otherwise.
        """
        result = render_star_rating(
            message_id=self.message_id,
            query=self.query,
            response_summary=self.response_summary,
            key=key,
            on_submit=on_submit,
            show_comment_box=self.show_comment,
        )

        if result:
            self._submitted = True
            self._feedback = result

        return result


def render_feedback_summary() -> None:
    """Render a summary of collected feedback statistics."""
    stats = get_feedback_stats()

    if stats["total"] == 0:
        st.info("No feedback collected yet.")
        return

    st.markdown(
        f"""
        <div style="
            background: {THEME['bg_card']};
            border: 1px solid rgba(212, 168, 75, 0.2);
            border-radius: 12px;
            padding: 20px;
        ">
            <h4 style="color: {THEME['gold_light']}; margin-bottom: 16px;">
                Feedback Summary
            </h4>
            <div style="display: flex; gap: 24px; flex-wrap: wrap;">
                <div>
                    <span style="color: {THEME['text_secondary']}; font-size: 13px;">
                        Total Responses
                    </span>
                    <p style="color: {THEME['text_primary']}; font-size: 24px; font-weight: 700; margin: 4px 0;">
                        {stats['total']}
                    </p>
                </div>
                <div>
                    <span style="color: {THEME['text_secondary']}; font-size: 13px;">
                        Average Rating
                    </span>
                    <p style="color: {THEME['gold_primary']}; font-size: 24px; font-weight: 700; margin: 4px 0;">
                        {stats['average_rating']:.1f} / 5.0
                    </p>
                </div>
                <div>
                    <span style="color: {THEME['text_secondary']}; font-size: 13px;">
                        Positive
                    </span>
                    <p style="color: #4CAF50; font-size: 24px; font-weight: 700; margin: 4px 0;">
                        {stats['positive_count']}
                    </p>
                </div>
                <div>
                    <span style="color: {THEME['text_secondary']}; font-size: 13px;">
                        Negative
                    </span>
                    <p style="color: #F44336; font-size: 24px; font-weight: 700; margin: 4px 0;">
                        {stats['negative_count']}
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Rating distribution bar
    st.markdown("**Rating Distribution**")
    for rating in range(5, 0, -1):
        count = stats["rating_distribution"][rating]
        percentage = (count / stats["total"]) * 100 if stats["total"] > 0 else 0

        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.write(f"{'*' * rating}")
        with col2:
            st.progress(percentage / 100)
        with col3:
            st.write(f"{count}")


def render_inline_feedback(
    message_id: str,
    query: str,
    response_summary: str,
    key: Optional[str] = None,
) -> Optional[int]:
    """
    Render compact inline feedback (thumbs up/down or quick stars).

    Args:
        message_id: Unique ID for the message.
        query: User's original query.
        response_summary: Brief summary of the response.
        key: Unique key for the component.

    Returns:
        Rating if submitted (5 for positive, 1 for negative), None otherwise.
    """
    if key is None:
        key = f"inline_{message_id}"

    col1, col2, col3 = st.columns([8, 1, 1])

    with col2:
        if st.button("\U0001F44D", key=f"{key}_up", help="Helpful"):
            feedback = FeedbackRecord(
                rating=5,
                message_id=message_id,
                query=query,
                response_summary=response_summary,
                metadata={"type": "inline", "sentiment": "positive"},
            )
            save_feedback(feedback)
            st.toast("Thanks for the feedback!")
            return 5

    with col3:
        if st.button("\U0001F44E", key=f"{key}_down", help="Not helpful"):
            feedback = FeedbackRecord(
                rating=1,
                message_id=message_id,
                query=query,
                response_summary=response_summary,
                metadata={"type": "inline", "sentiment": "negative"},
            )
            save_feedback(feedback)
            st.toast("Thanks for the feedback!")
            return 1

    return None
