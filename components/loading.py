"""Loading indicators and skeleton states for Ra'd AI."""

import random

try:
    import streamlit as st
except ImportError:
    st = None


LOADING_MESSAGES = [
    "Analyzing financial data...",
    "Crunching the numbers...",
    "Querying the database...",
    "Processing your request...",
    "Fetching insights...",
    "Computing results...",
]


def get_random_loading_message() -> str:
    """Get a random loading message."""
    return random.choice(LOADING_MESSAGES)


def _inject_skeleton_css_once() -> None:
    """Inject skeleton CSS once per session."""
    if st is None:
        return
    if not st.session_state.get("_skeleton_css_injected"):
        st.markdown(get_skeleton_css(), unsafe_allow_html=True)
        st.session_state._skeleton_css_injected = True


def get_skeleton_css() -> str:
    """Return CSS for skeleton loading states."""
    return """
<style>
@keyframes skeleton-pulse {
    0% { opacity: 0.6; }
    50% { opacity: 0.3; }
    100% { opacity: 0.6; }
}

.skeleton {
    background: linear-gradient(90deg, var(--bg-card) 25%, var(--bg-card-hover) 50%, var(--bg-card) 75%);
    background-size: 200% 100%;
    animation: skeleton-pulse 1.5s ease-in-out infinite;
    border-radius: var(--radius-sm);
}

.skeleton-text {
    height: 1em;
    margin: 0.5em 0;
}

.skeleton-chart {
    height: 200px;
    margin: 1em 0;
}

.skeleton-table {
    height: 150px;
    margin: 1em 0;
}
</style>
"""


def render_skeleton_text(lines: int = 3) -> None:
    """Render skeleton text placeholders."""
    if st is None:
        raise RuntimeError("Streamlit is required to render skeleton text")

    _inject_skeleton_css_once()

    widths = [100, 80, 90, 70, 85]
    for i in range(lines):
        width = widths[i % len(widths)]
        st.markdown(
            f'<div class="skeleton skeleton-text" style="width: {width}%;"></div>',
            unsafe_allow_html=True
        )


def render_skeleton_chart() -> None:
    """Render skeleton chart placeholder."""
    if st is None:
        raise RuntimeError("Streamlit is required to render skeleton chart")

    _inject_skeleton_css_once()
    st.markdown(
        '<div class="skeleton skeleton-chart"></div>',
        unsafe_allow_html=True
    )


def render_skeleton_table() -> None:
    """Render skeleton table placeholder."""
    if st is None:
        raise RuntimeError("Streamlit is required to render skeleton table")

    _inject_skeleton_css_once()
    st.markdown(
        '<div class="skeleton skeleton-table"></div>',
        unsafe_allow_html=True
    )
