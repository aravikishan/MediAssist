# MediAssist

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)

**Medical Symptom Checker with Differential Diagnosis, Drug Interaction Warnings & Health Knowledge Base**

---

> **MEDICAL DISCLAIMER**: MediAssist is designed for **educational and informational
> purposes only**. It is NOT a substitute for professional medical advice, diagnosis,
> or treatment. Never disregard professional medical advice or delay seeking it because
> of something provided by this application. If you think you may have a medical
> emergency, call your doctor or emergency services immediately.

---

## Overview

MediAssist is a Flask-based web application that provides:

- **Symptom Checker** -- Select symptoms from a categorized list, get ranked differential diagnoses with confidence scores
- **Differential Diagnosis Engine** -- Weighted overlap + Jaccard similarity algorithms with prevalence adjustment
- **Condition Browser** -- Explore 22+ medical conditions with symptoms, risk factors, and care guidance
- **Drug Interaction Checker** -- Select 2+ medications, check for interactions with severity levels
- **Drug Database** -- 22 common medications with uses, side effects, and warnings
- **REST API** -- Full API for programmatic access to all features
- **Session History** -- SQLite-backed storage of symptom check sessions

## Screenshots

The application features a clean, medical-grade blue/white theme designed for trustworthiness and readability.

## Features

### Symptom Checker
- Browse symptoms by **body region** (Head, Chest, Abdomen, etc.)
- **Multi-select** symptoms with **severity sliders** (mild/moderate/severe)
- Three scoring methods: Weighted Overlap, Jaccard Similarity, Combined
- Ranked results with confidence percentages and matching symptom highlighting

### Differential Diagnosis Engine
- **Weighted overlap scoring**: Each symptom contributes its configured weight, multiplied by severity
- **Jaccard similarity**: Intersection-over-union for set-based comparison
- **Combined method**: Blended score with prevalence adjustment for clinical relevance
- Minimum confidence threshold filtering
- Session persistence for audit trail

### Drug Interaction Checker
- Select medications from searchable list
- Pairwise interaction checking with **severity classification**:
  - Minor, Moderate, Major, Contraindicated
- Interaction details with clinical recommendations
- 20 documented drug-drug interactions

### Knowledge Base
- **45 symptoms** across 11 body regions
- **22 medical conditions** across 10 categories
- **22 medications** across 13 drug classes
- Risk factors and "when to seek care" guidance
- Comprehensive seed data in JSON format

## Quick Start

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourname/mediassist.git
cd mediassist

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The application starts on **http://localhost:8011**

### Using the Start Script

```bash
chmod +x start.sh
./start.sh
```

### Using Docker

```bash
# Build and run
docker-compose up --build

# Or manually
docker build -t mediassist .
docker run -p 8011:8011 mediassist
```

## API Reference

### Symptoms

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/symptoms` | List all symptoms |
| GET | `/api/symptoms?region=Head` | Filter symptoms by body region |
| GET | `/api/symptoms/grouped` | Get symptoms grouped by region |

### Diagnosis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/diagnose` | Run differential diagnosis |
| GET | `/api/history` | Get check session history |

**POST /api/diagnose** request body:
```json
{
  "symptoms": ["headache", "fever", "cough"],
  "severities": {"headache": "severe", "fever": "moderate"},
  "method": "combined"
}
```

### Conditions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/conditions` | List all conditions |
| GET | `/api/conditions/:id` | Get condition details |

### Drugs & Interactions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/drugs` | List all drugs |
| GET | `/api/drugs?q=aspirin` | Search drugs |
| GET | `/api/drugs/:id` | Get drug details |
| GET | `/api/drugs/grouped` | Get drugs by class |
| POST | `/api/interactions/check` | Check drug interactions |
| POST | `/api/interactions/matrix` | Get interaction matrix |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Service health check |

## Project Structure

```
mediassist/
|-- app.py                          # Flask entry point
|-- config.py                       # Configuration constants
|-- requirements.txt                # Python dependencies
|-- Dockerfile                      # Container definition
|-- docker-compose.yml              # Container orchestration
|-- start.sh                        # Quick-start script
|-- models/
|   |-- __init__.py
|   |-- database.py                 # SQLite/SQLAlchemy setup
|   |-- schemas.py                  # ORM models
|-- routes/
|   |-- __init__.py
|   |-- api.py                      # REST API endpoints
|   |-- views.py                    # HTML view routes
|-- services/
|   |-- __init__.py
|   |-- diagnosis.py                # Differential diagnosis engine
|   |-- knowledge.py                # Drug interaction service
|-- templates/                      # Jinja2 HTML templates
|-- static/
|   |-- css/style.css               # Healthcare-themed styles
|   |-- js/main.js                  # Frontend interaction logic
|-- tests/                          # pytest test suite
|-- seed_data/data.json             # Medical knowledge base
```

## Diagnosis Algorithm

The differential diagnosis engine uses a **combined scoring** approach:

1. **Weighted Overlap Score (60%)**: For each matching symptom, its configured weight is multiplied by a severity factor (mild=0.5, moderate=1.0, severe=1.5), then divided by the total possible weight for the condition.

2. **Jaccard Similarity (40%)**: Standard set-based similarity: |intersection| / |union| of patient symptoms and condition symptoms.

3. **Prevalence Adjustment**: The combined score is scaled by 0.8 + 0.4 * prevalence, giving more common conditions a slight boost.

4. **Confidence Capping**: Final score is capped at 99% since algorithmic diagnosis cannot be certain.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `MEDIASSIST_PORT` | `8011` | Server port |
| `MEDIASSIST_DEBUG` | `false` | Enable debug mode |
| `DATABASE_URL` | `sqlite:///...` | Database connection string |
| `SECRET_KEY` | (dev key) | Flask secret key |

## Medical Disclaimer

**This application is for educational purposes only.**

- It does NOT provide medical advice, diagnosis, or treatment
- It should NOT be used for self-diagnosis or self-treatment
- Always consult a qualified healthcare professional for medical concerns
- If you believe you have a medical emergency, call emergency services immediately
- The symptom checker uses a simplified algorithm that does not account for medical history, physical examination, or laboratory results
- Drug interaction data may not be complete or up-to-date

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## Acknowledgments

- Medical information is simplified for educational purposes
- Drug interaction data is illustrative and may not reflect current clinical guidelines
- Built with Flask, SQLAlchemy, and modern web technologies
