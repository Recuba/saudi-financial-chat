"""Comparison mode for side-by-side analysis."""

from typing import Any, Dict, List, Optional

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import streamlit as st
except ImportError:
    st = None

try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None


def get_comparison_metrics(df: "pd.DataFrame") -> List[str]:
    """Get numeric columns suitable for comparison.

    Args:
        df: DataFrame to extract metrics from

    Returns:
        List of column names that are numeric and suitable for comparison
    """
    if pd is None:
        return []
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    exclude = ["id", "filing_id", "fiscal_year"]
    return [c for c in numeric_cols if c.lower() not in exclude]


def compare_entities(
    df: "pd.DataFrame",
    entity_col: str,
    entities: List[str],
    metrics: List[str],
    year: Optional[int] = None
) -> "pd.DataFrame":
    """Compare multiple entities across metrics.

    Args:
        df: Source DataFrame
        entity_col: Column containing entity identifiers (e.g., 'company_name')
        entities: List of entities to compare
        metrics: List of metric columns to include
        year: Optional fiscal year filter

    Returns:
        DataFrame with comparison data
    """
    if pd is None:
        raise ImportError("pandas required")

    filtered = df[df[entity_col].isin(entities)]

    if year and "fiscal_year" in filtered.columns:
        filtered = filtered[filtered["fiscal_year"] == year]

    # Include entity_col, fiscal_year (if exists), and selected metrics
    cols = [entity_col]
    if "fiscal_year" in filtered.columns:
        cols.append("fiscal_year")
    cols.extend([m for m in metrics if m in filtered.columns])

    result = filtered[cols].drop_duplicates()
    return result


def format_comparison_table(data: Dict[str, Dict[str, Any]]) -> "pd.DataFrame":
    """Format comparison data as table.

    Args:
        data: Dictionary mapping entity names to metric dictionaries

    Returns:
        DataFrame with entities as index and metrics as columns
    """
    if pd is None:
        raise ImportError("pandas required")
    return pd.DataFrame(data).T


def create_comparison_chart(
    df: "pd.DataFrame",
    entity_col: str,
    metric: str,
    title: str = ""
) -> Any:
    """Create comparison bar chart.

    Args:
        df: DataFrame with comparison data
        entity_col: Column containing entity identifiers
        metric: Metric column to visualize
        title: Chart title (optional)

    Returns:
        Plotly figure object
    """
    if px is None:
        raise ImportError("plotly required")

    fig = px.bar(
        df,
        x=entity_col,
        y=metric,
        title=title or f"{metric.replace('_', ' ').title()} Comparison",
        color=entity_col,
        color_discrete_sequence=["#D4A84B", "#8B7355", "#FFD700"]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E8E8E8"),
        showlegend=False,
        xaxis=dict(
            title="",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.1)"
        ),
    )

    return fig


def _format_metric_value(value: Any) -> str:
    """Format a metric value for display.

    Args:
        value: Numeric value to format

    Returns:
        Formatted string
    """
    if pd is not None and pd.isna(value):
        return "N/A"
    if isinstance(value, (int, float)):
        if abs(value) >= 1_000_000_000:
            return f"{value/1_000_000_000:,.2f}B"
        elif abs(value) >= 1_000_000:
            return f"{value/1_000_000:,.2f}M"
        elif abs(value) >= 1_000:
            return f"{value/1_000:,.2f}K"
        else:
            return f"{value:,.2f}"
    return str(value)


def render_comparison_mode(df: "pd.DataFrame") -> None:
    """Render comparison mode interface.

    Args:
        df: DataFrame containing financial data to compare
    """
    if st is None:
        raise RuntimeError("Streamlit required")

    st.subheader("Compare Companies")

    if "company_name" not in df.columns:
        st.warning("Comparison requires company_name column")
        return

    companies = sorted(df["company_name"].unique().tolist())

    if len(companies) < 2:
        st.info("At least 2 companies needed for comparison")
        return

    col1, col2 = st.columns(2)
    with col1:
        company_a = st.selectbox(
            "Company A",
            options=companies,
            key="compare_a"
        )
    with col2:
        # Filter out selected company A from options
        other_companies = [c for c in companies if c != company_a]
        company_b = st.selectbox(
            "Company B",
            options=other_companies,
            key="compare_b"
        )

    metrics = get_comparison_metrics(df)

    if not metrics:
        st.warning("No numeric metrics available for comparison")
        return

    default_metrics = metrics[:3] if len(metrics) >= 3 else metrics
    selected_metrics = st.multiselect(
        "Metrics to Compare",
        options=metrics,
        default=default_metrics,
        max_selections=5,
        help="Select up to 5 metrics to compare"
    )

    # Year filter if available
    year = None
    if "fiscal_year" in df.columns:
        years = sorted(df["fiscal_year"].unique().tolist(), reverse=True)
        year = st.selectbox("Fiscal Year", options=years)

    if st.button("Compare", type="primary", width="stretch"):
        if not selected_metrics:
            st.warning("Select at least one metric")
            return

        comparison_df = compare_entities(
            df,
            entity_col="company_name",
            entities=[company_a, company_b],
            metrics=selected_metrics,
            year=year
        )

        if len(comparison_df) == 0:
            st.warning("No data available for selected companies and year")
            return

        # Display side-by-side metrics
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### {company_a}")
            a_data = comparison_df[comparison_df["company_name"] == company_a]
            for metric in selected_metrics:
                if metric in a_data.columns and len(a_data) > 0:
                    value = a_data[metric].iloc[0]
                    formatted = _format_metric_value(value)
                    st.metric(
                        metric.replace("_", " ").title(),
                        formatted
                    )

        with col2:
            st.markdown(f"### {company_b}")
            b_data = comparison_df[comparison_df["company_name"] == company_b]
            for metric in selected_metrics:
                if metric in b_data.columns and len(b_data) > 0:
                    value = b_data[metric].iloc[0]
                    formatted = _format_metric_value(value)
                    # Calculate delta if both values exist
                    delta = None
                    delta_color = "normal"
                    if len(a_data) > 0 and metric in a_data.columns:
                        a_val = a_data[metric].iloc[0]
                        if a_val != 0 and not pd.isna(a_val) and not pd.isna(value):
                            pct_diff = ((value - a_val) / abs(a_val)) * 100
                            delta = f"{pct_diff:+.1f}%"
                    st.metric(
                        metric.replace("_", " ").title(),
                        formatted,
                        delta=delta,
                        delta_color=delta_color
                    )

        # Show comparison charts
        if len(comparison_df) > 0 and selected_metrics and px is not None:
            st.markdown("---")
            st.markdown("### Visual Comparison")

            # Display up to 2 charts
            for metric in selected_metrics[:2]:
                fig = create_comparison_chart(
                    comparison_df,
                    entity_col="company_name",
                    metric=metric
                )
                st.plotly_chart(fig, width="stretch")
