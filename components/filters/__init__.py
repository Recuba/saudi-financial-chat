"""
Filtering & Selection Components
================================
Dynamic filters, tree selectors, and date pickers for the Saudi Financial Chat app.
"""

from .dynamic_filters import (
    DynamicFilterManager,
    extract_filter_options,
    apply_filters,
    render_filter_summary,
    render_dynamic_filters,
    clear_all_filters,
)

from .tree_selector import (
    TreeSelectorManager,
    build_tree_structure,
    extract_selected_values,
    render_tree_selector,
    render_cascading_selectors,
)

from .date_picker import (
    DatePickerManager,
    fiscal_year_to_date_range,
    get_date_presets,
    render_date_range_picker,
    render_fiscal_year_selector,
    render_quick_date_presets,
)

__all__ = [
    # Dynamic Filters
    "DynamicFilterManager",
    "extract_filter_options",
    "apply_filters",
    "render_filter_summary",
    "render_dynamic_filters",
    "clear_all_filters",
    # Tree Selector
    "TreeSelectorManager",
    "build_tree_structure",
    "extract_selected_values",
    "render_tree_selector",
    "render_cascading_selectors",
    # Date Picker
    "DatePickerManager",
    "fiscal_year_to_date_range",
    "get_date_presets",
    "render_date_range_picker",
    "render_fiscal_year_selector",
    "render_quick_date_presets",
]
