"""Status indicator component for Ra'd AI.

Provides visual indicators for app status, loading states, and dependencies.
"""

import streamlit as st
from typing import List, Dict, Optional


def render_loading_state(message: str = "Loading...") -> None:
    """Render a loading state indicator.

    Args:
        message: Loading message to display
    """
    st.markdown(f'''
    <div class="loading-indicator">
        <span>{message}</span>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
        <div class="loading-dot"></div>
    </div>
    ''', unsafe_allow_html=True)


def render_status_badge(
    label: str,
    status: str,
    help_text: Optional[str] = None
) -> None:
    """Render a status badge.

    Args:
        label: Badge label
        status: One of 'success', 'warning', 'error', 'info'
        help_text: Optional hover tooltip
    """
    colors = {
        "success": ("var(--status-success)", "checkmark"),
        "warning": ("var(--status-warning)", "warning"),
        "error": ("var(--status-error)", "x"),
        "info": ("var(--status-info)", "info"),
    }

    color, icon = colors.get(status, colors["info"])
    icon_map = {"checkmark": "check", "warning": "!", "x": "x", "info": "i"}
    icon_char = icon_map.get(icon, "i")

    badge_html = f'''
    <span style="
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 4px 12px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid {color};
        border-radius: 20px;
        font-size: 12px;
        color: {color};
    " title="{help_text or ''}">
        {icon_char} {label}
    </span>
    '''
    st.markdown(badge_html, unsafe_allow_html=True)


def render_dependency_status(dependencies: List[Dict]) -> None:
    """Render a list of dependency statuses.

    Args:
        dependencies: List of dicts with 'name', 'installed', 'version' keys
    """
    st.markdown("**Component Status:**")

    for dep in dependencies:
        status = "success" if dep.get("installed") else "error"
        icon = "OK" if dep.get("installed") else "X"
        version = dep.get("version", "")

        col1, col2, col3 = st.columns([3, 1, 2])

        with col1:
            st.markdown(f"{icon} **{dep['name']}**")
        with col2:
            st.markdown(f"`{version}`" if version else "-")
        with col3:
            if not dep.get("installed"):
                st.code(f"pip install {dep['name'].lower()}", language="bash")


def check_optional_dependencies() -> List[Dict]:
    """Check status of optional dependencies.

    Returns:
        List of dependency status dictionaries
    """
    dependencies = []

    # Check streamlit-echarts
    try:
        import streamlit_echarts
        dependencies.append({
            "name": "streamlit-echarts",
            "installed": True,
            "version": getattr(streamlit_echarts, "__version__", "unknown"),
            "description": "Interactive charts and treemaps"
        })
    except ImportError:
        dependencies.append({
            "name": "streamlit-echarts",
            "installed": False,
            "description": "Interactive charts and treemaps"
        })

    # Check pygwalker
    try:
        import pygwalker
        dependencies.append({
            "name": "pygwalker",
            "installed": True,
            "version": getattr(pygwalker, "__version__", "unknown"),
            "description": "Visual data exploration"
        })
    except ImportError:
        dependencies.append({
            "name": "pygwalker",
            "installed": False,
            "description": "Visual data exploration"
        })

    return dependencies
