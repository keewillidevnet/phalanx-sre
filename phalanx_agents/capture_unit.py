"""
capture_unit.py
Start/stop scoped rotating captures using dumpcap (preferred) or tcpdump.
Writes PID files and a small manifest to artifacts/captures/.
"""
from pathlib import Path
import os, json, subprocess, sys, shutil

ART = Path("artifacts"); ART.mkdir(exist_ok=True)
CAPDIR = ART / "captures"; CAPDIR.mkdir(exist_ok=True)
MANIFEST = CAPDIR / "manifest.json"

def has(cmd): return shutil.which(cmd) is not None

def start(node: str, bpf: str, duration=30, files=20):
    outdir = CAPDIR / node
    outdir.mkdir(exist_ok=True)
    pcap_path = outdir / "cap.pcapng"
    pidfile = outdir / "capture.pid"

    if pidfile.exists():
        raise SystemExit(f"Capture already running for {node} (pidfile exists)")

    if has("dumpcap"):
        cmd = ["dumpcap", "-f", bpf, "-b", f"duration:{duration}", "-b", f"files:{files}", "-w", str(pcap_path)]
    elif has("tcpdump"):
        # Fallback: rotate by time using tcpdump (-G / -W)
        cmd = ["tcpdump", "-n", "-s", "0", "-w", str(outdir / "cap_%Y%m%d%H%M%S.pcap"), "-G", str(duration), "-W", str(files), bpf]
    else:
        raise SystemExit("Neither dumpcap nor tcpdump found. Please install one.")

    # Start detached
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
    pidfile.write_text(str(proc.pid))

    # update manifest
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    manifest[node] = {"bpf": bpf, "duration": duration, "files": files, "pid": proc.pid}
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"▶️ capture started for {node} (pid {proc.pid}) → {outdir}")

def stop(node: str):
    outdir = CAPDIR / node
    pidfile = outdir / "capture.pid"
    if not pidfile.exists():
        print(f"ℹ️ no running capture for {node}")
        return
    pid = int(pidfile.read_text().strip())
    try:
        os.killpg(pid, 15)  # SIGTERM process group
    except ProcessLookupError:
        pass
    pidfile.unlink(missing_ok=True)
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    if node in manifest: del manifest[node]
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"🛑 capture stopped for {node}")

def status():
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:\n  python -m phalanx_agents.capture_unit start <node> <BPF>\n  python -m phalanx_agents.capture_unit stop <node>\n  python -m phalanx_agents.capture_unit status")
        raise SystemExit(1)
    cmd = sys.argv[1]
    if cmd == "start":
        if len(sys.argv) < 4: raise SystemExit("start requires <node> and <BPF>")
        start(sys.argv[2], " ".join(sys.argv[3:]))
    elif cmd == "stop":
        if len(sys.argv) < 3: raise SystemExit("stop requires <node>")
        stop(sys.argv[2])
    elif cmd == "status":
        status()
    else:
        raise SystemExit(f"unknown command: {cmd}")
