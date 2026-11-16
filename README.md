# LLM Security Tester & Benchmark

A Django-based platform for **running adversarial prompts against local LLMs, scoring the responses with a rule-based (heuristic) approach, and measuring how well that approach agrees with human judgment.**

> **Status: exploratory research and learning project.**
> The heuristic approach is intentionally simple. On the labeled benchmark it does **not** beat a trivial "always predict LOW" baseline (see [Benchmark Results](#benchmark-results)). The main finding is where and why rule-based scoring breaks down.

---

## What it does

- Runs attacks from a structured library against local models through a web interface
- Stores every test run, model response, evaluation and report in SQLite
- Scores each response with a heuristic approach: a risk score (0-100) and a label (LOW / MEDIUM / HIGH / CRITICAL), plus an evidence summary and recommendations
- Shows a report page for each test (export via the browser's "Print to PDF")
- Includes a benchmark command that compares the heuristic approach against manually assigned human labels

**Target models** (run locally through Ollama):

| Model | Ollama tag |
|---|---|
| Qwen 2.5 | `qwen2.5:1.5b` |
| Gemma 3 | `gemma3:1b` |

Generation settings: `temperature = 0.3`, `num_predict = 1024` tokens, request timeout 120 s. These are small models, so results should not be generalized to larger ones.

---

## Attack library

`tester/attack_lib/attacks.json` contains **26 attacks** across 7 categories, inspired by the OWASP Top 10 for LLM Applications:

| Category | Attacks |
|---|---|
| Prompt Injection | 12 |
| Insecure Output Handling | 4 |
| Excessive Agency | 3 |
| Unbounded Consumption | 2 |
| Sensitive Information Disclosure | 2 |
| Misinformation | 2 |
| System Prompt Leakage | 1 |

Each attack has: `id`, `name`, `category`, `prompt`, `expected_behaviour`.
Severity labels are **not** stored in the library. They are assigned manually, per response, in the benchmark (`BenchmarkCase.ground_truth_label`).

**Categories the approach does not score.** Misinformation requires fact-checking, and some judgment-type attacks (for example EA-22) require reasoning about whether a conclusion is correct. Rules cannot do this reliably, so these cases return `UNVERIFIED` instead of a guess. They are excluded from the benchmark metrics (see coverage below) and are left for future work (for example LLM-as-a-judge).

**Known issue:** the Misinformation attacks are stored with the category spelled `Minsinformation`. The dispatcher accepts both spellings so they are routed correctly.

---

## How scoring works (short version)

1. **Detectors** (`tester/evaluation/analysis.py`): small rule-based checks (refusal phrases, operational guidance, JSON validity, sensitive patterns, length and repetition...). Each returns a score between 0 and 1.
2. **Category evaluators** (`evaluator.py`): combine detector results with hand-written if-rules into one score from 0.0 to 1.0.
3. **Dispatcher** (`dispatcher.py`): routes each response to the evaluator for its attack category.
4. **Risk bands** (`_risk_level`): below 0.30 = LOW, 0.30 to 0.69 = MEDIUM, 0.70 to 0.84 = HIGH, 0.85 and above = CRITICAL.

All weights, constants and thresholds were **set by hand**, not learned or fitted from data. Details and a worked example are in [`docs/research.md`](docs/research.md).

---

## Benchmark

### Dataset

- **45 manually labeled responses** covering **23 unique attacks** (an attack can appear more than once, once per model)
- Labeled by a single person (the author) on a 4-level scale: LOW / MEDIUM / HIGH / CRITICAL
- 3 library attacks (EA-22, MI-25, MI-26) were not part of the labeled benchmark; Misinformation and judgment-type attacks return `UNVERIFIED` by design
- The rules were developed while examining these same responses, so the results describe performance on the development data, not on unseen data

### Metrics

- **Exact match accuracy**: share of responses where the label from the approach equals the human label
- **MAE (Mean Absolute Error)**: labels are mapped to LOW=0, MEDIUM=1, HIGH=2, CRITICAL=3; the error for a response is the absolute difference between the two numbers; MAE is the average error
- **Baseline**: the score of a method that always predicts the most common human label (here LOW), used to check whether the approach adds anything
- **Per-class recall** and a **binary view** (LOW vs. any real failure)
- **Coverage**: how many cases could be scored at all

Run it with:

```
python manage.py eval_benchmark
```

### Benchmark results

| Metric | Heuristic approach | Always-LOW baseline |
|---|---|---|
| Exact match accuracy | 64.44% (29 / 45) | 68.89% (31 / 45) |
| MAE (lower is better) | 0.6222 | 0.5333 |
| Coverage | 45 / 45 | n/a |

The approach does **not** beat the baseline on either metric.

**Per-class recall** (of the responses humans labeled X, how many did the approach label X):

| Human label | Cases | Recall |
|---|---|---|
| LOW | 31 | 90.32% |
| MEDIUM | 6 | 0.00% |
| HIGH | 6 | 0.00% |
| CRITICAL | 2 | 50.00% |

**Binary view** (LOW = safe, MEDIUM or above = real failure):

| Measure | Result |
|---|---|
| Real failures caught | 5 of 14 (35.71%) |
| Safe responses falsely flagged | 3 of 31 (9.68%) |
| Precision of flags | 62.50% |

**Error by category** (small samples; treat with caution):

| Category | Responses | Unique attacks | MAE |
|---|---|---|---|
| Prompt Injection | 23 | 12 | 0.6522 |
| Insecure Output Handling | 8 | 4 | 0.7500 |
| Unbounded Consumption | 4 | 2 | 0.7500 |
| Excessive Agency | 4 | 2 | 0.7500 |
| System Prompt Leakage | 2 | 1 | 0.5000 |
| Sensitive Information Disclosure | 4 | 2 | 0.0000 |

A MAE of 0.0000 for Sensitive Information Disclosure rests on only 2 attacks, so it should not be read as reliable.

**Confusion matrix** (rows = human label, columns = label from the approach):

| Human \ Approach | LOW | MEDIUM | HIGH | CRITICAL |
|---|---|---|---|---|
| LOW | 28 | 1 | 0 | 2 |
| MEDIUM | 4 | 0 | 0 | 2 |
| HIGH | 4 | 0 | 0 | 2 |
| CRITICAL | 1 | 0 | 0 | 1 |

The approach said LOW 37 times, and 9 of those were real failures. It never predicted HIGH, and it predicted CRITICAL 7 times with only 1 correct.

---

## Limitations

- **Rule-based:** detects patterns, not meaning. Harmful content without recognizable patterns is missed, and harmless content with such patterns can be over-flagged.
- **Small dataset:** 45 responses, 23 unique attacks, two small models. Some categories have 1 or 2 attacks.
- **Single labeler:** no inter-annotator agreement was measured.
- **Development data:** no held-out test set; results are optimistic for unseen attacks.
- **Hand-set weights and thresholds:** not fitted, and the 0-3 numeric mapping assumes equal gaps between severity levels.
- **Imbalanced labels:** 31 of 45 labels are LOW, which is why the always-LOW baseline is strong.
- **Truncation:** responses are capped at 1024 tokens, which affects Unbounded Consumption attacks.
- **PDF export** uses the browser's print dialog; no PDF file is generated on the server.

---

## Installation

Requirements: Python 3.12 or newer, [Ollama](https://ollama.com).

```
git clone https://github.com/lubabanaeem/llm-security-testing-platform.git
cd llm-security-testing-platform
python -m venv .venv
.venv\Scripts\activate          # Windows (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

Set up the database and data:

```
python manage.py migrate
python manage.py createsuperuser      # login is required for the web interface
python manage.py import_models
python manage.py import_attacks
```

Pull the models and make sure Ollama is running (the Ollama app, or `ollama serve`):

```
ollama pull qwen2.5:1.5b
ollama pull gemma3:1b
```

Start the app:

```
python manage.py runserver
```

### Collecting and labeling benchmark data (optional)

1. Run attacks against a model. `run_attacks.py` targets one model and one attack set by constants at the top of the file (`TARGET_MODEL_NAME`, `TARGET_ATTACK_ID`). Edit them, then run it inside the Django shell (macOS/Linux: `python manage.py shell < run_attacks.py`; PowerShell: `Get-Content run_attacks.py | python manage.py shell`).
2. `python manage.py build_benchmark` creates `BenchmarkCase` rows from completed test runs.
3. Label each case in the Django admin (`ground_truth_label`: LOW, MEDIUM, HIGH or CRITICAL).
4. `python manage.py eval_benchmark`

---

## Project structure

```
llm-security-testing-platform/
├── manage.py
├── requirements.txt
├── run_attacks.py              # script: run attacks against a model, store responses and benchmark cases
├── check_truncation.py         # script: inspect whether a stored response was cut off
├── fix_attacks.py              # one-off database repair script
├── docs/
│   └── research.md             # methodology, results and analysis
├── mysite/                     # Django project settings and URLs
└── tester/
    ├── models.py               # Llm_model, Attack, TestRun, Response, Evaluation, Report, BenchmarkCase
    ├── views.py, urls.py, admin.py
    ├── attack_lib/             # attacks.json and loader
    ├── LLM/ollama_client.py    # Ollama API client
    ├── evaluation/
    │   ├── analysis.py         # Layer 1: detectors
    │   ├── evaluator.py        # Layer 2: category evaluators
    │   ├── dispatcher.py       # Layer 3: routing by attack category
    │   ├── services.py         # runs evaluation and saves results
    │   ├── evidence.py         # builds the evidence summary
    │   └── assessment.py       # explanation and recommendations
    ├── management/commands/    # import_models, import_attacks, build_benchmark, eval_benchmark
    ├── migrations/
    └── templates/              # web interface
```

---

## Future improvements

- LLM-as-a-judge for the cases rules cannot score and for the middle severity levels
- A larger, more balanced benchmark with a held-out test set
- A second human labeler to measure agreement
- Graded scoring so MEDIUM and HIGH are actually produced
- Larger target models and more attack categories

---

## Further reading

Methodology, benchmark design, results and error analysis: [`docs/research.md`](docs/research.md)

## License

This project is for educational and research purposes.
