"""
Main Navigation Component
==========================
Primary navigation component using streamlit-option-menu for the
Saudi Financial Chat application.
"""

from typing import List, Optional, Dict, Any, NamedTuple
from dataclasses import dataclass
import streamlit as st

# Try to import streamlit-option-menu
try:
    from streamlit_option_menu import option_menu
    OPTION_MENU_AVAILABLE = True
except ImportError:
    OPTION_MENU_AVAILABLE = False
    option_menu = None


# Default navigation icons matching the app theme
NAV_ICONS = {
    "home": "house",
    "chat": "chat-dots",
    "analytics": "graph-up",
    "companies": "building",
    "sectors": "pie-chart",
    "compare": "layout-split",
    "ratios": "calculator",
    "reports": "file-earmark-text",
    "settings": "gear",
    "help": "question-circle",
    "search": "search",
    "filter": "funnel",
    "download": "download",
    "upload": "upload",
    "refresh": "arrow-clockwise",
}


@dataclass
class NavItem:
    """Configuration for a navigation menu item."""
    label: str
    icon: str = "circle"
    key: Optional[str] = None
    disabled: bool = False

    def __post_init__(self):
        if self.key is None:
            self.key = self.label.lower().replace(" ", "_")


# Default navigation styles matching the gold/dark theme
DEFAULT_STYLES = {
    "container": {
        "padding": "0!important",
        "background-color": "transparent",
    },
    "icon": {
        "color": "#D4A84B",
        "font-size": "18px",
    },
    "nav-link": {
        "font-size": "14px",
        "text-align": "left",
        "margin": "0px",
        "padding": "10px 15px",
        "color": "#FFFFFF",
        "background-color": "transparent",
        "border-radius": "8px",
        "--hover-color": "#252525",
    },
    "nav-link-selected": {
        "background": "linear-gradient(135deg, #B8860B 0%, #D4A84B 100%)",
        "color": "#0E0E0E",
        "font-weight": "600",
    },
}

DEFAULT_HORIZONTAL_STYLES = {
    "container": {
        "padding": "5px!important",
        "background-color": "#1A1A1A",
        "border-radius": "12px",
        "border": "1px solid rgba(212, 168, 75, 0.2)",
    },
    "icon": {
        "color": "#D4A84B",
        "font-size": "16px",
    },
    "nav-link": {
        "font-size": "14px",
        "text-align": "center",
        "margin": "0px 5px",
        "padding": "8px 20px",
        "color": "#B0B0B0",
        "background-color": "transparent",
        "border-radius": "8px",
        "--hover-color": "#252525",
    },
    "nav-link-selected": {
        "background": "linear-gradient(135deg, #B8860B 0%, #D4A84B 100%)",
        "color": "#0E0E0E",
        "font-weight": "600",
    },
}


def render_main_nav(
    items: List[NavItem],
    default_index: int = 0,
    key: str = "main_nav",
    orientation: str = "vertical",
    styles: Optional[Dict[str, Any]] = None,
    menu_title: Optional[str] = None,
) -> Optional[str]:
    """
    Render the main navigation menu.

    Uses streamlit-option-menu if available, otherwise falls back
    to a simple radio button interface.

    Args:
        items: List of NavItem configurations.
        default_index: Index of default selected item.
        key: Unique key for the component.
        orientation: "vertical" or "horizontal".
        styles: Custom CSS styles dict (overrides defaults).
        menu_title: Optional title above the menu.

    Returns:
        Selected item label, or None if no selection.
    """
    if not items:
        return None

    labels = [item.label for item in items]
    icons = [item.icon for item in items]

    if OPTION_MENU_AVAILABLE:
        # Use streamlit-option-menu
        if styles is None:
            styles = DEFAULT_STYLES if orientation == "vertical" else DEFAULT_HORIZONTAL_STYLES

        selected = option_menu(
            menu_title=menu_title,
            options=labels,
            icons=icons,
            default_index=default_index,
            key=key,
            orientation=orientation,
            styles=styles,
        )
        return selected
    else:
        # Fallback to Streamlit radio buttons
        if menu_title:
            st.markdown(f"**{menu_title}**")

        if orientation == "horizontal":
            cols = st.columns(len(items))
            selected = None
            for i, (col, item) in enumerate(zip(cols, items)):
                with col:
                    if st.button(
                        f"{item.label}",
                        key=f"{key}_{item.key}",
                        disabled=item.disabled,
                        use_container_width=True,
                    ):
                        selected = item.label
                        st.session_state[f"{key}_selected"] = item.label

            # Return persisted selection
            return st.session_state.get(f"{key}_selected", labels[default_index])
        else:
            selected = st.radio(
                label="Navigation" if not menu_title else menu_title,
                options=labels,
                index=default_index,
                key=key,
                label_visibility="collapsed" if menu_title else "visible",
            )
            return selected


