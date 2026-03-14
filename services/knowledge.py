"""Medical knowledge base and drug interaction checker."""

from typing import Optional

from models.schemas import Drug, Interaction
from models.database import db


class KnowledgeBase:
    """Provides access to the drug and interaction database."""

    def get_all_drugs(self) -> list[dict]:
        """Return all drugs sorted alphabetically."""
        drugs = Drug.query.order_by(Drug.name).all()
        return [d.to_dict() for d in drugs]

    def get_drug_detail(self, drug_id: int) -> Optional[dict]:
        """Get detailed info for a single drug."""
        drug = Drug.query.get(drug_id)
        if drug is None:
            return None
        return drug.to_dict()

    def search_drugs(self, query: str) -> list[dict]:
        """Search drugs by name or generic name."""
        term = f"%{query}%"
        drugs = Drug.query.filter(
            db.or_(
                Drug.name.ilike(term),
                Drug.generic_name.ilike(term),
                Drug.drug_class.ilike(term),
            )
        ).order_by(Drug.name).all()
        return [d.to_dict() for d in drugs]

    def check_interactions(self, drug_ids: list[int]) -> list[dict]:
        """Check all pairwise interactions among the given drugs.

        Parameters
        ----------
        drug_ids : list[int]
            IDs of drugs to check.

        Returns
        -------
        list[dict]
            Interaction records found, sorted by severity (most severe first).
        """
        if len(drug_ids) < 2:
            return []

        interactions = Interaction.query.filter(
            db.or_(
                db.and_(
                    Interaction.drug_a_id.in_(drug_ids),
                    Interaction.drug_b_id.in_(drug_ids),
                ),
            )
        ).all()

        severity_order = {
            "contraindicated": 0,
            "major": 1,
            "moderate": 2,
            "minor": 3,
        }

        result = [ix.to_dict() for ix in interactions]
        result.sort(key=lambda x: severity_order.get(x["severity"], 99))
        return result

    def check_interactions_by_name(self, drug_names: list[str]) -> list[dict]:
        """Check interactions by drug names instead of IDs."""
        drugs = Drug.query.filter(Drug.name.in_(drug_names)).all()
        drug_ids = [d.id for d in drugs]
        return self.check_interactions(drug_ids)

    def get_drugs_by_class(self) -> dict[str, list[dict]]:
        """Group drugs by their therapeutic class."""
        drugs = Drug.query.order_by(Drug.drug_class, Drug.name).all()
        grouped: dict[str, list[dict]] = {}
        for d in drugs:
            cls = d.drug_class or "Other"
            if cls not in grouped:
                grouped[cls] = []
            grouped[cls].append(d.to_dict())
        return grouped

    def get_interaction_matrix(self, drug_ids: list[int]) -> dict:
        """Build an interaction matrix for a set of drugs.

        Returns a dict with drug info and a matrix of severity values.
        """
        drugs = Drug.query.filter(Drug.id.in_(drug_ids)).order_by(Drug.name).all()
        drug_list = [d.to_dict() for d in drugs]
        ordered_ids = [d.id for d in drugs]

        matrix = {}
        for i, id_a in enumerate(ordered_ids):
            for j, id_b in enumerate(ordered_ids):
                if i >= j:
                    continue
                ix = Interaction.query.filter(
                    db.or_(
                        db.and_(
                            Interaction.drug_a_id == id_a,
                            Interaction.drug_b_id == id_b,
                        ),
                        db.and_(
                            Interaction.drug_a_id == id_b,
                            Interaction.drug_b_id == id_a,
                        ),
                    )
                ).first()
                key = f"{id_a}-{id_b}"
                if ix:
                    matrix[key] = {
                        "severity": ix.severity,
                        "description": ix.description,
                        "recommendation": ix.recommendation,
                    }
                else:
                    matrix[key] = None

        return {
            "drugs": drug_list,
            "matrix": matrix,
        }
