# 🛡️ Phalanx SRE – System Design & Architecture

## Mission
Phalanx SRE unifies telemetry, service topology, and multi-hop packet forensics into a single operational intelligence layer.
It is built for Site Reliability Engineers who must **see everything, understand instantly, and act with precision**.

Inspired by **Palantir Foundry** (data fusion & governance) and **Palantir Gotham** (entity resolution & investigative tooling),
Phalanx brings these capabilities to the **SRE battlefield**.

---

## High-Level Architecture

```
+--------------------------+        +--------------------------+
|   signal_capture/        |        |  phalanx_agents/         |
|--------------------------|        |--------------------------|
| - tcpdump/dumpcap hooks  |  --->  | - Capture Agents         |
| - BPF Filters            |        | - Stitcher               |
| - pcap rotation          |        | - Intel (AI analysis)    |
+--------------------------+        +--------------------------+
          |                                  |
          v                                  v
+-------------------------------------------------------------+
|                         intel_core/                         |
|-------------------------------------------------------------|
| - Feature Extraction (RTT, loss, MSS, reorder)              |
| - Rules Engine (PMTUD, asymmetry, congestion)               |
| - ML Models (classification, anomaly detection)             |
| - LLM Explainer (plain-English root cause)                   |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                          battlemap/                         |
|-------------------------------------------------------------|
| - Topology Map (live hop-by-hop view)                       |
| - Ladder Diagram (timeline of packets/events)               |
| - Root Cause Panel (diagnosis & recommendations)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                             ui/                             |
|-------------------------------------------------------------|
| - Streamlit Dashboard                                        |
| - Real-time updates via WebSockets                           |
| - Demo Mode (synthetic LinkedIn-friendly data)               |
+-------------------------------------------------------------+
```

---

## Data Flow

1. **Signal Capture Layer**
   - `tcpdump` or `dumpcap` agents deployed at each hop
   - Filters applied via `filters.py` (5-tuple matching or service-specific)
   - Rolling PCAP buffers managed by `pcap_rotate.sh`
   - Optional `ingest_api.py` for centralized packet collection

2. **Packet Stitching & Entity Resolution**
   - Multi-hop captures aligned via `stitch_unit.py`
   - Sequence/ACK number matching reconstructs full TCP or UDP conversation
   - Loss, reordering, retransmissions identified

3. **Intelligence Core**
   - `features.py` extracts KPIs (RTT, jitter, MSS, drop %)
   - `rules.py` runs expert system checks (PMTUD blackholes, asymmetric paths, congestion)
   - `model.py` classifies incident severity or type
   - `llm_explainer.py` produces human-readable diagnosis and likely remediation steps

4. **Visualization Layer**
   - `topology_map.py` renders hop-by-hop graph with KPI heat coloring
   - `ladder_diagram.py` shows conversation timeline and packet exchanges
   - `root_cause_panel.py` presents cause, impact, and recommendations

5. **Governance & Decisioning**
   - `advisor_unit.py` uses trust-weighted agent voting for automated changes
   - Policies defined in `command_structure/trust_policy.json`

---

## Module Roles

### **phalanx_agents/**
- **capture_unit.py** – Deploys and controls tcpdump/dumpcap instances per node
- **stitch_unit.py** – Merges multi-hop PCAPs into coherent flows
- **intel_unit.py** – Runs feature extraction + rules + AI classification
- **advisor_unit.py** – Applies trust-weighted logic to remediation
- **viz_unit.py** – Pushes updates to dashboard in real time

### **signal_capture/**
- **filters.py** – Defines capture filters by 5-tuple, VLAN, or service
- **pcap_rotate.sh** – Maintains rolling captures without disk overflow
- **ingest_api.py** – Ingest endpoint for remote capture uploads

### **intel_core/**
- **features.py** – Converts packets into structured KPIs
- **rules.py** – Detects known network/SRE failure patterns
- **model.py** – Optional ML component for anomaly detection
- **llm_explainer.py** – Converts technical findings into plain English

### **battlemap/**
- **topology_map.py** – Graph of services, nodes, and paths
- **ladder_diagram.py** – Time-sequenced packet/conversation view
- **root_cause_panel.py** – Single-pane cause summary

---

## Palantir-Inspired Features in Phalanx

| Palantir Concept | Phalanx Implementation |
|------------------|------------------------|
| **Foundry Ontology** | Unified graph of services, packets, topology, incidents |
| **Data Pipelines** | Automated ingest + transform + visualization chain |
| **Gotham Entity Resolution** | Multi-hop packet stitching into single conversation |
| **Operational Case Management** | AI-generated incident narratives |
| **Governance Layer** | Trust-weighted multi-agent approvals for changes |

---

## Trust-Weighted Remediation Flow

```
Incident → Intel Core Diagnosis → Advisor Unit Proposal →
  ├─ Consensus Achieved → Automated Fix
  └─ Consensus Failed → Escalation to Human SRE
```

---

## AI & ML Roles

- **Rules Engine** – Deterministic detection of known issues
- **ML Models** – Learn network/application-specific anomaly patterns
- **LLM Explainer** – Contextual, human-readable incident reports
- **Simulation Engine** – Predictive failure and SLO burn-down modeling

---

## Scalability & Extensibility

- **Distributed Capture** – Agents run at any hop, in containers or native
- **Cloud or On-Prem** – Works in bare metal, k8s, or hybrid
- **API-First** – All features exposed via REST/WebSocket for integration
- **Pluggable Models** – Swap AI/ML models without changing pipeline
- **Custom Rules** – Drop-in rules for environment-specific failure modes

---

## Next Steps to PoC

1. Implement multi-hop packet capture & stitching
2. Add KPI extraction + rules
3. Build LLM diagnosis layer
4. Render real-time topology + ladder diagrams
5. Implement demo datasets for public showcase
6. Package and release to GitHub + LinkedIn

---

Phalanx SRE is built to **fuse signal and context** so that the operational battlefield is never a mystery.
It’s **not just observability** it’s *decisive operational intelligence*.