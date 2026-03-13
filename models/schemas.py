"""SQLAlchemy models for MediAssist."""

import json
from datetime import datetime, timezone

from models.database import db


class Symptom(db.Model):
    """A medical symptom."""
    __tablename__ = "symptoms"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    body_region = db.Column(db.String(60), default="General", index=True)
    severity_weight = db.Column(db.Float, default=1.0)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "body_region": self.body_region,
            "severity_weight": self.severity_weight,
        }


class Condition(db.Model):
    """A medical condition with associated symptoms and metadata."""
    __tablename__ = "conditions"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, default="")
    category = db.Column(db.String(80), default="General", index=True)
    risk_factors = db.Column(db.Text, default="[]")
    when_to_seek_care = db.Column(db.Text, default="")
    symptom_names = db.Column(db.Text, default="[]")
    symptom_weights = db.Column(db.Text, default="{}")
    prevalence = db.Column(db.Float, default=0.5)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def get_symptom_names(self):
        return json.loads(self.symptom_names) if self.symptom_names else []

    def get_symptom_weights(self):
        return json.loads(self.symptom_weights) if self.symptom_weights else {}

    def get_risk_factors(self):
        return json.loads(self.risk_factors) if self.risk_factors else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "risk_factors": self.get_risk_factors(),
            "when_to_seek_care": self.when_to_seek_care,
            "symptoms": self.get_symptom_names(),
            "symptom_weights": self.get_symptom_weights(),
            "prevalence": self.prevalence,
        }


class Drug(db.Model):
    """A medication in the knowledge base."""
    __tablename__ = "drugs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=False, index=True)
    generic_name = db.Column(db.String(200), default="")
    drug_class = db.Column(db.String(120), default="")
    uses = db.Column(db.Text, default="[]")
    side_effects = db.Column(db.Text, default="[]")
    warnings = db.Column(db.Text, default="")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def get_uses(self):
        return json.loads(self.uses) if self.uses else []

    def get_side_effects(self):
        return json.loads(self.side_effects) if self.side_effects else []

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "generic_name": self.generic_name,
            "drug_class": self.drug_class,
            "uses": self.get_uses(),
            "side_effects": self.get_side_effects(),
            "warnings": self.warnings,
        }


class Interaction(db.Model):
    """A drug-drug interaction record."""
    __tablename__ = "interactions"

    id = db.Column(db.Integer, primary_key=True)
    drug_a_id = db.Column(db.Integer, db.ForeignKey("drugs.id"), nullable=False)
    drug_b_id = db.Column(db.Integer, db.ForeignKey("drugs.id"), nullable=False)
    severity = db.Column(db.String(30), default="minor")
    description = db.Column(db.Text, default="")
    recommendation = db.Column(db.Text, default="")
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    drug_a = db.relationship("Drug", foreign_keys=[drug_a_id], backref="interactions_as_a")
    drug_b = db.relationship("Drug", foreign_keys=[drug_b_id], backref="interactions_as_b")

    def to_dict(self):
        return {
            "id": self.id,
            "drug_a": self.drug_a.to_dict() if self.drug_a else None,
            "drug_b": self.drug_b.to_dict() if self.drug_b else None,
            "severity": self.severity,
            "description": self.description,
            "recommendation": self.recommendation,
        }


class CheckSession(db.Model):
    """A symptom check session storing user input and results."""
    __tablename__ = "check_sessions"

    id = db.Column(db.Integer, primary_key=True)
    symptoms_input = db.Column(db.Text, default="[]")
    severity_input = db.Column(db.Text, default="{}")
    results = db.Column(db.Text, default="[]")
    top_condition = db.Column(db.String(200), default="")
    confidence = db.Column(db.Float, default=0.0)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc)
    )

    def get_symptoms(self):
        return json.loads(self.symptoms_input) if self.symptoms_input else []

    def get_results(self):
        return json.loads(self.results) if self.results else []

    def to_dict(self):
        return {
            "id": self.id,
            "symptoms": self.get_symptoms(),
            "results": self.get_results(),
            "top_condition": self.top_condition,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
