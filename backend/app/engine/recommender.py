"""
Core Recommendation Engine workflow coordinator.
Executes multi-factor evaluation, ranking, coverage calculations, and decision support packaging.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any

from ..config import settings
from ..data.loader import CropDataLoader
from ..schemas.input_schema import CropRecommendationRequest
from ..schemas.output_schema import (
    RecommendationResponse,
    CropRecommendationCard,
    FactorStatusEnum,
    SuitabilityCategoryEnum,
)
from .scoring import evaluate_crop_compatibility
from .explanations import (
    generate_crop_explanation,
    generate_suggested_next_steps,
    generate_assumptions_and_limitations,
)


def run_crop_recommendation(request: CropRecommendationRequest) -> RecommendationResponse:
    """
    Executes the full explainable recommendation pipeline.
    """
    request_id = f"REC-{uuid.uuid4().hex[:8].upper()}"
    generation_date = datetime.now().isoformat()
    crops = CropDataLoader.load_crops()
    weights = settings.weights

    # Format user inputs summary
    user_inputs_summary = {
        "location": {
            "country": request.location.country,
            "state": request.location.state,
            "district": request.location.district or "Not specified",
            "season": request.location.season.value,
            "irrigation": request.location.irrigation.value,
        },
        "soil": {
            "soil_type": request.soil.soil_type.value,
            "soil_ph": request.soil.soil_ph if request.soil.soil_ph is not None else "Not provided",
            "nitrogen": f"{request.soil.nitrogen} {request.soil.npk_unit}" if request.soil.nitrogen is not None else "Not provided",
            "phosphorus": f"{request.soil.phosphorus} {request.soil.npk_unit}" if request.soil.phosphorus is not None else "Not provided",
            "potassium": f"{request.soil.potassium} {request.soil.npk_unit}" if request.soil.potassium is not None else "Not provided",
            "is_measured": request.soil.is_measured,
        },
        "environment": {
            "temperature": f"{request.environment.temperature}°C" if request.environment.temperature is not None else "Not provided",
            "rainfall": f"{request.environment.rainfall} mm ({request.environment.rainfall_period.value})" if request.environment.rainfall is not None else "Not provided",
            "relative_humidity": f"{request.environment.relative_humidity}%" if request.environment.relative_humidity is not None else "Not provided",
            "sunlight_hours": f"{request.environment.sunlight_hours} hrs" if request.environment.sunlight_hours is not None else "Not provided",
            "is_measured": request.environment.is_measured,
        }
    }

    # Evaluate each crop in dataset
    crop_cards: List[CropRecommendationCard] = []
    overall_coverages: List[float] = []

    for crop in crops:
        score, coverage, factor_evals, category = evaluate_crop_compatibility(
            crop_data=crop,
            request=request,
            weights=weights
        )
        overall_coverages.append(coverage)

        matched_names = [e.factor_name for e in factor_evals if e.status == FactorStatusEnum.MATCHED]
        mismatched_names = [e.factor_name for e in factor_evals if e.status == FactorStatusEnum.POTENTIAL_MISMATCH]
        unevaluated_names = [e.factor_name for e in factor_evals if e.status == FactorStatusEnum.UN_EVALUATED]

        # Extract risks from mismatched factors
        risks = [f"{e.factor_name}: {e.explanation}" for e in factor_evals if e.status == FactorStatusEnum.POTENTIAL_MISMATCH]

        why_crop = generate_crop_explanation(
            crop_name=crop["name"],
            evaluations=factor_evals,
            matched=matched_names,
            mismatched=mismatched_names,
            unevaluated=unevaluated_names,
            request=request,
            score=score
        )

        card = CropRecommendationCard(
            crop_id=crop["id"],
            crop_name=crop["name"],
            scientific_name=crop["scientific_name"],
            category=crop["category"],
            suitability_category=category,
            compatibility_score=score if category != SuitabilityCategoryEnum.INSUFFICIENT_DATA else None,
            data_coverage_pct=coverage,
            matched_factors=matched_names,
            mismatched_factors=mismatched_names,
            unevaluated_factors=unevaluated_names,
            factor_evaluations=factor_evals,
            why_this_crop=why_crop,
            key_risks_or_mismatches=risks,
            irrigation_advice=crop.get("irrigation_considerations", "Ensure optimal moisture management."),
            data_source=crop.get("data_source", "ICAR"),
            reference_date=crop.get("reference_date", "2024-03"),
            is_verified_agronomic=crop.get("is_verified_agronomic", True)
        )
        crop_cards.append(card)

    # Average coverage across evaluated factors
    avg_coverage = round(sum(overall_coverages) / len(overall_coverages), 1) if overall_coverages else 0.0

    # Sort crops by score (descending) and coverage (descending)
    crop_cards.sort(key=lambda c: (c.compatibility_score or -1, c.data_coverage_pct), reverse=True)

    # Check sufficient data criteria
    insufficient_reasons = []
    is_sufficient = True

    if avg_coverage < settings.min_coverage_threshold_pct:
        is_sufficient = False
        insufficient_reasons.append(
            f"Overall input coverage is only {avg_coverage}%, which falls below the minimum required "
            f"threshold of {settings.min_coverage_threshold_pct}%."
        )

    # Check if both soil and environment are completely blank
    has_soil_info = (
        request.soil.soil_type != "Unknown"
        or request.soil.soil_ph is not None
        or request.soil.nitrogen is not None
    )
    has_env_info = (
        request.environment.temperature is not None
        or request.environment.rainfall is not None
        or request.environment.relative_humidity is not None
    )

    if not has_soil_info and not has_env_info:
        is_sufficient = False
        insufficient_reasons.append(
            "Neither soil characteristics nor environmental data were provided. Recommendations cannot be reliably made on location and season alone."
        )

    # Extreme temperature check
    if request.environment.temperature is not None and request.environment.temperature > 46.0:
        insufficient_reasons.append(
            f"Extreme ambient temperature of {request.environment.temperature}°C exceeds biological thermal tolerance limits for commercial field crops."
        )

    suggested_steps = generate_suggested_next_steps(request)
    limitations = generate_assumptions_and_limitations()

    return RecommendationResponse(
        request_id=request_id,
        generation_date=generation_date,
        status="INSUFFICIENT_DATA" if not is_sufficient else "SUCCESS",
        is_sufficient_data=is_sufficient,
        overall_coverage_pct=avg_coverage,
        user_inputs_summary=user_inputs_summary,
        insufficient_data_reasons=insufficient_reasons,
        suggested_next_steps=suggested_steps,
        recommendations=crop_cards,
        dataset_version=settings.dataset_version,
        assumptions_and_limitations=limitations,
        safety_notice=settings.safety_notice
    )
