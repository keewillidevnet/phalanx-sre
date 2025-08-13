import sys
import json
from pathlib import Path
import streamlit as st

# --- Bootstrap to ensure repo root is importable ---
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- Constants ---
SCENARIOS_DIR = Path("campaign_scenarios")
DEFAULT_SCENARIO = SCENARIOS_DIR / "01_cross_domain_causality.md"
ART = Path("artifacts")
STATUS_PATH = ART / "status.json"

# --- Session flags ---
if "show_scenario" not in st.session_state:
    st.session_state.show_scenario = False
if "demo_running" not in st.session_state:
    st.session_state.demo_running = False
if "scenario_choice" not in st.session_state:
    st.session_state.scenario_choice = str(DEFAULT_SCENARIO)

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

def list_scenarios():
    if not SCENARIOS_DIR.exists():
        return []
    return sorted([str(p) for p in SCENARIOS_DIR.glob("*.md")])

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
    if st.button("🎬 Demo Mode", disabled=st.session_state.demo_running):
        st.session_state.demo_running = True
        with st.spinner("Generating sample PCAPs, merging, analyzing…"):
            try:
                from ui.demo_mode import run_demo
            except ModuleNotFoundError:
                sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
                from ui.demo_mode import run_demo
            try:
                result = run_demo()
                st.session_state.demo_running = False
                if result.get("ok"):
                    st.session_state.show_scenario = True
                    # ensure default scenario is selected after demo
                    if DEFAULT_SCENARIO.exists():
                        st.session_state.scenario_choice = str(DEFAULT_SCENARIO)
                    st.success("Demo artifacts generated. Refreshing…")
                    st.rerun()
                else:
                    st.error(result.get("error", "Demo failed"))
            except Exception as e:
                st.session_state.demo_running = False
                st.error(f"Demo failed: {e}")

st.divider()

# --- Main layout ---
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

    # Scenario picker
    st.divider()
    st.subheader("Scenario Walkthrough")
    scenarios = list_scenarios()
    if scenarios:
        st.session_state.scenario_choice = st.selectbox(
            "Choose a scenario",
            scenarios,
            index=max(0, scenarios.index(str(DEFAULT_SCENARIO)) if str(DEFAULT_SCENARIO) in scenarios else 0),
        )
        if st.session_state.get("show_scenario"):
            scenepath = Path(st.session_state.scenario_choice)
            if scenepath.exists():
                st.markdown(scenepath.read_text())
            else:
                st.info("Selected scenario file not found.")
    else:
        st.info("No scenarios found in `campaign_scenarios/`.")

with col2:
    st.subheader("Quick Actions")
    st.write("1) Put PCAPs in artifacts/ and run merge via stitch_unit")
    st.code("python -m phalanx_agents.stitch_unit artifacts/*hop*.pcap", language="bash")
    st.write("2) Analyze")
    st.code("python -m phalanx_agents.intel_unit artifacts/merged.pcap", language="bash")
    st.write("3) Refresh this page")

st.divider()

# --- Battlemap (simple topology preview) ---
st.subheader("Battlemap (Topology Preview)")
from battlemap.topology_map import render_battlemap_if_available
render_battlemap_if_available()

st.divider()
st.subheader("Demo Scenarios")
st.write("Open `campaign_scenarios/` for the 5 Palantir-inspired SRE use cases.")