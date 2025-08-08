import json
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Phalanx SRE", layout="wide")
st.title("Phalanx SRE — Coordinated intelligence for the modern SRE battlefield")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Root Cause & Evidence")
    dpath = Path("artifacts/diagnosis.json")
    epath = Path("artifacts/explanation.md")
    if dpath.exists():
        st.json(json.loads(dpath.read_text()))
    else:
        st.info("No diagnosis yet. Merge or place a PCAP at artifacts/merged.pcapng then run: "
                "`python -m phalanx_agents.intel_unit artifacts/merged.pcapng`")
    if epath.exists():
        st.markdown(epath.read_text())

with col2:
    st.subheader("Quick Actions")
    st.write("1) Put PCAPs in artifacts/ and run merge via stitch_unit")
    st.code("python -m phalanx_agents.stitch_unit artifacts/*hop*.pcapng")
    st.write("2) Analyze")
    st.code("python -m phalanx_agents.intel_unit artifacts/merged.pcapng")
    st.write("3) Refresh this page")

st.divider()
st.subheader("Demo Scenarios")
st.write("Open `campaign_scenarios/` for the 5 Palantir-inspired SRE use cases.")