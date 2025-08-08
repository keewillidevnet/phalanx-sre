def explain(diagnosis: dict) -> str:
    cause = diagnosis["primary_cause"]
    conf = diagnosis["confidence"]
    ev = diagnosis["evidence"]
    tips = {
        "packet_loss_or_mtu_issue": "Retransmissions suggest loss or a PMTUD/MSS issue along the path.",
        "congestion_or_queueing": "Handshake RTT appears inflated; could indicate queueing or a saturated link.",
        "application_stall_or_empty_payloads": "Little to no application payload observed; consider server think-time or upstream dependency stalls.",
        "no_issue_detected": "No strong anomalies detected in this capture."
    }
    return (
        f"**Primary cause:** {cause} (confidence {conf:.2f})\n\n"
        f"**Evidence**: pkts={ev.get('pkts')}, retrans_rate={ev.get('retrans_rate')}, "
        f"syn_rtt_estimate={ev.get('syn_rtt_estimate')}, app_bytes={ev.get('app_bytes')}.\n\n"
        f"**Interpretation**: {tips.get(cause, '')}\n\n"
        f"**Next steps**:\n"
        f"- Validate MTU/ICMP behavior and interface drops\n"
        f"- Compare before/after deploy timings and path asymmetry\n"
        f"- Capture a longer window if the issue is intermittent\n"
    )
