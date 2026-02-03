#!/usr/bin/env python3
"""
Setup PostgreSQL schema for stock prices and valuation metrics.

This script creates the necessary tables and views for tracking
live stock prices from Yahoo Finance for TASI listed companies.

Usage:
    python scripts/setup_stock_prices_pg.py

Environment variables:
    DATABASE_URL or POSTGRES_* variables for connection
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_db_config():
    """Get database configuration from environment."""
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "database": os.getenv("POSTGRES_DB", "tasi_financials"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "schema": os.getenv("POSTGRES_SCHEMA", "tasi"),
    }


STOCK_PRICES_SCHEMA = """
-- Stock Prices Table
-- Stores daily OHLCV data from Yahoo Finance
CREATE TABLE IF NOT EXISTS {schema}.stock_prices (
    id SERIAL,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open_price NUMERIC(15,4),
    high_price NUMERIC(15,4),
    low_price NUMERIC(15,4),
    close_price NUMERIC(15,4),
    adj_close NUMERIC(15,4),
    volume BIGINT,
    currency VARCHAR(10) DEFAULT 'SAR',
    source VARCHAR(50) DEFAULT 'yfinance',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, date)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker ON {schema}.stock_prices(ticker);
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON {schema}.stock_prices(date DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_ticker_date ON {schema}.stock_prices(ticker, date DESC);

COMMENT ON TABLE {schema}.stock_prices IS
'Daily stock prices (OHLCV) from Yahoo Finance for TASI listed companies.
Data is fetched using yfinance with ticker format: XXXX.SR (e.g., 2222.SR for Aramco)';


-- Stock Info Table
-- Stores company stock information and valuation data
CREATE TABLE IF NOT EXISTS {schema}.stock_info (
    ticker VARCHAR(10) PRIMARY KEY,
    company_name VARCHAR(255),
    currency VARCHAR(10) DEFAULT 'SAR',
    exchange VARCHAR(50) DEFAULT 'SAU',
    market_cap NUMERIC(20,2),
    shares_outstanding NUMERIC(20,2),
    float_shares NUMERIC(20,2),
    book_value NUMERIC(15,4),
    price_to_book NUMERIC(10,4),
    trailing_pe NUMERIC(10,4),
    forward_pe NUMERIC(10,4),
    dividend_yield NUMERIC(10,6),
    dividend_rate NUMERIC(10,4),
    ex_dividend_date DATE,
    payout_ratio NUMERIC(10,4),
    beta NUMERIC(10,4),
    fifty_two_week_high NUMERIC(15,4),
    fifty_two_week_low NUMERIC(15,4),
    fifty_day_average NUMERIC(15,4),
    two_hundred_day_average NUMERIC(15,4),
    average_volume NUMERIC(20,2),
    average_volume_10days NUMERIC(20,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_stock_info_market_cap ON {schema}.stock_info(market_cap DESC);

COMMENT ON TABLE {schema}.stock_info IS
'Company stock information including market cap, P/E ratios, dividend yields, and technical indicators.
Data is fetched from Yahoo Finance using yfinance library.';


-- Latest Prices View
-- Most recent price for each ticker
CREATE OR REPLACE VIEW {schema}.latest_prices AS
SELECT
    sp.ticker,
    sp.date AS price_date,
    sp.open_price,
    sp.high_price,
    sp.low_price,
    sp.close_price,
    sp.adj_close,
    sp.volume,
    sp.currency,
    sp.source,
    sp.updated_at
FROM {schema}.stock_prices sp
INNER JOIN (
    SELECT ticker, MAX(date) AS max_date
    FROM {schema}.stock_prices
    GROUP BY ticker
) latest ON sp.ticker = latest.ticker AND sp.date = latest.max_date;

COMMENT ON VIEW {schema}.latest_prices IS
'Most recent stock price for each ticker. Use this for current price lookups.';


-- Valuation Metrics View
-- Combines stock prices with company info for valuation analysis
CREATE OR REPLACE VIEW {schema}.valuation_metrics AS
SELECT
    si.ticker,
    si.company_name,
    lp.close_price AS price,
    lp.price_date,
    -- Market Cap (in billions SAR)
    ROUND(si.market_cap / 1e9, 2) AS market_cap_billions,
    -- P/E Ratios
    si.trailing_pe AS pe_ratio,
    si.forward_pe,
    -- Dividend metrics (already in percentage from yfinance)
    ROUND(si.dividend_yield * 100, 2) AS dividend_yield_pct,
    si.dividend_rate,
    si.payout_ratio,
    -- Price metrics
    si.price_to_book,
    si.book_value,
    si.beta,
    -- 52-week range
    si.fifty_two_week_high,
    si.fifty_two_week_low,
    si.fifty_day_average,
    si.two_hundred_day_average,
    -- Volume
    si.average_volume,
    si.average_volume_10days,
    -- Valuation category based on P/E
    CASE
        WHEN si.trailing_pe IS NULL THEN 'Unknown'
        WHEN si.trailing_pe < 0 THEN 'Loss-making'
        WHEN si.trailing_pe < 10 THEN 'Value'
        WHEN si.trailing_pe < 20 THEN 'Fair'
        WHEN si.trailing_pe < 30 THEN 'Growth'
        ELSE 'Premium'
    END AS valuation_category,
    -- Market cap category
    CASE
        WHEN si.market_cap IS NULL THEN 'Unknown'
        WHEN si.market_cap >= 50e9 THEN 'Mega Cap'
        WHEN si.market_cap >= 10e9 THEN 'Large Cap'
        WHEN si.market_cap >= 2e9 THEN 'Mid Cap'
        WHEN si.market_cap >= 500e6 THEN 'Small Cap'
        ELSE 'Micro Cap'
    END AS market_cap_category,
    -- Last updated
    si.last_updated
FROM {schema}.stock_info si
LEFT JOIN {schema}.latest_prices lp ON si.ticker = lp.ticker;

COMMENT ON VIEW {schema}.valuation_metrics IS
'Comprehensive valuation metrics combining stock prices and company info.
Includes P/E ratios, dividend yields, market cap categories, and technical indicators.
dividend_yield_pct is already in percentage form (e.g., 5.12 = 5.12%)';


-- Price History Function (for charting)
CREATE OR REPLACE FUNCTION {schema}.get_price_history(
    p_ticker VARCHAR(10),
    p_days INTEGER DEFAULT 30
)
RETURNS TABLE (
    date DATE,
    close_price NUMERIC(15,4),
    volume BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT sp.date, sp.close_price, sp.volume
    FROM {schema}.stock_prices sp
    WHERE sp.ticker = p_ticker
    ORDER BY sp.date DESC
    LIMIT p_days;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION {schema}.get_price_history IS
'Get price history for a ticker. Returns date, close_price, volume.
Example: SELECT * FROM tasi.get_price_history(''2222'', 30)';
"""


def setup_stock_prices_schema():
    """Create stock prices tables and views in PostgreSQL."""
    config = get_db_config()

    logger.info("=" * 60)
    logger.info("SETTING UP STOCK PRICES SCHEMA")
    logger.info("=" * 60)
    logger.info(f"Host: {config['host']}")
    logger.info(f"Database: {config['database']}")
    logger.info(f"Schema: {config['schema']}")

    try:
        # Connect to database
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )
        conn.autocommit = False
        cursor = conn.cursor()

        logger.info("\n1. Creating schema if not exists...")
        cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
            sql.Identifier(config["schema"])
        ))

        logger.info("2. Creating tables and views...")
        schema_sql = STOCK_PRICES_SCHEMA.format(schema=config["schema"])

        # Split by semicolon and execute each statement
        statements = schema_sql.split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    cursor.execute(stmt + ';')
                except Exception as e:
                    logger.warning(f"   Statement warning: {e}")
                    conn.rollback()
                    continue

        conn.commit()

        # Verify tables
        logger.info("\n3. Verifying created objects...")
        cursor.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name IN ('stock_prices', 'stock_info')
            UNION ALL
            SELECT table_name, 'VIEW'
            FROM information_schema.views
            WHERE table_schema = %s
            AND table_name IN ('latest_prices', 'valuation_metrics')
            ORDER BY table_name
        """, (config["schema"], config["schema"]))

        results = cursor.fetchall()
        for name, obj_type in results:
            logger.info(f"   [{obj_type}] {name}")

        cursor.close()
        conn.close()

        logger.info("\n" + "=" * 60)
        logger.info("SCHEMA SETUP COMPLETE")
        logger.info("=" * 60)
        logger.info("\nTo populate stock prices, run:")
        logger.info("  python scripts/batch_price_update_pg.py 1 --days 5")
        logger.info("  python scripts/batch_price_update_pg.py 2 --days 5")
        logger.info("  ... (batches 1-4)")

        return True

    except Exception as e:
        logger.error(f"Error setting up schema: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_stock_prices_schema()
    sys.exit(0 if success else 1)
