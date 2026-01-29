"""
Relationship Graph Visualization Components.

Provides network graph visualization for company ownership structures
and relationships using the streamlit-agraph library.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

# Optional dependency guard
try:
    from streamlit_agraph import agraph, Node, Edge, Config
    AGRAPH_AVAILABLE = True
except ImportError:
    AGRAPH_AVAILABLE = False
    agraph = None
    Node = None
    Edge = None
    Config = None

try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None


# Saudi Financial theme color palette
THEME_COLORS = {
    "gold_primary": "#D4A84B",
    "gold_light": "#E8C872",
    "gold_dark": "#B8860B",
    "background_dark": "#0E0E0E",
    "background_light": "#1A1A1A",
    "positive": "#4CAF50",
    "negative": "#F44336",
    "neutral": "#9E9E9E",
    "text_primary": "#FFFFFF",
    "text_secondary": "#B0B0B0",
    "node_border": "#333333",
}

# Sector-specific colors for node styling
SECTOR_COLORS = {
    "Banks": "#D4A84B",
    "Banking": "#D4A84B",
    "Petrochemicals": "#4CAF50",
    "Chemicals": "#4CAF50",
    "Retail": "#2196F3",
    "Consumer Services": "#2196F3",
    "Telecom": "#9C27B0",
    "Telecommunications": "#9C27B0",
    "Insurance": "#FF9800",
    "Real Estate": "#00BCD4",
    "REITs": "#00BCD4",
    "Healthcare": "#E91E63",
    "Health Care": "#E91E63",
    "Materials": "#795548",
    "Utilities": "#607D8B",
    "Food & Beverages": "#8BC34A",
    "Consumer Staples": "#8BC34A",
    "Energy": "#FF5722",
    "Capital Goods": "#3F51B5",
    "Industrials": "#3F51B5",
    "Transportation": "#009688",
    "Media": "#673AB7",
    "Technology": "#03A9F4",
    "Diversified": "#9E9E9E",
    "default": "#757575",
}


class RelationshipType(str, Enum):
    """Types of relationships between entities."""
    OWNS = "owns"
    SUBSIDIARY = "subsidiary"
    PARTNERSHIP = "partnership"
    INVESTOR = "investor"
    BOARD_MEMBER = "board_member"
    SUPPLIER = "supplier"
    CUSTOMER = "customer"
    COMPETITOR = "competitor"
    AFFILIATE = "affiliate"


# Relationship styling configuration
RELATIONSHIP_STYLES = {
    RelationshipType.OWNS: {
        "color": THEME_COLORS["gold_primary"],
        "width": 3,
        "dashes": False,
        "arrows": "to",
        "label": "owns",
    },
    RelationshipType.SUBSIDIARY: {
        "color": THEME_COLORS["gold_light"],
        "width": 2,
        "dashes": False,
        "arrows": "to",
        "label": "subsidiary",
    },
    RelationshipType.PARTNERSHIP: {
        "color": THEME_COLORS["positive"],
        "width": 2,
        "dashes": True,
        "arrows": "to;from",
        "label": "partner",
    },
    RelationshipType.INVESTOR: {
        "color": "#2196F3",
        "width": 2,
        "dashes": False,
        "arrows": "to",
        "label": "invests in",
    },
    RelationshipType.BOARD_MEMBER: {
        "color": "#9C27B0",
        "width": 1,
        "dashes": True,
        "arrows": "to",
        "label": "board",
    },
    RelationshipType.SUPPLIER: {
        "color": "#FF9800",
        "width": 1,
        "dashes": False,
        "arrows": "to",
        "label": "supplies",
    },
    RelationshipType.CUSTOMER: {
        "color": "#00BCD4",
        "width": 1,
        "dashes": False,
        "arrows": "to",
        "label": "customer",
    },
    RelationshipType.COMPETITOR: {
        "color": THEME_COLORS["negative"],
        "width": 1,
        "dashes": True,
        "arrows": None,
        "label": "competes",
    },
    RelationshipType.AFFILIATE: {
        "color": THEME_COLORS["neutral"],
        "width": 1,
        "dashes": True,
        "arrows": None,
        "label": "affiliate",
    },
}


@dataclass
class CompanyNode:
    """
    Representation of a company node in the relationship graph.

    Attributes:
        id: Unique identifier for the node
        name: Display name
        sector: Business sector for color coding
        market_cap: Market capitalization (affects node size)
        symbol: Stock ticker symbol
        metadata: Additional data to store with node
    """
    id: str
    name: str
    sector: str = "default"
    market_cap: Optional[float] = None
    symbol: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def color(self) -> str:
        """Get sector-based color."""
        return SECTOR_COLORS.get(self.sector, SECTOR_COLORS["default"])

    @property
    def size(self) -> int:
        """Calculate node size based on market cap."""
        if self.market_cap is None:
            return 25

        # Scale: 20-50 based on market cap
        if self.market_cap < 1e9:
            return 20
        elif self.market_cap < 10e9:
            return 25
        elif self.market_cap < 50e9:
            return 30
        elif self.market_cap < 100e9:
            return 40
        else:
            return 50


@dataclass
class RelationshipEdge:
    """
    Representation of a relationship edge in the graph.

    Attributes:
        source: Source node ID
        target: Target node ID
        relationship_type: Type of relationship
        weight: Relationship strength (e.g., ownership percentage)
        label: Custom label override
        metadata: Additional data to store with edge
    """
    source: str
    target: str
    relationship_type: RelationshipType = RelationshipType.OWNS
    weight: Optional[float] = None
    label: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def style(self) -> Dict[str, Any]:
        """Get style configuration for this relationship type."""
        return RELATIONSHIP_STYLES.get(
            self.relationship_type,
            RELATIONSHIP_STYLES[RelationshipType.AFFILIATE]
        )

    @property
    def display_label(self) -> str:
        """Get display label for edge."""
        if self.label:
            return self.label
        if self.weight is not None:
            return f"{self.style['label']} ({self.weight:.1f}%)"
        return self.style["label"]


def create_company_node(
    id: str,
    name: str,
    sector: str = "default",
    market_cap: Optional[float] = None,
    symbol: Optional[str] = None,
    **metadata,
) -> "Node":
    """
    Create an agraph Node for a company.

    Args:
        id: Unique identifier
        name: Company display name
        sector: Business sector for coloring
        market_cap: Market capitalization for sizing
        symbol: Stock ticker symbol
        **metadata: Additional node data

    Returns:
        agraph Node object
    """
    if not AGRAPH_AVAILABLE:
        raise ImportError("streamlit-agraph is required. Install with: pip install streamlit-agraph")

    company = CompanyNode(
        id=id,
        name=name,
        sector=sector,
        market_cap=market_cap,
        symbol=symbol,
        metadata=metadata,
    )

    # Build label
    label = name
    if symbol:
        label = f"{name}\n({symbol})"

    return Node(
        id=id,
        label=label,
        size=company.size,
        color=company.color,
        font={"color": THEME_COLORS["text_primary"], "size": 12},
        borderWidth=2,
        borderWidthSelected=4,
        shape="dot",
        title=_build_node_tooltip(company),
    )


def create_relationship_edge(
    source: str,
    target: str,
    relationship_type: Union[RelationshipType, str] = RelationshipType.OWNS,
    weight: Optional[float] = None,
    label: Optional[str] = None,
    **metadata,
) -> "Edge":
    """
    Create an agraph Edge for a relationship.

    Args:
        source: Source node ID
        target: Target node ID
        relationship_type: Type of relationship
        weight: Relationship strength (e.g., ownership %)
        label: Custom label override
        **metadata: Additional edge data

    Returns:
        agraph Edge object
    """
    if not AGRAPH_AVAILABLE:
        raise ImportError("streamlit-agraph is required. Install with: pip install streamlit-agraph")

    # Convert string to enum if needed
    if isinstance(relationship_type, str):
        try:
            relationship_type = RelationshipType(relationship_type.lower())
        except ValueError:
            relationship_type = RelationshipType.AFFILIATE

    edge = RelationshipEdge(
        source=source,
        target=target,
        relationship_type=relationship_type,
        weight=weight,
        label=label,
        metadata=metadata,
    )

    style = edge.style

    return Edge(
        source=source,
        target=target,
        label=edge.display_label,
        color=style["color"],
        width=style["width"],
        dashes=style["dashes"],
        arrows=style["arrows"],
        font={"color": THEME_COLORS["text_secondary"], "size": 10},
    )


def build_ownership_graph(
    ownership_data: Union[pd.DataFrame, List[Dict[str, Any]]],
    parent_column: str = "parent",
    child_column: str = "child",
    ownership_column: str = "ownership_pct",
    parent_sector_column: Optional[str] = "parent_sector",
    child_sector_column: Optional[str] = "child_sector",
    parent_market_cap_column: Optional[str] = None,
    child_market_cap_column: Optional[str] = None,
) -> Tuple[List["Node"], List["Edge"]]:
    """
    Build ownership graph from data.

    Args:
        ownership_data: DataFrame or list of ownership records
        parent_column: Column name for parent company
        child_column: Column name for child/subsidiary company
        ownership_column: Column name for ownership percentage
        parent_sector_column: Column for parent sector (optional)
        child_sector_column: Column for child sector (optional)
        parent_market_cap_column: Column for parent market cap (optional)
        child_market_cap_column: Column for child market cap (optional)

    Returns:
        Tuple of (nodes, edges) for agraph
    """
    if not AGRAPH_AVAILABLE:
        raise ImportError("streamlit-agraph is required. Install with: pip install streamlit-agraph")

    # Convert to DataFrame if needed
    if isinstance(ownership_data, list):
        df = pd.DataFrame(ownership_data)
    else:
        df = ownership_data.copy()

    nodes_dict: Dict[str, Node] = {}
    edges: List[Edge] = []

    for _, row in df.iterrows():
        parent_id = str(row[parent_column])
        child_id = str(row[child_column])
        ownership_pct = row.get(ownership_column, 100.0)

        # Create parent node if not exists
        if parent_id not in nodes_dict:
            parent_sector = row.get(parent_sector_column, "default") if parent_sector_column else "default"
            parent_mcap = row.get(parent_market_cap_column) if parent_market_cap_column else None

            nodes_dict[parent_id] = create_company_node(
                id=parent_id,
                name=parent_id,
                sector=parent_sector,
                market_cap=parent_mcap,
            )

        # Create child node if not exists
        if child_id not in nodes_dict:
            child_sector = row.get(child_sector_column, "default") if child_sector_column else "default"
            child_mcap = row.get(child_market_cap_column) if child_market_cap_column else None

            nodes_dict[child_id] = create_company_node(
                id=child_id,
                name=child_id,
                sector=child_sector,
                market_cap=child_mcap,
            )

        # Determine relationship type based on ownership
        if ownership_pct >= 50:
            rel_type = RelationshipType.SUBSIDIARY
        elif ownership_pct > 0:
            rel_type = RelationshipType.OWNS
        else:
            rel_type = RelationshipType.AFFILIATE

        # Create edge
        edges.append(create_relationship_edge(
            source=parent_id,
            target=child_id,
            relationship_type=rel_type,
            weight=ownership_pct,
        ))

    return list(nodes_dict.values()), edges


def render_relationship_graph(
    nodes: List["Node"],
    edges: List["Edge"],
    height: int = 600,
    width: Optional[int] = None,
    physics_enabled: bool = True,
    hierarchical: bool = False,
    direction: str = "UD",
    node_spacing: int = 150,
    level_separation: int = 200,
    show_legend: bool = True,
    key: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Render the relationship graph with agraph.

    Args:
        nodes: List of Node objects
        edges: List of Edge objects
        height: Graph height in pixels
        width: Graph width (None for full width)
        physics_enabled: Whether to enable physics simulation
        hierarchical: Whether to use hierarchical layout
        direction: Layout direction ('UD', 'DU', 'LR', 'RL')
        node_spacing: Spacing between nodes
        level_separation: Spacing between hierarchy levels
        show_legend: Whether to show relationship type legend
        key: Unique key for the component

    Returns:
        Selected node/edge data if interaction occurred
    """
    if not AGRAPH_AVAILABLE:
        raise ImportError("streamlit-agraph is required. Install with: pip install streamlit-agraph")

    if not STREAMLIT_AVAILABLE:
        raise ImportError("streamlit is required")

    # Show legend if requested
    if show_legend:
        _render_legend()

    # Configure graph options
    config = Config(
        width=width or "100%",
        height=height,
        directed=True,
        physics=physics_enabled,
        hierarchical=hierarchical,
        nodeHighlightBehavior=True,
        highlightColor=THEME_COLORS["gold_light"],
        collapsible=True,
        node={
            "highlightStrokeColor": THEME_COLORS["gold_primary"],
        },
        link={
            "highlightColor": THEME_COLORS["gold_light"],
        },
    )

    # Add hierarchical layout settings if enabled
    if hierarchical:
        config.hierarchical_sort_method = "directed"
        config.hierarchical_direction = direction
        config.hierarchical_node_spacing = node_spacing
        config.hierarchical_level_separation = level_separation

    # Render graph
    return agraph(
        nodes=nodes,
        edges=edges,
        config=config,
    )


