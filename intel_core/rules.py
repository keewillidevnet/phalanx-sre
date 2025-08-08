def diagnose(m):
    findings = []
    # Rough heuristics
    if m.get("retrans_rate", 0) > 0.05:
        findings.append(("packet_loss_or_mtu_issue", 0.75))
    if m.get("syn_rtt_estimate") and m["syn_rtt_estimate"] > 0.3:
        findings.append(("congestion_or_queueing", 0.60))
    if not findings and (m.get("app_bytes", 0) == 0) and m.get("pkts", 0) > 0:
        findings.append(("application_stall_or_empty_payloads", 0.55))
    if not findings:
        findings.append(("no_issue_detected", 0.30))
    findings.sort(key=lambda x: x[1], reverse=True)
    root, conf = findings[0]
    return {"primary_cause": root, "confidence": conf, "evidence": m}
