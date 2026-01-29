"""Session state management for Ra'd AI."""

from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import streamlit as st
except ImportError:
    st = None


SESSION_DEFAULTS: Dict[str, Any] = {
    "chat_history": [],
    "favorite_queries": [],
    "recent_queries": [],
    "filters": {},
    "selected_dataset": "analytics",
    "selected_model": None,
    "theme_preference": "dark",
    "show_code_by_default": False,
}


def get_session_defaults() -> Dict[str, Any]:
    """Get default session state values.

    Returns:
        Dictionary of default values
    """
    return SESSION_DEFAULTS.copy()


def get_recent_queries_structure() -> Dict[str, Any]:
    """Get structure for recent queries storage.

    Returns:
        Configuration for recent queries
    """
    return {
        "max_items": 10,
        "fields": ["query", "timestamp", "dataset"],
    }


def initialize_session() -> None:
    """Initialize all session state with defaults."""
    if st is None:
        raise RuntimeError("Streamlit required")

    for key, default_value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_session_value(key: str, default: Any = None) -> Any:
    """Safely get a session state value.

    Args:
        key: The session state key to retrieve
        default: Default value if key doesn't exist

    Returns:
        The session value or default
    """
    if st is None:
        return default
    return st.session_state.get(key, default)


def set_session_value(key: str, value: Any) -> None:
    """Set a session state value.

    Args:
        key: The session state key to set
        value: The value to store
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    st.session_state[key] = value


def add_favorite_query(query: str) -> None:
    """Add a query to favorites.

    Args:
        query: The query string to save as favorite
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    initialize_session()
    favorites = st.session_state.favorite_queries
    if query not in favorites:
        favorites.append(query)
        st.session_state.favorite_queries = favorites[-20:]  # Keep last 20


def remove_favorite_query(query: str) -> None:
    """Remove a query from favorites.

    Args:
        query: The query string to remove
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    favorites = st.session_state.get("favorite_queries", [])
    if query in favorites:
        favorites.remove(query)
        st.session_state.favorite_queries = favorites


def get_favorite_queries() -> List[str]:
    """Get all favorite queries.

    Returns:
        List of favorite query strings
    """
    if st is None:
        return []
    return st.session_state.get("favorite_queries", [])


def add_recent_query(query: str, dataset: str = "") -> None:
    """Add a query to recent history.

    Args:
        query: The query string to add
        dataset: Optional dataset name associated with query
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    initialize_session()
    entry = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "dataset": dataset,
    }
    recent = st.session_state.recent_queries
    # Remove duplicate if exists
    recent = [r for r in recent if r.get("query") != query]
    recent.insert(0, entry)
    st.session_state.recent_queries = recent[:10]  # Keep last 10


def get_recent_queries() -> List[Dict[str, Any]]:
    """Get recent queries.

    Returns:
        List of recent query entries with query, timestamp, dataset
    """
    if st is None:
        return []
    return st.session_state.get("recent_queries", [])


def clear_recent_queries() -> None:
    """Clear all recent queries."""
    if st is None:
        raise RuntimeError("Streamlit required")
    st.session_state.recent_queries = []


def render_favorites_section() -> Optional[str]:
    """Render favorites section in sidebar.

    Returns:
        Selected query string if user clicked one, None otherwise
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    favorites = get_favorite_queries()
    if not favorites:
        return None
    selected = None
    with st.expander("Favorite Queries", expanded=False):
        for i, query in enumerate(favorites[:5]):
            col1, col2 = st.columns([4, 1])
            with col1:
                short_query = query[:35] + "..." if len(query) > 35 else query
                st.caption(short_query)
            with col2:
                if st.button("Run", key=f"fav_{i}", help="Run this query"):
                    selected = query
    return selected


def render_recent_queries_section() -> Optional[str]:
    """Render recent queries section.

    Returns:
        Selected query string if user clicked one, None otherwise
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    recent = get_recent_queries()
    if not recent:
        return None
    selected = None
    with st.expander("Recent Queries", expanded=False):
        for i, entry in enumerate(recent[:5]):
            col1, col2 = st.columns([4, 1])
            with col1:
                query = entry["query"]
                short_query = query[:35] + "..." if len(query) > 35 else query
                st.caption(short_query)
            with col2:
                if st.button("Rerun", key=f"recent_{i}", help="Re-run this query"):
                    selected = entry["query"]
    return selected


def save_filter_state(filters: Dict[str, Any]) -> None:
    """Save current filter state.

    Args:
        filters: Dictionary of filter values
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    st.session_state.filters = filters


def get_filter_state() -> Dict[str, Any]:
    """Get saved filter state.

    Returns:
        Dictionary of saved filter values
    """
    if st is None:
        return {}
    return st.session_state.get("filters", {})


def set_selected_dataset(dataset: str) -> None:
    """Set the selected dataset.

    Args:
        dataset: Dataset name to select
    """
    if st is None:
        raise RuntimeError("Streamlit required")
    st.session_state.selected_dataset = dataset


def get_selected_dataset() -> str:
    """Get the selected dataset.

    Returns:
        Currently selected dataset name
    """
    if st is None:
        return "analytics"
    return st.session_state.get("selected_dataset", "analytics")
