#!/usr/bin/env python3
"""
Batch Stock Price Updater for PostgreSQL
=========================================
Processes a specific batch of tickers with concurrent-safe PostgreSQL writes.

Usage: python scripts/batch_price_update_pg.py <batch_number> [--days N]
  batch_number: 1-4
  --days N: days of price history (default: 5)

Environment variables:
    DATABASE_URL or POSTGRES_* variables for connection
"""

import sys
import os
import time
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# All 303 TASI tickers split into 4 batches (~76 each)
TICKER_BATCHES = [
    # Batch 1: 76 tickers (0-2100)
    [0, 1010, 1020, 1030, 1050, 1060, 1080, 1111, 1120, 1140, 1150, 1180, 1182, 1183,
     1201, 1202, 1210, 1211, 1212, 1213, 1214, 1301, 1302, 1303, 1304, 1320, 1321,
     1322, 1323, 1810, 1820, 1830, 1831, 1832, 1833, 1834, 2001, 2010, 2020, 2030,
     2040, 2050, 2060, 2070, 2080, 2081, 2082, 2083, 2084, 2090, 2100, 2110, 2120,
     2130, 2140, 2150, 2170, 2180, 2190, 2200, 2210, 2222, 2223, 2230, 2240, 2250,
     2270, 2280, 2281, 2282, 2283, 2285, 2286, 2287, 2290, 2300],

    # Batch 2: 76 tickers (2310-4082)
    [2310, 2320, 2330, 2340, 2350, 2360, 2370, 2380, 2381, 2382, 3002, 3003, 3005,
     3007, 3008, 3010, 3020, 3030, 3040, 3050, 3060, 3080, 3090, 3091, 3092, 4001,
     4002, 4003, 4004, 4005, 4006, 4007, 4008, 4009, 4011, 4012, 4013, 4014, 4015,
     4016, 4017, 4018, 4019, 4020, 4021, 4030, 4031, 4040, 4050, 4051, 4061, 4070,
     4071, 4072, 4080, 4081, 4082, 4083, 4084, 4090, 4100, 4110, 4130, 4140, 4142,
     4145, 4146, 4150, 4160, 4161, 4162, 4163, 4164, 4165, 4170, 4180],

    # Batch 3: 76 tickers (4190-7203)
    [4190, 4191, 4192, 4193, 4200, 4210, 4220, 4230, 4240, 4250, 4260, 4261, 4262,
     4263, 4264, 4265, 4270, 4280, 4290, 4291, 4292, 4300, 4310, 4320, 4321, 4322,
     4323, 4324, 4325, 4326, 5110, 6001, 6002, 6004, 6010, 6012, 6014, 6015, 6017,
     6018, 6020, 6040, 6050, 6060, 6070, 6090, 7010, 7020, 7030, 7040, 7200, 7201,
     7202, 7203, 7204, 7211, 8010, 8012, 8020, 8030, 8040, 8050, 8060, 8070, 8100,
     8120, 8150, 8160, 8170, 8180, 8190, 8200, 8230, 8240, 8250, 8260],

    # Batch 4: 75 tickers (8280-9649)
    [8280, 8300, 8310, 8311, 8313, 9506, 9511, 9512, 9513, 9514, 9517, 9518, 9519,
     9521, 9524, 9526, 9528, 9530, 9531, 9534, 9537, 9540, 9541, 9543, 9545, 9547,
     9552, 9555, 9556, 9557, 9559, 9564, 9565, 9566, 9568, 9569, 9570, 9572, 9575,
     9578, 9583, 9589, 9590, 9591, 9594, 9595, 9596, 9598, 9600, 9601, 9603, 9604,
     9606, 9607, 9609, 9611, 9612, 9615, 9617, 9618, 9620, 9621, 9622, 9623, 9624,
     9625, 9626, 9627, 9630, 9631, 9633, 9634, 9636, 9639, 9649]
]


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


