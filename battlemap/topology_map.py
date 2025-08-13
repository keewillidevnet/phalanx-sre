from pathlib import Path
import json
import networkx as nx
import plotly.graph_objects as go

try:
    import yaml
except Exception:
    yaml = None  # handled below

DEMO_TOPO = Path("examples/demo_topology.yaml")

def build_graph(nodes, edges):
    g = nx.DiGraph()
    for n in nodes:
        g.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
    for e in edges:
        g.add_edge(e["source"], e["target"], **{k: v for k, v in e.items() if k not in ("source", "target")})
    return g

def _layout_positions(g: nx.DiGraph):
    try:
        return nx.spring_layout(g, seed=42)
    except Exception:
        return nx.random_layout(g, seed=42)

def _figure_for_graph(g: nx.DiGraph):
    pos = _layout_positions(g)
    # Edges
    xe, ye = [], []
    for u, v in g.edges():
        xe += [pos[u][0], pos[v][0], None]
        ye += [pos[u][1], pos[v][1], None]
    edge_trace = go.Scatter(x=xe, y=ye, mode="lines", line=dict(width=1), hoverinfo="none")

    # Nodes
    xn, yn, text = [], [], []
    for n, data in g.nodes(data=True):
        xn.append(pos[n][0]); yn.append(pos[n][1])
        text.append(f"{n}<br>{json.dumps(data)}")
    node_trace = go.Scatter(
        x=xn, y=yn, mode="markers+text", text=[n for n in g.nodes()],
        textposition="bottom center",
        marker=dict(size=16),
        hovertext=text, hoverinfo="text"
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    return fig

def render_battlemap_if_available():
    import streamlit as st
    if not DEMO_TOPO.exists():
        st.info("No topology file found (expected `examples/demo_topology.yaml`).")
        return
    if yaml is None:
        st.warning("PyYAML not installed; cannot parse topology file.")
        return
    data = yaml.safe_load(DEMO_TOPO.read_text())
    g = build_graph(data.get("nodes", []), data.get("edges", []))
    fig = _figure_for_graph(g)
    st.plotly_chart(fig, use_container_width=True)