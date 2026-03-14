"""Differential diagnosis engine using weighted symptom-condition matching.

The engine supports three scoring algorithms:
- Weighted overlap: each matching symptom contributes its weight
- Jaccard similarity: intersection / union of symptom sets
- Combined: blended score of both methods with prevalence adjustment
"""

import json
from typing import Optional

from models.schemas import Condition, Symptom, CheckSession
from models.database import db


class DiagnosisEngine:
    """Core engine for symptom-based differential diagnosis."""

    def __init__(self, min_confidence: float = 0.15, max_results: int = 10):
        self.min_confidence = min_confidence
        self.max_results = max_results

    def diagnose(
        self,
        symptom_names: list[str],
        severities: Optional[dict[str, str]] = None,
        method: str = "combined",
    ) -> list[dict]:
        """Run differential diagnosis and return ranked conditions.

        Parameters
        ----------
        symptom_names : list[str]
            Names of reported symptoms.
        severities : dict[str, str] | None
            Optional mapping of symptom name -> severity level
            ("mild", "moderate", "severe").
        method : str
            Scoring method: "weighted", "jaccard", or "combined".

        Returns
        -------
        list[dict]
            Ranked list of conditions with confidence scores.
        """
        if not symptom_names:
            return []

        if severities is None:
            severities = {}

        severity_multipliers = {
            "mild": 0.5,
            "moderate": 1.0,
            "severe": 1.5,
        }

        patient_symptoms = set(s.lower().strip() for s in symptom_names)
        conditions = Condition.query.all()
        results = []

        for condition in conditions:
            condition_symptoms = set(
                s.lower().strip() for s in condition.get_symptom_names()
            )
            if not condition_symptoms:
                continue

            weights = condition.get_symptom_weights()
            weights_lower = {k.lower().strip(): v for k, v in weights.items()}

            matching = patient_symptoms & condition_symptoms

            if not matching:
                continue

            if method == "weighted":
                score = self._weighted_overlap(
                    matching, condition_symptoms, weights_lower,
                    severities, severity_multipliers,
                )
            elif method == "jaccard":
                score = self._jaccard_similarity(
                    patient_symptoms, condition_symptoms
                )
            else:
                w_score = self._weighted_overlap(
                    matching, condition_symptoms, weights_lower,
                    severities, severity_multipliers,
                )
                j_score = self._jaccard_similarity(
                    patient_symptoms, condition_symptoms
                )
                prevalence_factor = 0.8 + 0.4 * condition.prevalence
                score = (0.6 * w_score + 0.4 * j_score) * prevalence_factor

            score = min(score, 0.99)

            if score >= self.min_confidence:
                matching_symptom_list = sorted(matching)
                missing_symptoms = sorted(condition_symptoms - patient_symptoms)

                results.append({
                    "condition": condition.to_dict(),
                    "confidence": round(score, 4),
                    "matching_symptoms": matching_symptom_list,
                    "missing_symptoms": missing_symptoms,
                    "match_ratio": round(
                        len(matching) / len(condition_symptoms), 3
                    ),
                    "method": method,
                })

        results.sort(key=lambda r: r["confidence"], reverse=True)
        return results[: self.max_results]

    def _weighted_overlap(
        self,
        matching: set,
        condition_symptoms: set,
        weights: dict,
        severities: dict,
        severity_multipliers: dict,
    ) -> float:
        """Score based on sum of weights for matching symptoms."""
        total_possible = sum(
            weights.get(s, 1.0) for s in condition_symptoms
        )
        if total_possible == 0:
            return 0.0

        earned = 0.0
        for symptom in matching:
            base_weight = weights.get(symptom, 1.0)
            sev = severities.get(symptom, "moderate")
            multiplier = severity_multipliers.get(sev, 1.0)
            earned += base_weight * multiplier

        return earned / total_possible

    @staticmethod
    def _jaccard_similarity(set_a: set, set_b: set) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set_a and not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        return intersection / union if union > 0 else 0.0

    def save_session(
        self,
        symptom_names: list[str],
        severities: dict,
        results: list[dict],
    ) -> CheckSession:
        """Persist a check session to the database."""
        top_condition = results[0]["condition"]["name"] if results else ""
        confidence = results[0]["confidence"] if results else 0.0

        serializable_results = []
        for r in results:
            serializable_results.append({
                "condition_name": r["condition"]["name"],
                "confidence": r["confidence"],
                "matching_symptoms": r["matching_symptoms"],
                "missing_symptoms": r["missing_symptoms"],
                "match_ratio": r["match_ratio"],
            })

        session = CheckSession(
            symptoms_input=json.dumps(symptom_names),
            severity_input=json.dumps(severities),
            results=json.dumps(serializable_results),
            top_condition=top_condition,
            confidence=confidence,
        )
        db.session.add(session)
        db.session.commit()
        return session

    def get_history(self, limit: int = 20) -> list[dict]:
        """Retrieve recent check sessions."""
        sessions = (
            CheckSession.query
            .order_by(CheckSession.created_at.desc())
            .limit(limit)
            .all()
        )
        return [s.to_dict() for s in sessions]

    def get_symptoms_by_region(self) -> dict[str, list[dict]]:
        """Group all symptoms by body region."""
        symptoms = Symptom.query.order_by(Symptom.body_region, Symptom.name).all()
        grouped: dict[str, list[dict]] = {}
        for s in symptoms:
            region = s.body_region or "General"
            if region not in grouped:
                grouped[region] = []
            grouped[region].append(s.to_dict())
        return grouped

    def get_all_symptoms(self) -> list[dict]:
        """Return all symptoms as dicts."""
        symptoms = Symptom.query.order_by(Symptom.name).all()
        return [s.to_dict() for s in symptoms]

    def get_condition_detail(self, condition_id: int) -> Optional[dict]:
        """Get detailed info for a single condition."""
        condition = Condition.query.get(condition_id)
        if condition is None:
            return None
        return condition.to_dict()

    def get_all_conditions(self) -> list[dict]:
        """Return all conditions as dicts."""
        conditions = Condition.query.order_by(Condition.name).all()
        return [c.to_dict() for c in conditions]
