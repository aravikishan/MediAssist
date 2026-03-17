"""Model / schema tests for MediAssist."""

import json

from models.schemas import Symptom, Condition, Drug, Interaction, CheckSession


class TestSymptomModel:
    def test_to_dict(self, db_session):
        symptom = Symptom.query.filter_by(name="headache").first()
        assert symptom is not None
        d = symptom.to_dict()
        assert d["name"] == "headache"
        assert "body_region" in d

    def test_body_region(self, db_session):
        symptom = Symptom.query.filter_by(name="fever").first()
        assert symptom.body_region == "General"


class TestConditionModel:
    def test_get_symptom_names(self, db_session):
        cond = Condition.query.filter_by(name="Common Cold").first()
        names = cond.get_symptom_names()
        assert "cough" in names
        assert isinstance(names, list)

    def test_get_symptom_weights(self, db_session):
        cond = Condition.query.filter_by(name="Migraine").first()
        weights = cond.get_symptom_weights()
        assert weights.get("headache") == 2.0

    def test_to_dict(self, db_session):
        cond = Condition.query.filter_by(name="Influenza").first()
        d = cond.to_dict()
        assert d["category"] == "Respiratory"
        assert isinstance(d["symptoms"], list)


class TestDrugModel:
    def test_drug_to_dict(self, db_session):
        drug = Drug.query.filter_by(name="Ibuprofen").first()
        d = drug.to_dict()
        assert d["drug_class"] == "NSAID"
        assert isinstance(d["uses"], list)
        assert len(d["uses"]) > 0
