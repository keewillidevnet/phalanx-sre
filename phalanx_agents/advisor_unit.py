"""
advisor_unit.py
Evaluates remediation proposals against trust_policy.json.
Computes consensus and emits a decision json to artifacts/advice.json.
"""
from pathlib import Path
import json, sys

POLICY = Path("command_structure/trust_policy.json")
ART = Path("artifacts"); ART.mkdir(exist_ok=True)
ADVICE = ART / "advice.json"

def load_policy():
    if not POLICY.exists():
        raise SystemExit("trust_policy.json not found")
    return json.loads(POLICY.read_text())

def evaluate(action: str, votes: list[str]):
    pol = load_policy()
    actions = pol.get("actions", {})
    roles = pol.get("roles", {})
    need = actions.get(action)
    if not need:
        return {"action": action, "approved": False, "reason": "unknown_action"}

    # Sum trust across roles present in votes; also count votes
    trust_sum = 0.0
    counted = 0
    details = []
    for v in votes:
        t = roles.get(v, 0.0)
        trust_sum += t
        counted += 1
        details.append({"role": v, "trust": t})

    approved = (trust_sum / max(counted,1) >= need["min_trust"]) and (counted >= need["min_votes"])
    result = {"action": action, "approved": approved, "votes": details, "requirements": need, "trust_avg": (trust_sum / max(counted,1))}
    ADVICE.write_text(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:\n  python -m phalanx_agents.advisor_unit <action> <Role1,Role2,...>\nExample:\n  python -m phalanx_agents.advisor_unit apply_mss_clamp SREBot,OpsLeadAgent")
        raise SystemExit(1)
    action = sys.argv[1]
    votes = sys.argv[2].split(",")
    out = evaluate(action, votes)
    print(json.dumps(out, indent=2))
