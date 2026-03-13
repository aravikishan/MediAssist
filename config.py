"""Application configuration for MediAssist."""

import os

# Server
HOST = "0.0.0.0"
PORT = int(os.environ.get("MEDIASSIST_PORT", 8011))
DEBUG = os.environ.get("MEDIASSIST_DEBUG", "false").lower() == "true"

# Database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "instance", "mediassist.db")
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", f"sqlite:///{DATABASE_PATH}"
)

# Diagnosis engine
MIN_CONFIDENCE_THRESHOLD = 0.15
MAX_RESULTS = 10
SYMPTOM_WEIGHT_DEFAULT = 1.0
SEVERITY_MULTIPLIER = {
    "mild": 0.5,
    "moderate": 1.0,
    "severe": 1.5,
}

# Body regions for symptom browsing
BODY_REGIONS = [
    "Head", "Eyes", "Ears", "Nose/Throat", "Chest",
    "Abdomen", "Back", "Arms", "Legs", "Skin", "General",
]

# Drug interaction severity levels
INTERACTION_SEVERITY = {
    "minor": {"label": "Minor", "color": "#ffc107", "priority": 1},
    "moderate": {"label": "Moderate", "color": "#fd7e14", "priority": 2},
    "major": {"label": "Major", "color": "#dc3545", "priority": 3},
    "contraindicated": {"label": "Contraindicated", "color": "#6f42c1", "priority": 4},
}

# Application
SECRET_KEY = os.environ.get("SECRET_KEY", "mediassist-dev-key-change-in-prod")
TESTING = False
