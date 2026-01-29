"""
Hierarchical Tree Selector
==========================
Provides hierarchical tree selection for Sector -> Industry -> Company
using streamlit-tree-select with fallback to cascading selectboxes.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pandas as pd
import streamlit as st

# Import guard for optional dependency
try:
    from streamlit_tree_select import tree_select
    TREE_SELECT_AVAILABLE = True
except ImportError:
    TREE_SELECT_AVAILABLE = False


class TreeSelectorManager:
    """
    Manager class for hierarchical tree selection.

    Builds and manages a tree structure from flat data, supporting
    Sector -> Industry -> Company hierarchies common in financial data.

    Attributes:
        df: Source DataFrame
        hierarchy_columns: List of columns defining the hierarchy (parent to child)
        value_column: Column to use as the selection value
        key_prefix: Prefix for session state keys
    """

    def __init__(
        self,
        df: pd.DataFrame,
        hierarchy_columns: List[str],
        value_column: Optional[str] = None,
        key_prefix: str = "tree"
    ):
        """
        Initialize the TreeSelectorManager.

        Args:
            df: DataFrame containing hierarchical data
            hierarchy_columns: Columns defining hierarchy (e.g., ["sector", "industry", "company_name"])
            value_column: Column for final selection values (default: last hierarchy column)
            key_prefix: Prefix for session state keys
        """
        self.df = df
        self.hierarchy_columns = [col for col in hierarchy_columns if col in df.columns]
        self.value_column = value_column or self.hierarchy_columns[-1]
        self.key_prefix = key_prefix
        self._tree_data: Optional[List[Dict]] = None
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state for selections."""
        state_key = f"{self.key_prefix}_selected"
        if state_key not in st.session_state:
            st.session_state[state_key] = {"checked": [], "expanded": []}

    def _build_tree(self) -> List[Dict]:
        """Build tree structure from flat DataFrame."""
        if self._tree_data is not None:
            return self._tree_data

        self._tree_data = build_tree_structure(
            self.df,
            self.hierarchy_columns,
            self.value_column
        )
        return self._tree_data

    def render(
        self,
        label: str = "Select Items",
        expanded: bool = True,
        check_model: str = "leaf",
        only_leaf_checkboxes: bool = False,
        show_expand_all: bool = True
    ) -> List[Any]:
        """
        Render the tree selector and return selected values.

        Args:
            label: Label for the selector
            expanded: Whether to expand all nodes by default
            check_model: Check model ("leaf", "all", or "independent")
            only_leaf_checkboxes: Only show checkboxes on leaf nodes
            show_expand_all: Show expand/collapse all buttons

        Returns:
            List of selected leaf values
        """
        tree_data = self._build_tree()
        state_key = f"{self.key_prefix}_selected"

        if TREE_SELECT_AVAILABLE:
            return self._render_with_tree_select(
                tree_data=tree_data,
                label=label,
                expanded=expanded,
                check_model=check_model,
                only_leaf_checkboxes=only_leaf_checkboxes,
                show_expand_all=show_expand_all
            )
        else:
            return self._render_with_cascading_selectors(label)

    def _render_with_tree_select(
        self,
        tree_data: List[Dict],
        label: str,
        expanded: bool,
        check_model: str,
        only_leaf_checkboxes: bool,
        show_expand_all: bool
    ) -> List[Any]:
        """Render using streamlit-tree-select."""
        state_key = f"{self.key_prefix}_selected"

        st.markdown(f"**{label}**")

        # Get initial expanded nodes
        if expanded and not st.session_state[state_key].get("expanded"):
            expanded_nodes = self._get_all_node_values(tree_data)
        else:
            expanded_nodes = st.session_state[state_key].get("expanded", [])

        result = tree_select(
            nodes=tree_data,
            check_model=check_model,
            only_leaf_checkboxes=only_leaf_checkboxes,
            show_expand_all=show_expand_all,
            checked=st.session_state[state_key].get("checked", []),
            expanded=expanded_nodes,
            key=f"{self.key_prefix}_tree_widget"
        )

        # Update session state
        st.session_state[state_key] = {
            "checked": result.get("checked", []),
            "expanded": result.get("expanded", [])
        }

        return result.get("checked", [])

    def _render_with_cascading_selectors(self, label: str) -> List[Any]:
        """Render fallback cascading selectboxes."""
        st.markdown(f"**{label}**")
        return render_cascading_selectors(
            df=self.df,
            hierarchy_columns=self.hierarchy_columns,
            value_column=self.value_column,
            key_prefix=self.key_prefix
        )

    def _get_all_node_values(self, nodes: List[Dict]) -> List[str]:
        """Get all node values for expansion."""
        values = []
        for node in nodes:
            values.append(node["value"])
            if "children" in node:
                values.extend(self._get_all_node_values(node["children"]))
        return values

    def get_selected_values(self) -> List[Any]:
        """Get currently selected leaf values."""
        state_key = f"{self.key_prefix}_selected"
        if state_key not in st.session_state:
            return []
        return st.session_state[state_key].get("checked", [])

    def clear_selection(self) -> None:
        """Clear all selections."""
        state_key = f"{self.key_prefix}_selected"
        st.session_state[state_key] = {"checked": [], "expanded": []}


