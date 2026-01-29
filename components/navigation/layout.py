"""
Layout Components
==================
Antd-based layout components for the Saudi Financial Chat application,
including tabs, metric cards, and other UI elements.
"""

from typing import List, Optional, Dict, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import streamlit as st

# Try to import streamlit-antd-components
try:
    import streamlit_antd_components as sac
    ANTD_AVAILABLE = True
except ImportError:
    ANTD_AVAILABLE = False
    sac = None


class AlertType(Enum):
    """Alert type enumeration."""
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class CardSize(Enum):
    """Card size enumeration."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class TabItem:
    """Configuration for a tab item."""
    label: str
    icon: Optional[str] = None
    key: Optional[str] = None
    disabled: bool = False

    def __post_init__(self):
        if self.key is None:
            self.key = self.label.lower().replace(" ", "_")


@dataclass
class MetricConfig:
    """Configuration for a metric card."""
    label: str
    value: Union[str, int, float]
    delta: Optional[Union[str, int, float]] = None
    delta_color: str = "normal"  # "normal", "inverse", "off"
    icon: Optional[str] = None
    help_text: Optional[str] = None
    prefix: str = ""
    suffix: str = ""

    def formatted_value(self) -> str:
        """Get formatted value with prefix and suffix."""
        if isinstance(self.value, (int, float)):
            if self.value >= 1_000_000_000:
                formatted = f"{self.value / 1_000_000_000:.2f}B"
            elif self.value >= 1_000_000:
                formatted = f"{self.value / 1_000_000:.2f}M"
            elif self.value >= 1_000:
                formatted = f"{self.value / 1_000:.1f}K"
            else:
                formatted = f"{self.value:,.2f}" if isinstance(self.value, float) else f"{self.value:,}"
        else:
            formatted = str(self.value)

        return f"{self.prefix}{formatted}{self.suffix}"


@dataclass
class StepItem:
    """Configuration for a step item."""
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    status: str = "wait"  # "wait", "process", "finish", "error"


def render_tabs(
    items: List[TabItem],
    default_index: int = 0,
    key: str = "tabs",
    size: str = "default",
    align: str = "start",
    grow: bool = False,
) -> Optional[str]:
    """
    Render a tabbed interface.

    Uses streamlit-antd-components if available, otherwise falls back
    to Streamlit's native tabs.

    Args:
        items: List of TabItem configurations.
        default_index: Index of default selected tab.
        key: Unique key for the component.
        size: Tab size ("small", "default", "large").
        align: Tab alignment ("start", "center", "end").
        grow: Whether tabs should grow to fill width.

    Returns:
        Selected tab label, or None if no selection.
    """
    if not items:
        return None

    labels = [item.label for item in items]

    if ANTD_AVAILABLE:
        # Build sac.TabsItem list
        sac_items = []
        for item in items:
            sac_items.append(
                sac.TabsItem(
                    label=item.label,
                    icon=item.icon,
                    disabled=item.disabled,
                )
            )

        selected = sac.tabs(
            items=sac_items,
            index=default_index,
            key=key,
            size=size,
            align=align,
            grow=grow,
            color="#D4A84B",
            variant="outline",
        )
        return selected
    else:
        # Fallback to Streamlit tabs
        tabs = st.tabs(labels)

        # Store selected tab in session state
        if f"{key}_selected" not in st.session_state:
            st.session_state[f"{key}_selected"] = labels[default_index]

        # Return a container-based approach
        for i, (tab, item) in enumerate(zip(tabs, items)):
            if st.session_state.get(f"{key}_active") == i:
                return item.label

        return labels[default_index]


def render_metric_card(
    config: MetricConfig,
    key: Optional[str] = None,
) -> None:
    """
    Render a styled metric card.

    Args:
        config: MetricConfig with metric details.
        key: Optional unique key for the component.
    """
    # Build delta display
    delta_display = None
    if config.delta is not None:
        if isinstance(config.delta, (int, float)):
            delta_display = f"{config.delta:+.2f}%" if abs(config.delta) < 100 else f"{config.delta:+,.0f}"
        else:
            delta_display = str(config.delta)

    # Use Streamlit metric with custom styling
    if config.icon:
        st.markdown(
            f'<span style="color: #D4A84B; font-size: 24px; margin-right: 8px;">{config.icon}</span>',
            unsafe_allow_html=True,
        )

    st.metric(
        label=config.label,
        value=config.formatted_value(),
        delta=delta_display,
        delta_color=config.delta_color,
        help=config.help_text,
    )


def render_metric_row(
    metrics: List[MetricConfig],
    columns: Optional[int] = None,
) -> None:
    """
    Render a row of metric cards.

    Args:
        metrics: List of MetricConfig objects.
        columns: Number of columns (defaults to number of metrics, max 6).
    """
    if not metrics:
        return

    if columns is None:
        columns = min(len(metrics), 6)

    cols = st.columns(columns)

    for i, metric in enumerate(metrics):
        with cols[i % columns]:
            render_metric_card(metric)


def render_card(
    title: Optional[str] = None,
    content: Optional[str] = None,
    icon: Optional[str] = None,
    size: CardSize = CardSize.MEDIUM,
    hoverable: bool = True,
    bordered: bool = True,
) -> Any:
    """
    Render a styled card container.

    Args:
        title: Card title.
        content: Card content (markdown supported).
        icon: Icon to display in header.
        size: Card size enum.
        hoverable: Whether card has hover effect.
        bordered: Whether to show border.

    Returns:
        Streamlit container for adding content.
    """
    padding = {"small": "0.5rem", "medium": "1rem", "large": "1.5rem"}[size.value]
    border = "1px solid rgba(212, 168, 75, 0.3)" if bordered else "none"
    hover_css = """
        transition: all 0.3s ease;
    """ if hoverable else ""

    card_id = f"card_{hash(title or '')}"

    css = f"""
    <style>
    #{card_id} {{
        background: #1A1A1A;
        border: {border};
        border-radius: 12px;
        padding: {padding};
        {hover_css}
    }}
    #{card_id}:hover {{
        border-color: #D4A84B;
        box-shadow: 0 4px 20px rgba(212, 168, 75, 0.15);
    }}
    #{card_id} .card-title {{
        color: #D4A84B;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    #{card_id} .card-content {{
        color: #FFFFFF;
    }}
    </style>
    """

    st.markdown(css, unsafe_allow_html=True)

    html = f'<div id="{card_id}">'

    if title:
        icon_html = f'<span>{icon}</span>' if icon else ''
        html += f'<div class="card-title">{icon_html}{title}</div>'

    if content:
        html += f'<div class="card-content">{content}</div>'

    html += '</div>'

    st.markdown(html, unsafe_allow_html=True)

    return st.container()


def render_segmented_control(
    options: List[str],
    default_index: int = 0,
    key: str = "segmented",
    icons: Optional[List[str]] = None,
    size: str = "default",
    disabled: bool = False,
) -> Optional[str]:
    """
    Render a segmented control (button group).

    Args:
        options: List of option labels.
        default_index: Index of default selected option.
        key: Unique key for the component.
        icons: Optional list of icons for each option.
        size: Control size ("small", "default", "large").
        disabled: Whether control is disabled.

    Returns:
        Selected option label.
    """
    if not options:
        return None

    if ANTD_AVAILABLE:
        # Build items with icons if provided
        if icons and len(icons) == len(options):
            items = [
                sac.SegmentedItem(label=opt, icon=icon)
                for opt, icon in zip(options, icons)
            ]
        else:
            items = [sac.SegmentedItem(label=opt) for opt in options]

        selected = sac.segmented(
            items=items,
            index=default_index,
            key=key,
            size=size,
            disabled=disabled,
            color="#D4A84B",
        )
        return selected
    else:
        # Fallback to button columns
        cols = st.columns(len(options))

        if f"{key}_selected" not in st.session_state:
            st.session_state[f"{key}_selected"] = options[default_index]

        for i, (col, option) in enumerate(zip(cols, options)):
            with col:
                is_selected = st.session_state[f"{key}_selected"] == option
                button_type = "primary" if is_selected else "secondary"

                if st.button(
                    option,
                    key=f"{key}_{i}",
                    disabled=disabled,
                    use_container_width=True,
                    type=button_type,
                ):
                    st.session_state[f"{key}_selected"] = option
                    st.rerun()

        return st.session_state[f"{key}_selected"]


def render_steps(
    items: List[StepItem],
    current: int = 0,
    key: str = "steps",
    direction: str = "horizontal",
    size: str = "default",
) -> None:
    """
    Render a steps/progress indicator.

    Args:
        items: List of StepItem configurations.
        current: Index of current step.
        key: Unique key for the component.
        direction: "horizontal" or "vertical".
        size: Step size ("small", "default").
    """
    if not items:
        return

    if ANTD_AVAILABLE:
        sac_items = [
            sac.StepsItem(
                title=item.title,
                subtitle=item.description,
                icon=item.icon,
                disabled=(item.status == "wait" and items.index(item) > current),
            )
            for item in items
        ]

        sac.steps(
            items=sac_items,
            index=current,
            key=key,
            direction=direction,
            size=size,
            color="#D4A84B",
        )
    else:
        # Fallback to custom HTML steps
        if direction == "horizontal":
            cols = st.columns(len(items))
            for i, (col, item) in enumerate(zip(cols, items)):
                with col:
                    status_color = {
                        "wait": "#707070",
                        "process": "#D4A84B",
                        "finish": "#4CAF50",
                        "error": "#F44336",
                    }.get(item.status, "#707070")

                    is_current = i == current

                    st.markdown(
                        f"""
                        <div style="text-align: center;">
                            <div style="
                                width: 32px;
                                height: 32px;
                                border-radius: 50%;
                                background: {'#D4A84B' if is_current else 'transparent'};
                                border: 2px solid {status_color};
                                color: {'#0E0E0E' if is_current else status_color};
                                display: inline-flex;
                                align-items: center;
                                justify-content: center;
                                font-weight: 600;
                                margin-bottom: 8px;
                            ">{i + 1}</div>
                            <div style="color: {'#D4A84B' if is_current else '#B0B0B0'}; font-size: 14px;">
                                {item.title}
                            </div>
                            <div style="color: #707070; font-size: 12px;">
                                {item.description or ''}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
        else:
            for i, item in enumerate(items):
                is_current = i == current
                status_color = {
                    "wait": "#707070",
                    "process": "#D4A84B",
                    "finish": "#4CAF50",
                    "error": "#F44336",
                }.get(item.status, "#707070")

                st.markdown(
                    f"""
                    <div style="display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px;">
                        <div style="
                            min-width: 32px;
                            height: 32px;
                            border-radius: 50%;
                            background: {'#D4A84B' if is_current else 'transparent'};
                            border: 2px solid {status_color};
                            color: {'#0E0E0E' if is_current else status_color};
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: 600;
                        ">{i + 1}</div>
                        <div>
                            <div style="color: {'#D4A84B' if is_current else '#FFFFFF'}; font-weight: 500;">
                                {item.title}
                            </div>
                            <div style="color: #707070; font-size: 13px;">
                                {item.description or ''}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_alert(
    message: str,
    alert_type: AlertType = AlertType.INFO,
    title: Optional[str] = None,
    icon: Optional[str] = None,
    closable: bool = False,
    key: str = "alert",
) -> None:
    """
    Render an alert/notification banner.

    Args:
        message: Alert message text.
        alert_type: Type of alert (success, info, warning, error).
        title: Optional alert title.
        icon: Optional custom icon.
        closable: Whether alert can be dismissed.
        key: Unique key for the component.
    """
    if ANTD_AVAILABLE:
        sac.alert(
            message=message,
            description=title,
            type=alert_type.value,
            icon=icon,
            closable=closable,
            key=key,
        )
    else:
        # Fallback to Streamlit native alerts
        alert_map = {
            AlertType.SUCCESS: st.success,
            AlertType.INFO: st.info,
            AlertType.WARNING: st.warning,
            AlertType.ERROR: st.error,
        }

        display_message = f"**{title}**\n\n{message}" if title else message
        alert_map[alert_type](display_message)


def render_divider(
    text: Optional[str] = None,
    icon: Optional[str] = None,
    align: str = "center",
) -> None:
    """
    Render a styled divider.

    Args:
        text: Optional text to display on divider.
        icon: Optional icon before text.
        align: Text alignment ("left", "center", "right").
    """
    if ANTD_AVAILABLE and text:
        sac.divider(
            label=text,
            icon=icon,
            align=align,
            color="#D4A84B",
        )
    else:
        if text:
            st.markdown(
                f"""
                <div style="
                    display: flex;
                    align-items: center;
                    margin: 1rem 0;
                    color: #707070;
                ">
                    <div style="flex: 1; height: 1px; background: rgba(212, 168, 75, 0.3);"></div>
                    <span style="padding: 0 1rem; color: #D4A84B;">{icon or ''} {text}</span>
                    <div style="flex: 1; height: 1px; background: rgba(212, 168, 75, 0.3);"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.divider()


def render_empty_state(
    message: str = "No data available",
    icon: str = "inbox",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None,
) -> None:
    """
    Render an empty state placeholder.

    Args:
        message: Message to display.
        icon: Icon name to display.
        action_label: Optional action button label.
        action_callback: Optional callback for action button.
    """
    st.markdown(
        f"""
        <div style="
            text-align: center;
            padding: 3rem;
            color: #707070;
        ">
            <div style="font-size: 48px; margin-bottom: 1rem; opacity: 0.5;">
                {icon}
            </div>
            <div style="font-size: 16px; color: #B0B0B0;">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, use_container_width=True):
                action_callback()


def inject_layout_css() -> None:
    """
    Inject custom CSS for layout component styling.
    """
    css = """
    <style>
    /* Antd Components Theme Override */
    .ant-tabs-tab-active {
        color: #D4A84B !important;
    }

    .ant-tabs-ink-bar {
        background: #D4A84B !important;
    }

    .ant-segmented-item-selected {
        background: linear-gradient(135deg, #B8860B 0%, #D4A84B 100%) !important;
    }

    .ant-steps-item-process .ant-steps-item-icon {
        background: #D4A84B !important;
        border-color: #D4A84B !important;
    }

    .ant-steps-item-finish .ant-steps-item-icon {
        border-color: #4CAF50 !important;
    }

    .ant-alert {
        border-radius: 8px !important;
    }

    /* Card hover animations */
    .metric-card {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(212, 168, 75, 0.2);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