def _build_node_tooltip(company: CompanyNode) -> str:
    """Build HTML tooltip for a company node."""
    parts = [f"<b>{company.name}</b>"]

    if company.symbol:
        parts.append(f"Symbol: {company.symbol}")

    parts.append(f"Sector: {company.sector}")

    if company.market_cap:
        if company.market_cap >= 1e12:
            mcap_str = f"{company.market_cap/1e12:.1f}T"
        elif company.market_cap >= 1e9:
            mcap_str = f"{company.market_cap/1e9:.1f}B"
        else:
            mcap_str = f"{company.market_cap/1e6:.1f}M"
        parts.append(f"Market Cap: SAR {mcap_str}")

    for key, value in company.metadata.items():
        parts.append(f"{key}: {value}")

    return "<br>".join(parts)


def _render_legend() -> None:
    """Render relationship type legend."""
    if not STREAMLIT_AVAILABLE:
        return

    st.markdown("""
    <style>
    .graph-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        padding: 10px;
        background-color: #1A1A1A;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.85rem;
        color: #B0B0B0;
    }
    .legend-line {
        width: 30px;
        height: 3px;
        border-radius: 2px;
    }
    .legend-line-dashed {
        width: 30px;
        height: 0;
        border-top: 3px dashed;
    }
    </style>
    """, unsafe_allow_html=True)

    legend_items = []
    for rel_type, style in RELATIONSHIP_STYLES.items():
        line_class = "legend-line-dashed" if style["dashes"] else "legend-line"
        line_style = f"background-color: {style['color']};" if not style["dashes"] else f"border-color: {style['color']};"

        legend_items.append(
            f'<div class="legend-item">'
            f'<div class="{line_class}" style="{line_style}"></div>'
            f'<span>{rel_type.value.replace("_", " ").title()}</span>'
            f'</div>'
        )

    st.markdown(
        f'<div class="graph-legend">{"".join(legend_items)}</div>',
        unsafe_allow_html=True
    )


