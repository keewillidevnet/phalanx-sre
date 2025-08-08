from scapy.all import rdpcap, TCP, IP, Raw
from collections import defaultdict

def tcp_basic_features(pcap_path: str):
    pkts = rdpcap(pcap_path)
    total = len(pkts)

    # Track handshake timing & simple retrans detection
    syn_time = None
    synack_time = None
    retrans = 0
    seen_seq = set()

    bytes_app = 0
    fwd_pkts = 0
    rev_pkts = 0
    fwd_bytes = 0
    rev_bytes = 0

    client_ip = None
    server_ip = None
    client_port = None
    server_port = None

    # Simple infer direction from first SYN
    for p in pkts:
        if TCP in p:
            if p[TCP].flags & 0x02:  # SYN
                client_ip = p[IP].src
                client_port = p[TCP].sport
                server_ip = p[IP].dst
                server_port = p[TCP].dport
                syn_time = float(p.time)
                break

    for p in pkts:
        if not (IP in p and TCP in p):
            continue
        t = float(p.time)
        ip = p[IP]; tcp = p[TCP]
        key = (ip.src, tcp.sport, tcp.seq, len(bytes(p[TCP].payload)))
        if key in seen_seq and tcp.flags & 0x10:  # ACK with same seq/len again -> rough retrans indicator
            retrans += 1
        else:
            seen_seq.add(key)

        direction = "fwd" if (client_ip and ip.src == client_ip and tcp.sport == client_port) else "rev"
        plen = len(bytes(tcp.payload))
        if direction == "fwd":
            fwd_pkts += 1
            fwd_bytes += plen
        else:
            rev_pkts += 1
            rev_bytes += plen

        if (tcp.flags & 0x12) == 0x12 and synack_time is None and syn_time is not None:
            # SYN-ACK observed
            synack_time = t

        # app-layer-ish bytes (payload present)
        if plen > 0 and Raw in p:
            bytes_app += plen

    syn_rtt = (synack_time - syn_time) if (syn_time and synack_time) else None

    return {
        "pkts": total,
        "retrans_estimate": retrans,
        "retrans_rate": (retrans / total) if total else 0.0,
        "syn_rtt_estimate": syn_rtt,   # seconds, handshake RTT-ish
        "client_ip": client_ip,
        "server_ip": server_ip,
        "client_port": client_port,
        "server_port": server_port,
        "fwd_pkts": fwd_pkts,
        "rev_pkts": rev_pkts,
        "fwd_bytes": fwd_bytes,
        "rev_bytes": rev_bytes,
        "app_bytes": bytes_app
    }
