"""
Valuation Dashboard Component
=============================
Live stock prices and valuation metrics from PostgreSQL database.
Data sourced from Yahoo Finance via yfinance library.
"""

import streamlit as st
import pandas as pd
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def get_valuation_data() -> Optional[pd.DataFrame]:
    """Fetch valuation metrics from PostgreSQL database."""
    try:
        from utils.db_config import get_db_config, check_db_connection

        # Check connection first
        status = check_db_connection()
        if not status.get("connected"):
            logger.warning(f"Database not connected: {status.get('error')}")
            return None

        if not status.get("stock_prices_table"):
            logger.warning("Stock prices table does not exist")
            return None

        import psycopg2
        config = get_db_config()
        schema = config["schema"]

        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            connect_timeout=5,
        )

        query = f"""
            SELECT
                ticker, company_name, price, price_date,
                market_cap_billions as mkt_cap_B,
                pe_ratio as P_E,
                ROUND(dividend_yield_pct::numeric, 2) as div_yield_pct,
                ROUND(price_to_book::numeric, 2) as P_B,
                ROUND(beta::numeric, 2) as beta,
                fifty_two_week_high as high_52w,
                fifty_two_week_low as low_52w,
                valuation_category,
                market_cap_category
            FROM {schema}.valuation_metrics
            ORDER BY market_cap_billions DESC NULLS LAST
        """

        df = pd.read_sql(query, conn)
        conn.close()
        return df

    except ImportError:
        logger.error("psycopg2 not installed")
        return None
    except Exception as e:
        logger.error(f"Error fetching valuation data: {e}")
        return None


def get_stock_price_history(ticker: str, days: int = 30) -> Optional[pd.DataFrame]:
    """Get price history for a specific ticker."""
    try:
        from utils.db_config import get_db_config
        import psycopg2

        config = get_db_config()
        schema = config["schema"]

        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )

        query = f"""
            SELECT date, close_price, volume
            FROM {schema}.stock_prices
            WHERE ticker = %s
            ORDER BY date DESC
            LIMIT %s
        """

        df = pd.read_sql(query, conn, params=(ticker, days))
        conn.close()
        return df.sort_values('date') if len(df) > 0 else None

    except Exception as e:
        logger.error(f"Error fetching price history: {e}")
        return None


