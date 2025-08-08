# 🔒 Phalanx SRE – Privacy, Security & Data Governance

Phalanx SRE is built to deliver **deep operational intelligence** while respecting
data privacy, security, and compliance requirements from the first packet to the final report.

---

## 🛡 Privacy-First Design Principles

1. **Minimum Necessary Capture**
   - Packet capture is scoped via **BPF filters** (`filters.py`) to target specific flows, services, or time ranges.
   - Optional **header-only capture mode** for when full payloads are not required.
   - User-defined **PCAP retention policies** ensure data is purged after analysis.

2. **On-Node Processing**
   - Feature extraction and KPI calculation can occur **at the capture node**,
     reducing the need to transmit raw PCAPs.
   - Sensitive payloads can be **hashed, masked, or redacted** before leaving the node.

3. **Encryption Everywhere**
   - All inter-agent and ingest API communications use **TLS 1.3+**.
   - At-rest data (PCAPs, extracted features, AI reports) is encrypted using **AES-256**.
   - Encryption keys stored in **vault-managed secrets** (HashiCorp Vault, AWS KMS, etc.).

4. **AI Safety**
   - LLM analysis is performed **locally or in a trusted VPC**; no packet content is sent to public LLM APIs without explicit approval.
   - AI prompts are stripped of any sensitive data not required for diagnosis.

5. **Auditability**
   - Every access, packet ingest, and AI inference is logged with:
     - **Who** initiated it
     - **What** was accessed/analyzed
     - **When** and **where** it occurred
   - Logs stored in **append-only** format for compliance.

---

## 📜 Compliance Alignment

Phalanx SRE can be configured to align with:
- **GDPR** – Right to be forgotten, explicit consent, data minimization.
- **HIPAA** – Masking of PHI, encryption in transit/at rest.
- **PCI DSS** – No storage of sensitive cardholder data in PCAP payloads.
- **SOC 2** – Security, Availability, Processing Integrity, Confidentiality.

---

## 🔍 Data Capture Safety

- **Payload Redaction** – Regex-based scrubbing of sensitive strings before storage.
- **Selective Retention** – Time-based and event-triggered deletion policies.
- **Edge Filtering** – Drop non-essential traffic at the capture point to reduce exposure.

Example:
```bash
tcpdump -i eth0 tcp port 443 and host 203.0.113.10 -s 96 -G 60 -W 5 -w /secure/pcaps/
```
- `-s 96` → capture first 96 bytes only (enough for headers + TLS handshake info).
- `-G 60` & `-W 5` → rotate every minute, keep only 5 files.

---

## 🧩 Integration Without Exposure

Because Phalanx SRE is **API-first** and **modular**, it can be integrated without exposing raw packet payloads to third parties:
- Metrics and features can be exported instead of full PCAPs.
- Incident narratives can be shared without sensitive packet data.
- Demo mode allows testing integrations without touching production traffic.

---

## 🛠 Governance Layer

Phalanx includes an optional **command_structure/trust_policy.json** file that defines:
- Who can start a capture
- Who can view raw PCAPs
- Which agents are authorized to run AI diagnosis
- Thresholds for automated remediation approval

This ensures that **sensitive operational actions** follow the same approval patterns as production change management.

---

## 🚫 Example “Do Not Capture” Policies

Phalanx can be configured to automatically skip:
- Traffic to/from HR, finance, or medical systems
- Authentication flows (Kerberos, OAuth tokens, etc.)
- Known encrypted user content streams (video calls, personal email)

---

## 📦 Data Deletion & Expiration

- Configurable retention: `delete after N hours/days` per capture policy
- Secure deletion via **shred** or equivalent methods
- Expiration metadata stored alongside each PCAP for automatic cleanup

---

## 📈 Transparency

Phalanx SRE ships with a **Privacy Status Panel** in the dashboard:
- Shows current capture scopes and retention timers
- Flags when sensitive capture filters are active
- Allows authorized users to stop or adjust capture in real time

---

## 💡 Summary

Phalanx SRE treats privacy as a **first-class feature**, not an afterthought.

By combining:
- Scoped capture
- Edge processing
- Encryption everywhere
- AI safety practices
- Audit trails and governance

…we ensure that **deep operational visibility** and **data responsibility** can coexist.

Operational intelligence should never come at the cost of trust.