def render_sidebar_nav(
    items: List[NavItem],
    default_index: int = 0,
    key: str = "sidebar_nav",
    show_title: bool = True,
    title: str = "Navigation",
) -> Optional[str]:
    """
    Render navigation in the sidebar with appropriate styling.

    Args:
        items: List of NavItem configurations.
        default_index: Index of default selected item.
        key: Unique key for the component.
        show_title: Whether to show a title above the nav.
        title: Navigation section title.

    Returns:
        Selected item label.
    """
    with st.sidebar:
        return render_main_nav(
            items=items,
            default_index=default_index,
            key=key,
            orientation="vertical",
            menu_title=title if show_title else None,
        )


def render_horizontal_nav(
    items: List[NavItem],
    default_index: int = 0,
    key: str = "horizontal_nav",
) -> Optional[str]:
    """
    Render a horizontal navigation bar.

    Args:
        items: List of NavItem configurations.
        default_index: Index of default selected item.
        key: Unique key for the component.

    Returns:
        Selected item label.
    """
    return render_main_nav(
        items=items,
        default_index=default_index,
        key=key,
        orientation="horizontal",
        styles=DEFAULT_HORIZONTAL_STYLES,
        menu_title=None,
    )


def create_page_nav(
    pages: Dict[str, str],
    default_page: Optional[str] = None,
    key: str = "page_nav",
) -> Optional[str]:
    """
    Create navigation from a pages dictionary.

    Args:
        pages: Dict mapping page names to icon names.
        default_page: Default selected page name.
        key: Unique key for the component.

    Returns:
        Selected page name.
    """
    items = [
        NavItem(label=name, icon=icon)
        for name, icon in pages.items()
    ]

    default_index = 0
    if default_page:
        for i, item in enumerate(items):
            if item.label == default_page:
                default_index = i
                break

    return render_main_nav(items, default_index=default_index, key=key)


def create_default_nav() -> List[NavItem]:
    """
    Create default navigation items for the Saudi Financial app.

    Returns:
        List of NavItem for standard app navigation.
    """
    return [
        NavItem(label="Chat", icon=NAV_ICONS["chat"]),
        NavItem(label="Analytics", icon=NAV_ICONS["analytics"]),
        NavItem(label="Companies", icon=NAV_ICONS["companies"]),
        NavItem(label="Sectors", icon=NAV_ICONS["sectors"]),
        NavItem(label="Compare", icon=NAV_ICONS["compare"]),
        NavItem(label="Ratios", icon=NAV_ICONS["ratios"]),
    ]


def inject_nav_css() -> None:
    """
    Inject custom CSS for navigation styling.

    Enhances the option menu appearance to match the gold/dark theme.
    """
    css = """
    <style>
    /* Option Menu Container */
    .nav-link {
        transition: all 0.3s ease !important;
    }

    .nav-link:hover {
        transform: translateX(5px);
    }

    /* Active indicator */
    .nav-link-selected::before {
        content: "";
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 3px;
        height: 60%;
        background: #D4A84B;
        border-radius: 0 2px 2px 0;
    }

    /* Icon animation */
    .nav-link:hover .icon {
        transform: scale(1.1);
    }

    /* Mobile responsive */
    @media (max-width: 768px) {
        .nav-link {
            padding: 8px 10px !important;
            font-size: 13px !important;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_breadcrumb(
    path: List[str],
    separator: str = " / ",
    key: str = "breadcrumb",
) -> Optional[str]:
    """
    Render a breadcrumb navigation trail.

    Args:
        path: List of breadcrumb items (e.g., ["Home", "Analytics", "Revenue"]).
        separator: String to separate items.
        key: Unique key for the component.

    Returns:
        Clicked breadcrumb item, or None if no click.
    """
    clicked = None

    breadcrumb_html = '<div style="display: flex; align-items: center; gap: 5px; color: #B0B0B0; font-size: 14px;">'

    for i, item in enumerate(path):
        is_last = i == len(path) - 1

        if is_last:
            breadcrumb_html += f'<span style="color: #D4A84B; font-weight: 500;">{item}</span>'
        else:
            breadcrumb_html += f'<span style="cursor: pointer;" class="breadcrumb-item">{item}</span>'
            breadcrumb_html += f'<span style="color: #707070;">{separator}</span>'

    breadcrumb_html += '</div>'

    st.markdown(breadcrumb_html, unsafe_allow_html=True)

    # Handle clicks via session state (simplified version)
    # For full interactivity, would need JavaScript integration

    return clicked


def get_nav_state(key: str = "main_nav") -> Optional[str]:
    """
    Get the current navigation selection from session state.

    Args:
        key: Navigation component key.

    Returns:
        Currently selected navigation item.
    """
    return st.session_state.get(key)


def set_nav_state(value: str, key: str = "main_nav") -> None:
    """
    Set the navigation selection in session state.

    Args:
        value: Navigation item to select.
        key: Navigation component key.
    """
    st.session_state[key] = value