def render_valuation_dashboard():
    """Render the valuation dashboard with live stock data."""
    st.subheader("Live Valuation Metrics")
    st.caption("Data from Yahoo Finance | Updated via PostgreSQL")

    # Try to fetch data
    val_df = get_valuation_data()

    if val_df is None or len(val_df) == 0:
        st.warning("No valuation data available.")
        st.info("""
        **Setup Required:**
        1. Ensure PostgreSQL is running with the TASI schema
        2. Run the schema setup: `python scripts/setup_stock_prices_pg.py`
        3. Populate stock prices: `python scripts/batch_price_update_pg.py 1 --days 5`
        """)

        # Show database connection status
        try:
            from utils.db_config import check_db_connection
            status = check_db_connection()

            with st.expander("Database Connection Status"):
                if status.get("connected"):
                    st.success(f"Connected to: {status.get('host')}/{status.get('database')}")
                    st.write(f"Schema exists: {status.get('schema_exists')}")
                    st.write(f"Stock prices table: {status.get('stock_prices_table')}")
                else:
                    st.error(f"Not connected: {status.get('error')}")
        except ImportError:
            st.error("psycopg2 not installed. Run: `pip install psycopg2-binary`")

        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Stocks Tracked", len(val_df))
    with col2:
        avg_pe = val_df[val_df['p_e'] > 0]['p_e'].mean() if 'p_e' in val_df.columns else 0
        st.metric("Avg P/E Ratio", f"{avg_pe:.1f}" if pd.notna(avg_pe) else "N/A")
    with col3:
        avg_div = val_df[val_df['div_yield_pct'] > 0]['div_yield_pct'].mean() if 'div_yield_pct' in val_df.columns else 0
        st.metric("Avg Dividend Yield", f"{avg_div:.2f}%" if pd.notna(avg_div) else "N/A")
    with col4:
        total_mkt_cap = val_df['mkt_cap_b'].sum() if 'mkt_cap_b' in val_df.columns else 0
        st.metric("Total Market Cap", f"{total_mkt_cap:,.0f}B SAR" if pd.notna(total_mkt_cap) else "N/A")

    st.divider()

    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        val_categories = ["All"] + sorted(val_df['valuation_category'].dropna().unique().tolist())
        val_filter = st.selectbox(
            "Valuation Category",
            val_categories,
            key="val_filter"
        )
    with col2:
        cap_categories = ["All"] + sorted(val_df['market_cap_category'].dropna().unique().tolist())
        cap_filter = st.selectbox(
            "Market Cap Category",
            cap_categories,
            key="cap_filter"
        )
    with col3:
        sort_by = st.selectbox(
            "Sort By",
            ["Market Cap", "P/E Ratio", "Dividend Yield", "Price"],
            key="sort_by"
        )

    # Apply filters
    filtered_df = val_df.copy()
    if val_filter != "All":
        filtered_df = filtered_df[filtered_df['valuation_category'] == val_filter]
    if cap_filter != "All":
        filtered_df = filtered_df[filtered_df['market_cap_category'] == cap_filter]

    # Apply sorting
    sort_cols = {
        "Market Cap": ("mkt_cap_b", False),
        "P/E Ratio": ("p_e", True),
        "Dividend Yield": ("div_yield_pct", False),
        "Price": ("price", False)
    }
    sort_col, ascending = sort_cols[sort_by]
    if sort_col in filtered_df.columns:
        filtered_df = filtered_df.sort_values(sort_col, ascending=ascending, na_position='last')

    # Display table with proper column config
    st.dataframe(
        filtered_df,
        hide_index=True,
        column_config={
            "ticker": st.column_config.TextColumn("Ticker", width="small"),
            "company_name": st.column_config.TextColumn("Company", width="medium"),
            "price": st.column_config.NumberColumn("Price (SAR)", format="%.2f"),
            "price_date": st.column_config.DateColumn("Date", format="YYYY-MM-DD"),
            "mkt_cap_b": st.column_config.NumberColumn("Mkt Cap (B)", format="%.1f"),
            "p_e": st.column_config.NumberColumn("P/E", format="%.1f"),
            "div_yield_pct": st.column_config.NumberColumn("Div Yield %", format="%.2f"),
            "p_b": st.column_config.NumberColumn("P/B", format="%.2f"),
            "beta": st.column_config.NumberColumn("Beta", format="%.2f"),
            "high_52w": st.column_config.NumberColumn("52w High", format="%.2f"),
            "low_52w": st.column_config.NumberColumn("52w Low", format="%.2f"),
        },
        use_container_width=True
    )

    # Download button
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Valuation Data (CSV)",
        data=csv,
        file_name="tasi_valuation_metrics.csv",
        mime="text/csv"
    )

    # Quick screeners
    st.divider()
    st.subheader("Quick Screeners")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.expander("Value Stocks (P/E < 15)"):
            value_stocks = val_df[(val_df['p_e'] > 0) & (val_df['p_e'] < 15)].head(10)
            if len(value_stocks) > 0:
                st.dataframe(
                    value_stocks[['ticker', 'company_name', 'p_e', 'div_yield_pct']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No stocks match this criteria")

    with col2:
        with st.expander("High Dividend (> 4%)"):
            high_div = val_df[val_df['div_yield_pct'] > 4].head(10)
            if len(high_div) > 0:
                st.dataframe(
                    high_div[['ticker', 'company_name', 'div_yield_pct', 'p_e']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No stocks match this criteria")

    with col3:
        with st.expander("Large Caps (> 50B SAR)"):
            large_caps = val_df[val_df['mkt_cap_b'] > 50].head(10)
            if len(large_caps) > 0:
                st.dataframe(
                    large_caps[['ticker', 'company_name', 'mkt_cap_b', 'p_e']],
                    hide_index=True,
                    use_container_width=True
                )
            else:
                st.info("No stocks match this criteria")
