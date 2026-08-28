from .dispatcher import dispatch_evaluation
from .evidence import build_evidence_summary
from .assessment import build_assessment
from tester.models import TestRun, Evaluation, Report


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

    # 2. Run dispatcher to get evaluator verdict & score
    eval_result = dispatch_evaluation(category, prompt_text, response_text)

    raw_score = eval_result.get("score")  # Can be 0.0 - 1.0 or None
    verdict = eval_result.get("verdict", "UNKNOWN")
    signals = eval_result.get("signals", {})

    # 3. Convert score to integer (0 - 100) for Evaluation.risk_score
    if raw_score is None:
        integer_risk_score = 0
    else:
        integer_risk_score = int(round(raw_score * 100))

    # 4. Check if verdict is unsupported, unverified, or unhandled
    verdict_str = str(verdict).upper()
    is_unsupported = (
        raw_score is None
        or "UNSUPPORTED_CATEGORY" in verdict_str
        or verdict_str in ["UNVERIFIED", "UNKNOWN"]
    )

    # 5. Build evidence summary conditionally (avoid default 'Clean output' on unsupported)
    if is_unsupported:
        evidence_text = ""
    else:
        evidence_text = build_evidence_summary(signals)

    # 6. Build assessment explanation & recommendations
    assessment = build_assessment(category, raw_score, verdict, evidence_text)

    # 7. Create & save Evaluation record (passes assessment explanation to evidence_summary field for UI display)
    evaluation_record = Evaluation.objects.create(
        test_run=test_run,
        risk_score=integer_risk_score,
        risk_level=verdict,
        verdict=verdict,
        evidence_summary=assessment["explanation"],
        recommendations=assessment["recommendations"],
    )

    # 8. Create or retrieve corresponding Admin Report record
    Report.objects.get_or_create(
        test_run=test_run,
        defaults={
            "report_title": f"Security Report: {category} (Run #{test_run.id})",
            "report_path": f"/reports/test_run_{test_run.id}.pdf",
        },
    )

    return evaluation_record
