import networkx as nx

def build_graph(nodes, edges):
    g = nx.DiGraph()
    for n in nodes:
        g.add_node(n["id"], **{k:v for k,v in n.items() if k!="id"})
    for e in edges:
        g.add_edge(e["source"], e["target"], **{k:v for k,v in e.items() if k not in ("source","target")})
    return g
