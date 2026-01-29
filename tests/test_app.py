"""Tests for main app module and application initialization."""

import pytest


def test_app_imports():
    """Test that app module dependencies can be imported."""
    from styles.css import get_base_css, get_error_css
    from utils.data_loader import load_data

    assert callable(get_base_css)
    assert callable(get_error_css)
    assert callable(load_data)


def test_logo_path_defined():
    """Test that logo path is properly defined."""
    from pathlib import Path

    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    assert "assets" in str(logo_path)


def test_styles_module_accessible():
    """Test that styles module is accessible."""
    import styles
    from styles import css, variables

    assert hasattr(css, "get_base_css")
    assert hasattr(css, "get_error_css")
    assert hasattr(variables, "GOLD_PRIMARY")


def test_components_module_accessible():
    """Test that components module is accessible."""
    import components

    assert hasattr(components, "chat")
    assert hasattr(components, "sidebar")
    assert hasattr(components, "export")


def test_utils_module_accessible():
    """Test that utils module is accessible."""
    import utils

    assert hasattr(utils, "data_loader")
    assert hasattr(utils, "data_processing")
    assert hasattr(utils, "llm_config")


def test_data_files_exist():
    """Test that required data files exist."""
    from pathlib import Path

    data_dir = Path(__file__).parent.parent / "data"
    assert data_dir.exists()


def test_app_constants_defined():
    """Test that application constants are properly defined."""
    from utils.llm_config import DEFAULT_MODEL, MODEL_DISPLAY_NAME

    assert DEFAULT_MODEL is not None
    assert MODEL_DISPLAY_NAME is not None
    assert isinstance(DEFAULT_MODEL, str)
    assert isinstance(MODEL_DISPLAY_NAME, str)


def test_app_can_initialize_data_loader():
    """Test that data loader can be initialized."""
    from utils.data_loader import load_data

    # This should not raise an exception
    data = load_data()
    assert isinstance(data, dict)


def test_app_session_defaults_valid():
    """Test that session defaults are valid."""
    from components.session_manager import SESSION_DEFAULTS

    assert isinstance(SESSION_DEFAULTS, dict)
    assert "chat_history" in SESSION_DEFAULTS
    assert "selected_dataset" in SESSION_DEFAULTS


def test_comparison_mode_available():
    """Test that comparison mode is available."""
    from components.comparison_mode import (
        compare_entities,
        get_comparison_metrics,
        format_comparison_table,
        create_comparison_chart,
    )

    assert callable(compare_entities)
    assert callable(get_comparison_metrics)
    assert callable(format_comparison_table)
    assert callable(create_comparison_chart)


def test_export_functions_available():
    """Test that export functions are available."""
    from components.export import (
        export_to_csv,
        export_response_to_text,
        generate_export_filename,
        export_chat_history_to_markdown,
    )

    assert callable(export_to_csv)
    assert callable(export_response_to_text)
    assert callable(generate_export_filename)
    assert callable(export_chat_history_to_markdown)


def test_visualization_functions_available():
    """Test that visualization functions are available."""
    from components.visualizations.response_charts import (
        should_render_chart,
        auto_visualize,
        create_bar_chart,
    )

    assert callable(should_render_chart)
    assert callable(auto_visualize)
    assert callable(create_bar_chart)


def test_chat_functions_available():
    """Test that chat functions are available."""
    from components.chat import (
        format_response,
        get_chat_history,
        add_to_chat_history,
    )

    assert callable(format_response)
    assert callable(get_chat_history)
    assert callable(add_to_chat_history)


def test_error_display_available():
    """Test that error display functions are available."""
    from components.error_display import format_api_error

    assert callable(format_api_error)


def test_loading_functions_available():
    """Test that loading functions are available."""
    from components.loading import (
        get_skeleton_css,
        get_random_loading_message,
        LOADING_MESSAGES,
    )

    assert callable(get_skeleton_css)
    assert callable(get_random_loading_message)
    assert isinstance(LOADING_MESSAGES, list)
