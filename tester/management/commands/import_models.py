from django.core.management.base import BaseCommand

from tester.models import Llm_model


class Command(BaseCommand):
    help = "Import available LLM models"

    def handle(self, *args, **kwargs):

        models = [
            {
                "name": "qwen2.5",
                "version": "1.5b",
                "provider": "Ollama",
            },
            {
                "name": "gemma",
                "version": "3",
                "provider": "Ollama",
            },
        ]

        for model in models:

            Llm_model.objects.get_or_create(
                name=model["name"],
                defaults={
                    "version": model["version"],
                    "provider": model["provider"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Models imported successfully."))
