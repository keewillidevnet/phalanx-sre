# battlemap/topology_map.py
from pathlib import Path
import json
import math

import plotly.graph_objects as go

# Optional deps handled gracefully
try:
    import yaml
except Exception:
    yaml = None

try:
    import networkx as nx
except Exception:
    nx = None

DEMO_TOPO = Path("examples/demo_topology.yaml")


# --------------------------- helpers ---------------------------

def _coalesce_edges(topology: dict):
    """Support either 'edges' or 'links' keys in YAML."""
    if "edges" in topology and isinstance(topology["edges"], list):
        return topology["edges"]
    if "links" in topology and isinstance(topology["links"], list):
        return topology["links"]
    return []

def _kpi(edge, key, default=None):
    # normalize common KPI keys across different samples
    return (
        edge.get(key)
        or edge.get(f"kpi_{key}")
        or edge.get(f"{key}_ms")
        or edge.get(f"latency_{key}")
        or default
    )

def _latency_to_color(lat_ms: float | None) -> str:
    """
    Map latency to a color on green→yellow→red.
    <20ms green, ~50ms yellow, >=120ms red.
    """
    if lat_ms is None:
        return "#7a7f8c"  # neutral
    # clamp 0..120
    x = max(0.0, min(120.0, float(lat_ms))) / 120.0
    # simple GYR ramp
    # green (0,170,0) -> yellow (255,200,0) -> red (220,0,0)
    if x < 0.5:
        t = x / 0.5
        r = int(0 + t * (255 - 0))
        g = int(170 + t * (200 - 170))
        b = 0
    else:
        t = (x - 0.5) / 0.5
        r = int(255 + t * (220 - 255))
        g = int(200 + t * (0 - 200))
        b = 0
    return f"rgb({r},{g},{b})"

def _node_color(status: str | None) -> str:
    if (status or "").lower() in ("degraded", "warning"):
        return "#ffb020"  # amber
    if (status or "").lower() in ("down", "critical", "error", "failed"):
        return "#e11d48"  # red
    return "#22c55e"      # green

def _layout_positions(g):
    """Stable-ish layout. Use provided xy if present; else spring_layout."""
    if nx is None:
        # fallback fixed pseudo-positions if networkx missing
        nodes = list(g)
        n = len(nodes)
        return {n_id: (math.cos(i*2*math.pi/n), math.sin(i*2*math.pi/n))
                for i, n_id in enumerate(nodes)}
    # prefer explicit coordinates from node data
    pos = {}
    missing = []
    for n, data in g.nodes(data=True):
        if "x" in data and "y" in data:
            pos[n] = (float(data["x"]), float(data["y"]))
        else:
            missing.append(n)
    if missing:
        spring = nx.spring_layout(g, seed=42, k=1.1)
        for n in missing:
            pos[n] = spring[n]
    return pos


# --------------------------- rendering ---------------------------

def _figure_for_topology(topology: dict):
    if nx is None:
        raise RuntimeError("networkx is required for battlemap rendering")
    nodes = topology.get("nodes", [])
    edges = _coalesce_edges(topology)

    # Build graph
    g = nx.DiGraph()
    for n in nodes:
        nid = n.get("id") or n.get("name")
        if not nid:
            continue
        g.add_node(nid, **{k: v for k, v in n.items() if k not in ("id", "name")})
    for e in edges:
        src = e.get("source"); dst = e.get("target")
        if not (src and dst) or src not in g or dst not in g:
            continue
        g.add_edge(src, dst, **e)

    pos = _layout_positions(g)

    # Edge traces
    edge_x, edge_y, edge_colors = [], [], []
    edge_text_x, edge_text_y, edge_labels = [], [], []
    for u, v, data in g.edges(data=True):
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
        lat = _kpi(data, "latency_ms")
        edge_colors.append(_latency_to_color(lat))
        # label position (midpoint)
        mx = (x0 + x1) / 2.0; my = (y0 + y1) / 2.0
        edge_text_x.append(mx); edge_text_y.append(my)
        edge_labels.append(f"{lat if lat is not None else '?'} ms")

    # Plotly wants a single color, so we split edges per-color batch
    # For simplicity, draw lines with a single neutral color and show latency via labels and node color.
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y, mode="lines",
        line=dict(width=2, color="#7a7f8c"),
        hoverinfo="none", name="links"
    )

    label_trace = go.Scatter(
        x=edge_text_x, y=edge_text_y, mode="text",
        text=edge_labels, textposition="middle center",
        textfont=dict(size=12), hoverinfo="none", name="latency"
    )

    # Node trace
    node_x, node_y, node_text, node_colors = [], [], [], []
    for n, data in g.nodes(data=True):
        node_x.append(pos[n][0]); node_y.append(pos[n][1])
        label = data.get("label", n)
        role = data.get("role", "node")
        status = data.get("status", "healthy")
        node_text.append(f"{label}<br>role={role} · status={status}")
        node_colors.append(_node_color(status))

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=[n for n in g.nodes()],
        textposition="bottom center",
        hovertext=node_text, hoverinfo="text",
        marker=dict(size=18, color=node_colors, line=dict(width=1, color="#1f2937")),
        name="nodes"
    )

    fig = go.Figure(data=[edge_trace, label_trace, node_trace])
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


# --------------------------- public API ---------------------------

def render_battlemap_if_available():
    """Streamlit-friendly wrapper that reads YAML and renders the battlemap."""
    import streamlit as st
    if not DEMO_TOPO.exists():
        st.info("No topology file found (expected `examples/demo_topology.yaml`).")
        return
    if yaml is None:
        st.warning("PyYAML not installed; cannot parse topology file.")
        return
    try:
        topology = yaml.safe_load(DEMO_TOPO.read_text()) or {}
        fig = _figure_for_topology(topology)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render battlemap: {e}")