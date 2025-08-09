"""
viz_unit.py
Aggregates current artifacts into a single status snapshot for the UI.
Writes artifacts/status.json.
"""
from pathlib import Path
import json

ART = Path("artifacts"); ART.mkdir(exist_ok=True)
STATUS = ART / "status.json"

def snapshot():
    data = {}
    data["merged_pcap"] = (ART / "merged.pcap").exists()
    data["diagnosis"]   = (ART / "diagnosis.json").exists()
    data["advice"]      = (ART / "advice.json").exists()
    # Optional: capture manifest if present
    cap_manifest = ART / "captures" / "manifest.json"
    data["captures"] = json.loads(cap_manifest.read_text()) if cap_manifest.exists() else {}
    STATUS.write_text(json.dumps(data, indent=2))
    return data

if __name__ == "__main__":
    print(json.dumps(snapshot(), indent=2))
