from .evaluator import (
    evaluate_excessive_agency,
    evaluate_insecure_output_handling,
    evaluate_misinformation,
    evaluate_prompt_injection,
    evaluate_sensitive_info_disclosure,
    evaluate_system_prompt_leakage,
    evaluate_unbounded_consumption,
)

# Standard lookup dictionary using lowercased, stripped strings
CATEGORY_DISPATCH = {
    "prompt injection": evaluate_prompt_injection,
    "insecure output handling": evaluate_insecure_output_handling,
    "excessive agency": evaluate_excessive_agency,
    "system prompt leakage": evaluate_system_prompt_leakage,
    "sensitive information disclosure": evaluate_sensitive_info_disclosure,
    # Common variations/aliases:
    "sensitive disclosure": evaluate_sensitive_info_disclosure,
    "sensitive info disclosure": evaluate_sensitive_info_disclosure,
    "misinformation": evaluate_misinformation,
    "unbounded consumption": evaluate_unbounded_consumption,
}


def dispatch_evaluation(category, prompt_text, response_text):
    """Routes an evaluation request to the correct category evaluator."""
    if not category:
        normalized_category = ""
    else:
        normalized_category = str(category).strip().lower()

    evaluator = CATEGORY_DISPATCH.get(normalized_category)

    if evaluator is None:
        return {
            "verdict": "UNSUPPORTED_CATEGORY",
            "score": None,
            "notes": f"No evaluator exists for '{category}'.",
        }

    return evaluator(response_text=response_text, prompt_text=prompt_text)
