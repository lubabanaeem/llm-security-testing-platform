from collections import defaultdict
from django.core.management.base import BaseCommand
from tester.evaluation.services import evaluate_security_response
from tester.models import BenchmarkCase
from tester.evaluation.services import dispatch_evaluation


class Command(BaseCommand):
    help = "Evaluates benchmark test cases with category MAE, confusion matrix, and prediction persistence."

    SEVERITY_MAP = {
        "LOW": 0,
        "MEDIUM": 1,
        "HIGH": 2,
        "CRITICAL": 3,
    }

    LABELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def handle(self, *args, **options):
        test_cases = BenchmarkCase.objects.select_related("attack", "model").all()
        total_cases = test_cases.count()

        if total_cases == 0:
            self.stdout.write(
                self.style.ERROR("No benchmark test cases found in database.")
            )
            return

        total_distance = 0
        exact_matches = 0

        # Category tracking: category_name -> list of distances
        category_distances = defaultdict(list)

        # Confusion Matrix: matrix[gt_label][pred_label] = count
        confusion_matrix = {gt: {pred: 0 for pred in self.LABELS} for gt in self.LABELS}

        self.stdout.write(
            f"Evaluating engine against {total_cases} benchmark cases...\n"
        )

        for case in test_cases:
            # 1. Extract values directly from model relationships
            category = case.attack.category or "Uncategorized"
            prompt_text = case.attack.prompt
            response_text = case.response_text

            # 2. Dispatch directly to Layer 1 and Layer 2 pipeline
            eval_result = dispatch_evaluation(category, prompt_text, response_text)

            predicted_verdict = str(eval_result.get("verdict")).strip().upper()
            gt_verdict = str(case.ground_truth_label).strip().upper()

            # 3. Strict Label Validation
            if gt_verdict not in self.SEVERITY_MAP:
                raise ValueError(
                    f"Invalid Ground Truth label '{gt_verdict}' in BenchmarkCase ID: {case.id}"
                )
            if predicted_verdict not in self.SEVERITY_MAP:
                raise ValueError(
                    f"Invalid Predicted verdict '{predicted_verdict}' in BenchmarkCase ID: {case.id}"
                )

            # 4. Update DB field engine_prediction
            case.engine_prediction = predicted_verdict
            case.save(update_fields=["engine_prediction"])

            # 5. Calculating Distances and Confusion Matrix
            gt_rank = self.SEVERITY_MAP[gt_verdict]
            pred_rank = self.SEVERITY_MAP[predicted_verdict]

            distance = abs(gt_rank - pred_rank)
            total_distance += distance

            category_distances[category].append(distance)
            confusion_matrix[gt_verdict][predicted_verdict] += 1

            if distance == 0:
                exact_matches += 1
                status_str = self.style.SUCCESS("[EXACT MATCH]")
            elif distance == 1:
                status_str = self.style.WARNING(f"[NEAR MISS - Dist: {distance}]")
            else:
                status_str = self.style.ERROR(f"[LARGE DEVIATION - Dist: {distance}]")

            self.stdout.write(
                f"{status_str} ID: {case.attack.attack_id:<8} | Category: {str(category):<25} | GT: {gt_verdict:<8} | Pred: {predicted_verdict:<8}"
            )

        # Overall Metrics Calculations
        overall_mae = total_distance / total_cases
        severity_distance_accuracy = (1.0 - (overall_mae / 3.0)) * 100
        exact_accuracy = (exact_matches / total_cases) * 100

        #  Output Report
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(
            "              BENCHMARK EVALUATION SUMMARY REPORT             "
        )
        self.stdout.write("=" * 70)
        self.stdout.write(f"Total Cases Evaluated        : {total_cases}")
        self.stdout.write(f"Exact Matches                : {exact_matches}")
        self.stdout.write(f"Overall MAE                  : {overall_mae:.4f}")
        self.stdout.write(f"Exact Match Accuracy         : {exact_accuracy:.2f}%")
        self.stdout.write(
            self.style.SUCCESS(
                f"Severity Distance Accuracy   : {severity_distance_accuracy:.2f}%"
            )
        )

        # Category Breakdown
        self.stdout.write("\n" + "-" * 70)
        self.stdout.write("MEAN ABSOLUTE ERROR (MAE) BY CATEGORY")
        self.stdout.write("-" * 70)
        for cat, dists in category_distances.items():
            cat_mae = sum(dists) / len(dists)
            self.stdout.write(
                f"{str(cat):<35} | Count: {len(dists):<3} | MAE: {cat_mae:.4f}"
            )

        # Confusion Matrix Printout
        self.stdout.write("\n" + "-" * 70)
        self.stdout.write("CONFUSION MATRIX")
        self.stdout.write("-" * 70)
        self.stdout.write(
            f"{'GT \\ Pred':<12} | {'LOW':<8} | {'MEDIUM':<8} | {'HIGH':<8} | {'CRITICAL':<8}"
        )
        self.stdout.write("-" * 60)
        for gt_label in self.LABELS:
            row_str = " | ".join(
                f"{confusion_matrix[gt_label][pred_label]:<8}"
                for pred_label in self.LABELS
            )
            self.stdout.write(f"{gt_label:<12} | {row_str}")
        self.stdout.write("=" * 70 + "\n")
