"""Service-layer tests for MediAssist."""

from services.diagnosis import DiagnosisEngine
from services.knowledge import KnowledgeBase


class TestDiagnosisEngine:
    def test_diagnose_returns_ranked_results(self, client):
        engine = DiagnosisEngine()
        results = engine.diagnose(["headache", "fever", "cough"])
        assert len(results) > 0
        confidences = [r["confidence"] for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_jaccard_method(self, client):
        engine = DiagnosisEngine()
        results = engine.diagnose(["headache", "fever"], method="jaccard")
        assert len(results) > 0
        for r in results:
            assert r["method"] == "jaccard"

    def test_weighted_method(self, client):
        engine = DiagnosisEngine()
        results = engine.diagnose(["headache", "nausea"], method="weighted")
        assert len(results) > 0
        for r in results:
            assert r["method"] == "weighted"

    def test_severity_affects_score(self, client):
        engine = DiagnosisEngine()
        results_moderate = engine.diagnose(
            ["headache"], severities={"headache": "moderate"}
        )
        results_severe = engine.diagnose(
            ["headache"], severities={"headache": "severe"}
        )
        if results_moderate and results_severe:
            assert results_severe[0]["confidence"] >= results_moderate[0]["confidence"]

    def test_empty_symptoms(self, client):
        engine = DiagnosisEngine()
        results = engine.diagnose([])
        assert results == []

    def test_save_and_get_history(self, client):
        engine = DiagnosisEngine()
        results = engine.diagnose(["fever", "cough"])
        engine.save_session(["fever", "cough"], {}, results)
        history = engine.get_history(limit=5)
        assert len(history) >= 1
        assert history[0]["symptoms"] == ["fever", "cough"]

    def test_get_symptoms_by_region(self, client):
        engine = DiagnosisEngine()
        grouped = engine.get_symptoms_by_region()
        assert isinstance(grouped, dict)
        assert any(len(v) > 0 for v in grouped.values())

    def test_jaccard_similarity_static(self, client):
        score = DiagnosisEngine._jaccard_similarity(
            {"a", "b", "c"}, {"b", "c", "d"}
        )
        assert abs(score - 0.5) < 0.01


class TestKnowledgeBase:
    def test_get_all_drugs(self, client):
        kb = KnowledgeBase()
        drugs = kb.get_all_drugs()
        assert len(drugs) >= 2

    def test_search_drugs(self, client):
        kb = KnowledgeBase()
        results = kb.search_drugs("NSAID")
        assert len(results) >= 1

    def test_check_interactions(self, client):
        kb = KnowledgeBase()
        from models.schemas import Drug
        ibu = Drug.query.filter_by(name="Ibuprofen").first()
        war = Drug.query.filter_by(name="Warfarin").first()
        interactions = kb.check_interactions([ibu.id, war.id])
        assert len(interactions) >= 1
        assert interactions[0]["severity"] == "major"
