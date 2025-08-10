# Use Case 1 — Cross-Domain Incident Causality (Cinematic)

**Mission:** Explain a checkout latency spike by fusing deploy metadata, service topology, and multi-hop packet forensics.

## Narrative

- **T-00:00** — Deploy `checkout-api v3.12.4` to region `us-west`.
- **T+00:02** — SLO burn begins. APM shows 95p latency +220 ms.
- **T+00:03** — Phalanx *battlemap* flags rising RTT on path `client-a → gw-1 → gw-2 → service-b`.
- **T+00:04** — Multi-hop PCAP stitch reveals:
  - SYN→SYN-ACK RTT +45 ms vs baseline
  - Retrans bursts between **gw-1** and **gw-2**
  - Server MSS == 1460; path MTU change suspected
- **T+00:05** — **Intel Unit** diagnosis: `packet_loss_or_mtu_issue` (confidence 0.75)
  Evidence: elevated retransmissions, handshake RTT inflation.
- **T+00:06** — **Advisor Unit** proposal: `apply_mss_clamp` to 1360 at edge `gw-1`.
  - Votes: `SREBot(0.5) + OpsLeadAgent(0.9)` → **approved** (avg 0.7 ≥ 0.7, min_votes 2)
- **T+00:08** — Clamp applied. Retrans rate drops; SLO burn stops.

## Reproduce with Demo Mode

1. Open the dashboard: `streamlit run ui/app.py`
2. Click **🎬 Demo Mode**
3. Observe updated **Root Cause & Evidence** panel and green checks in **Status** bar.

## What Palantir Would Notice

- **Foundry-like fusion** of deploy + path + packet evidence.
- **Gotham-style entity resolution** from multi-hop PCAPs into a single conversation.
- **Governance-first automation** via trust-weighted remediation.