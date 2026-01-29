"""Example questions component for Ra'd AI.

Provides clickable example queries to help users get started.
"""

import streamlit as st
from typing import List, Dict, Optional


# Example questions organized by category
EXAMPLE_QUESTIONS = {
    "Popular": [
        {
            "label": "Top 10 companies by revenue 2024",
            "query": "What are the top 10 companies by revenue in 2024?",
            "icon": "📈"
        },
        {
            "label": "Average ROE by sector 2023",
            "query": "Show average ROE by sector in 2023",
            "icon": "📊"
        },
        {
            "label": "Companies with high debt",
            "query": "Which companies have debt to equity ratio greater than 2?",
            "icon": "💳"
        },
    ],
    "Analysis": [
        {
            "label": "Net profit margins by sector",
            "query": "Compare net profit margins across sectors",
            "icon": "📉"
        },
        {
            "label": "Negative profit companies 2024",
            "query": "List companies with negative net profit in 2024",
            "icon": "⚠️"
        },
        {
            "label": "Top 5 by total assets chart",
            "query": "Create a bar chart showing top 5 companies by total assets",
            "icon": "📊"
        },
    ],
    "Exploration": [
        {
            "label": "Sector breakdown",
            "query": "How many companies are in each sector?",
            "icon": "🏢"
        },
        {
            "label": "Average current ratio",
            "query": "What is the average current ratio by sector?",
            "icon": "💰"
        },
    ]
}


def render_example_questions(
    expanded: bool = True,
    max_visible: int = 3
) -> Optional[str]:
    """Render example question buttons.

    Args:
        expanded: Whether to show the expander as expanded
        max_visible: Number of questions to show by default

    Returns:
        Selected query string or None
    """
    selected_query = None

    # Show a few examples prominently
    st.subheader("Try an Example")

    # Display first few examples as prominent buttons
    popular = EXAMPLE_QUESTIONS["Popular"][:max_visible]

    cols = st.columns(len(popular))
    for i, example in enumerate(popular):
        with cols[i]:
            if st.button(
                f"{example['icon']} {example['label']}",
                key=f"example_prominent_{i}",
                use_container_width=True,
                help=example["query"]
            ):
                selected_query = example["query"]

    # More examples in expander
    with st.expander("More Examples", expanded=False):
        for category, questions in EXAMPLE_QUESTIONS.items():
            if category == "Popular":
                # Skip first 3 already shown
                questions = questions[max_visible:]
                if not questions:
                    continue

            st.markdown(f"**{category}**")

            for j, example in enumerate(questions):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"{example['icon']} {example['label']}")
                with col2:
                    if st.button(
                        "Try",
                        key=f"example_{category}_{j}",
                        help=example["query"]
                    ):
                        selected_query = example["query"]

            st.markdown("")  # Spacing

    return selected_query


def render_example_questions_minimal() -> Optional[str]:
    """Render a minimal version of example questions (just buttons).

    Returns:
        Selected query string or None
    """
    st.markdown("**Quick Examples:**")

    examples = [
        ("Top 10 revenue", "What are the top 10 companies by revenue in 2024?"),
        ("ROE by sector", "Show average ROE by sector in 2023"),
        ("High debt", "Which companies have debt to equity ratio greater than 2?"),
    ]

    cols = st.columns(len(examples))
    for i, (label, query) in enumerate(examples):
        with cols[i]:
            if st.button(label, key=f"quick_{i}", use_container_width=True):
                return query

    return None
