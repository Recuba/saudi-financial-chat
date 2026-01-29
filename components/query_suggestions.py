"""Query suggestions and autocomplete for Ra'd AI."""

from typing import List, Optional

try:
    import streamlit as st
except ImportError:
    st = None


COMMON_QUERIES = [
    "What are the top 10 companies by revenue?",
    "Show average ROE by sector",
    "Which companies have negative net profit?",
    "Compare revenue across sectors",
    "What is the total market cap?",
    "List companies with debt ratio above 2",
    "Show profit margins by industry",
    "What is the average current ratio?",
    "Top 5 companies by total assets",
    "Companies with highest dividend yield",
    "Revenue trend over the last 3 years",
    "Sector breakdown by number of companies",
    "Average net profit margin by sector",
    "Companies with revenue over 1 billion",
    "Show financial ratios for SABIC",
]

QUERY_TEMPLATES = {
    "top": "What are the top {n} companies by {metric}?",
    "average": "What is the average {metric} by sector?",
    "compare": "Compare {metric} across sectors",
    "trend": "Show {metric} trend over time",
    "filter": "Which companies have {metric} {condition}?",
    "chart": "Create a {chart_type} chart of {metric} by {dimension}",
}


def get_suggestions(partial_query: str, limit: int = 5) -> List[str]:
    """Get query suggestions based on partial input.

    Args:
        partial_query: User's partial query text
        limit: Maximum suggestions to return

    Returns:
        List of suggested queries
    """
    if not partial_query or len(partial_query) < 2:
        return COMMON_QUERIES[:limit]

    partial_lower = partial_query.lower()

    # Filter common queries that match
    matches = [
        q for q in COMMON_QUERIES
        if partial_lower in q.lower()
    ]

    # Also match by keywords
    keywords = partial_lower.split()
    keyword_matches = [
        q for q in COMMON_QUERIES
        if all(kw in q.lower() for kw in keywords)
    ]

    # Combine and dedupe
    all_matches = list(dict.fromkeys(matches + keyword_matches))

    return all_matches[:limit]


def get_column_suggestions(columns: List[str], partial_query: str) -> List[str]:
    """Generate suggestions based on available columns.

    Args:
        columns: List of column names
        partial_query: User's partial query

    Returns:
        List of column-specific suggestions
    """
    suggestions = []

    # Metrics/value columns
    metric_cols = [c for c in columns if any(
        kw in c.lower() for kw in ["revenue", "profit", "asset", "debt", "margin", "ratio"]
    )]

    for col in metric_cols[:3]:
        col_display = col.replace("_", " ")
        suggestions.extend([
            f"What is the average {col_display}?",
            f"Top 10 companies by {col_display}",
            f"Show {col_display} by sector",
        ])

    return suggestions


def render_suggestions_dropdown(partial_query: str) -> Optional[str]:
    """Render suggestions as clickable options.

    Args:
        partial_query: Current partial query

    Returns:
        Selected suggestion or None
    """
    if st is None:
        raise RuntimeError("Streamlit required")

    suggestions = get_suggestions(partial_query, limit=5)

    if not suggestions:
        return None

    selected = None

    st.caption("Suggestions:")
    cols = st.columns(min(len(suggestions), 3))

    for i, suggestion in enumerate(suggestions[:3]):
        with cols[i]:
            short_text = suggestion[:30] + "..." if len(suggestion) > 30 else suggestion
            if st.button(short_text, key=f"suggestion_{i}", help=suggestion):
                selected = suggestion

    return selected
