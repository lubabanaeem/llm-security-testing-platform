# tester/management/commands/import_attacks.py (SAFE VERSION)
from pathlib import Path
import json
from django.core.management.base import BaseCommand
from tester.models import Attack


class Command(BaseCommand):
    help = "Import or update attacks from attacks.json safely"

    def handle(self, *args, **kwargs):
        # DO NOT call Attack.objects.all().delete()!

        json_path = Path(__file__).resolve().parents[2] / "attack_lib" / "attacks.json"

        with open(json_path, "r", encoding="utf-8") as file:
            attacks = json.load(file)

        for attack in attacks:
            # Safely updates existing attacks or creates new ones without dropping PK references
            Attack.objects.update_or_create(
                attack_id=attack["id"],
                defaults={
                    "name": attack["name"],
                    "category": attack["category"],
                    "prompt": attack["prompt"],
                    "expected_behaviour": attack["expected_behaviour"],
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Attack library updated successfully without wiping dependent tables!"
            )
        )
