from pathlib import Path
import json
from intel_core.features import tcp_basic_features
from intel_core.rules import diagnose
from intel_core.llm_explainer import explain

ART = Path("artifacts"); ART.mkdir(exist_ok=True)

def run(pcap_path: str = "artifacts/merged.pcap"):
    feats = tcp_basic_features(pcap_path)
    diag = diagnose(feats)
    narrative = explain(diag)
    (ART / "diagnosis.json").write_text(json.dumps(diag, indent=2))
    (ART / "explanation.md").write_text(narrative)
    return diag

if __name__ == "__main__":
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else "artifacts/merged.pcap"
    result = run(p)
    print(json.dumps(result, indent=2))
