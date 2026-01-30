"""Chart Generator for Ra'd AI.

Provides intelligent chart generation based on user queries and data context.
Integrates with PandasAI responses to enhance visualizations for financial data.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import re

logger = logging.getLogger(__name__)

# Import with graceful fallback
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
    pd = None

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

try:
    from components.visualizations.financial_charts import (
        create_income_statement_waterfall,
        create_balance_sheet_composition,
        create_ratio_radar_chart,
        create_ratio_comparison_bars,
        create_multi_year_trend,
        create_yoy_comparison_chart,
        create_sector_sunburst,
        create_sector_performance_heatmap,
        create_risk_return_scatter,
        create_financial_dashboard,
        recommend_chart,
        FINANCIAL_COLORS,
    )
    HAS_FINANCIAL_CHARTS = True
except ImportError:
    HAS_FINANCIAL_CHARTS = False


# Chart type keywords for detection
CHART_KEYWORDS = {
    "waterfall": ["waterfall", "income statement breakdown", "profit breakdown", "revenue to profit"],
    "balance_sheet": ["balance sheet", "assets liabilities", "asset composition", "financial position"],
    "radar": ["radar", "ratio profile", "financial health", "company profile"],
    "bar_comparison": ["compare", "comparison", "vs", "versus", "top companies", "ranking"],
    "trend": ["trend", "over time", "historical", "growth", "multi-year", "timeline"],
    "yoy": ["year over year", "yoy", "annual comparison", "yearly change"],
    "sunburst": ["sunburst", "market composition", "sector breakdown", "hierarchical"],
    "heatmap": ["heatmap", "sector performance", "correlation", "matrix"],
    "scatter": ["scatter", "risk return", "quadrant", "distribution"],
    "dashboard": ["dashboard", "overview", "summary", "kpi", "metrics"],
    "pie": ["pie", "distribution", "share", "proportion"],
    "line": ["line", "series", "progression"],
}

# Metric mappings for chart generation
INCOME_STATEMENT_METRICS = [
    "revenue", "cost_of_sales", "gross_profit", "operating_expenses",
    "operating_profit", "other_income", "interest_expense", "tax_expense", "net_profit"
]

BALANCE_SHEET_METRICS = [
    "total_assets", "current_assets", "non_current_assets",
    "total_liabilities", "current_liabilities", "non_current_liabilities",
    "total_equity"
]

RATIO_METRICS = [
    "roe", "roa", "net_margin", "gross_margin", "operating_margin",
    "current_ratio", "quick_ratio", "debt_to_equity", "debt_to_assets",
    "asset_turnover", "inventory_turnover"
]


def detect_chart_intent(query: str) -> Dict[str, Any]:
    """Detect if the user wants a chart and what type.

    Args:
        query: User's natural language query

    Returns:
        Dictionary with chart detection results
    """
    query_lower = query.lower()

    result = {
        "wants_chart": False,
        "chart_type": None,
        "confidence": 0.0,
        "keywords_matched": [],
        "suggested_function": None,
    }

    # Check for explicit chart requests
    explicit_chart_words = ["chart", "graph", "plot", "visualize", "visualization", "show me a", "display"]
    has_explicit_request = any(word in query_lower for word in explicit_chart_words)

    # Check for chart type keywords
    for chart_type, keywords in CHART_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in query_lower]
        if matched:
            result["keywords_matched"].extend(matched)
            if result["chart_type"] is None or len(matched) > len(result.get("best_match", [])):
                result["chart_type"] = chart_type
                result["best_match"] = matched

    # Calculate confidence
    if has_explicit_request and result["chart_type"]:
        result["confidence"] = 0.9
        result["wants_chart"] = True
    elif has_explicit_request:
        result["confidence"] = 0.7
        result["wants_chart"] = True
        result["chart_type"] = "auto"  # Let system decide
    elif result["chart_type"]:
        result["confidence"] = 0.5
        result["wants_chart"] = True

    # Map chart type to function
    function_map = {
        "waterfall": "create_income_statement_waterfall",
        "balance_sheet": "create_balance_sheet_composition",
        "radar": "create_ratio_radar_chart",
        "bar_comparison": "create_ratio_comparison_bars",
        "trend": "create_multi_year_trend",
        "yoy": "create_yoy_comparison_chart",
        "sunburst": "create_sector_sunburst",
        "heatmap": "create_sector_performance_heatmap",
        "scatter": "create_risk_return_scatter",
        "dashboard": "create_financial_dashboard",
    }

    if result["chart_type"] in function_map:
        result["suggested_function"] = function_map[result["chart_type"]]

    return result


def extract_chart_parameters(query: str, df: "pd.DataFrame" = None) -> Dict[str, Any]:
    """Extract chart parameters from query and data.

    Args:
        query: User's query
        df: Optional DataFrame for context

    Returns:
        Dictionary of extracted parameters
    """
    query_lower = query.lower()
    params = {}

    # Extract company names if mentioned
    if df is not None and HAS_PANDAS and "company_name" in df.columns:
        companies = df["company_name"].unique().tolist()
        mentioned_companies = []
        for company in companies:
            if company.lower() in query_lower or any(word in query_lower for word in company.lower().split()[:2]):
                mentioned_companies.append(company)
        if mentioned_companies:
            params["companies"] = mentioned_companies

    # Extract years
    year_pattern = r'\b(20\d{2})\b'
    years = re.findall(year_pattern, query)
    if years:
        params["years"] = [int(y) for y in years]

    # Extract sectors
    sectors = ["banks", "petrochemicals", "retail", "real estate", "telecom",
               "healthcare", "insurance", "energy", "materials", "utilities"]
    mentioned_sectors = [s.title() for s in sectors if s in query_lower]
    if mentioned_sectors:
        params["sectors"] = mentioned_sectors

    # Extract metrics
    metrics = []
    metric_keywords = {
        "revenue": ["revenue", "sales", "top line"],
        "net_profit": ["net profit", "net income", "bottom line", "earnings"],
        "gross_profit": ["gross profit", "gross margin"],
        "roe": ["roe", "return on equity"],
        "roa": ["roa", "return on assets"],
        "debt_to_equity": ["debt to equity", "leverage", "d/e"],
    }
    for metric, keywords in metric_keywords.items():
        if any(kw in query_lower for kw in keywords):
            metrics.append(metric)
    if metrics:
        params["metrics"] = metrics

    # Extract top N
    top_pattern = r'top\s+(\d+)'
    top_match = re.search(top_pattern, query_lower)
    if top_match:
        params["top_n"] = int(top_match.group(1))

    return params


def generate_chart_from_data(
    df: "pd.DataFrame",
    chart_type: str,
    params: Dict[str, Any] = None
) -> Optional[Any]:
    """Generate a chart from DataFrame based on detected type.

    Args:
        df: DataFrame with financial data
        chart_type: Type of chart to generate
        params: Additional parameters

    Returns:
        Plotly figure or None
    """
    if not HAS_FINANCIAL_CHARTS or not HAS_PANDAS:
        return None

    params = params or {}

    try:
        if chart_type == "waterfall":
            # Get company data for waterfall
            company = params.get("companies", [None])[0]
            if company:
                company_df = df[df["company_name"] == company].iloc[0]
            else:
                company_df = df.iloc[0]

            return create_income_statement_waterfall(
                revenue=company_df.get("revenue", 0),
                cost_of_sales=company_df.get("cost_of_sales", 0),
                gross_profit=company_df.get("gross_profit", 0),
                operating_expenses=company_df.get("operating_expenses", 0),
                operating_profit=company_df.get("operating_profit", 0),
                other_income=company_df.get("other_income", 0),
                interest_expense=company_df.get("interest_expense", 0),
                tax_expense=company_df.get("tax_expense", 0),
                net_profit=company_df.get("net_profit", 0),
                company_name=company or company_df.get("company_name", ""),
                fiscal_year=company_df.get("fiscal_year"),
            )

        elif chart_type == "balance_sheet":
            company = params.get("companies", [None])[0]
            if company:
                company_df = df[df["company_name"] == company].iloc[0]
            else:
                company_df = df.iloc[0]

            return create_balance_sheet_composition(
                total_assets=company_df.get("total_assets", 0),
                current_assets=company_df.get("current_assets", 0),
                non_current_assets=company_df.get("total_assets", 0) - company_df.get("current_assets", 0),
                total_liabilities=company_df.get("total_liabilities", 0),
                current_liabilities=company_df.get("current_liabilities", 0),
                non_current_liabilities=company_df.get("total_liabilities", 0) - company_df.get("current_liabilities", 0),
                total_equity=company_df.get("total_equity", 0),
                company_name=company or company_df.get("company_name", ""),
                fiscal_year=company_df.get("fiscal_year"),
            )

        elif chart_type == "radar":
            company = params.get("companies", [None])[0]
            if company:
                company_df = df[df["company_name"] == company].iloc[0]
            else:
                company_df = df.iloc[0]

            ratios = {}
            for metric in RATIO_METRICS:
                if metric in company_df.index or metric in df.columns:
                    val = company_df.get(metric, 0)
                    if val is not None and val == val:  # Check for NaN
                        ratios[metric.upper().replace("_", " ")] = float(val)

            if ratios:
                return create_ratio_radar_chart(
                    ratios=ratios,
                    company_name=company or company_df.get("company_name", ""),
                )

        elif chart_type == "trend":
            company = params.get("companies", [None])[0]
            metrics = params.get("metrics", ["revenue", "net_profit"])

            if company:
                return create_multi_year_trend(
                    df=df,
                    company_name=company,
                    metrics=metrics,
                )

        elif chart_type == "yoy":
            years = params.get("years", [])
            metric = params.get("metrics", ["revenue"])[0]
            top_n = params.get("top_n", 10)

            if len(years) >= 2:
                return create_yoy_comparison_chart(
                    df=df,
                    metric=metric,
                    year1=min(years),
                    year2=max(years),
                    top_n=top_n,
                )

        elif chart_type == "sunburst":
            metric = params.get("metrics", ["revenue"])[0] if params.get("metrics") else "revenue"
            if metric in df.columns:
                return create_sector_sunburst(
                    df=df,
                    value_column=metric,
                )

        elif chart_type == "heatmap":
            metrics = params.get("metrics", RATIO_METRICS[:6])
            available_metrics = [m for m in metrics if m in df.columns]
            if available_metrics:
                return create_sector_performance_heatmap(
                    df=df,
                    metrics=available_metrics,
                )

        elif chart_type == "scatter":
            return create_risk_return_scatter(
                df=df,
                return_column="roe" if "roe" in df.columns else "net_margin",
                risk_column="debt_to_equity" if "debt_to_equity" in df.columns else "debt_to_assets",
            )

        elif chart_type == "dashboard":
            company = params.get("companies", [None])[0]
            if company:
                company_df = df[df["company_name"] == company].iloc[0]
            else:
                company_df = df.iloc[0]

            company_data = {col: company_df.get(col) for col in df.columns}
            return create_financial_dashboard(
                company_data=company_data,
                company_name=company or company_df.get("company_name", ""),
                fiscal_year=company_df.get("fiscal_year"),
            )

    except Exception as e:
        logger.error(f"Error generating {chart_type} chart: {e}")
        return None

    return None


def render_enhanced_chart(
    fig: Any,
    title: str = None,
    height: int = 500
) -> None:
    """Render a Plotly figure in Streamlit with enhancements.

    Args:
        fig: Plotly figure object
        title: Optional title override
        height: Chart height
    """
    if not HAS_STREAMLIT or fig is None:
        return

    try:
        import plotly.io as pio

        # Update layout if title provided
        if title:
            fig.update_layout(title_text=title)

        # Render with Streamlit
        st.plotly_chart(fig, use_container_width=True, height=height)

    except Exception as e:
        logger.error(f"Error rendering chart: {e}")
        st.error(f"Could not render chart: {e}")


def get_chart_suggestions(df: "pd.DataFrame") -> List[Dict[str, str]]:
    """Get suggested charts based on available data.

    Args:
        df: DataFrame to analyze

    Returns:
        List of chart suggestions with descriptions
    """
    suggestions = []

    if not HAS_PANDAS or df is None:
        return suggestions

    columns = set(df.columns)

    # Check for income statement data
    income_cols = {"revenue", "net_profit", "gross_profit", "operating_profit"}
    if income_cols.intersection(columns):
        suggestions.append({
            "type": "waterfall",
            "title": "Income Statement Waterfall",
            "description": "See how revenue flows to net profit",
            "query": "Show income statement waterfall for [company]"
        })

    # Check for balance sheet data
    balance_cols = {"total_assets", "total_liabilities", "total_equity"}
    if balance_cols.intersection(columns):
        suggestions.append({
            "type": "balance_sheet",
            "title": "Balance Sheet Composition",
            "description": "View assets, liabilities, and equity breakdown",
            "query": "Show balance sheet composition for [company]"
        })

    # Check for ratio data
    ratio_cols = {"roe", "roa", "current_ratio", "debt_to_equity"}
    if ratio_cols.intersection(columns):
        suggestions.append({
            "type": "radar",
            "title": "Financial Ratio Profile",
            "description": "Compare ratios in a radar chart",
            "query": "Show ratio radar chart for [company]"
        })

    # Check for multi-year data
    if "fiscal_year" in columns and df["fiscal_year"].nunique() > 1:
        suggestions.append({
            "type": "trend",
            "title": "Multi-Year Trend",
            "description": "Track financial metrics over time",
            "query": "Show revenue trend for [company]"
        })
        suggestions.append({
            "type": "yoy",
            "title": "Year-over-Year Comparison",
            "description": "Compare metrics between years",
            "query": "Compare revenue 2023 vs 2024"
        })

    # Check for sector data
    if "sector" in columns:
        suggestions.append({
            "type": "sunburst",
            "title": "Sector Composition",
            "description": "Hierarchical view of market by sector",
            "query": "Show sector sunburst by revenue"
        })
        suggestions.append({
            "type": "heatmap",
            "title": "Sector Performance Heatmap",
            "description": "Compare sector performance across metrics",
            "query": "Show sector performance heatmap"
        })

    # Risk-return analysis
    if {"roe", "debt_to_equity"}.intersection(columns) or {"roa", "debt_to_assets"}.intersection(columns):
        suggestions.append({
            "type": "scatter",
            "title": "Risk-Return Analysis",
            "description": "Plot companies by risk and return metrics",
            "query": "Show risk-return scatter plot"
        })

    # Dashboard suggestion
    suggestions.append({
        "type": "dashboard",
        "title": "Financial Dashboard",
        "description": "Overview of key financial metrics",
        "query": "Show financial dashboard for [company]"
    })

    return suggestions


# Export key functions
__all__ = [
    "detect_chart_intent",
    "extract_chart_parameters",
    "generate_chart_from_data",
    "render_enhanced_chart",
    "get_chart_suggestions",
    "CHART_KEYWORDS",
]
