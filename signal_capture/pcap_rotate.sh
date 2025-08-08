#!/usr/bin/env bash
# Rotate pcaps safely using dumpcap (preferred over tcpdump for ring buffers)
# Usage: sudo ./pcap_rotate.sh "<BPF_FILTER>" /tmp/captures 30 20
set -euo pipefail
FILTER="${1:-tcp}"
OUTDIR="${2:-/tmp/captures}"
DURATION="${3:-30}"   # seconds per file
FILES="${4:-20}"      # how many files to retain
mkdir -p "$OUTDIR"
exec dumpcap -f "$FILTER" -b duration:"$DURATION" -b files:"$FILES" -w "$OUTDIR/cap.pcapng"
