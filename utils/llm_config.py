"""LLM configuration utilities for Ra'd AI.

Provides configuration validation and initialization for PandasAI + OpenRouter.
"""

import streamlit as st
import requests
import hashlib
import re
import html
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Default model configuration
DEFAULT_MODEL = "openrouter/google/gemini-2.0-flash-001"
MODEL_DISPLAY_NAME = "Gemini 2.0 Flash"

# OpenRouter API endpoint
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

# API key format pattern (OpenRouter keys typically start with sk-or-)
API_KEY_PATTERN = re.compile(r'^sk-or-[a-zA-Z0-9-_]{20,}$')

# Default fallback models when API fetch fails
DEFAULT_FALLBACK_MODELS = [
    {"id": "google/gemini-2.0-flash-001", "name": "Gemini 2.0 Flash", "pricing": {"prompt": "0", "completion": "0"}},
    {"id": "google/gemini-pro", "name": "Gemini Pro", "pricing": {"prompt": "0.000001", "completion": "0.000002"}},
    {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku", "pricing": {"prompt": "0.00000025", "completion": "0.00000125"}},
]


def _hash_api_key(api_key: str) -> str:
    """Create a secure hash of the API key for caching purposes.

    Args:
        api_key: The API key to hash

    Returns:
        SHA-256 hash of the API key (first 16 chars for brevity)
    """
    return hashlib.sha256(api_key.encode()).hexdigest()[:16]


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_models_cached(api_key_hash: str, _api_key: str) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Fetch available models from OpenRouter API with secure caching.

    Uses api_key_hash for cache key to avoid exposing the actual key.

    Args:
        api_key_hash: Hash of API key (used as cache key)
        _api_key: Actual API key (underscore prefix tells Streamlit not to hash it)

    Returns:
        Tuple of (models list, error message or None)
    """
    try:
        response = requests.get(
            OPENROUTER_MODELS_URL,
            headers={"Authorization": f"Bearer {_api_key}"},
            timeout=15,
            verify=True  # Explicitly verify SSL certificates
        )
        response.raise_for_status()

        models_data = response.json().get("data", [])

        # Filter for text models and sort by name
        text_models = [
            model for model in models_data
            if "text" in model.get("output_modalities", ["text"])
        ]

        # Sort by provider and name
        text_models.sort(key=lambda x: x.get("name", x.get("id", "")))

        logger.info(f"Fetched {len(text_models)} text models from OpenRouter")
        return text_models, None

    except requests.exceptions.Timeout:
        error_msg = "Request timed out while fetching models"
        logger.warning(f"{error_msg} - using fallback models")
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except requests.exceptions.SSLError as e:
        error_msg = f"SSL certificate verification failed: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except requests.exceptions.ConnectionError as e:
        error_msg = f"Connection error: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            error_msg = "Invalid API key - authentication failed"
        elif e.response.status_code == 429:
            error_msg = "Rate limit exceeded - please wait before retrying"
        else:
            error_msg = f"HTTP error {e.response.status_code}: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except ValueError as e:
        error_msg = f"Invalid JSON response: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg

    except Exception as e:
        error_msg = f"Unexpected error fetching models: {e}"
        logger.error(error_msg)
        return DEFAULT_FALLBACK_MODELS.copy(), error_msg


def fetch_openrouter_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from OpenRouter API.

    Args:
        api_key: OpenRouter API key for authentication

    Returns:
        List of model dictionaries with id, name, and pricing info
    """
    api_key_hash = _hash_api_key(api_key)
    models, error = _fetch_models_cached(api_key_hash, api_key)

    if error:
        # Store error in session state for UI to display
        st.session_state.model_fetch_error = error
    elif "model_fetch_error" in st.session_state:
        del st.session_state.model_fetch_error

    return models


def clear_model_cache() -> None:
    """Clear the cached model list to force a refresh."""
    _fetch_models_cached.clear()
    if "model_fetch_error" in st.session_state:
        del st.session_state.model_fetch_error
    logger.info("Model cache cleared")


def get_model_fetch_error() -> Optional[str]:
    """Get any error that occurred during model fetching."""
    return st.session_state.get("model_fetch_error")


def get_model_options(api_key: str) -> Dict[str, str]:
    """Get model options for dropdown selection.

    Args:
        api_key: OpenRouter API key

    Returns:
        Dictionary mapping model IDs to display names
    """
    models = fetch_openrouter_models(api_key)

    if not models:
        # Return default model if fetch fails completely
        logger.warning("No models available, returning default")
        return {DEFAULT_MODEL: MODEL_DISPLAY_NAME}

    options = {}
    for model in models:
        model_id = model.get("id", "")
        if not model_id:
            continue

        model_name = model.get("name", model_id)

        # Add pricing info to display name
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", "0")
        completion_price = pricing.get("completion", "0")

        # Format: "Model Name ($input/$output per 1M tokens)"
        try:
            prompt_cost = float(prompt_price) * 1_000_000
            completion_cost = float(completion_price) * 1_000_000
            if prompt_cost > 0 or completion_cost > 0:
                display_name = f"{model_name} (${prompt_cost:.2f}/${completion_cost:.2f})"
            else:
                display_name = f"{model_name} (Free)"
        except (ValueError, TypeError) as e:
            logger.debug(f"Could not parse pricing for {model_id}: {e}")
            display_name = model_name

        options[f"openrouter/{model_id}"] = display_name

    # Ensure we always have at least the default model
    if not options:
        options[DEFAULT_MODEL] = MODEL_DISPLAY_NAME

    return options


def get_selected_model() -> str:
    """Get the currently selected model from session state."""
    return st.session_state.get("selected_model", DEFAULT_MODEL)


def set_selected_model(model_id: str) -> None:
    """Set the selected model in session state.

    Args:
        model_id: The model ID to set as selected
    """
    if model_id:
        st.session_state.selected_model = model_id
        logger.info(f"Selected model changed to: {model_id}")


def validate_api_key(api_key: Optional[str]) -> Dict[str, Any]:
    """Validate an OpenRouter API key.

    Args:
        api_key: The API key to validate

    Returns:
        Dictionary with 'valid' boolean, optional 'error' message, and 'warnings' list
    """
    warnings = []

    if api_key is None:
        return {
            "valid": False,
            "error": "API key is missing. Please configure OPENROUTER_API_KEY in secrets.",
            "warnings": warnings
        }

    if not api_key or not api_key.strip():
        return {
            "valid": False,
            "error": "API key is empty. Please provide a valid OpenRouter API key.",
            "warnings": warnings
        }

    key = api_key.strip()

    # Check minimum length
    if len(key) < 20:
        return {
            "valid": False,
            "error": "API key is too short. OpenRouter keys are typically 40+ characters.",
            "warnings": warnings
        }

    # Check format pattern (warning only, not blocking)
    if not API_KEY_PATTERN.match(key):
        warnings.append("API key format doesn't match expected pattern (sk-or-...). It may still work.")
        logger.warning(f"API key format warning: doesn't match expected pattern")

    return {
        "valid": True,
        "error": None,
        "warnings": warnings
    }


def get_api_key() -> Optional[str]:
    """Get the OpenRouter API key from Streamlit secrets.

    Returns:
        The API key string or None if not configured
    """
    try:
        key = st.secrets.get("OPENROUTER_API_KEY")
        if key:
            return key.strip()
        return None
    except Exception as e:
        logger.debug(f"Could not retrieve API key from secrets: {e}")
        return None


def get_llm_config_status() -> Dict[str, Any]:
    """Get the current LLM configuration status.

    Returns:
        Dictionary with configuration status including:
        - configured: bool
        - model: str (model ID)
        - model_display: str (display name)
        - error: Optional[str]
        - warnings: List[str]
        - has_key: bool
        - fetch_error: Optional[str] (error from model fetching)
    """
    api_key = get_api_key()
    validation = validate_api_key(api_key)
    selected_model = get_selected_model()

    # Get display name for selected model
    if validation["valid"]:
        model_options = get_model_options(api_key)
        model_display = model_options.get(selected_model, selected_model.split("/")[-1])
    else:
        model_display = MODEL_DISPLAY_NAME

    return {
        "configured": validation["valid"],
        "model": selected_model,
        "model_display": model_display,
        "error": validation.get("error"),
        "warnings": validation.get("warnings", []),
        "has_key": api_key is not None,
        "fetch_error": get_model_fetch_error(),
    }


def initialize_llm(model_id: Optional[str] = None) -> Tuple[Any, Optional[str]]:
    """Initialize the LLM configuration for PandasAI.

    Args:
        model_id: Optional model ID to use. If None, uses selected model from session state.

    Returns:
        Tuple of (llm_instance, error_message)

    Example:
        llm, error = initialize_llm()
        if error:
            st.error(f"Failed to initialize: {error}")
        else:
            # LLM is ready to use
            pass
    """
    api_key = get_api_key()
    validation = validate_api_key(api_key)

    if not validation["valid"]:
        logger.warning(f"LLM initialization failed: {validation['error']}")
        return None, validation["error"]

    # Log any warnings
    for warning in validation.get("warnings", []):
        logger.warning(f"API key warning: {warning}")

    # Use provided model_id or get from session state
    selected_model = model_id or get_selected_model()

    if not selected_model:
        selected_model = DEFAULT_MODEL
        logger.warning(f"No model selected, using default: {DEFAULT_MODEL}")

    try:
        import pandasai as pai
        from pandasai_litellm.litellm import LiteLLM

        llm = LiteLLM(
            model=selected_model,
            api_key=api_key,
        )

        pai.config.set({"llm": llm})

        logger.info(f"LLM initialized successfully with {selected_model}")
        return llm, None

    except ImportError as e:
        error = f"Missing required package: {e}"
        logger.error(error)
        return None, error
    except ValueError as e:
        error = f"Invalid configuration: {e}"
        logger.error(error)
        return None, error
    except Exception as e:
        error = f"Failed to initialize LLM: {html.escape(str(e))}"
        logger.error(f"LLM initialization error: {e}")
        return None, error


def check_llm_ready() -> bool:
    """Check if the LLM is ready for use.

    Returns:
        True if LLM is configured and ready, False otherwise
    """
    status = get_llm_config_status()
    return status["configured"]
