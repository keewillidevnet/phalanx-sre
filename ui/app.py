import sys
import json
from pathlib import Path
import streamlit as st

# --- Bootstrap to ensure repo root is importable ---
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- Constants ---
SCENARIO_PATH = Path("campaign_scenarios/01_cross_domain_causality.md")
ART = Path("artifacts")
STATUS_PATH = ART / "status.json"

if "show_scenario" not in st.session_state:
    st.session_state.show_scenario = False

# --- Streamlit Page Config ---
st.set_page_config(page_title="Phalanx SRE", layout="wide")
st.title("Phalanx SRE — Coordinated intelligence for the modern SRE battlefield")


# --- Helpers ---
def load_status():
    if STATUS_PATH.exists():
        try:
            return json.loads(STATUS_PATH.read_text())
        except Exception:
            return {}
    return {}

def badge(ok: bool) -> str:
    return "✅" if ok else "❌"


# --- Status Bar + Controls ---
status = load_status()
st.markdown("### Status")
st.markdown(
    f"- Merged PCAP: {badge(status.get('merged_pcap', False))}  "
    f"- Diagnosis: {badge(status.get('diagnosis', False))}  "
    f"- Advice: {badge(status.get('advice', False))}  "
    f"- Active Captures: {len(status.get('captures', {})) if isinstance(status.get('captures', {}), dict) else 0}"
)

cols = st.columns([1, 1, 6])
with cols[0]:
    if st.button("🔄 Refresh status"):
        st.rerun()
with cols[1]:
    if st.button("🎬 Demo Mode"):
        with st.spinner("Generating sample PCAPs, merging, analyzing…"):
            try:
                from ui.demo_mode import run_demo
            except ModuleNotFoundError:
                sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                from ui.demo_mode import run_demo
            try:
                result = run_demo()
                if result.get("ok"):
                    st.session_state.show_scenario = True
                    st.success("Demo artifacts generated. Refreshing…")
                    st.rerun()
                else:
                    st.error(result.get("error", "Demo failed"))
            except Exception as e:
                st.error(f"Demo failed: {e}")

st.divider()


# --- Root Cause & Evidence + Quick Actions ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Root Cause & Evidence")
    dpath = ART / "diagnosis.json"
    epath = ART / "explanation.md"
    if dpath.exists():
        st.json(json.loads(dpath.read_text()))
    else:
        st.info("No diagnosis yet. Merge or place a PCAP at artifacts/merged.pcap then run: "
                "`python -m phalanx_agents.intel_unit artifacts/merged.pcap`")
    if epath.exists():
        st.markdown(epath.read_text())

    # Show the cinematic scenario after Demo Mode runs
    if st.session_state.get("show_scenario") and SCENARIO_PATH.exists():
        st.divider()
        st.subheader("Scenario Walkthrough – Cross-Domain Causality")
        st.markdown(SCENARIO_PATH.read_text())

with col2:
    st.subheader("Quick Actions")
    st.write("1) Put PCAPs in artifacts/ and run merge via stitch_unit")
    st.code("python -m phalanx_agents.stitch_unit artifacts/*hop*.pcap", language="bash")
    st.write("2) Analyze")
    st.code("python -m phalanx_agents.intel_unit artifacts/merged.pcap", language="bash")
    st.write("3) Refresh this page")

st.divider()
st.subheader("Demo Scenarios")
st.write("Open `campaign_scenarios/` for the 5 Palantir-inspired SRE use cases.")