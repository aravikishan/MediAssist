"""Shared pytest fixtures for MediAssist tests."""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from models.database import db as _db


@pytest.fixture(scope="session")
def app():
    """Create a test application instance."""
    application = create_app(testing=True)
    yield application


@pytest.fixture(scope="session")
def _setup_db(app):
    """Create tables and seed minimal test data once per session."""
    with app.app_context():
        _db.create_all()
        _seed_test_data()
        yield
        _db.drop_all()


@pytest.fixture()
def client(app, _setup_db):
    """Flask test client."""
    with app.test_client() as c:
        with app.app_context():
            yield c


@pytest.fixture()
def db_session(app, _setup_db):
    """Provide a database session within app context."""
    with app.app_context():
        yield _db.session


def _seed_test_data():
    """Insert minimal test data."""
    from models.schemas import Symptom, Condition, Drug, Interaction

    symptoms = [
        Symptom(name="headache", description="Pain in the head", body_region="Head", severity_weight=1.0),
        Symptom(name="fever", description="Elevated body temperature", body_region="General", severity_weight=1.2),
        Symptom(name="cough", description="Repetitive expulsion of air", body_region="Chest", severity_weight=1.0),
        Symptom(name="fatigue", description="Extreme tiredness", body_region="General", severity_weight=0.8),
        Symptom(name="nausea", description="Feeling of sickness", body_region="Abdomen", severity_weight=0.9),
        Symptom(name="sore throat", description="Pain in the throat", body_region="Nose/Throat", severity_weight=1.0),
    ]
    for s in symptoms:
        _db.session.add(s)

    conditions = [
        Condition(
            name="Common Cold",
            description="Viral infection of the upper respiratory tract.",
            category="Respiratory",
            symptom_names=json.dumps(["headache", "fever", "cough", "sore throat", "fatigue"]),
            symptom_weights=json.dumps({"cough": 1.5, "sore throat": 1.3, "fever": 1.0, "headache": 0.8, "fatigue": 0.7}),
            prevalence=0.9,
            when_to_seek_care="If symptoms last more than 10 days or worsen.",
            risk_factors=json.dumps(["Weakened immune system", "Cold weather exposure"]),
        ),
        Condition(
            name="Migraine",
            description="Severe recurring headache often with nausea.",
            category="Neurological",
            symptom_names=json.dumps(["headache", "nausea", "fatigue"]),
            symptom_weights=json.dumps({"headache": 2.0, "nausea": 1.2, "fatigue": 0.8}),
            prevalence=0.6,
            when_to_seek_care="If headaches are sudden and severe.",
            risk_factors=json.dumps(["Family history", "Stress", "Hormonal changes"]),
        ),
        Condition(
            name="Influenza",
            description="Viral infection causing high fever and body aches.",
            category="Respiratory",
            symptom_names=json.dumps(["fever", "cough", "fatigue", "headache"]),
            symptom_weights=json.dumps({"fever": 2.0, "fatigue": 1.5, "cough": 1.0, "headache": 0.8}),
            prevalence=0.7,
            when_to_seek_care="If you have difficulty breathing or persistent chest pain.",
            risk_factors=json.dumps(["Age over 65", "Chronic conditions"]),
        ),
    ]
    for c in conditions:
        _db.session.add(c)

    drugs = [
        Drug(name="Ibuprofen", generic_name="Ibuprofen", drug_class="NSAID",
             uses=json.dumps(["Pain relief", "Fever reduction", "Anti-inflammatory"]),
             side_effects=json.dumps(["Stomach upset", "Nausea"])),
        Drug(name="Aspirin", generic_name="Acetylsalicylic acid", drug_class="NSAID",
             uses=json.dumps(["Pain relief", "Blood thinner"]),
             side_effects=json.dumps(["Stomach bleeding", "Tinnitus"])),
        Drug(name="Warfarin", generic_name="Warfarin", drug_class="Anticoagulant",
             uses=json.dumps(["Blood clot prevention"]),
             side_effects=json.dumps(["Bleeding", "Bruising"])),
    ]
    for d in drugs:
        _db.session.add(d)
    _db.session.flush()

    ix = Interaction(
        drug_a_id=drugs[0].id, drug_b_id=drugs[2].id,
        severity="major",
        description="NSAIDs may increase the anticoagulant effect of warfarin, raising bleeding risk.",
        recommendation="Avoid concurrent use or monitor INR closely.",
    )
    _db.session.add(ix)

    ix2 = Interaction(
        drug_a_id=drugs[1].id, drug_b_id=drugs[2].id,
        severity="major",
        description="Aspirin enhances anticoagulant effect of warfarin significantly.",
        recommendation="Generally avoid combination; consult physician.",
    )
    _db.session.add(ix2)

    _db.session.commit()
