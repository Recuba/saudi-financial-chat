"""
URL State Synchronization Utilities
====================================
Provides URL state sync for shareable links using streamlit-ext,
enabling users to share specific app states via URL parameters.
"""

from typing import Any, Dict, List, Optional, TypeVar, Callable, Union
from urllib.parse import urlencode, parse_qs, urlparse
import json
import base64
import zlib
import streamlit as st

# Try to import streamlit-ext for URL state sync
try:
    from streamlit_ext import sync_widget_state, get_url_params
    STREAMLIT_EXT_AVAILABLE = True
except ImportError:
    STREAMLIT_EXT_AVAILABLE = False

T = TypeVar("T")


# Default state keys that should be synced to URL
DEFAULT_SYNC_KEYS = [
    "dataset_choice",
    "selected_company",
    "selected_sector",
    "fiscal_year",
    "view_mode",
    "chart_type",
]


def get_query_params() -> Dict[str, Any]:
    """
    Get current URL query parameters.

    Uses streamlit-ext if available, otherwise falls back to
    Streamlit's built-in experimental query params.

    Returns:
        Dict of query parameter names to values.
    """
    if STREAMLIT_EXT_AVAILABLE:
        try:
            params = get_url_params()
            if params:
                return params
        except Exception:
            pass

    # Fallback to Streamlit's query params
    try:
        return dict(st.query_params)
    except Exception:
        return {}


def set_query_params(**params: Any) -> None:
    """
    Set URL query parameters.

    Args:
        **params: Key-value pairs to set as query parameters.
                  Pass None as value to remove a parameter.
    """
    try:
        current = dict(st.query_params)

        for key, value in params.items():
            if value is None:
                current.pop(key, None)
            else:
                current[key] = str(value)

        st.query_params.update(current)
    except Exception:
        # Silently fail if query params not supported
        pass


def sync_state_to_url(
    keys: Optional[List[str]] = None,
    prefix: str = "",
) -> None:
    """
    Sync session state values to URL parameters.

    Enables shareable URLs that preserve app state.

    Args:
        keys: List of session state keys to sync. If None, uses DEFAULT_SYNC_KEYS.
        prefix: Optional prefix for URL parameter names.
    """
    if keys is None:
        keys = DEFAULT_SYNC_KEYS

    params_to_set = {}

    for key in keys:
        if key in st.session_state:
            value = st.session_state[key]
            param_name = f"{prefix}{key}" if prefix else key

            if value is not None:
                if isinstance(value, (list, dict)):
                    # Encode complex types as JSON
                    params_to_set[param_name] = json.dumps(value)
                elif isinstance(value, bool):
                    params_to_set[param_name] = "1" if value else "0"
                else:
                    params_to_set[param_name] = str(value)

    set_query_params(**params_to_set)


def restore_state_from_url(
    keys: Optional[List[str]] = None,
    prefix: str = "",
    type_hints: Optional[Dict[str, type]] = None,
) -> Dict[str, Any]:
    """
    Restore session state from URL parameters.

    Should be called early in the app before widgets are rendered.

    Args:
        keys: List of session state keys to restore. If None, uses DEFAULT_SYNC_KEYS.
        prefix: Optional prefix for URL parameter names.
        type_hints: Dict mapping keys to their expected types for conversion.

    Returns:
        Dict of restored key-value pairs.
    """
    if keys is None:
        keys = DEFAULT_SYNC_KEYS

    if type_hints is None:
        type_hints = {}

    params = get_query_params()
    restored = {}

    for key in keys:
        param_name = f"{prefix}{key}" if prefix else key

        if param_name in params:
            value = params[param_name]

            # Handle list values from repeated params
            if isinstance(value, list):
                value = value[0] if value else None

            if value is not None:
                # Convert to expected type
                expected_type = type_hints.get(key)

                try:
                    if expected_type == bool:
                        value = value in ("1", "true", "True", "yes")
                    elif expected_type == int:
                        value = int(value)
                    elif expected_type == float:
                        value = float(value)
                    elif expected_type in (list, dict):
                        value = json.loads(value)
                    # else keep as string

                    st.session_state[key] = value
                    restored[key] = value
                except (ValueError, json.JSONDecodeError):
                    # Keep original string value on conversion error
                    st.session_state[key] = value
                    restored[key] = value

    return restored


