"""HTML-serving view routes for MediAssist."""

from flask import Blueprint, render_template, request, jsonify

from services.diagnosis import DiagnosisEngine
from services.knowledge import KnowledgeBase

views_bp = Blueprint("views", __name__)

engine = DiagnosisEngine()
kb = KnowledgeBase()


@views_bp.route("/")
def index():
    """Symptom checker home page."""
    grouped = engine.get_symptoms_by_region()
    return render_template("index.html", symptom_regions=grouped)


@views_bp.route("/check", methods=["POST"])
def check():
    """Process symptom check form and show results."""
    selected = request.form.getlist("symptoms")
    severities = {}
    for s in selected:
        sev_key = f"severity_{s}"
        severities[s] = request.form.get(sev_key, "moderate")

    method = request.form.get("method", "combined")
    results = engine.diagnose(selected, severities, method)
    engine.save_session(selected, severities, results)

    return render_template(
        "results.html",
        symptoms=selected,
        severities=severities,
        results=results,
    )


@views_bp.route("/conditions")
def conditions():
    """Browse conditions."""
    all_conditions = engine.get_all_conditions()
    categories = sorted(set(c["category"] for c in all_conditions))
    selected_cat = request.args.get("category", "")
    if selected_cat:
        all_conditions = [c for c in all_conditions if c["category"] == selected_cat]
    return render_template(
        "conditions.html",
        conditions=all_conditions,
        categories=categories,
        selected_category=selected_cat,
    )


@views_bp.route("/drugs")
def drugs():
    """Drug interaction checker page."""
    all_drugs = kb.get_all_drugs()
    return render_template("drugs.html", drugs=all_drugs)


@views_bp.route("/about")
def about():
    """About page with medical disclaimer."""
    return render_template("about.html")
