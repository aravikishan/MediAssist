"""API endpoint tests for MediAssist."""

import json


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "MediAssist"


class TestSymptomsAPI:
    def test_list_all_symptoms(self, client):
        resp = client.get("/api/symptoms")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "symptoms" in data
        assert len(data["symptoms"]) >= 3

    def test_symptoms_grouped_by_region(self, client):
        resp = client.get("/api/symptoms/grouped")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "regions" in data
        assert isinstance(data["regions"], dict)

    def test_filter_symptoms_by_region(self, client):
        resp = client.get("/api/symptoms?region=Head")
        assert resp.status_code == 200
        data = resp.get_json()
        for s in data["symptoms"]:
            assert s["body_region"] == "Head"


class TestDiagnoseAPI:
    def test_diagnose_returns_results(self, client):
        resp = client.post(
            "/api/diagnose",
            data=json.dumps({"symptoms": ["headache", "fever", "cough"]}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert len(data["results"]) > 0
        assert data["results"][0]["confidence"] > 0
        assert "disclaimer" in data

    def test_diagnose_empty_symptoms(self, client):
        resp = client.post(
            "/api/diagnose",
            data=json.dumps({"symptoms": []}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_diagnose_with_severities(self, client):
        resp = client.post(
            "/api/diagnose",
            data=json.dumps({
                "symptoms": ["headache", "nausea"],
                "severities": {"headache": "severe", "nausea": "moderate"},
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["results"]) > 0


class TestConditionsAPI:
    def test_list_conditions(self, client):
        resp = client.get("/api/conditions")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["conditions"]) >= 2

    def test_condition_detail(self, client):
        resp = client.get("/api/conditions/1")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "name" in data

    def test_condition_not_found(self, client):
        resp = client.get("/api/conditions/9999")
        assert resp.status_code == 404


class TestDrugsAPI:
    def test_list_drugs(self, client):
        resp = client.get("/api/drugs")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["drugs"]) >= 2

    def test_search_drugs(self, client):
        resp = client.get("/api/drugs?q=ibuprofen")
        data = resp.get_json()
        assert any("Ibuprofen" in d["name"] for d in data["drugs"])


class TestInteractionsAPI:
    def test_check_interactions_by_name(self, client):
        resp = client.post(
            "/api/interactions/check",
            data=json.dumps({"drug_names": ["Ibuprofen", "Warfarin"]}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] >= 1
        assert data["interactions"][0]["severity"] == "major"
