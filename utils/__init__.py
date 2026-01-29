"""Utility functions for Ra'd AI / Saudi Financial Chat."""

from .data_loader import (
    load_data,
    get_dataset,
    get_dataset_info,
    get_column_info,
    get_dataset_display_name,
    DATASET_DISPLAY_NAMES,
)

from .llm_config import (
    validate_api_key,
    get_llm_config_status,
    initialize_llm,
    check_llm_ready,
    DEFAULT_MODEL,
    MODEL_DISPLAY_NAME,
)

# Data processing utilities
try:
    from .data_processing import normalize_to_sar, format_dataframe_for_display, create_styled_dataframe
    DATA_PROCESSING_AVAILABLE = True
except ImportError:
    DATA_PROCESSING_AVAILABLE = False

__all__ = [
    # Data loader
    "load_data",
    "get_dataset",
    "get_dataset_info",
    "get_column_info",
    "get_dataset_display_name",
    "DATASET_DISPLAY_NAMES",
    # LLM config
    "validate_api_key",
    "get_llm_config_status",
    "initialize_llm",
    "check_llm_ready",
    "DEFAULT_MODEL",
    "MODEL_DISPLAY_NAME",
]

# Add data processing exports if available
if DATA_PROCESSING_AVAILABLE:
    __all__.extend([
        "normalize_to_sar",
        "format_dataframe_for_display",
        "create_styled_dataframe",
    ])
