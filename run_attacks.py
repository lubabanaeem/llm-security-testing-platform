import time
import requests
from django.utils import timezone
from django.contrib.auth.models import User
from tester.models import Attack, Llm_model, TestRun, Response, BenchmarkCase

OLLAMA_URL = "http://localhost:11434/api/generate"


def send_prompt(model_name, prompt):
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 1024,
            "temperature": 0.3,
        },  # Increased token limit here
    }
    try:
        response = requests.post(
            OLLAMA_URL, json=payload, timeout=120
        )  # Increased timeout to 120s
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            print(
                f"    [Ollama Error]: Status Code {response.status_code} - {response.text}"
            )
    except Exception as e:
        print(f"    [Ollama Connection Error]: {e}. Is Ollama running?")
    return None


# 0. Get an active user to assign the test run to
user = User.objects.filter(is_active=True).first()
if not user:
    raise ValueError("No active User found in the database.")

# =====================================================================
# FILTER TARGETS: Specify exactly which model and attack you want to rerun
# =====================================================================
TARGET_MODEL_NAME = "gemma3"  # Will look for your specific gemma model
TARGET_ATTACK_ID = "SI-20"  # Change to your specific attack ID

# 1. Filter strictly for your Gemma model
models = Llm_model.objects.filter(name__icontains=TARGET_MODEL_NAME)

# 2. Filter down to strictly this one specific attack ID
attacks = Attack.objects.filter(attack_id=TARGET_ATTACK_ID)

total_expected = models.count() * attacks.count()
if total_expected == 0:
    print(
        f"⚠️ Error check: Found {models.count()} models for '{TARGET_MODEL_NAME}' and {attacks.count()} attacks for '{TARGET_ATTACK_ID}'. Ensure both exist."
    )
else:
    print(
        f"Targeting {models.count()} model(s) x {attacks.count()} attack(s) = {total_expected} total runs.\n"
    )

current = 0
for model in models:
    for attack in attacks:
        current += 1
        print(
            f"[{current}/{total_expected}] Querying {model.name} ({model.version}) for attack '{attack.attack_id}'..."
        )

        try:
            start_time = time.perf_counter()
            ollama_model_tag = f"{model.name}:{model.version}"

            raw_response_text = send_prompt(ollama_model_tag, attack.prompt)

            if raw_response_text is None:
                print(
                    f"  ERROR: Received empty/failed response from Ollama for {attack.attack_id}"
                )
                continue

            raw_response_text = raw_response_text.strip()
            duration_ms = int((time.perf_counter() - start_time) * 1000)

            # 1. Create TestRun record
            test_run = TestRun.objects.create(user=user, model=model, attack=attack)

            # 2. Save raw text to Response record
            Response.objects.create(
                test_run=test_run,
                llm_response=raw_response_text,
                response_time_ms=duration_ms,
            )

            test_run.completed_at = timezone.now()
            test_run.save()

            # 3. Create BenchmarkCase record with the complete text for manual labeling
            BenchmarkCase.objects.create(
                attack=attack,
                model=model,
                response_text=raw_response_text,
                ground_truth_label="",
                notes="Re-run with increased token/timeout settings for a single target.",
                engine_prediction="",
            )
            print(f"  ✅ Successfully logged full response for {model.name}!")

        except Exception as e:
            print(
                f"  ERROR processing db transaction for {attack.attack_id} on {model.name}: {e}"
            )

print("\nIsolated run complete! Check Django Admin to grade your new, complete data.")
