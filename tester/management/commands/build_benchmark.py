from django.core.management.base import BaseCommand
from tester.models import TestRun, Response, BenchmarkCase


class Command(BaseCommand):
    help = "Auto-populate BenchmarkCase entries from completed TestRuns"

    def handle(self, *args, **kwargs):
        runs = TestRun.objects.filter(completed_at__isnull=False)
        created_count = 0

        for run in runs:
            try:
                response = run.response
            except Response.DoesNotExist:
                continue

            exists = BenchmarkCase.objects.filter(
                attack=run.attack,
                model=run.model,
                response_text=response.llm_response,
            ).exists()

            if not exists:
                BenchmarkCase.objects.create(
                    attack=run.attack,
                    model=run.model,
                    response_text=response.llm_response,
                    ground_truth_label="",
                    split="train",
                )
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} benchmark cases created — go label them in admin."
            )
        )
