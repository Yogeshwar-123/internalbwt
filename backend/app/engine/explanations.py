"""
Explainability and rationale generation module.
Translates factor evaluations into natural-language agronomic explanations.
Guarantees explanations reflect actual input-to-dataset comparisons.
"""

from typing import List, Dict, Any
from ..schemas.input_schema import CropRecommendationRequest
from ..schemas.output_schema import FactorEvaluation, FactorStatusEnum


def generate_crop_explanation(
    crop_name: str,
    evaluations: List[FactorEvaluation],
    matched: List[str],
    mismatched: List[str],
    unevaluated: List[str],
    request: CropRecommendationRequest,
    score: float,
) -> str:
    """
    Builds a grounded, dynamic 'Why this crop?' explanation
    referencing actual evaluated parameters.
    """
    parts = []

    # 1. Opening statement with score and season context
    season_val = request.location.season.value
    state_val = request.location.state
    parts.append(
        f"{crop_name} receives an estimated compatibility score of {score}/100 "
        f"for {season_val} season cultivation in {state_val}."
    )

    # 2. Key matching drivers
    matched_evals = [e for e in evaluations if e.status == FactorStatusEnum.MATCHED and e.score_awarded >= e.weight * 0.7]
    if matched_evals:
        matched_summaries = []
        for e in matched_evals:
            if e.factor_name == "Growing Season":
                matched_summaries.append(f"{season_val} season alignment")
            elif e.factor_name == "Soil Type":
                matched_summaries.append(f"favorable {e.user_value} soil texture")
            elif e.factor_name == "Soil pH":
                matched_summaries.append(f"soil pH {e.user_value} within the crop's preferred range")
            elif e.factor_name == "Temperature":
                matched_summaries.append(f"recorded temperature ({e.user_value}) falling within thermal limits")
            elif e.factor_name.startswith("Rainfall"):
                matched_summaries.append(f"adequate moisture ({e.user_value})")
            elif e.factor_name == "Relative Humidity":
                matched_summaries.append(f"atmospheric humidity ({e.user_value})")
            else:
                matched_summaries.append(f"{e.factor_name} availability")

        parts.append("Key positive factors: " + "; ".join(matched_summaries) + ".")

    # 3. Notable constraints or potential mismatches
    mismatched_evals = [e for e in evaluations if e.status == FactorStatusEnum.POTENTIAL_MISMATCH]
    if mismatched_evals:
        constraint_summaries = []
        for e in mismatched_evals:
            constraint_summaries.append(f"{e.factor_name}: {e.explanation}")
        parts.append("Important constraints to manage: " + " ".join(constraint_summaries))

    # 4. Un-evaluated factors notice
    if unevaluated:
        parts.append(
            f"Note: {len(unevaluated)} parameter(s) ({', '.join(unevaluated)}) were not provided and were "
            "excluded from scoring without penalty."
        )

    return " ".join(parts)


def generate_suggested_next_steps(request: CropRecommendationRequest) -> List[str]:
    """Generates practical, actionable agronomic next steps based on missing or estimated inputs."""
    steps = []

    # Check soil lab status
    if not request.soil.is_measured or any(v is None for v in [request.soil.nitrogen, request.soil.phosphorus, request.soil.potassium]):
        steps.append(
            "Conduct laboratory soil testing through your local Krishi Vigyan Kendra (KVK) or state agriculture office "
            "to obtain verified N-P-K nutrient status and organic carbon content."
        )

    if request.soil.soil_ph is None:
        steps.append(
            "Determine soil pH using an on-farm test kit or lab test. Extreme acidity or alkalinity significantly inhibits nutrient uptake."
        )

    if not request.environment.is_measured:
        steps.append(
            "Cross-reference local monsoon forecast and temperature trends from the India Meteorological Department (IMD) "
            "or district agromet advisory services (Gramin Krishi Mausam Sewa)."
        )

    steps.append(
        "Consult your local Block Agricultural Officer (BAO) or Agricultural Extension Officer (AEO) to verify variety selection, "
        "local seed availability, and current pest/disease pressures before planting."
    )

    return steps


def generate_assumptions_and_limitations() -> List[str]:
    """Provides complete scientific and operational disclaimers."""
    return [
        "Compatibility scores represent prototype agro-ecological suitability indices, NOT probabilistic success rates or yield forecasts.",
        "Reference thresholds are compiled from published ICAR, TNAU, and FAO crop cultivation guidelines (2024).",
        "Microclimatic variations, subsoil hardpans, saline groundwater, and sudden extreme weather events cannot be captured by broad environmental indicators.",
        "Pest outbreaks, weed competition, market price volatility, and seed germination quality must be evaluated separately by the farm manager.",
        "Missing user inputs are mathematically excluded from the score denominator to avoid penalizing unmeasured fields, which may affect absolute comparability."
    ]
