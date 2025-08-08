# 🛡️ Phalanx SRE – Coordinated Intelligence for the Modern SRE Battlefield

Palantir-inspired (Foundry/Gotham) PoC that fuses service topology, multi-hop packet forensics,
and agentic AI into a single operational platform for SREs.

👉 Full intro: `docs/README.md`  
👉 Design: `docs/DESIGN.md`  
👉 Use cases: `docs/USE_CASES.md`  
👉 Privacy/Governance: `docs/PRIVACY.md`

## Quickstart
```bash
python examples/sample_pcap_merger.py
python -m phalanx_agents.stitch_unit artifacts/sample_hop1.pcap artifacts/sample_hop2.pcap
python -m phalanx_agents.intel_unit artifacts/merged.pcap
streamlit run ui/app.py
