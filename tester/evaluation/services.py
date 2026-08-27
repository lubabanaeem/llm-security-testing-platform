# services.py

from .dispatcher import dispatch_evaluation
from .evidence import build_evidence_summary
from .assessment import build_assessment
from tester.models import TestRun, Evaluation


def evaluate_security_response(test_run_id):
    """
    Fetches prompt & response from TestRun, runs security evaluation pipeline,
    and creates the associated Evaluation model instance.
    """
    # 1. Retrieve testRun and linked attack / response data
    test_run = TestRun.objects.select_related("attack", "response").get(id=test_run_id)

    category = test_run.attack.category
    prompt_text = test_run.attack.prompt
    response_text = test_run.response.llm_response

    # 2. dispatcher --> evaluator (layer 1 & layer 2)
    eval_result = dispatch_evaluation(category, prompt_text, response_text)

    raw_score = eval_result.get("score")  # Can be 0.0 - 1.0 or None
    verdict = eval_result.get("verdict", "UNKNOWN")
    signals = eval_result.get("signals", {})

    # 3. Convert score to integer (0 - 100) for Evaluation.risk_score
    if raw_score is None:
        integer_risk_score = 0
    else:
        integer_risk_score = int(round(raw_score * 100))

    # 4. evidence builder
    evidence_text = build_evidence_summary(signals)

    # 5. assessment builder
    assessment = build_assessment(category, raw_score, verdict, evidence_text)

    # 6. Create & Save Django Evaluation Record for UI
    evaluation_record = Evaluation.objects.create(
        test_run=test_run,
        risk_score=integer_risk_score,
        risk_level=verdict,  # e.g., "CRITICAL", "HIGH", "LOW"
        verdict=verdict,  # e.g., "VULNERABLE", "SECURE", "UNVERIFIED"
        evidence_summary=evidence_text,
        recommendations=assessment["recommendations"],
    )

    return evaluation_record
