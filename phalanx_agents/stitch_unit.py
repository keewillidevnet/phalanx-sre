import sys
from pathlib import Path
from scapy.all import rdpcap, wrpcap

ART = Path("artifacts"); ART.mkdir(exist_ok=True)

def merge_pcaps(pcap_paths, output_path):
    packets = []
    for p in pcap_paths:
        print(f"[+] Reading {p}")
        packets.extend(rdpcap(str(p)))
    packets.sort(key=lambda pkt: pkt.time)
    wrpcap(str(output_path), packets)
    print(f"[+] Wrote merged PCAP: {output_path}")
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python -m phalanx_agents.stitch_unit <pcap1> <pcap2> [pcap3...]")
        sys.exit(1)
    out = merge_pcaps(sys.argv[1:], Path("artifacts/merged.pcap"))  # use .pcap for scapy
