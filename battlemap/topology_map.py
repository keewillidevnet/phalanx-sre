# battlemap/topology_map.py
from pathlib import Path
import math
from typing import Dict, Any, List, Tuple

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

# ---- Tunables ---------------------------------------------------
THRESHOLDS = {
    "good": 20,    # <= green
    "warn": 80,    # <= yellow
}   # > warn => red
EDGE_WIDTHS = {"good": 2.5, "warn": 3.5, "bad": 5.0}
NODE_SIZE_BASE = 16
NODE_SIZE_FACTOR = 8
ARROW_OPACITY = 0.85
ARROW_HEAD = 7
ARROW_STEM = 0.94           # where arrow head sits along the edge
LABEL_OFFSET = 0.045        # perpendicular offset for latency labels
# ----------------------------------------------------------------

# --------------------------- helpers ----------------------------

def _coalesce_edges(topology: dict) -> List[dict]:
    if "edges" in topology and isinstance(topology["edges"], list):
        return topology["edges"]
    if "links" in topology and isinstance(topology["links"], list):
        return topology["links"]
    return []

def _bucket_latency(ms: float | None) -> str:
    if ms is None:
        return "warn"
    if ms <= THRESHOLDS["good"]:
        return "good"
    if ms <= THRESHOLDS["warn"]:
        return "warn"
    return "bad"

def _latency_color(bucket: str) -> str:
    return {"good": "#22c55e", "warn": "#f9a825", "bad": "#ef4444"}.get(bucket, "#9ca3af")

def _node_color(status: str | None) -> str:
    s = (status or "").lower()
    if s in ("degraded", "warning"):
        return "#f59e0b"
    if s in ("down", "critical", "error", "failed"):
        return "#ef4444"
    return "#22c55e"

def _layout_positions(g) -> Dict[Any, Tuple[float, float]]:
    if nx is None:
        nodes = list(g)
        n = max(1, len(nodes))
        return {nid: (math.cos(i*2*math.pi/n), math.sin(i*2*math.pi/n)) for i, nid in enumerate(nodes)}
    pos = {}
    missing = []
    for n, data in g.nodes(data=True):
        if "x" in data and "y" in data:
            pos[n] = (float(data["x"]), float(data["y"]))
        else:
            missing.append(n)
    if missing:
        spring = nx.spring_layout(g, seed=42, k=1.0)
        for n in missing:
            pos[n] = spring[n]
    return pos

def _node_size_for_degree(deg: int) -> float:
    return NODE_SIZE_BASE + NODE_SIZE_FACTOR * math.log2(max(1, deg) + 1)

def _perp_offset(x0, y0, x1, y1, frac=0.5, offset=0.05) -> Tuple[float, float]:
    """Point at 'frac' along edge plus a perpendicular offset of 'offset'."""
    mx = x0 + (x1 - x0) * frac
    my = y0 + (y1 - y0) * frac
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy) or 1.0
    # unit normal (rotate 90°)
    nx_ = -dy / length
    ny_ = dx / length
    return mx + nx_ * offset, my + ny_ * offset

# --------------------------- rendering --------------------------

