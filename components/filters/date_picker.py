"""
Calendar Date Range Picker
==========================
Provides calendar-based date range selection using streamlit-calendar
with support for fiscal years, quarters, and quick presets.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
import pandas as pd
import streamlit as st

# Import guard for optional dependency
try:
    from streamlit_calendar import calendar
    CALENDAR_AVAILABLE = True
except ImportError:
    CALENDAR_AVAILABLE = False


class DatePickerManager:
    """
    Manager class for date range selection.

    Provides date picking with support for fiscal years, quarters,
    and quick presets common in financial analysis.

    Attributes:
        min_date: Minimum selectable date
        max_date: Maximum selectable date
        fiscal_year_start_month: Month when fiscal year starts (default: 1 for January)
        key_prefix: Prefix for session state keys
    """

    FISCAL_YEAR_START_MONTH: int = 1  # January (Saudi fiscal year)

    def __init__(
        self,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        fiscal_year_start_month: int = 1,
        key_prefix: str = "date"
    ):
        """
        Initialize the DatePickerManager.

        Args:
            min_date: Minimum selectable date
            max_date: Maximum selectable date
            fiscal_year_start_month: Month when fiscal year starts
            key_prefix: Session state key prefix
        """
        self.min_date = min_date or date(2016, 1, 1)
        self.max_date = max_date or date.today()
        self.fiscal_year_start_month = fiscal_year_start_month
        self.key_prefix = key_prefix
        self._initialize_session_state()

    def _initialize_session_state(self) -> None:
        """Initialize session state."""
        state_key = f"{self.key_prefix}_range"
        if state_key not in st.session_state:
            st.session_state[state_key] = {
                "start": self.min_date,
                "end": self.max_date
            }

    def render(
        self,
        label: str = "Select Date Range",
        show_presets: bool = True,
        show_fiscal_years: bool = True,
        container: Optional[Any] = None
    ) -> Tuple[date, date]:
        """
        Render date picker and return selected range.

        Args:
            label: Label for the picker
            show_presets: Show quick preset buttons
            show_fiscal_years: Show fiscal year selector
            container: Container to render in

        Returns:
            Tuple of (start_date, end_date)
        """
        if container is None:
            container = st

        container.markdown(f"**{label}**")

        # Show presets if requested
        if show_presets:
            self._render_presets(container)

        # Show fiscal year selector if requested
        if show_fiscal_years:
            self._render_fiscal_year_picker(container)

        # Render main date picker
        if CALENDAR_AVAILABLE:
            return self._render_with_calendar(container)
        else:
            return self._render_with_native_widgets(container)

    def _render_presets(self, container: Any) -> None:
        """Render quick preset buttons."""
        presets = get_date_presets(self.max_date)

        cols = container.columns(len(presets))
        for i, (name, (start, end)) in enumerate(presets.items()):
            if cols[i].button(name, key=f"{self.key_prefix}_preset_{name}"):
                self._set_range(start, end)
                st.rerun()

    def _render_fiscal_year_picker(self, container: Any) -> None:
        """Render fiscal year selector."""
        years = self._get_available_fiscal_years()

        selected_years = container.multiselect(
            "Fiscal Years",
            options=years,
            default=[],
            key=f"{self.key_prefix}_fiscal_years",
            help="Select fiscal years to filter"
        )

        if selected_years:
            start_date, end_date = fiscal_years_to_date_range(
                selected_years,
                self.fiscal_year_start_month
            )
            self._set_range(start_date, end_date)

    def _render_with_calendar(self, container: Any) -> Tuple[date, date]:
        """Render using streamlit-calendar."""
        state_key = f"{self.key_prefix}_range"
        current = st.session_state[state_key]

        # Calendar configuration for date range selection
        calendar_options = {
            "initialView": "dayGridMonth",
            "selectable": True,
            "selectMirror": True,
            "initialDate": current["start"].isoformat(),
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,dayGridYear"
            },
            "validRange": {
                "start": self.min_date.isoformat(),
                "end": self.max_date.isoformat()
            }
        }

        # Events to highlight selected range
        events = [{
            "title": "Selected Range",
            "start": current["start"].isoformat(),
            "end": (current["end"] + timedelta(days=1)).isoformat(),
            "backgroundColor": "#D4A84B",
            "borderColor": "#B8860B"
        }]

        result = calendar(
            events=events,
            options=calendar_options,
            key=f"{self.key_prefix}_calendar"
        )

        # Handle calendar selection
        if result.get("select"):
            selection = result["select"]
            start = datetime.fromisoformat(selection["start"].replace("Z", "")).date()
            end = datetime.fromisoformat(selection["end"].replace("Z", "")).date() - timedelta(days=1)
            self._set_range(start, end)

        return current["start"], current["end"]

    def _render_with_native_widgets(self, container: Any) -> Tuple[date, date]:
        """Render using native Streamlit date inputs."""
        state_key = f"{self.key_prefix}_range"
        current = st.session_state[state_key]

        col1, col2 = container.columns(2)

        with col1:
            start = st.date_input(
                "Start Date",
                value=current["start"],
                min_value=self.min_date,
                max_value=self.max_date,
                key=f"{self.key_prefix}_start"
            )

        with col2:
            end = st.date_input(
                "End Date",
                value=current["end"],
                min_value=self.min_date,
                max_value=self.max_date,
                key=f"{self.key_prefix}_end"
            )

        # Validate and update
        if start > end:
            container.warning("Start date must be before end date")
            return current["start"], current["end"]

        self._set_range(start, end)
        return start, end

    def _set_range(self, start: date, end: date) -> None:
        """Set the date range in session state."""
        state_key = f"{self.key_prefix}_range"
        st.session_state[state_key] = {"start": start, "end": end}

    def _get_available_fiscal_years(self) -> List[int]:
        """Get list of available fiscal years."""
        start_year = self.min_date.year
        end_year = self.max_date.year
        return list(range(start_year, end_year + 1))

    def get_current_range(self) -> Tuple[date, date]:
        """Get currently selected date range."""
        state_key = f"{self.key_prefix}_range"
        current = st.session_state.get(state_key, {})
        return (
            current.get("start", self.min_date),
            current.get("end", self.max_date)
        )


def fiscal_year_to_date_range(
    fiscal_year: int,
    start_month: int = 1
) -> Tuple[date, date]:
    """
    Convert a fiscal year to a date range.

    Args:
        fiscal_year: The fiscal year (e.g., 2024)
        start_month: Month when fiscal year starts (default: 1 for January)

    Returns:
        Tuple of (start_date, end_date)

    Example:
        >>> start, end = fiscal_year_to_date_range(2024, start_month=1)
        >>> # Returns (date(2024, 1, 1), date(2024, 12, 31))
    """
    if start_month == 1:
        # Calendar year alignment
        start = date(fiscal_year, 1, 1)
        end = date(fiscal_year, 12, 31)
    else:
        # Fiscal year spans two calendar years
        start = date(fiscal_year - 1, start_month, 1)

        # End is last day of month before start_month
        if start_month == 1:
            end = date(fiscal_year, 12, 31)
        else:
            end_year = fiscal_year
            end_month = start_month - 1
            # Get last day of end month
            if end_month in [4, 6, 9, 11]:
                end_day = 30
            elif end_month == 2:
                # Check for leap year
                if end_year % 4 == 0 and (end_year % 100 != 0 or end_year % 400 == 0):
                    end_day = 29
                else:
                    end_day = 28
            else:
                end_day = 31
            end = date(end_year, end_month, end_day)

    return start, end


def fiscal_years_to_date_range(
    fiscal_years: List[int],
    start_month: int = 1
) -> Tuple[date, date]:
    """
    Convert multiple fiscal years to a combined date range.

    Args:
        fiscal_years: List of fiscal years
        start_month: Month when fiscal year starts

    Returns:
        Tuple of (min_start_date, max_end_date)
    """
    if not fiscal_years:
        return date(2016, 1, 1), date.today()

    ranges = [fiscal_year_to_date_range(fy, start_month) for fy in fiscal_years]
    min_start = min(r[0] for r in ranges)
    max_end = max(r[1] for r in ranges)

    return min_start, max_end


def get_date_presets(reference_date: Optional[date] = None) -> Dict[str, Tuple[date, date]]:
    """
    Get common date range presets for financial analysis.

    Args:
        reference_date: Reference date for calculations (default: today)

    Returns:
        Dictionary mapping preset names to (start, end) tuples
    """
    ref = reference_date or date.today()

    return {
        "YTD": (date(ref.year, 1, 1), ref),
        "1Y": (ref - timedelta(days=365), ref),
        "3Y": (ref - timedelta(days=365 * 3), ref),
        "5Y": (ref - timedelta(days=365 * 5), ref),
        "All": (date(2016, 1, 1), ref),
    }


def get_fiscal_quarters(
    fiscal_year: int,
    start_month: int = 1
) -> Dict[str, Tuple[date, date]]:
    """
    Get fiscal quarter date ranges for a fiscal year.

    Args:
        fiscal_year: The fiscal year
        start_month: Month when fiscal year starts

    Returns:
        Dictionary mapping quarter names to (start, end) tuples
    """
    quarters = {}
    year_start, _ = fiscal_year_to_date_range(fiscal_year, start_month)

    for q in range(1, 5):
        q_start_month = ((start_month - 1 + (q - 1) * 3) % 12) + 1
        q_start_year = year_start.year if q_start_month >= start_month else year_start.year + 1

        q_end_month = ((q_start_month - 1 + 2) % 12) + 1
        q_end_year = q_start_year if q_end_month >= q_start_month else q_start_year + 1

        # Get last day of end month
        if q_end_month in [4, 6, 9, 11]:
            q_end_day = 30
        elif q_end_month == 2:
            if q_end_year % 4 == 0 and (q_end_year % 100 != 0 or q_end_year % 400 == 0):
                q_end_day = 29
            else:
                q_end_day = 28
        else:
            q_end_day = 31

        quarters[f"Q{q}"] = (
            date(q_start_year, q_start_month, 1),
            date(q_end_year, q_end_month, q_end_day)
        )

    return quarters


def render_date_range_picker(
    label: str = "Date Range",
    min_date: Optional[date] = None,
    max_date: Optional[date] = None,
    key_prefix: str = "date_range",
    show_presets: bool = True,
    container: Optional[Any] = None
) -> Tuple[date, date]:
    """
    Convenience function to render a date range picker.

    Args:
        label: Label for the picker
        min_date: Minimum selectable date
        max_date: Maximum selectable date
        key_prefix: Session state key prefix
        show_presets: Show quick preset buttons
        container: Container to render in

    Returns:
        Tuple of (start_date, end_date)

    Example:
        >>> start, end = render_date_range_picker(
        ...     label="Analysis Period",
        ...     min_date=date(2016, 1, 1),
        ...     show_presets=True
        ... )
    """
    manager = DatePickerManager(
        min_date=min_date,
        max_date=max_date,
        key_prefix=key_prefix
    )

    return manager.render(
        label=label,
        show_presets=show_presets,
        show_fiscal_years=False,
        container=container
    )


def render_fiscal_year_selector(
    available_years: Optional[List[int]] = None,
    key_prefix: str = "fiscal_year",
    multi_select: bool = True,
    default_years: Optional[List[int]] = None,
    container: Optional[Any] = None
) -> Union[List[int], int]:
    """
    Render a fiscal year selector.

    Args:
        available_years: List of available fiscal years
        key_prefix: Session state key prefix
        multi_select: Allow multiple year selection
        default_years: Default selected years
        container: Container to render in

    Returns:
        List of selected years (multi) or single year

    Example:
        >>> years = render_fiscal_year_selector(
        ...     available_years=list(range(2016, 2026)),
        ...     multi_select=True,
        ...     default_years=[2024]
        ... )
    """
    if container is None:
        container = st

    years = available_years or list(range(2016, date.today().year + 1))

    if multi_select:
        selected = container.multiselect(
            "Fiscal Year(s)",
            options=sorted(years, reverse=True),
            default=default_years or [],
            key=f"{key_prefix}_select",
            help="Select one or more fiscal years"
        )
        return selected
    else:
        selected = container.selectbox(
            "Fiscal Year",
            options=sorted(years, reverse=True),
            index=0 if not default_years else years.index(default_years[0]),
            key=f"{key_prefix}_select",
            help="Select a fiscal year"
        )
        return selected


def render_quick_date_presets(
    key_prefix: str = "preset",
    reference_date: Optional[date] = None,
    container: Optional[Any] = None
) -> Optional[Tuple[date, date]]:
    """
    Render quick date preset buttons.

    Args:
        key_prefix: Session state key prefix
        reference_date: Reference date for calculations
        container: Container to render in

    Returns:
        Selected date range if a preset was clicked, None otherwise
    """
    if container is None:
        container = st

    presets = get_date_presets(reference_date)

    cols = container.columns(len(presets))

    for i, (name, date_range) in enumerate(presets.items()):
        if cols[i].button(name, key=f"{key_prefix}_{name}", use_container_width=True):
            return date_range

    return None


def render_fiscal_quarter_selector(
    fiscal_year: int,
    key_prefix: str = "quarter",
    multi_select: bool = True,
    container: Optional[Any] = None
) -> List[str]:
    """
    Render a fiscal quarter selector for a specific year.

    Args:
        fiscal_year: The fiscal year to show quarters for
        key_prefix: Session state key prefix
        multi_select: Allow multiple quarter selection
        container: Container to render in

    Returns:
        List of selected quarter names (e.g., ["Q1", "Q3"])
    """
    if container is None:
        container = st

    quarters = ["Q1", "Q2", "Q3", "Q4"]

    if multi_select:
        selected = container.multiselect(
            f"Quarters ({fiscal_year})",
            options=quarters,
            key=f"{key_prefix}_{fiscal_year}",
            help="Select quarters to include"
        )
    else:
        selected = container.selectbox(
            f"Quarter ({fiscal_year})",
            options=quarters,
            key=f"{key_prefix}_{fiscal_year}",
            help="Select a quarter"
        )
        selected = [selected] if selected else []

    return selected


def filter_dataframe_by_fiscal_year(
    df: pd.DataFrame,
    fiscal_years: List[int],
    year_column: str = "fiscal_year"
) -> pd.DataFrame:
    """
    Filter DataFrame to include only specified fiscal years.

    Args:
        df: DataFrame to filter
        fiscal_years: List of fiscal years to include
        year_column: Name of the fiscal year column

    Returns:
        Filtered DataFrame
    """
    if not fiscal_years:
        return df

    if year_column not in df.columns:
        st.warning(f"Column '{year_column}' not found in DataFrame")
        return df

    return df[df[year_column].isin(fiscal_years)]


def filter_dataframe_by_date_range(
    df: pd.DataFrame,
    start_date: date,
    end_date: date,
    date_column: str = "filing_date"
) -> pd.DataFrame:
    """
    Filter DataFrame by date range.

    Args:
        df: DataFrame to filter
        start_date: Start of date range
        end_date: End of date range
        date_column: Name of the date column

    Returns:
        Filtered DataFrame
    """
    if date_column not in df.columns:
        st.warning(f"Column '{date_column}' not found in DataFrame")
        return df

    # Ensure column is datetime
    df_copy = df.copy()
    df_copy[date_column] = pd.to_datetime(df_copy[date_column])

    mask = (df_copy[date_column].dt.date >= start_date) & (df_copy[date_column].dt.date <= end_date)
    return df_copy[mask]


def render_complete_date_filter(
    df: pd.DataFrame,
    key_prefix: str = "date_filter",
    year_column: str = "fiscal_year",
    date_column: Optional[str] = None,
    container: Optional[Any] = None
) -> pd.DataFrame:
    """
    Render a complete date filtering interface with fiscal years and quarters.

    Args:
        df: DataFrame to filter
        key_prefix: Session state key prefix
        year_column: Name of fiscal year column
        date_column: Name of date column for range filtering (optional)
        container: Container to render in

    Returns:
        Filtered DataFrame

    Example:
        >>> filtered_df = render_complete_date_filter(
        ...     df=analytics_df,
        ...     year_column="fiscal_year"
        ... )
    """
    if container is None:
        container = st

    container.markdown("**Time Period**")

    # Get available years from data
    if year_column in df.columns:
        available_years = sorted(df[year_column].dropna().unique().tolist())
    else:
        available_years = list(range(2016, date.today().year + 1))

    # Quick presets
    preset = render_quick_date_presets(
        key_prefix=f"{key_prefix}_preset",
        container=container
    )

    # Fiscal year selector
    selected_years = render_fiscal_year_selector(
        available_years=available_years,
        key_prefix=f"{key_prefix}_fy",
        multi_select=True,
        container=container
    )

    # Apply filters
    filtered_df = df.copy()

    if selected_years:
        filtered_df = filter_dataframe_by_fiscal_year(
            filtered_df,
            selected_years,
            year_column
        )

    if preset and date_column and date_column in df.columns:
        filtered_df = filter_dataframe_by_date_range(
            filtered_df,
            preset[0],
            preset[1],
            date_column
        )

    # Show summary
    if selected_years:
        years_str = ", ".join(str(y) for y in sorted(selected_years))
        container.caption(f"Showing data for: {years_str}")

    return filtered_df
