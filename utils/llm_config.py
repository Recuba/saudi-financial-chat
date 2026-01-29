"""LLM configuration utilities for Ra'd AI.

Provides configuration validation and initialization for PandasAI + OpenRouter.
"""

import streamlit as st
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Default model configuration
DEFAULT_MODEL = "openrouter/google/gemini-2.0-flash-001"
MODEL_DISPLAY_NAME = "Gemini 2.0 Flash"


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

    return {
        "configured": validation["valid"],
        "model": DEFAULT_MODEL,
        "model_display": MODEL_DISPLAY_NAME,
        "error": validation.get("error"),
        "has_key": api_key is not None,
    }


def initialize_llm():
    """Initialize the LLM configuration for PandasAI.

    Returns:
        Tuple of (llm_instance, error_message)
    """
    api_key = get_api_key()
    validation = validate_api_key(api_key)

    if not validation["valid"]:
        logger.warning(f"LLM initialization failed: {validation['error']}")
        return None, validation["error"]

    try:
        import pandasai as pai
        from pandasai_litellm.litellm import LiteLLM

        llm = LiteLLM(
            model=DEFAULT_MODEL,
            api_key=api_key,
        )

        pai.config.set({"llm": llm})

        logger.info(f"LLM initialized successfully with {MODEL_DISPLAY_NAME}")
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