def update_prices_batch(batch_num: int, days: int = 5):
    """Update prices for a specific batch of tickers using PostgreSQL."""

    if batch_num < 1 or batch_num > len(TICKER_BATCHES):
        print(f"Error: batch_num must be 1-{len(TICKER_BATCHES)}")
        return {"success": 0, "failed": 0, "errors": ["Invalid batch number"]}

    tickers = TICKER_BATCHES[batch_num - 1]

    print(f"{'='*60}")
    print(f"BATCH {batch_num} - PostgreSQL Stock Price Update")
    print(f"{'='*60}")
    print(f"Processing {len(tickers)} tickers")
    print(f"Range: {tickers[0]} to {tickers[-1]}")
    print(f"Days of history: {days}")
    print()

    # Import dependencies
    try:
        import yfinance as yf
    except ImportError:
        print("Installing yfinance...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance", "-q"])
        import yfinance as yf

    try:
        import psycopg2
    except ImportError:
        print("Installing psycopg2-binary...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"])
        import psycopg2

    config = get_db_config()
    schema = config["schema"]

    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )
        conn.autocommit = False
        cur = conn.cursor()
        print(f"Connected to PostgreSQL: {config['host']}:{config['port']}/{config['database']}")
    except Exception as e:
        print(f"Database connection error: {e}")
        return {"success": 0, "failed": len(tickers), "errors": [str(e)]}

    stats = {"success": 0, "failed": 0, "prices_inserted": 0, "errors": []}
    start_time = time.time()

    for i, ticker in enumerate(tickers, 1):
        ticker_str = str(int(ticker)) if isinstance(ticker, float) else str(ticker)
        yf_ticker = f"{ticker_str}.SR"

        try:
            stock = yf.Ticker(yf_ticker)

            # Get historical prices
            hist = stock.history(period=f"{days}d")

            if len(hist) > 0:
                for date, row in hist.iterrows():
                    date_str = date.strftime('%Y-%m-%d')

                    # PostgreSQL UPSERT (INSERT ... ON CONFLICT)
                    cur.execute(f"""
                        INSERT INTO {schema}.stock_prices
                        (ticker, date, open_price, high_price, low_price, close_price, adj_close, volume, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (ticker, date) DO UPDATE SET
                            open_price = EXCLUDED.open_price,
                            high_price = EXCLUDED.high_price,
                            low_price = EXCLUDED.low_price,
                            close_price = EXCLUDED.close_price,
                            adj_close = EXCLUDED.adj_close,
                            volume = EXCLUDED.volume,
                            updated_at = CURRENT_TIMESTAMP
                    """, (
                        ticker_str, date_str,
                        float(row['Open']) if row['Open'] else None,
                        float(row['High']) if row['High'] else None,
                        float(row['Low']) if row['Low'] else None,
                        float(row['Close']) if row['Close'] else None,
                        float(row.get('Adj Close', row['Close'])) if row.get('Adj Close', row['Close']) else None,
                        int(row['Volume']) if row['Volume'] else None
                    ))
                    stats["prices_inserted"] += 1

                # Get stock info
                info = stock.info
                if info:
                    # Handle ex_dividend_date conversion
                    ex_div_date = None
                    if info.get('exDividendDate'):
                        try:
                            from datetime import datetime
                            ex_div_date = datetime.fromtimestamp(info['exDividendDate']).strftime('%Y-%m-%d')
                        except:
                            pass

                    cur.execute(f"""
                        INSERT INTO {schema}.stock_info
                        (ticker, company_name, currency, exchange, market_cap, shares_outstanding,
                         float_shares, book_value, price_to_book, trailing_pe, forward_pe,
                         dividend_yield, dividend_rate, ex_dividend_date, payout_ratio, beta,
                         fifty_two_week_high, fifty_two_week_low, fifty_day_average,
                         two_hundred_day_average, average_volume, average_volume_10days, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (ticker) DO UPDATE SET
                            company_name = EXCLUDED.company_name,
                            currency = EXCLUDED.currency,
                            exchange = EXCLUDED.exchange,
                            market_cap = EXCLUDED.market_cap,
                            shares_outstanding = EXCLUDED.shares_outstanding,
                            float_shares = EXCLUDED.float_shares,
                            book_value = EXCLUDED.book_value,
                            price_to_book = EXCLUDED.price_to_book,
                            trailing_pe = EXCLUDED.trailing_pe,
                            forward_pe = EXCLUDED.forward_pe,
                            dividend_yield = EXCLUDED.dividend_yield,
                            dividend_rate = EXCLUDED.dividend_rate,
                            ex_dividend_date = EXCLUDED.ex_dividend_date,
                            payout_ratio = EXCLUDED.payout_ratio,
                            beta = EXCLUDED.beta,
                            fifty_two_week_high = EXCLUDED.fifty_two_week_high,
                            fifty_two_week_low = EXCLUDED.fifty_two_week_low,
                            fifty_day_average = EXCLUDED.fifty_day_average,
                            two_hundred_day_average = EXCLUDED.two_hundred_day_average,
                            average_volume = EXCLUDED.average_volume,
                            average_volume_10days = EXCLUDED.average_volume_10days,
                            last_updated = CURRENT_TIMESTAMP
                    """, (
                        ticker_str,
                        info.get('longName', info.get('shortName', '')),
                        info.get('currency', 'SAR'),
                        info.get('exchange', 'SAU'),
                        info.get('marketCap'),
                        info.get('sharesOutstanding'),
                        info.get('floatShares'),
                        info.get('bookValue'),
                        info.get('priceToBook'),
                        info.get('trailingPE'),
                        info.get('forwardPE'),
                        info.get('dividendYield'),
                        info.get('dividendRate'),
                        ex_div_date,
                        info.get('payoutRatio'),
                        info.get('beta'),
                        info.get('fiftyTwoWeekHigh'),
                        info.get('fiftyTwoWeekLow'),
                        info.get('fiftyDayAverage'),
                        info.get('twoHundredDayAverage'),
                        info.get('averageVolume'),
                        info.get('averageVolume10days')
                    ))

                # Commit after each successful ticker
                conn.commit()
                stats["success"] += 1
                status = "OK"
            else:
                stats["failed"] += 1
                status = "NO DATA"
                stats["errors"].append(f"{ticker_str}: No price data")

        except Exception as e:
            # Rollback on error and continue
            conn.rollback()
            stats["failed"] += 1
            status = "ERROR"
            stats["errors"].append(f"{ticker_str}: {str(e)[:50]}")

        # Progress update every 10 tickers
        if i % 10 == 0 or i == len(tickers):
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 0
            eta = (len(tickers) - i) / rate if rate > 0 else 0
            print(f"[{i}/{len(tickers)}] {ticker_str}: {status} | {stats['success']} OK, {stats['failed']} failed | ETA: {eta:.0f}s")

    cur.close()
    conn.close()

    # Final summary
    elapsed = time.time() - start_time
    print()
    print(f"{'='*60}")
    print(f"BATCH {batch_num} COMPLETE")
    print(f"{'='*60}")
    print(f"Duration: {elapsed:.1f}s")
    print(f"Success: {stats['success']}/{len(tickers)} ({100*stats['success']/len(tickers):.1f}%)")
    print(f"Failed: {stats['failed']}")
    print(f"Prices inserted: {stats['prices_inserted']}")

    if stats["errors"]:
        print(f"\nErrors ({len(stats['errors'])}):")
        for err in stats["errors"][:10]:
            print(f"  - {err}")
        if len(stats["errors"]) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")

    return stats


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/batch_price_update_pg.py <batch_number> [--days N]")
        print("  batch_number: 1-4")
        print("  --days N: days of price history (default: 5)")
        sys.exit(1)

    batch_num = int(sys.argv[1])
    days = 5

    if "--days" in sys.argv:
        idx = sys.argv.index("--days")
        if idx + 1 < len(sys.argv):
            days = int(sys.argv[idx + 1])

    update_prices_batch(batch_num, days)
