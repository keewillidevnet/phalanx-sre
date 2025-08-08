# 📚 Phalanx SRE — Technical Handbook

This document provides the deep technical background, architectural blueprint, and integration details for **Phalanx SRE** — the Palantir-inspired platform for coordinated intelligence in modern Site Reliability Engineering.

---

## 1. Purpose & Vision

Phalanx SRE aims to unify **service topology awareness**, **multi-hop packet forensics**, and **agentic AI reasoning** into one cohesive platform that can both *see* and *act* across complex operational environments.

Unlike traditional SRE toolkits that silo metrics, logs, and packet captures, Phalanx SRE merges all core reliability pillars into a **single source of operational truth**.

---

## 2. Architectural Overview

### High-Level Flow
1. **Signal Capture Layer** — Multi-hop packet collection, filterable by BPF.
2. **Analysis Core** — Feature extraction, rule evaluation, ML classification.
3. **Agentic Units** — Autonomous modules (capture, stitch, intel, advisor, viz) powered by AGNTCY patterns.
4. **Visualization Layer** — Real-time “battlemap” topology, root cause panels, timeline ladders.
5. **Governance & Trust Layer** — Policy-driven consensus before remediation.
6. **Scenario Modules** — Prebuilt playbooks for Palantir-style SRE use cases.

---

## 3. Directory Structure

    phalanx/
    ├── phalanx_agents/       # AGNTCY-powered battlefield units
    │   ├── capture_unit.py   # Scoped multi-hop packet capture
    │   ├── stitch_unit.py    # PCAP stitching + seq/ack alignment
    │   ├── intel_unit.py     # Rules + ML + LLM diagnosis
    │   ├── advisor_unit.py   # Remediation suggestions w/ trust votes
    │   └── viz_unit.py       # Updates battlemap & intel panels
    │
    ├── signal_capture/       # Network intelligence gathering
    │   ├── filters.py        # 5-tuple BPF filters
    │   ├── pcap_rotate.sh    # Rotation helper
    │   └── ingest_api.py     # FastAPI ingestion endpoint
    │
    ├── intel_core/           # Brain of the platform
    │   ├── features.py       # RTT, loss, reordering, MSS
    │   ├── rules.py          # PMTUD, asymmetry, congestion
    │   ├── model.py          # ML classifier
    │   └── llm_explainer.py  # Natural-language incident narrative
    │
    ├── battlemap/            # Visual command center
    │   ├── ladder_diagram.py # Conversation timeline
    │   ├── topology_map.py   # Hop-to-hop graph w/ KPI heat
    │   └── root_cause_panel.py
    │
    ├── campaign_scenarios/   # Palantir-style use cases
    ├── ui/                   # Streamlit dashboard
    ├── command_structure/    # Governance & rules of engagement
    ├── examples/             # Sample topologies & demo PCAPs
    ├── docs/                 # This handbook + other docs
    └── requirements.txt

---

## 4. Data Flow

1. **Capture Phase**
   - `capture_unit.py` listens on specified interfaces or ingests via API.
   - Filters (`filters.py`) enforce scoped capture (by 5-tuple, protocol, etc.).

2. **Stitching Phase**
   - `stitch_unit.py` aligns multi-hop PCAPs via seq/ack number correlation.
   - Produces a unified `.pcapng` representing the full conversation path.

3. **Analysis Phase**
   - `features.py` extracts KPIs (latency, jitter, loss).
   - `rules.py` applies heuristics for known patterns (e.g., PMTUD black hole).
   - `model.py` (optional) applies ML classification for unseen patterns.

4. **Intelligence Phase**
   - `llm_explainer.py` generates plain-English narrative of incident context.
   - `advisor_unit.py` proposes remediation steps, optionally requiring multi-agent trust consensus (`trust_policy.json`).

5. **Visualization Phase**
   - `viz_unit.py` feeds battlemap topology (`topology_map.py`), root cause panel, and ladder diagram for time-sequenced packet views.

---

## 5. Core Capabilities

- **Multi-Hop PCAP Forensics** — Capture at each hop, stitch into unified flow.
- **AI-Driven Diagnosis** — LLM + ML hybrid reasoning.
- **Root Cause Visualization** — Live battlemap with KPI overlays.
- **Trust-Weighted Actions** — Agentic consensus before changes.
- **Scenario Simulation** — Prebuilt Palantir-style use cases for demo or training.
- **Integration-Ready** — API endpoints for ingest/export into other systems.

---

## 6. Palantir-Style SRE Use Cases

1. **Cross-Domain Causality Mapping**
   Linking network anomalies to app-layer incidents across silos.

2. **Trust-Weighted Remediation**
   Changes only deployed if multiple agents reach consensus.

3. **Dynamic SLO Prioritization**
   AI-driven reallocation of resources based on predicted breach risk.

4. **Incident War Room Automation**
   Auto-build dashboards & timelines from raw packet and metric data.

5. **Predictive Ops Planning**
   Forecast failure points based on topology and historical patterns.

---

## 7. Security & Privacy Considerations

- **Scoped Capture** — All captures are bounded by filters to avoid overspill.
- **PII Redaction** — Configurable scrubbing of payload data.
- **Immutable Audit Logs** — Every decision/action recorded.
- **Governance Hooks** — `trust_policy.json` enforces org-specific guardrails.

---

## 8. Integration Pathways

- **Metrics/Logs** — Ingest from Prometheus, Grafana Loki, Elastic.
- **Packet** — Native PCAP or API push.
- **Topology** — Import from NetBox, OpenConfig, or custom YAML.
- **Remediation** — Trigger Ansible, Salt, NSO, or Kubernetes operators.

---

## 9. Extending the Platform

- **Custom Rules** — Add heuristics in `rules.py`.
- **ML Models** — Train and swap models in `model.py`.
- **UI Panels** — Extend Streamlit app with new visualizations.
- **Capture Methods** — Support sFlow, NetFlow, or other collectors.

---

## 10. Roadmap Alignment

Phalanx SRE is evolving alongside:
- **Phase 3** — Feature hardening & stability.
- **Phase 4** — Governance, multi-agent consensus, wireless/edge adaptation.
- **Phase 5** — Monetization strategy and ecosystem integration.

---

*Document version:* 1.0 — Matches repository commit at initial public PoC release.