def create_sector_graph(
    companies: List[Dict[str, Any]],
    relationships: Optional[List[Dict[str, Any]]] = None,
    name_key: str = "name",
    sector_key: str = "sector",
    market_cap_key: str = "market_cap",
    symbol_key: str = "symbol",
) -> Tuple[List["Node"], List["Edge"]]:
    """
    Create a graph showing companies grouped by sector.

    Args:
        companies: List of company dictionaries
        relationships: Optional list of relationships between companies
        name_key: Key for company name in dict
        sector_key: Key for sector in dict
        market_cap_key: Key for market cap in dict
        symbol_key: Key for symbol in dict

    Returns:
        Tuple of (nodes, edges)
    """
    if not AGRAPH_AVAILABLE:
        raise ImportError("streamlit-agraph is required. Install with: pip install streamlit-agraph")

    nodes = []
    edges = []
    sector_nodes: Dict[str, str] = {}  # sector -> node_id

    # Create sector center nodes
    sectors = set(c.get(sector_key, "default") for c in companies)
    for sector in sectors:
        sector_id = f"sector_{sector}"
        sector_nodes[sector] = sector_id

        nodes.append(Node(
            id=sector_id,
            label=sector,
            size=40,
            color=SECTOR_COLORS.get(sector, SECTOR_COLORS["default"]),
            font={"color": THEME_COLORS["text_primary"], "size": 14, "bold": True},
            shape="diamond",
            borderWidth=3,
        ))

    # Create company nodes
    for company in companies:
        company_id = str(company.get(name_key, company.get("id", "")))
        sector = company.get(sector_key, "default")

        nodes.append(create_company_node(
            id=company_id,
            name=company.get(name_key, company_id),
            sector=sector,
            market_cap=company.get(market_cap_key),
            symbol=company.get(symbol_key),
        ))

        # Connect to sector
        edges.append(Edge(
            source=sector_nodes[sector],
            target=company_id,
            color=SECTOR_COLORS.get(sector, SECTOR_COLORS["default"]),
            width=1,
            dashes=True,
        ))

    # Add explicit relationships if provided
    if relationships:
        for rel in relationships:
            edges.append(create_relationship_edge(
                source=str(rel.get("source", rel.get("from"))),
                target=str(rel.get("target", rel.get("to"))),
                relationship_type=rel.get("type", RelationshipType.AFFILIATE),
                weight=rel.get("weight"),
                label=rel.get("label"),
            ))

    return nodes, edges


def find_connected_companies(
    nodes: List["Node"],
    edges: List["Edge"],
    company_id: str,
    max_depth: int = 2,
) -> Set[str]:
    """
    Find all companies connected to a given company within max depth.

    Args:
        nodes: List of nodes in graph
        edges: List of edges in graph
        company_id: Starting company ID
        max_depth: Maximum relationship depth to traverse

    Returns:
        Set of connected company IDs
    """
    connected = {company_id}
    current_level = {company_id}

    for _ in range(max_depth):
        next_level = set()

        for edge in edges:
            if edge.source in current_level and edge.target not in connected:
                next_level.add(edge.target)
            if hasattr(edge, 'to') and edge.to in current_level and edge.source not in connected:
                next_level.add(edge.source)

        connected.update(next_level)
        current_level = next_level

        if not next_level:
            break

    return connected
