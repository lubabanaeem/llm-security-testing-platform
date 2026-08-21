# dispatcher.py

from .evaluator import (
    evaluate_prompt_injection,
    evaluate_insecure_output_handling,
    evaluate_excessive_agency,
    evaluate_system_prompt_leakage,
    evaluate_sensitive_info_disclosure,
    evaluate_misinformation,
    evaluate_unbounded_consumption,
)

CATEGORY_DISPATCH = {
    "Prompt Injection": evaluate_prompt_injection,
    "Insecure Output Handling": evaluate_insecure_output_handling,
    "Excessive Agency": evaluate_excessive_agency,
    "System Prompt Leakage": evaluate_system_prompt_leakage,
    "Sensitive Information Disclosure": evaluate_sensitive_info_disclosure,
    "Misinformation": evaluate_misinformation,
    "Unbounded Consumption": evaluate_unbounded_consumption,
}


def dispatch_evaluation(category, prompt_text, response_text):
    """
    Routes an evaluation request to the correct category evaluator.
    """

    evaluator = CATEGORY_DISPATCH.get(category)

    if evaluator is None:
        return {
            "verdict": "UNSUPPORTED_CATEGORY",
            "score": None,
            "notes": f"No evaluator exists for '{category}'.",
        }

    return evaluator(response_text=response_text, prompt_text=prompt_text)
