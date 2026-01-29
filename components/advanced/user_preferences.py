"""
User Preferences Component.

Manages user preferences using cookies (via streamlit-cookies-controller).
Falls back to session state when cookies are not available.
"""

import streamlit as st
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from copy import deepcopy

# Check if cookies controller is available
try:
    from streamlit_cookies_controller import CookieController
    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False
    CookieController = None


# Default preferences schema
DEFAULT_PREFERENCES: Dict[str, Any] = {
    # Display preferences
    "theme": "light",  # light, dark, auto
    "language": "en",  # en, ar
    "sidebar_state": "expanded",  # expanded, collapsed

    # Data display preferences
    "rows_per_page": 25,
    "number_format": "standard",  # standard, compact, scientific
    "date_format": "YYYY-MM-DD",
    "decimal_places": 2,
    "show_thousands_separator": True,

    # Chart preferences
    "default_chart_type": "line",  # line, bar, area, scatter
    "chart_color_scheme": "default",  # default, colorblind, monochrome
    "chart_animation": True,
    "chart_height": 400,

    # Financial data preferences
    "default_currency": "SAR",
    "default_market": "TASI",
    "favorite_symbols": [],
    "watchlist": [],

    # Query preferences
    "auto_execute_queries": False,
    "query_timeout_seconds": 30,
    "max_result_rows": 1000,
    "save_query_history": True,

    # Notification preferences
    "show_notifications": True,
    "notification_sound": False,

    # Advanced preferences
    "developer_mode": False,
    "show_sql_queries": False,
    "enable_caching": True,
    "cache_ttl_minutes": 60,

    # Metadata
    "_version": "1.0.0",
    "_last_updated": None,
}

# Preference categories for UI organization
PREFERENCE_CATEGORIES = {
    "Display": ["theme", "language", "sidebar_state"],
    "Data Display": ["rows_per_page", "number_format", "date_format", "decimal_places", "show_thousands_separator"],
    "Charts": ["default_chart_type", "chart_color_scheme", "chart_animation", "chart_height"],
    "Financial Data": ["default_currency", "default_market", "favorite_symbols", "watchlist"],
    "Queries": ["auto_execute_queries", "query_timeout_seconds", "max_result_rows", "save_query_history"],
    "Notifications": ["show_notifications", "notification_sound"],
    "Advanced": ["developer_mode", "show_sql_queries", "enable_caching", "cache_ttl_minutes"],
}

COOKIE_NAME = "saudi_financial_chat_preferences"
COOKIE_EXPIRY_DAYS = 365


def _serialize_preferences(preferences: Dict[str, Any]) -> str:
    """Serialize preferences to JSON string."""
    # Update timestamp
    prefs = deepcopy(preferences)
    prefs["_last_updated"] = datetime.now().isoformat()
    return json.dumps(prefs)


def _deserialize_preferences(json_str: str) -> Dict[str, Any]:
    """Deserialize preferences from JSON string."""
    try:
        prefs = json.loads(json_str)
        return prefs
    except (json.JSONDecodeError, TypeError):
        return {}


def _get_cookie_controller() -> Optional[Any]:
    """Get the cookie controller instance."""
    if not COOKIES_AVAILABLE:
        return None

    try:
        controller = CookieController()
        return controller
    except Exception:
        return None