def create_shareable_link(
    state: Optional[Dict[str, Any]] = None,
    keys: Optional[List[str]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Create a shareable URL with current or specified state.

    Args:
        state: Dict of state values to include. If None, uses current session state.
        keys: List of keys to include from state/session_state.
        base_url: Base URL to use. If None, attempts to detect current URL.

    Returns:
        Complete URL string with state encoded as query parameters.
    """
    if keys is None:
        keys = DEFAULT_SYNC_KEYS

    if state is None:
        state = {k: st.session_state.get(k) for k in keys if k in st.session_state}
    else:
        state = {k: v for k, v in state.items() if k in keys}

    # Build query string
    params = {}
    for key, value in state.items():
        if value is not None:
            if isinstance(value, (list, dict)):
                params[key] = json.dumps(value)
            elif isinstance(value, bool):
                params[key] = "1" if value else "0"
            else:
                params[key] = str(value)

    query_string = urlencode(params)

    # Determine base URL
    if base_url is None:
        # Try to get from Streamlit context
        try:
            # This works in some Streamlit deployments
            base_url = st.context.headers.get("Origin", "")
        except Exception:
            base_url = ""

    if query_string:
        separator = "?" if "?" not in base_url else "&"
        return f"{base_url}{separator}{query_string}"

    return base_url


def compress_state(state: Dict[str, Any]) -> str:
    """
    Compress state dict into a URL-safe string.

    Useful for complex state that would be too long as individual params.

    Args:
        state: Dict of state values to compress.

    Returns:
        Base64-encoded compressed string.
    """
    json_str = json.dumps(state, separators=(",", ":"))
    compressed = zlib.compress(json_str.encode("utf-8"))
    return base64.urlsafe_b64encode(compressed).decode("ascii")


def decompress_state(compressed: str) -> Dict[str, Any]:
    """
    Decompress state from URL-safe string.

    Args:
        compressed: Base64-encoded compressed string from compress_state.

    Returns:
        Original state dict.

    Raises:
        ValueError: If decompression or JSON parsing fails.
    """
    try:
        decoded = base64.urlsafe_b64decode(compressed.encode("ascii"))
        decompressed = zlib.decompress(decoded)
        return json.loads(decompressed.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to decompress state: {e}")


def url_synced_selectbox(
    label: str,
    options: List[Any],
    key: str,
    default_index: int = 0,
    format_func: Optional[Callable[[Any], str]] = None,
    **kwargs: Any,
) -> Any:
    """
    Create a selectbox that syncs its value to URL parameters.

    Args:
        label: Label for the selectbox.
        options: List of options.
        key: Session state key (also used as URL parameter name).
        default_index: Default selected index.
        format_func: Optional function to format option display.
        **kwargs: Additional arguments passed to st.selectbox.

    Returns:
        Selected value.
    """
    # Check URL params for initial value
    params = get_query_params()

    if key in params and key not in st.session_state:
        url_value = params[key]
        if isinstance(url_value, list):
            url_value = url_value[0]

        # Find matching option
        for i, opt in enumerate(options):
            if str(opt) == url_value:
                default_index = i
                break

    # Render selectbox
    value = st.selectbox(
        label,
        options,
        index=default_index,
        key=key,
        format_func=format_func,
        **kwargs,
    )

    # Sync to URL
    set_query_params(**{key: str(value)})

    return value


def url_synced_multiselect(
    label: str,
    options: List[Any],
    key: str,
    default: Optional[List[Any]] = None,
    **kwargs: Any,
) -> List[Any]:
    """
    Create a multiselect that syncs its value to URL parameters.

    Args:
        label: Label for the multiselect.
        options: List of options.
        key: Session state key (also used as URL parameter name).
        default: Default selected values.
        **kwargs: Additional arguments passed to st.multiselect.

    Returns:
        List of selected values.
    """
    if default is None:
        default = []

    # Check URL params for initial value
    params = get_query_params()

    if key in params and key not in st.session_state:
        url_value = params[key]
        try:
            if isinstance(url_value, str):
                default = json.loads(url_value)
            elif isinstance(url_value, list):
                default = url_value
        except json.JSONDecodeError:
            pass

    # Render multiselect
    value = st.multiselect(
        label,
        options,
        default=default,
        key=key,
        **kwargs,
    )

    # Sync to URL
    set_query_params(**{key: json.dumps(value)})

    return value


def url_synced_slider(
    label: str,
    min_value: Union[int, float],
    max_value: Union[int, float],
    key: str,
    default_value: Optional[Union[int, float]] = None,
    **kwargs: Any,
) -> Union[int, float]:
    """
    Create a slider that syncs its value to URL parameters.

    Args:
        label: Label for the slider.
        min_value: Minimum value.
        max_value: Maximum value.
        key: Session state key (also used as URL parameter name).
        default_value: Default value.
        **kwargs: Additional arguments passed to st.slider.

    Returns:
        Selected value.
    """
    if default_value is None:
        default_value = min_value

    # Check URL params for initial value
    params = get_query_params()

    if key in params and key not in st.session_state:
        url_value = params[key]
        if isinstance(url_value, list):
            url_value = url_value[0]
        try:
            if isinstance(min_value, int):
                default_value = int(url_value)
            else:
                default_value = float(url_value)
        except ValueError:
            pass

    # Render slider
    value = st.slider(
        label,
        min_value=min_value,
        max_value=max_value,
        value=default_value,
        key=key,
        **kwargs,
    )

    # Sync to URL
    set_query_params(**{key: str(value)})

    return value


def clear_url_state(keys: Optional[List[str]] = None) -> None:
    """
    Clear specified URL parameters.

    Args:
        keys: List of parameter names to clear. If None, clears all DEFAULT_SYNC_KEYS.
    """
    if keys is None:
        keys = DEFAULT_SYNC_KEYS

    params_to_clear = {key: None for key in keys}
    set_query_params(**params_to_clear)


def show_share_button(
    label: str = "Share Link",
    keys: Optional[List[str]] = None,
    help_text: str = "Copy link to share current view",
) -> None:
    """
    Display a button that copies a shareable link to clipboard.

    Args:
        label: Button label text.
        keys: List of state keys to include in the link.
        help_text: Tooltip help text.
    """
    link = create_shareable_link(keys=keys)

    # Use Streamlit's copy functionality via markdown
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <input type="text" value="{link}" id="share-link"
                   style="flex: 1; padding: 8px; border-radius: 4px;
                          border: 1px solid #D4A84B; background: #2A2A2A;
                          color: #FFFFFF;" readonly>
            <button onclick="navigator.clipboard.writeText(document.getElementById('share-link').value);
                            this.innerHTML='Copied!';"
                    style="padding: 8px 16px; border-radius: 4px; border: none;
                           background: linear-gradient(135deg, #B8860B, #D4A84B);
                           color: #0E0E0E; cursor: pointer; font-weight: 600;"
                    title="{help_text}">
                {label}
            </button>
        </div>
        """,
        unsafe_allow_html=True,
    )
