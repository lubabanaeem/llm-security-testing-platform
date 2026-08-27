def build_evidence_summary(signals):
    primary_evidence = []
    supporting_evidence = []

    # Checking if any tier 1 signal picked up a score > 0
    has_tier1_risk = any(
        data.get("tier") == 1 and data.get("score", 0.0) > 0.0
        for data in signals.values()
        if isinstance(data, dict)
    )

    for signal_name, data in signals.items():
        if not isinstance(data, dict):
            continue

        score = data.get("score", 0.0)
        found = data.get("found", False)
        matches = data.get("matches", [])
        tier = data.get("tier", 2)

        label = signal_name.replace("_", " ").title()
        match_str = f" ({', '.join(matches[:2])})" if matches else ""

        # Tier 1: include if score > 0.0 (ex,  0.3 for generic operational guidance)
        if tier == 1 and score > 0.0:
            primary_evidence.append(f"• [Primary] {label} detected{match_str}")

        # Tier 2: include supporting layout structure pnly if tier 1 detected risk
        elif tier == 2 and has_tier1_risk and (score > 0.0 or found):
            supporting_evidence.append(f"• [Supporting] {label} present{match_str}")

    all_evidence = primary_evidence + supporting_evidence

    if not all_evidence:
        return " Clean output: No primary security risks or compliance indicators detected."

    return "\n".join(all_evidence)