def _merge_with_defaults(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user preferences with defaults, filling in any missing keys."""
    merged = deepcopy(DEFAULT_PREFERENCES)

    for key, value in preferences.items():
        if key in merged:
            # Type check for safety
            if isinstance(merged[key], type(value)) or value is None:
                merged[key] = value
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = value

    return merged


def get_preferences() -> Dict[str, Any]:
    """
    Get user preferences from cookies or session state.

    Returns:
        Dictionary of user preferences merged with defaults
    """
    # Check session state first (fastest)
    if "user_preferences" in st.session_state:
        return st.session_state["user_preferences"]

    preferences = {}

    # Try to load from cookies
    controller = _get_cookie_controller()
    if controller is not None:
        try:
            cookie_value = controller.get(COOKIE_NAME)
            if cookie_value:
                preferences = _deserialize_preferences(cookie_value)
        except Exception:
            pass

    # Merge with defaults
    merged_prefs = _merge_with_defaults(preferences)

    # Store in session state for quick access
    st.session_state["user_preferences"] = merged_prefs

    return merged_prefs


def save_preferences(preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to cookies and session state.

    Args:
        preferences: Dictionary of preferences to save

    Returns:
        True if saved successfully, False otherwise
    """
    # Merge with defaults to ensure all keys exist
    merged_prefs = _merge_with_defaults(preferences)
    merged_prefs["_last_updated"] = datetime.now().isoformat()

    # Always save to session state
    st.session_state["user_preferences"] = merged_prefs

    # Try to save to cookies
    controller = _get_cookie_controller()
    if controller is not None:
        try:
            json_str = _serialize_preferences(merged_prefs)
            controller.set(
                COOKIE_NAME,
                json_str,
                max_age=COOKIE_EXPIRY_DAYS * 24 * 60 * 60  # Convert days to seconds
            )
            return True
        except Exception as e:
            st.warning(f"Could not save preferences to cookies: {str(e)}")
            return False

    # Session state save successful even if cookies failed
    return True


def get_preference(key: str, default: Any = None) -> Any:
    """
    Get a single preference value.

    Args:
        key: Preference key
        default: Default value if key not found

    Returns:
        Preference value
    """
    prefs = get_preferences()
    return prefs.get(key, default if default is not None else DEFAULT_PREFERENCES.get(key))


def set_preference(key: str, value: Any) -> bool:
    """
    Set a single preference value.

    Args:
        key: Preference key
        value: Value to set

    Returns:
        True if saved successfully
    """
    prefs = get_preferences()
    prefs[key] = value
    return save_preferences(prefs)


def reset_preferences() -> Dict[str, Any]:
    """
    Reset all preferences to defaults.

    Returns:
        Default preferences dictionary
    """
    defaults = deepcopy(DEFAULT_PREFERENCES)
    defaults["_last_updated"] = datetime.now().isoformat()

    # Clear session state
    st.session_state["user_preferences"] = defaults

    # Clear cookie
    controller = _get_cookie_controller()
    if controller is not None:
        try:
            controller.remove(COOKIE_NAME)
        except Exception:
            pass

    return defaults


def _render_preference_input(key: str, value: Any, prefs: Dict[str, Any]) -> Any:
    """Render appropriate input widget for a preference."""

    # Theme selection
    if key == "theme":
        return st.selectbox(
            "Theme",
            options=["light", "dark", "auto"],
            index=["light", "dark", "auto"].index(value),
            key=f"pref_{key}"
        )

    # Language selection
    elif key == "language":
        return st.selectbox(
            "Language",
            options=["en", "ar"],
            format_func=lambda x: {"en": "English", "ar": "Arabic"}.get(x, x),
            index=["en", "ar"].index(value) if value in ["en", "ar"] else 0,
            key=f"pref_{key}"
        )

    # Sidebar state
    elif key == "sidebar_state":
        return st.selectbox(
            "Default Sidebar State",
            options=["expanded", "collapsed"],
            index=["expanded", "collapsed"].index(value),
            key=f"pref_{key}"
        )

    # Rows per page
    elif key == "rows_per_page":
        return st.number_input(
            "Rows Per Page",
            min_value=10,
            max_value=500,
            value=value,
            step=5,
            key=f"pref_{key}"
        )

    # Number format
    elif key == "number_format":
        return st.selectbox(
            "Number Format",
            options=["standard", "compact", "scientific"],
            format_func=lambda x: {"standard": "Standard (1,234.56)", "compact": "Compact (1.2K)", "scientific": "Scientific (1.23E3)"}.get(x, x),
            index=["standard", "compact", "scientific"].index(value),
            key=f"pref_{key}"
        )

    # Date format
    elif key == "date_format":
        return st.selectbox(
            "Date Format",
            options=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD-MMM-YYYY"],
            index=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD-MMM-YYYY"].index(value) if value in ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD-MMM-YYYY"] else 0,
            key=f"pref_{key}"
        )

    # Decimal places
    elif key == "decimal_places":
        return st.number_input(
            "Decimal Places",
            min_value=0,
            max_value=10,
            value=value,
            key=f"pref_{key}"
        )

    # Chart type
    elif key == "default_chart_type":
        return st.selectbox(
            "Default Chart Type",
            options=["line", "bar", "area", "scatter"],
            format_func=str.capitalize,
            index=["line", "bar", "area", "scatter"].index(value) if value in ["line", "bar", "area", "scatter"] else 0,
            key=f"pref_{key}"
        )

    # Chart color scheme
    elif key == "chart_color_scheme":
        return st.selectbox(
            "Chart Color Scheme",
            options=["default", "colorblind", "monochrome"],
            format_func=str.capitalize,
            index=["default", "colorblind", "monochrome"].index(value) if value in ["default", "colorblind", "monochrome"] else 0,
            key=f"pref_{key}"
        )

    # Chart height
    elif key == "chart_height":
        return st.slider(
            "Chart Height (px)",
            min_value=200,
            max_value=800,
            value=value,
            step=50,
            key=f"pref_{key}"
        )

    # Currency
    elif key == "default_currency":
        return st.selectbox(
            "Default Currency",
            options=["SAR", "USD", "EUR", "GBP"],
            index=["SAR", "USD", "EUR", "GBP"].index(value) if value in ["SAR", "USD", "EUR", "GBP"] else 0,
            key=f"pref_{key}"
        )

    # Market
    elif key == "default_market":
        return st.selectbox(
            "Default Market",
            options=["TASI", "NOMU"],
            index=["TASI", "NOMU"].index(value) if value in ["TASI", "NOMU"] else 0,
            key=f"pref_{key}"
        )

    # Favorite symbols / watchlist (list inputs)
    elif key in ["favorite_symbols", "watchlist"]:
        label = "Favorite Symbols" if key == "favorite_symbols" else "Watchlist"
        current_value = ", ".join(value) if isinstance(value, list) else ""
        text_input = st.text_input(
            label,
            value=current_value,
            help="Comma-separated list of stock symbols",
            key=f"pref_{key}"
        )
        return [s.strip().upper() for s in text_input.split(",") if s.strip()]

    # Query timeout
    elif key == "query_timeout_seconds":
        return st.number_input(
            "Query Timeout (seconds)",
            min_value=5,
            max_value=300,
            value=value,
            step=5,
            key=f"pref_{key}"
        )

    # Max result rows
    elif key == "max_result_rows":
        return st.number_input(
            "Max Result Rows",
            min_value=100,
            max_value=100000,
            value=value,
            step=100,
            key=f"pref_{key}"
        )

    # Cache TTL
    elif key == "cache_ttl_minutes":
        return st.number_input(
            "Cache TTL (minutes)",
            min_value=1,
            max_value=1440,
            value=value,
            step=5,
            key=f"pref_{key}"
        )

    # Boolean preferences
    elif isinstance(value, bool):
        label = key.replace("_", " ").title()
        return st.checkbox(label, value=value, key=f"pref_{key}")

    # Generic number input
    elif isinstance(value, (int, float)):
        label = key.replace("_", " ").title()
        return st.number_input(label, value=value, key=f"pref_{key}")

    # Generic text input
    elif isinstance(value, str):
        label = key.replace("_", " ").title()
        return st.text_input(label, value=value, key=f"pref_{key}")

    return value