def _figure_for_topology(topology: dict) -> go.Figure:
    if nx is None:
        raise RuntimeError("networkx is required for battlemap rendering")

    nodes = topology.get("nodes", [])
    edges = _coalesce_edges(topology)

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

    # ---- Nodes: size by degree, color by status, label by "label" or id,
    # and include a summary of adjacent edge KPIs in the hover text.
    node_x, node_y, node_text, node_sizes, node_colors, node_labels = [], [], [], [], [], []
    degrees = dict(g.degree())

    def edge_kpi_summary(nid: str) -> str:
        inbound  = [data for _, _, data in g.in_edges(nid, data=True)]
        outbound = [data for _, _, data in g.out_edges(nid, data=True)]
        def summarize(edges):
            if not edges:
                return None
            lat    = [e.get("latency_ms") or e.get("kpi_latency_ms") for e in edges if (e.get("latency_ms") or e.get("kpi_latency_ms")) is not None]
            loss   = [e.get("loss_pct")   for e in edges if e.get("loss_pct")   is not None]
            jitter = [e.get("jitter_ms")  for e in edges if e.get("jitter_ms")  is not None]
            parts = []
            if lat:    parts.append(f"lat max={max(lat):g} ms")
            if loss:   parts.append(f"loss max={max(loss):g}%")
            if jitter: parts.append(f"jitter max={max(jitter):g} ms")
            return ", ".join(parts) if parts else None

        inbound_s  = summarize(inbound)
        outbound_s = summarize(outbound)
        lines = []
        if inbound_s:  lines.append(f"inbound: {inbound_s}")
        if outbound_s: lines.append(f"outbound: {outbound_s}")
        return "<br>".join(lines)

    for n, data in g.nodes(data=True):
        x, y = pos[n]
        node_x.append(x); node_y.append(y)
        status = data.get("status", "healthy")
        label  = data.get("label", n)
        role   = data.get("role", "node")

        summary = edge_kpi_summary(n)
        hover = f"{label}<br>role={role} · status={status}"
        if summary:
            hover += f"<br><br><b>links</b><br>{summary}"

        node_labels.append(label)
        node_text.append(hover)
        node_colors.append(_node_color(status))
        node_sizes.append(_node_size_for_degree(degrees.get(n, 1)))

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode="markers+text",
        text=node_labels, textposition="bottom center",
        hovertext=node_text, hoverinfo="text",
        marker=dict(size=node_sizes, color=node_colors, line=dict(width=1, color="#1f2937")),
        name="nodes"
    )

    # ---- Base gray edge lines for structure
    edge_lines_x, edge_lines_y = [], []
    for u, v in g.edges():
        x0, y0 = pos[u]; x1, y1 = pos[v]
        edge_lines_x += [x0, x1, None]
        edge_lines_y += [y0, y1, None]
    base_edge_trace = go.Scatter(
        x=edge_lines_x, y=edge_lines_y,
        mode="lines",
        line=dict(width=1.5, color="#6b7280"),
        hoverinfo="none",
        name="links-base",
    )

    # ---- Arrow annotations (colored by latency bucket) + offset labels
    annotations = []
    label_x, label_y, hover_text = [], [], []

    for u, v, data in g.edges(data=True):
        x0, y0 = pos[u]; x1, y1 = pos[v]
        # arrow head
        ax = x0 + (x1 - x0) * ARROW_STEM
        ay = y0 + (y1 - y0) * ARROW_STEM

        lat_ms = data.get("latency_ms") or data.get("kpi_latency_ms")
        loss = data.get("loss_pct")
        jitter = data.get("jitter_ms")
        bucket = _bucket_latency(lat_ms)
        color = _latency_color(bucket)
        width = EDGE_WIDTHS["good"] if bucket == "good" else EDGE_WIDTHS["warn"] if bucket == "warn" else EDGE_WIDTHS["bad"]

        # offset label position so it doesn't overlap the line
        lx, ly = _perp_offset(x0, y0, x1, y1, frac=0.5, offset=LABEL_OFFSET)
        label_x.append(lx); label_y.append(ly)
        # hover template with extra KPIs if present
        txt = f"latency: {lat_ms if lat_ms is not None else '?'} ms"
        if loss is not None:   txt += f"<br>loss: {loss}%"
        if jitter is not None: txt += f"<br>jitter: {jitter} ms"
        hover_text.append(txt)

        # draw latency text as annotation (no arrow)
        annotations.append(dict(
            x=lx, y=ly, xref="x", yref="y",
            text=f"{lat_ms if lat_ms is not None else '?'} ms",
            showarrow=False, font=dict(size=12, color="#cbd5e1")
        ))

        # draw the arrow colored by bucket
        annotations.append(dict(
            x=ax, y=ay, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
            arrowhead=3, arrowsize=ARROW_HEAD/10, arrowwidth=width,
            opacity=ARROW_OPACITY, arrowcolor=color, standoff=2, startstandoff=2,
            showarrow=True
        ))

    # Invisible markers at label positions to host rich hover tooltips
    hover_trace = go.Scatter(
        x=label_x, y=label_y, mode="markers",
        marker=dict(size=8, color="rgba(0,0,0,0)"),
        hovertemplate="%{text}<extra></extra>",
        text=hover_text,
        name="edge-kpis"
    )

    fig = go.Figure(data=[base_edge_trace, node_trace, hover_trace])
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=annotations,
    )
    return fig

# --------------------------- public API --------------------------

def render_battlemap_if_available():
    import streamlit as st
    if not DEMO_TOPO.exists():
        st.info("No topology file found (expected `examples/demo_topology.yaml`).")
        return
    if yaml is None:
        st.warning("PyYAML not installed; cannot parse topology file.")
        return
    if nx is None:
        st.warning("networkx not installed; cannot render battlemap.")
        return
    try:
        topology = yaml.safe_load(DEMO_TOPO.read_text()) or {}
        fig = _figure_for_topology(topology)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Failed to render battlemap: {e}")