from scapy.all import IP, TCP, Ether, wrpcap, conf
from pathlib import Path
import time

conf.verb = 0  # silence ARP/BPF attempts

ART = Path("artifacts"); ART.mkdir(exist_ok=True)
SRC_MAC = "aa:aa:aa:aa:aa:aa"
DST_MAC = "bb:bb:bb:bb:bb:bb"

def mk_pkt(ts, src, sport, dst, dport, flags="S", seq=0, ack=0, ttl=64, payload=b""):
    p = Ether(src=SRC_MAC, dst=DST_MAC)/IP(src=src, dst=dst, ttl=ttl)/TCP(sport=sport, dport=dport, flags=flags, seq=seq, ack=ack)
    if payload: p = p/payload
    p.time = ts
    return p

def build_conversation():
    base = time.time()
    A="10.0.0.10"; B="10.0.2.40"; sport=51822; dport=443
    syn    = mk_pkt(base+0.000, A, sport, B, dport, "S",  seq=1000, ttl=64)
    synack = mk_pkt(base+0.050, B, dport, A, sport, "SA", seq=5000, ack=1001, ttl=62)
    ack    = mk_pkt(base+0.060, A, sport, B, dport, "A",  seq=1001, ack=5001, ttl=64)
    data1  = mk_pkt(base+0.090, A, sport, B, dport, "PA", seq=1001, ack=5001, ttl=64, payload=b"GET / HTTP/1.1\r\n\r\n")
    ack2   = mk_pkt(base+0.140, B, dport, A, sport, "A",  seq=5001, ack=1001+len(b"GET / HTTP/1.1\r\n\r\n"), ttl=62)
    return [syn, synack, ack, data1, ack2]

def write_hop_pcaps(pkts):
    hop1 = ART/"sample_hop1.pcap"; wrpcap(str(hop1), pkts)
    pkts_hop2=[]
    for p in pkts:
        q=p.copy(); q.time=p.time+0.004
        if q[IP].src.startswith("10.0.0."): q[IP].ttl=max(1, q[IP].ttl-1)
        else: q[IP].ttl=min(255, q[IP].ttl+1)
        pkts_hop2.append(q)
    hop2 = ART/"sample_hop2.pcap"; wrpcap(str(hop2), pkts_hop2)
    return hop1, hop2

if __name__ == "__main__":
    h1,h2 = write_hop_pcaps(build_conversation())
    print(f"Wrote sample hop pcaps:\n - {h1}\n - {h2}\n")
    print("Next:\n  python -m phalanx_agents.stitch_unit artifacts/sample_hop1.pcap artifacts/sample_hop2.pcap")
