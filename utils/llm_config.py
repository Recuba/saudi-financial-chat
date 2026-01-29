"""LLM configuration utilities for Ra'd AI.

Provides configuration validation and initialization for PandasAI + OpenRouter.
"""

import streamlit as st
import requests
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

# Default model configuration
DEFAULT_MODEL = "openrouter/google/gemini-2.0-flash-001"
MODEL_DISPLAY_NAME = "Gemini 2.0 Flash"

# OpenRouter API endpoint
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_openrouter_models(api_key: str) -> List[Dict[str, Any]]:
    """Fetch available models from OpenRouter API.

    Args:
        api_key: OpenRouter API key for authentication

    Returns:
        List of model dictionaries with id, name, and pricing info
    """
    try:
        response = requests.get(
            OPENROUTER_MODELS_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
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
        return text_models

    except requests.exceptions.Timeout:
        logger.warning("Timeout fetching OpenRouter models")
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching OpenRouter models: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching models: {e}")
        return []


def get_model_options(api_key: str) -> Dict[str, str]:
    """Get model options for dropdown selection.

    Args:
        api_key: OpenRouter API key

    Returns:
        Dictionary mapping model IDs to display names
    """
    models = fetch_openrouter_models(api_key)

    if not models:
        # Return default model if fetch fails
        return {DEFAULT_MODEL: MODEL_DISPLAY_NAME}

    options = {}
    for model in models:
        model_id = model.get("id", "")
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
        except (ValueError, TypeError):
            display_name = model_name

        options[f"openrouter/{model_id}"] = display_name

    return options


def get_selected_model() -> str:
    """Get the currently selected model from session state."""
    return st.session_state.get("selected_model", DEFAULT_MODEL)


def set_selected_model(model_id: str) -> None:
    """Set the selected model in session state."""
    st.session_state.selected_model = model_id


def validate_api_key(api_key: Optional[str]) -> Dict[str, Any]:
    """Validate an OpenRouter API key.

    Args:
        api_key: The API key to validate

    Returns:
        Dictionary with 'valid' boolean and optional 'error' message
    """
    if api_key is None:
        return {
            "valid": False,
            "error": "API key is missing. Please configure OPENROUTER_API_KEY in secrets."
        }

    if not api_key or not api_key.strip():
        return {
            "valid": False,
            "error": "API key is empty. Please provide a valid OpenRouter API key."
        }

    key = api_key.strip()
    if len(key) < 10:
        return {
            "valid": False,
            "error": "API key appears too short. Please check your key."
        }

    return {
        "valid": True,
        "error": None
    }


def get_api_key() -> Optional[str]:
    """Get the OpenRouter API key from Streamlit secrets."""
    try:
        return st.secrets.get("OPENROUTER_API_KEY")
    except Exception:
        return None


def get_llm_config_status() -> Dict[str, Any]:
    """Get the current LLM configuration status."""
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
        "has_key": api_key is not None,
    }


def initialize_llm(model_id: Optional[str] = None):
    """Initialize the LLM configuration for PandasAI.

    Args:
        model_id: Optional model ID to use. If None, uses selected model from session state.

    Returns:
        Tuple of (llm_instance, error_message)
    """
    api_key = get_api_key()
    validation = validate_api_key(api_key)

    if not validation["valid"]:
        logger.warning(f"LLM initialization failed: {validation['error']}")
        return None, validation["error"]

    # Use provided model_id or get from session state
    selected_model = model_id or get_selected_model()

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
    except Exception as e:
        error = f"Failed to initialize LLM: {str(e)}"
        logger.error(error)
        return None, error


def check_llm_ready() -> bool:
    """Check if the LLM is ready for use."""
    status = get_llm_config_status()
    return status["configured"]
