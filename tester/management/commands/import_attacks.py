import json
from pathlib import Path

from django.core.management.base import BaseCommand

from tester.models import Attack


class Command(BaseCommand):
    help = "Import attacks from attacks.json"

    def handle(self, *args, **kwargs):

        json_path = Path(__file__).resolve().parents[2] / "attack_lib" / "attacks.json"

        with open(json_path, "r", encoding="utf-8") as file:
            attacks = json.load(file)

        for attack in attacks:

            Attack.objects.get_or_create(
                attack_id=attack["id"],
                defaults={
                    "name": attack["name"],
                    "category": attack["category"],
                    "prompt": attack["prompt"],
                    "expected_behaviour": attack["expected_behaviour"],
                },
            )

        self.stdout.write(self.style.SUCCESS("Attack library imported successfully."))
