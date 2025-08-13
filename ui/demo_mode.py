"""
ui/demo_mode.py
Create a full demo in-place:
- Generate two tiny hop pcaps
- Merge into artifacts/merged.pcap
- Analyze to produce diagnosis/explanation
- Emit status.json
"""
from pathlib import Path
import json
from scapy.all import IP, TCP, Ether, wrpcap, conf

from phalanx_agents.stitch_unit import merge_pcaps
from phalanx_agents.intel_unit import run as run_analysis
from phalanx_agents.viz_unit import snapshot

ART = Path("artifacts")
ART.mkdir(exist_ok=True)

conf.verb = 0  # quiet scapy

SRC_MAC = "aa:aa:aa:aa:aa:aa"
DST_MAC = "bb:bb:bb:bb:bb:bb"

def _mk(ts, src, sport, dst, dport, flags="S", seq=0, ack=0, ttl=64, payload=b""):
    p = Ether(src=SRC_MAC, dst=DST_MAC)/IP(src=src, dst=dst, ttl=ttl)/TCP(sport=sport, dport=dport, flags=flags, seq=seq, ack=ack)
    if payload: p = p/payload
    p.time = ts
    return p

def _build_convo():
    import time
    base = time.time()
    A="10.0.0.10"; B="10.0.2.40"; sport=51822; dport=443
    syn    = _mk(base+0.000, A, sport, B, dport, "S",  seq=1000, ttl=64)
    synack = _mk(base+0.050, B, dport, A, sport, "SA", seq=5000, ack=1001, ttl=62)
    ack    = _mk(base+0.060, A, sport, B, dport, "A",  seq=1001, ack=5001, ttl=64)
    data1  = _mk(base+0.090, A, sport, B, dport, "PA", seq=1001, ack=5001, ttl=64, payload=b"GET / HTTP/1.1\\r\\n\\r\\n")
    ack2   = _mk(base+0.140, B, dport, A, sport, "A",  seq=5001, ack=1001+len(b"GET / HTTP/1.1\\r\\n\\r\\n"), ttl=62)
    return [syn, synack, ack, data1, ack2]

def _write_hops(pkts):
    h1 = ART/"sample_hop1.pcap"; wrpcap(str(h1), pkts)
    hop2=[]
    for p in pkts:
        q = p.copy(); q.time = p.time + 0.004
        if q[IP].src.startswith("10.0.0."): q[IP].ttl = max(1, q[IP].ttl-1)
        else: q[IP].ttl = min(255, q[IP].ttl+1)
        hop2.append(q)
    h2 = ART/"sample_hop2.pcap"; wrpcap(str(h2), hop2)
    return h1, h2

def run_demo():
    try:
        pkts = _build_convo()
        h1, h2 = _write_hops(pkts)
        merged = ART/"merged.pcap"
        merge_pcaps([str(h1), str(h2)], merged)
        run_analysis(str(merged))
        snapshot()
        return {"ok": True, "merged": str(merged)}
    except Exception as e:
        (ART/"demo_error.json").write_text(json.dumps({"error": str(e)}))
        return {"ok": False, "error": str(e)}