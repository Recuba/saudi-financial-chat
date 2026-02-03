"""Database configuration utilities for Ra'd AI.

Provides PostgreSQL connection management with connection pooling for concurrent operations.
Supports both local PostgreSQL and Neon serverless databases.
"""

import os
import streamlit as st
from typing import Optional, Dict, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Default database configuration
DEFAULT_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "tasi_financials",
    "user": "postgres",
    "password": "postgres",
    "schema": "tasi",
}

# Connection pool (lazy initialized)
_connection_pool = None


def get_database_url() -> Optional[str]:
    """Get database URL from Streamlit secrets or environment.

    Priority:
    1. Streamlit secrets (DATABASE_URL)
    2. Environment variable (DATABASE_URL)
    3. Constructed from individual parameters
    """
    # Try Streamlit secrets first
    try:
        url = st.secrets.get("DATABASE_URL")
        if url:
            return url
    except Exception:
        pass

    # Try environment variable
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Construct from individual parameters
    try:
        host = st.secrets.get("POSTGRES_HOST", os.getenv("POSTGRES_HOST", DEFAULT_CONFIG["host"]))
        port = st.secrets.get("POSTGRES_PORT", os.getenv("POSTGRES_PORT", DEFAULT_CONFIG["port"]))
        database = st.secrets.get("POSTGRES_DB", os.getenv("POSTGRES_DB", DEFAULT_CONFIG["database"]))
        user = st.secrets.get("POSTGRES_USER", os.getenv("POSTGRES_USER", DEFAULT_CONFIG["user"]))
        password = st.secrets.get("POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", DEFAULT_CONFIG["password"]))

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    except Exception as e:
        logger.warning(f"Could not construct database URL: {e}")
        return None


def get_db_config() -> Dict[str, str]:
    """Get database configuration dictionary."""
    try:
        return {
            "host": st.secrets.get("POSTGRES_HOST", os.getenv("POSTGRES_HOST", DEFAULT_CONFIG["host"])),
            "port": st.secrets.get("POSTGRES_PORT", os.getenv("POSTGRES_PORT", DEFAULT_CONFIG["port"])),
            "database": st.secrets.get("POSTGRES_DB", os.getenv("POSTGRES_DB", DEFAULT_CONFIG["database"])),
            "user": st.secrets.get("POSTGRES_USER", os.getenv("POSTGRES_USER", DEFAULT_CONFIG["user"])),
            "password": st.secrets.get("POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", DEFAULT_CONFIG["password"])),
            "schema": st.secrets.get("POSTGRES_SCHEMA", os.getenv("POSTGRES_SCHEMA", DEFAULT_CONFIG["schema"])),
        }
    except Exception:
        return DEFAULT_CONFIG.copy()


def init_connection_pool(min_conn: int = 1, max_conn: int = 10):
    """Initialize the connection pool for concurrent database access.

    Args:
        min_conn: Minimum number of connections to maintain
        max_conn: Maximum number of connections allowed
    """
    global _connection_pool

    if _connection_pool is not None:
        return _connection_pool

    try:
        from psycopg2 import pool

        config = get_db_config()
        _connection_pool = pool.ThreadedConnectionPool(
            min_conn,
            max_conn,
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
        )
        logger.info(f"Connection pool initialized with {min_conn}-{max_conn} connections")
        return _connection_pool
    except ImportError:
        logger.error("psycopg2 not installed. Run: pip install psycopg2-binary")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize connection pool: {e}")
        return None


def get_connection():
    """Get a connection from the pool.

    Returns:
        A database connection from the pool
    """
    global _connection_pool

    if _connection_pool is None:
        init_connection_pool()

    if _connection_pool is None:
        raise RuntimeError("Database connection pool not available")

    return _connection_pool.getconn()


def release_connection(conn):
    """Release a connection back to the pool.

    Args:
        conn: The connection to release
    """
    global _connection_pool

    if _connection_pool is not None and conn is not None:
        _connection_pool.putconn(conn)


@contextmanager
def get_db_connection():
    """Context manager for database connections.

    Automatically handles connection acquisition and release.

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasi.companies")
    """
    conn = None
    try:
        conn = get_connection()
        yield conn
    finally:
        if conn is not None:
            release_connection(conn)


def execute_query(query: str, params: tuple = None) -> list:
    """Execute a SELECT query and return results.

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        List of result rows
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return results


def execute_query_df(query: str, params: tuple = None):
    """Execute a SELECT query and return results as DataFrame.

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        pandas DataFrame with results
    """
    import pandas as pd

    with get_db_connection() as conn:
        return pd.read_sql(query, conn, params=params)


def check_db_connection() -> Dict[str, Any]:
    """Check database connectivity and return status.

    Returns:
        Dictionary with 'connected' boolean and status information
    """
    try:
        import psycopg2

        config = get_db_config()
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            database=config["database"],
            user=config["user"],
            password=config["password"],
            connect_timeout=5,
        )

        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]

        # Check if schema exists
        cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name = %s)",
            (config["schema"],)
        )
        schema_exists = cursor.fetchone()[0]

        # Check if stock_prices table exists
        cursor.execute(
            """SELECT EXISTS(
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s AND table_name = 'stock_prices'
            )""",
            (config["schema"],)
        )
        stock_prices_exists = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "connected": True,
            "version": version,
            "schema_exists": schema_exists,
            "stock_prices_table": stock_prices_exists,
            "host": config["host"],
            "database": config["database"],
        }
    except ImportError:
        return {
            "connected": False,
            "error": "psycopg2 not installed",
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }


def close_all_connections():
    """Close all connections in the pool."""
    global _connection_pool

    if _connection_pool is not None:
        _connection_pool.closeall()
        _connection_pool = None
        logger.info("All database connections closed")
