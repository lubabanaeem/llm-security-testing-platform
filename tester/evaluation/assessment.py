# assessment.py

CATEGORY_RECOMMENDATIONS = {
    "Prompt Injection": [
        "Strengthen refusal consistency across multi-turn prompts.",
        "Prevent refusal-followed-by-compliance transitions.",
        "Reinforce system prompt boundary isolation.",
    ],
    "Insecure Output Handling": [
        "Enforce strict schema validation on output JSON/XML.",
        "Sanitize HTML/Markdown tags prior to DOM rendering.",
        "Reject raw response payloads containing unescaped code blocks.",
    ],
    "Excessive Agency": [
        "Restrict tool-calling capabilities and API scope.",
        "Require human-in-the-loop approval for state-changing operations.",
    ],
    "System Prompt Leakage": [
        "Mask system instructions and internal guidelines.",
        "Apply output regex filters for sensitive prompt tokens.",
    ],
    "Sensitive Information Disclosure": [
        "Implement PII and credential redaction filters on model outputs."
    ],
    "Misinformation": [
        "Ground outputs with RAG-based factual verification.",
        "Append explicit disclaimer notices on uncertain generation.",
    ],
    "Unbounded Consumption": ["Enforce strict maximum token execution bounds."],
}


def build_assessment(category, score, verdict, evidence_summary_text):
    score_text = "N/A" if score is None else f"{score * 100:.0f}/100"

    # Clean Output Handling
    if score == 0.0 or verdict in ["Low", "SECURE"]:
        return {
            "explanation": f"Evaluation for category '{category}' yielded a verdict of {verdict} (Risk Score: {score_text}). The response successfully refused or contained no risk indicators.",
            "recommendations": "• No action required. Response maintained safety boundaries.",
        }

    # Standard recommendations for actual risks
    recs = CATEGORY_RECOMMENDATIONS.get(
        category, ["Review system prompt design and enforce response filtering."]
    )

    return {
        "explanation": f"Evaluation for category '{category}' yielded a verdict of {verdict} (Risk Score: {score_text}).\n\nEvidence Summary:\n{evidence_summary_text}",
        "recommendations": "\n".join([f"• {r}" for r in recs]),
    }
