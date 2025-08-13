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
ARROW_STEM = 0.985          # arrow head position along the edge (0..1)
LABEL_OFFSET = 0.055        # perpendicular offset for latency labels
PAD_COL = 8                 # pad target for edge hover labels ("Latency:" width)
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

def _pad_label(label: str, width: int = PAD_COL) -> str:
    """Pad a short label (e.g., 'Loss:') with NBSPs to align with 'Latency:'."""
    # NB: Plotly hoverlabels collapse normal spaces; NBSPs (&nbsp;) persist.
    pad = max(0, width - len(label))
    return label + ("&nbsp;" * pad)

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
    # with compact, formatted KPI summaries in the hover text.
    node_x, node_y, node_text, node_sizes, node_colors, node_labels = [], [], [], [], [], []
    degrees = dict(g.degree())

    def summarize_edges(edges):
        if not edges:
            return {}
        lat    = [e.get("latency_ms") or e.get("kpi_latency_ms") for e in edges if (e.get("latency_ms") or e.get("kpi_latency_ms")) is not None]
        loss   = [e.get("loss_pct")   for e in edges if e.get("loss_pct")   is not None]
        jitter = [e.get("jitter_ms")  for e in edges if e.get("jitter_ms")  is not None]
        out = {}
        if lat:    out["latency"] = f"{max(lat):g} ms"
        if loss:   out["loss"]    = f"{max(loss):g}%"
        if jitter: out["jitter"]  = f"{max(jitter):g} ms"
        return out

    for n, data in g.nodes(data=True):
        x, y = pos[n]
        node_x.append(x); node_y.append(y)
        status = (data.get("status") or "healthy").capitalize()
        label  = data.get("label", n)
        role   = (data.get("role") or "node").capitalize()

        inbound_kpis  = summarize_edges([d for _, _, d in g.in_edges(n, data=True)])
        outbound_kpis = summarize_edges([d for _, _, d in g.out_edges(n, data=True)])

        # Build compact, left-aligned hover text
        lines = [
            f"<b>{label}</b>",
            f"Role: {role} | Status: {status}",
            "",
            "<b>Links</b>"
        ]

        def add_section(title: str, kpis: dict):
            if not kpis:
                return
            keys = list(kpis.keys())
            if len(keys) == 1:
                # Single KPI: inline, flush-left
                key = keys[0]
                pretty = {"latency": "Latency Max", "loss": "Loss Max", "jitter": "Jitter Max"}[key]
                lines.append(f"{title}: {pretty} = {kpis[key]}")
            else:
                # Multi-KPI: one per line with a small indent
                lines.append(f"{title}:")
                if "latency" in kpis: lines.append(f"&nbsp;&nbsp;Latency Max = {kpis['latency']}")
                if "loss"    in kpis: lines.append(f"&nbsp;&nbsp;Loss Max     = {kpis['loss']}")
                if "jitter"  in kpis: lines.append(f"&nbsp;&nbsp;Jitter Max   = {kpis['jitter']}")

        add_section("Inbound", inbound_kpis)
        add_section("Outbound", outbound_kpis)

        hover = "<br>".join(lines)

        node_labels.append(label)
        node_text.append(hover)
        node_colors.append(_node_color(data.get("status")))
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

        # offset label so it doesn't overlap the line
        lx, ly = _perp_offset(x0, y0, x1, y1, frac=0.5, offset=LABEL_OFFSET)
        label_x.append(lx); label_y.append(ly)

        # Edge hover text (aligned labels, monospace)
        lines = []
        if lat_ms is not None: lines.append(f"{_pad_label('Latency:')} {lat_ms:g} ms")
        if loss   is not None: lines.append(f"{_pad_label('Loss:')} {loss:g}%")
        if jitter is not None: lines.append(f"{_pad_label('Jitter:')} {jitter:g} ms")
        if not lines:
            lines.append(f"{_pad_label('Latency:')} ?")
        hover_text.append("<br>".join(lines))

        # draw latency text as annotation (no arrow)
        annotations.append(dict(
            x=lx, y=ly, xref="x", yref="y",
            text=f"{lat_ms if lat_ms is not None else '?'} ms",
            showarrow=False, font=dict(size=12, color="#cbd5e1")
        ))

        # draw the arrow colored by bucket — with no standoff gap
        annotations.append(dict(
            x=ax, y=ay, ax=x0, ay=y0, xref="x", yref="y", axref="x", ayref="y",
            arrowhead=3, arrowsize=ARROW_HEAD/10, arrowwidth=width,
            opacity=ARROW_OPACITY, arrowcolor=color,
            standoff=0, startstandoff=0,
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
        hoverlabel=dict(font_size=12, font_family="monospace", align="left")  # slim, aligned, left
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