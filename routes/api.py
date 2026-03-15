"""REST API endpoints for MediAssist."""

from flask import Blueprint, jsonify, request

from services.diagnosis import DiagnosisEngine
from services.knowledge import KnowledgeBase

api_bp = Blueprint("api", __name__, url_prefix="/api")

engine = DiagnosisEngine()
kb = KnowledgeBase()


@api_bp.route("/symptoms", methods=["GET"])
def list_symptoms():
    """List all symptoms, optionally filtered by body region."""
    region = request.args.get("region")
    if region:
        grouped = engine.get_symptoms_by_region()
        symptoms = grouped.get(region, [])
    else:
        symptoms = engine.get_all_symptoms()
    return jsonify({"symptoms": symptoms})


@api_bp.route("/symptoms/grouped", methods=["GET"])
def symptoms_grouped():
    """Get symptoms grouped by body region."""
    grouped = engine.get_symptoms_by_region()
    return jsonify({"regions": grouped})


@api_bp.route("/diagnose", methods=["POST"])
def diagnose():
    """Run differential diagnosis on provided symptoms."""
    data = request.get_json(silent=True) or {}
    symptom_names = data.get("symptoms", [])
    severities = data.get("severities", {})
    method = data.get("method", "combined")

    if not symptom_names:
        return jsonify({"error": "No symptoms provided"}), 400

    if method not in ("weighted", "jaccard", "combined"):
        method = "combined"

    results = engine.diagnose(symptom_names, severities, method)
    session = engine.save_session(symptom_names, severities, results)

    return jsonify({
        "session_id": session.id,
        "symptom_count": len(symptom_names),
        "results": results,
        "disclaimer": (
            "This tool is for educational purposes only. "
            "It does not provide medical advice, diagnosis, or treatment. "
            "Always consult a qualified healthcare professional."
        ),
    })


@api_bp.route("/conditions", methods=["GET"])
def list_conditions():
    """List all conditions in the knowledge base."""
    conditions = engine.get_all_conditions()
    category = request.args.get("category")
    if category:
        conditions = [c for c in conditions if c["category"] == category]
    return jsonify({"conditions": conditions})


@api_bp.route("/conditions/<int:condition_id>", methods=["GET"])
def condition_detail(condition_id):
    """Get details for a specific condition."""
    detail = engine.get_condition_detail(condition_id)
    if detail is None:
        return jsonify({"error": "Condition not found"}), 404
    return jsonify(detail)


@api_bp.route("/drugs", methods=["GET"])
def list_drugs():
    """List all drugs, optionally filtered by search query."""
    query = request.args.get("q")
    if query:
        drugs = kb.search_drugs(query)
    else:
        drugs = kb.get_all_drugs()
    return jsonify({"drugs": drugs})


@api_bp.route("/drugs/<int:drug_id>", methods=["GET"])
def drug_detail(drug_id):
    """Get details for a specific drug."""
    detail = kb.get_drug_detail(drug_id)
    if detail is None:
        return jsonify({"error": "Drug not found"}), 404
    return jsonify(detail)


@api_bp.route("/drugs/grouped", methods=["GET"])
def drugs_grouped():
    """Get drugs grouped by therapeutic class."""
    grouped = kb.get_drugs_by_class()
    return jsonify({"classes": grouped})


@api_bp.route("/interactions/check", methods=["POST"])
def check_interactions():
    """Check drug interactions for a list of drug IDs."""
    data = request.get_json(silent=True) or {}
    drug_ids = data.get("drug_ids", [])
    drug_names = data.get("drug_names", [])

    if drug_names:
        interactions = kb.check_interactions_by_name(drug_names)
    elif drug_ids:
        interactions = kb.check_interactions(drug_ids)
    else:
        return jsonify({"error": "Provide drug_ids or drug_names"}), 400

    return jsonify({
        "interactions": interactions,
        "count": len(interactions),
    })


@api_bp.route("/interactions/matrix", methods=["POST"])
def interaction_matrix():
    """Build an interaction matrix for a set of drugs."""
    data = request.get_json(silent=True) or {}
    drug_ids = data.get("drug_ids", [])

    if len(drug_ids) < 2:
        return jsonify({"error": "Provide at least 2 drug IDs"}), 400

    matrix = kb.get_interaction_matrix(drug_ids)
    return jsonify(matrix)


@api_bp.route("/history", methods=["GET"])
def check_history():
    """Get recent symptom check sessions."""
    limit = request.args.get("limit", 20, type=int)
    history = engine.get_history(limit=limit)
    return jsonify({"sessions": history})


@api_bp.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "MediAssist"})