def build_tree_structure(
    df: pd.DataFrame,
    hierarchy_columns: List[str],
    value_column: Optional[str] = None,
    include_counts: bool = True
) -> List[Dict]:
    """
    Build a tree structure from flat DataFrame data.

    Creates a hierarchical tree suitable for streamlit-tree-select
    from flat data with columns representing hierarchy levels.

    Args:
        df: DataFrame with hierarchical data
        hierarchy_columns: Columns defining hierarchy (parent to child)
        value_column: Column for leaf node values (default: last hierarchy column)
        include_counts: Include item counts in parent labels

    Returns:
        List of tree node dictionaries with structure:
        [{"label": str, "value": str, "children": [...]}]

    Example:
        >>> tree = build_tree_structure(
        ...     df,
        ...     hierarchy_columns=["sector", "industry", "company_name"],
        ...     include_counts=True
        ... )
    """
    if not hierarchy_columns:
        return []

    value_column = value_column or hierarchy_columns[-1]
    valid_columns = [col for col in hierarchy_columns if col in df.columns]

    if not valid_columns:
        return []

    def build_level(data: pd.DataFrame, level: int) -> List[Dict]:
        """Recursively build tree levels."""
        if level >= len(valid_columns):
            return []

        current_col = valid_columns[level]
        is_leaf = level == len(valid_columns) - 1

        nodes = []
        for value in sorted(data[current_col].dropna().unique()):
            subset = data[data[current_col] == value]

            if is_leaf:
                # Leaf node
                node = {
                    "label": str(value),
                    "value": str(value)
                }
            else:
                # Parent node with children
                children = build_level(subset, level + 1)
                child_count = len(subset[value_column].unique()) if include_counts else 0

                label = f"{value} ({child_count})" if include_counts else str(value)
                node = {
                    "label": label,
                    "value": f"{current_col}:{value}",
                    "children": children
                }

            nodes.append(node)

        return nodes

    return build_level(df, 0)


def extract_selected_values(
    checked: List[str],
    tree_data: List[Dict],
    leaf_only: bool = True
) -> List[str]:
    """
    Extract actual values from tree selection results.

    Args:
        checked: List of checked node values from tree_select
        tree_data: The tree structure used for selection
        leaf_only: Only return leaf node values (default: True)

    Returns:
        List of selected values
    """
    if not checked:
        return []

    # Build lookup of all nodes
    def collect_nodes(nodes: List[Dict], parent_values: Set[str]) -> Tuple[Set[str], Set[str]]:
        """Collect leaf and parent node values."""
        leaves = set()
        parents = set()

        for node in nodes:
            value = node["value"]
            if "children" in node and node["children"]:
                parents.add(value)
                child_leaves, child_parents = collect_nodes(node["children"], parents)
                leaves.update(child_leaves)
                parents.update(child_parents)
            else:
                leaves.add(value)

        return leaves, parents

    all_leaves, all_parents = collect_nodes(tree_data, set())

    if leaf_only:
        return [v for v in checked if v in all_leaves]
    else:
        return checked


def render_tree_selector(
    df: pd.DataFrame,
    hierarchy_columns: List[str],
    label: str = "Select Items",
    key_prefix: str = "tree_sel",
    value_column: Optional[str] = None,
    expanded: bool = True,
    check_model: str = "leaf"
) -> List[Any]:
    """
    Convenience function to render a tree selector.

    Args:
        df: DataFrame with hierarchical data
        hierarchy_columns: Columns defining hierarchy
        label: Selector label
        key_prefix: Session state key prefix
        value_column: Column for leaf values
        expanded: Expand all nodes by default
        check_model: Check behavior model

    Returns:
        List of selected leaf values

    Example:
        >>> selected_companies = render_tree_selector(
        ...     df=analytics_df,
        ...     hierarchy_columns=["sector", "industry", "company_name"],
        ...     label="Select Companies"
        ... )
    """
    manager = TreeSelectorManager(
        df=df,
        hierarchy_columns=hierarchy_columns,
        value_column=value_column,
        key_prefix=key_prefix
    )

    return manager.render(
        label=label,
        expanded=expanded,
        check_model=check_model
    )


