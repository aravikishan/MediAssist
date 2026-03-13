"""SQLite database setup and initialisation for MediAssist."""

import json
import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Create tables and seed data if the database is empty."""
    with app.app_context():
        db.create_all()

        from models.schemas import Symptom, Condition, Drug, Interaction

        if Symptom.query.first() is None:
            _seed_database()


def _seed_database():
    """Load seed data from the JSON knowledge base."""
    from models.schemas import Symptom, Condition, Drug, Interaction

    seed_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "seed_data", "data.json"
    )
    if not os.path.exists(seed_path):
        return

    with open(seed_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    symptom_map = {}
    for s in data.get("symptoms", []):
        symptom = Symptom(
            name=s["name"],
            description=s.get("description", ""),
            body_region=s.get("body_region", "General"),
            severity_weight=s.get("severity_weight", 1.0),
        )
        db.session.add(symptom)
        db.session.flush()
        symptom_map[s["name"]] = symptom.id

    condition_map = {}
    for c in data.get("conditions", []):
        condition = Condition(
            name=c["name"],
            description=c.get("description", ""),
            category=c.get("category", "General"),
            risk_factors=json.dumps(c.get("risk_factors", [])),
            when_to_seek_care=c.get("when_to_seek_care", ""),
            symptom_names=json.dumps(c.get("symptoms", [])),
            symptom_weights=json.dumps(c.get("symptom_weights", {})),
            prevalence=c.get("prevalence", 0.5),
        )
        db.session.add(condition)
        db.session.flush()
        condition_map[c["name"]] = condition.id

    drug_map = {}
    for d in data.get("drugs", []):
        drug = Drug(
            name=d["name"],
            generic_name=d.get("generic_name", d["name"]),
            drug_class=d.get("drug_class", ""),
            uses=json.dumps(d.get("uses", [])),
            side_effects=json.dumps(d.get("side_effects", [])),
            warnings=d.get("warnings", ""),
        )
        db.session.add(drug)
        db.session.flush()
        drug_map[d["name"]] = drug.id

    for ix in data.get("interactions", []):
        drug_a = drug_map.get(ix["drug_a"])
        drug_b = drug_map.get(ix["drug_b"])
        if drug_a and drug_b:
            interaction = Interaction(
                drug_a_id=drug_a,
                drug_b_id=drug_b,
                severity=ix.get("severity", "minor"),
                description=ix.get("description", ""),
                recommendation=ix.get("recommendation", ""),
            )
            db.session.add(interaction)

    db.session.commit()
