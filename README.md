# LLM Security Tester & Benchmark Engine

A Django-based platform for **LLM security testing, adversarial prompt evaluation, and automated vulnerability classification**.

The system provides an interactive interface for executing LLM attacks, stores security test results, evaluates model behavior using a heuristic-based analysis engine, and generates benchmark reports.

The project focuses on evaluating how Large Language Models respond to security threats such as:

- Prompt Injection
- Jailbreak Attempts
- System Prompt Extraction
- Sensitive Information Disclosure
- Excessive Agency
- Unbounded Consumption
- Insecure Output Handling

----

# Features

## Interactive LLM Security platform

Run adversarial prompts against local LLM models through an interactive web interface.

Supported local models include:

- Qwen models through Ollama
- Gemma models through Ollama

Users can:

- Select a target model
- Select an attack scenario
- Execute security tests
- Review generated responses
- Analyze security impact

---

## Automated Security Evaluation Engine

The platform automatically analyzes LLM responses using a heuristic-based evaluation engine.

The evaluator examines:

- Refusal behavior
- Sensitive content exposure
- Prompt compliance
- Suspicious output patterns
- Security severity indicators

Each response receives a predicted severity classification:
- Low
- Medium
- High
- Critical

----

## Attack Library Management

The system contains a structured attack registry with search query filters containing:

- Attack ID
- Attack category
- Attack prompt
- Expected behavior
- Ground-truth severity label

Attack categories are mapped to modern LLM security risks.

----

## Security Assessment Reports

Each executed LLM security test generates a structured security assessment report that is stored in the database.

Each report contains:

- Target model information
- Attack scenario details
- Generated model response
- Automated evaluation results
- Severity classification
- Assessment timestamp

The Reports dashboard allows users to review individual security assessments through a detailed report view and export reports as PDF documents..

---

## Benchmark Evaluation Framework

The project includes a custom benchmarking system comparing:

Evaluator Prediction 
vs 
Human Ground Truth Labels

The benchmark calculates:

- Exact accuracy
- Severity distance accuracy
- Mean Absolute Error (MAE)
- Confusion matrix

Run benchmark evaluation:

```bash
python manage.py eval_benchmark
```

   Llm_model
       |
       |
    TestRun
       |
|-------------|----------------|
        
↓             ↓                ↓
Response  Evaluation         Report
                               |
                               ↓
                           PDF Export
              

## Technology Stack
# Backend
- Python
- Django
- SQLite
- Django ORM
- 
## LLM Integration
- Ollama API
- Local open-weight models

## Security Evaluation
- Custom heuristic evaluator
- Rule-based classification
- Severity scoring
  
## Reporting
- PDF report generation

# Project Structure
LLM-Security-Tester/

│
├── attacks/
│   └── attack library definitions
│
├── evaluator/
│   ├── detection rules
│   └── scoring logic
│
├── models/
│   └── database models
│
├── management/
│   └── benchmark commands
|
│
├── templates/
│   └── web interface
│
└── README.md

# Installation
Requirements
- Python 3.10+
- Django
- Ollama

# Clone Repository
git clone <repository-url>
cd LLM-Security-Tester

# Install Dependencies
pip install -r requirements.txt

# Database Setup
python manage.py migrate

# Start Application
python manage.py runserver

# Running LLM Tests
Start Ollama locally:
ollama serve

# Benchmark Results

The evaluation engine was tested against a manually labeled adversarial dataset.

## Dataset
Total test cases: 45

## Results
### Metric	Result
Exact Match Accuracy	64.44%
Severity Distance Accuracy	79.26%
Mean Absolute Error	0.6222

### Category Error Analysis
Category	MAE
Sensitive Information Disclosure	0.0000
System Prompt Leakage	0.5000
Prompt Injection	0.6522
Insecure Output Handling	0.7500
Unbounded Consumption	0.7500
Excessive Agency	0.7500

### Limitations

The current evaluation engine uses heuristic-based analysis.

Because of this:

It detects patterns effectively.
It cannot fully understand semantic context.
Complex attacks may require human security analysis.

The benchmark results are intended to identify improvement areas rather than represent absolute model safety.

# Future Improvements

## Planned improvements:

Semantic similarity evaluation
Embedding-based analysis
LLM-as-a-judge comparison
Larger benchmark datasets
Additional attack categories
Improved severity calibration
Documentation

## Detailed methodology, benchmark design, and research observations:
docs/research.md

## License
This project is for educational and research purposes.


