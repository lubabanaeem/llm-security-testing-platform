import json
from pathlib import Path


def load_attacks():
    json_path = Path(__file__).parent / "attacks.json"

    with open(json_path, "r", encoding="utf-8") as file:
        attacks = json.load(file)

    return attacks