def render_preferences_panel(
    key: str = "preferences_panel",
    show_categories: Optional[List[str]] = None,
    compact: bool = False
) -> Dict[str, Any]:
    """
    Render the user preferences settings panel.

    Args:
        key: Unique key for the component
        show_categories: List of categories to show (None = all)
        compact: Use compact layout

    Returns:
        Updated preferences dictionary
    """
    current_prefs = get_preferences()
    updated_prefs = deepcopy(current_prefs)

    # Cookie availability notice
    if not COOKIES_AVAILABLE:
        st.info(
            "Preferences will be saved for this session only. "
            "Install `streamlit-cookies-controller` for persistent preferences."
        )

    # Filter categories
    categories = show_categories or list(PREFERENCE_CATEGORIES.keys())

    if compact:
        # Compact layout - all in expandable sections
        for category in categories:
            if category not in PREFERENCE_CATEGORIES:
                continue

            pref_keys = PREFERENCE_CATEGORIES[category]

            with st.expander(category, expanded=False):
                for pref_key in pref_keys:
                    if pref_key.startswith("_"):
                        continue

                    current_value = current_prefs.get(pref_key, DEFAULT_PREFERENCES.get(pref_key))
                    new_value = _render_preference_input(pref_key, current_value, current_prefs)
                    updated_prefs[pref_key] = new_value
    else:
        # Full layout with tabs
        tabs = st.tabs(categories)

        for tab, category in zip(tabs, categories):
            if category not in PREFERENCE_CATEGORIES:
                continue

            with tab:
                pref_keys = PREFERENCE_CATEGORIES[category]

                # Create two columns for better layout
                col1, col2 = st.columns(2)

                for i, pref_key in enumerate(pref_keys):
                    if pref_key.startswith("_"):
                        continue

                    current_value = current_prefs.get(pref_key, DEFAULT_PREFERENCES.get(pref_key))

                    # Alternate between columns
                    with col1 if i % 2 == 0 else col2:
                        new_value = _render_preference_input(pref_key, current_value, current_prefs)
                        updated_prefs[pref_key] = new_value

    # Save and Reset buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        if st.button("Save Preferences", key=f"{key}_save", type="primary"):
            if save_preferences(updated_prefs):
                st.success("Preferences saved!")
                st.rerun()
            else:
                st.warning("Preferences saved to session only.")

    with col2:
        if st.button("Reset to Defaults", key=f"{key}_reset"):
            reset_preferences()
            st.success("Preferences reset to defaults!")
            st.rerun()

    # Show last updated time
    last_updated = current_prefs.get("_last_updated")
    if last_updated:
        st.caption(f"Last updated: {last_updated}")

    return updated_prefs


def apply_preferences_to_page():
    """
    Apply user preferences to the current page.

    This should be called early in the page to apply theme and other settings.
    """
    prefs = get_preferences()

    # Apply theme (if using custom theme support)
    theme = prefs.get("theme", "light")
    if theme == "dark":
        # Custom dark mode CSS could be injected here
        pass

    # Apply language (for RTL support with Arabic)
    language = prefs.get("language", "en")
    if language == "ar":
        # Inject RTL CSS
        st.markdown("""
            <style>
            .rtl { direction: rtl; text-align: right; }
            </style>
        """, unsafe_allow_html=True)

    return prefs