def render_cascading_selectors(
    df: pd.DataFrame,
    hierarchy_columns: List[str],
    value_column: Optional[str] = None,
    key_prefix: str = "cascade",
    show_all_option: bool = True,
    multi_select_leaf: bool = True
) -> List[Any]:
    """
    Render cascading selectboxes as fallback for tree selector.

    Each level filters the options available in subsequent levels.

    Args:
        df: DataFrame with hierarchical data
        hierarchy_columns: Columns defining hierarchy
        value_column: Column for final selection values
        key_prefix: Session state key prefix
        show_all_option: Include "All" option in parent selectors
        multi_select_leaf: Use multiselect for leaf level

    Returns:
        List of selected leaf values

    Example:
        >>> selected = render_cascading_selectors(
        ...     df=analytics_df,
        ...     hierarchy_columns=["sector", "industry", "company_name"]
        ... )
    """
    value_column = value_column or hierarchy_columns[-1]
    valid_columns = [col for col in hierarchy_columns if col in df.columns]

    if not valid_columns:
        return []

    filtered_df = df.copy()
    selections = {}

    # Render each level
    for i, column in enumerate(valid_columns):
        is_leaf = (i == len(valid_columns) - 1)
        display_name = column.replace("_", " ").title()
        select_key = f"{key_prefix}_{column}"

        # Get available options from filtered data
        options = sorted(filtered_df[column].dropna().unique().tolist())

        if not is_leaf:
            # Parent level - single select with optional "All"
            if show_all_option:
                options = ["All"] + options

            selection = st.selectbox(
                label=display_name,
                options=options,
                key=select_key,
                help=f"Select {display_name.lower()}"
            )

            selections[column] = selection

            # Filter for next level
            if selection != "All":
                filtered_df = filtered_df[filtered_df[column] == selection]

        else:
            # Leaf level
            if multi_select_leaf:
                selection = st.multiselect(
                    label=display_name,
                    options=options,
                    key=select_key,
                    help=f"Select one or more {display_name.lower()}",
                    default=None
                )
                selections[column] = selection
            else:
                if show_all_option:
                    options = ["All"] + options

                selection = st.selectbox(
                    label=display_name,
                    options=options,
                    key=select_key,
                    help=f"Select {display_name.lower()}"
                )
                selections[column] = [selection] if selection != "All" else options[1:]

    # Return leaf level selections
    leaf_selection = selections.get(value_column, [])
    if isinstance(leaf_selection, list):
        return leaf_selection
    return [leaf_selection] if leaf_selection and leaf_selection != "All" else []


def get_filtered_dataframe_from_tree(
    df: pd.DataFrame,
    selected_values: List[str],
    value_column: str
) -> pd.DataFrame:
    """
    Filter DataFrame based on tree selection.

    Args:
        df: Source DataFrame
        selected_values: List of selected leaf values
        value_column: Column containing the values to filter on

    Returns:
        Filtered DataFrame
    """
    if not selected_values:
        return df

    return df[df[value_column].isin(selected_values)]


def render_company_hierarchy_selector(
    df: pd.DataFrame,
    key_prefix: str = "company_tree",
    show_summary: bool = True
) -> Tuple[List[str], pd.DataFrame]:
    """
    Specialized selector for Sector -> Industry -> Company hierarchy.

    Common pattern for Saudi financial data with pre-configured settings.

    Args:
        df: DataFrame with sector, industry, company_name columns
        key_prefix: Session state key prefix
        show_summary: Show selection summary

    Returns:
        Tuple of (selected company names, filtered DataFrame)
    """
    hierarchy = ["sector", "industry", "company_name"]

    # Validate required columns
    missing = [col for col in hierarchy if col not in df.columns]
    if missing:
        st.warning(f"Missing columns for hierarchy: {missing}")
        return [], df

    selected = render_tree_selector(
        df=df,
        hierarchy_columns=hierarchy,
        label="Company Selection",
        key_prefix=key_prefix,
        check_model="leaf"
    )

    filtered_df = get_filtered_dataframe_from_tree(
        df=df,
        selected_values=selected,
        value_column="company_name"
    )

    if show_summary and selected:
        st.caption(f"Selected: {len(selected)} companies")

    return selected, filtered_df
