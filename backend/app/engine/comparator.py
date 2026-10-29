"""
Side-by-side crop comparison engine.
Compares 2 to 5 crops across agronomic parameters, soil requirements, water needs, and scores.
Produces an objective trade-off summary without declaring an unfounded 'universal winner'.
"""

from typing import List, Dict, Any, Optional
from ..data.loader import CropDataLoader
from ..config import settings
from ..schemas.input_schema import CropComparisonRequest
from ..schemas.output_schema import (
    CropComparisonResponse,
    ComparisonRow,
)
from .scoring import evaluate_crop_compatibility


def compare_crops(request: CropComparisonRequest) -> CropComparisonResponse:
    """
    Performs side-by-side comparison of selected crops.
    """
    crop_ids = request.crop_ids
    loaded_crops: Dict[str, Dict[str, Any]] = {}
    crop_names: Dict[str, str] = {}

    for cid in crop_ids:
        crop = CropDataLoader.get_crop_by_id(cid)
        if crop:
            loaded_crops[cid] = crop
            crop_names[cid] = crop["name"]
        else:
            raise ValueError(f"Crop with ID '{cid}' not found in reference dataset.")

    # Evaluate compatibility scores if user input context was provided
    eval_results: Dict[str, Any] = {}
    if request.user_inputs:
        for cid, crop in loaded_crops.items():
            score, coverage, factor_evals, category = evaluate_crop_compatibility(
                crop_data=crop,
                request=request.user_inputs,
                weights=settings.weights
            )
            eval_results[cid] = {
                "score": score,
                "coverage": coverage,
                "category": category.value,
                "factor_evals": {e.factor_name: e for e in factor_evals}
            }

    # Build comparison rows
    comparison_table: List[ComparisonRow] = []

    # 1. Scientific Name & Category
    comparison_table.append(ComparisonRow(
        factor_name="Scientific Name & Category",
        factor_key="scientific_name",
        values_by_crop={cid: f"{crop['scientific_name']} ({crop['category']})" for cid, crop in loaded_crops.items()},
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Botanical classification and crop family"
    ))

    # 2. Compatibility Score (if user inputs provided)
    if eval_results:
        comparison_table.append(ComparisonRow(
            factor_name="Compatibility Score & Suitability",
            factor_key="compatibility_score",
            values_by_crop={
                cid: f"{eval_results[cid]['score']}/100 ({eval_results[cid]['category']})"
                for cid in crop_ids
            },
            status_by_crop={
                cid: "High" if eval_results[cid]["score"] >= 75 else ("Moderate" if eval_results[cid]["score"] >= 55 else "Low")
                for cid in crop_ids
            },
            notes="Calculated over evaluated factors based on provided inputs"
        ))

        # Data Coverage
        comparison_table.append(ComparisonRow(
            factor_name="Data Coverage",
            factor_key="data_coverage",
            values_by_crop={
                cid: f"{eval_results[cid]['coverage']}%"
                for cid in crop_ids
            },
            status_by_crop={cid: "Coverage" for cid in crop_ids},
            notes="Percentage of parameters evaluated"
        ))

    # 3. Growing Seasons
    comparison_table.append(ComparisonRow(
        factor_name="Growing Seasons",
        factor_key="growing_seasons",
        values_by_crop={cid: ", ".join(crop["growing_seasons"]) for cid, crop in loaded_crops.items()},
        status_by_crop={
            cid: (
                "Matched" if request.user_inputs and request.user_inputs.location.season.value in crop["growing_seasons"]
                else "Neutral"
            )
            for cid, crop in loaded_crops.items()
        },
        notes="Agro-climatic crop calendar suitability"
    ))

    # 4. Compatible Soil Types
    comparison_table.append(ComparisonRow(
        factor_name="Compatible Soil Types",
        factor_key="soil_types",
        values_by_crop={cid: ", ".join(crop["compatible_soil_types"]) for cid, crop in loaded_crops.items()},
        status_by_crop={
            cid: (
                "Matched" if request.user_inputs and request.user_inputs.soil.soil_type.value in crop["compatible_soil_types"]
                else "Neutral"
            )
            for cid, crop in loaded_crops.items()
        },
        notes="Soil textures providing adequate aeration and drainage"
    ))

    # 5. Soil pH Range
    comparison_table.append(ComparisonRow(
        factor_name="Soil pH Requirement",
        factor_key="soil_ph",
        values_by_crop={
            cid: f"Optimal {crop['soil_ph_range'].get('optimal_min', crop['soil_ph_range']['min'])} - {crop['soil_ph_range'].get('optimal_max', crop['soil_ph_range']['max'])} (Tolerable {crop['soil_ph_range']['min']} - {crop['soil_ph_range']['max']})"
            for cid, crop in loaded_crops.items()
        },
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Standard pH scale"
    ))

    # 6. Temperature Range
    comparison_table.append(ComparisonRow(
        factor_name="Temperature Range",
        factor_key="temperature",
        values_by_crop={
            cid: f"Optimal {crop['temperature_range'].get('optimal_min', crop['temperature_range']['min'])}°C - {crop['temperature_range'].get('optimal_max', crop['temperature_range']['max'])}°C (Tolerable {crop['temperature_range']['min']}°C - {crop['temperature_range']['max']}°C)"
            for cid, crop in loaded_crops.items()
        },
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Mean temperature during vegetative and reproductive growth"
    ))

    # 7. Rainfall & Water Requirement
    comparison_table.append(ComparisonRow(
        factor_name="Rainfall & Water Demand",
        factor_key="rainfall",
        values_by_crop={
            cid: f"{crop['rainfall_range']['min']} - {crop['rainfall_range']['max']} mm ({crop.get('water_requirement_level', 'Moderate')} Water Need)"
            for cid, crop in loaded_crops.items()
        },
        status_by_crop={
            cid: "High Water Need" if crop.get("water_requirement_level") in ["High", "Very High"] else "Low-to-Moderate Water Need"
            for cid, crop in loaded_crops.items()
        },
        notes="Moisture requirement during the growth period"
    ))

    # 8. Relative Humidity
    comparison_table.append(ComparisonRow(
        factor_name="Relative Humidity Range",
        factor_key="humidity",
        values_by_crop={
            cid: f"{crop['humidity_range']['min']}% - {crop['humidity_range']['max']}% (Optimal: {crop['humidity_range'].get('optimal_min', crop['humidity_range']['min'])}% - {crop['humidity_range'].get('optimal_max', crop['humidity_range']['max'])}%)"
            for cid, crop in loaded_crops.items()
        },
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Atmospheric humidity preference"
    ))

    # 9. NPK Nutrient Needs
    comparison_table.append(ComparisonRow(
        factor_name="NPK Nutrient Demands (N : P : K)",
        factor_key="npk",
        values_by_crop={
            cid: f"N: {crop['npk_ranges']['nitrogen']['min']}-{crop['npk_ranges']['nitrogen']['max']} | P: {crop['npk_ranges']['phosphorus']['min']}-{crop['npk_ranges']['phosphorus']['max']} | K: {crop['npk_ranges']['potassium']['min']}-{crop['npk_ranges']['potassium']['max']} mg/kg"
            for cid, crop in loaded_crops.items()
        },
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Soil fertility guidelines"
    ))

    # 10. Irrigation & Agronomic Management
    comparison_table.append(ComparisonRow(
        factor_name="Irrigation & Agronomic Management",
        factor_key="irrigation",
        values_by_crop={cid: crop.get("irrigation_considerations", "N/A") for cid, crop in loaded_crops.items()},
        status_by_crop={cid: "Neutral" for cid in crop_ids},
        notes="Field water management practices"
    ))

    # Synthesize concise, objective comparison summary
    crop_summaries = []
    for cid, crop in loaded_crops.items():
        water_req = crop.get("water_requirement_level", "Moderate")
        seasons = "/".join(crop["growing_seasons"])
        crop_summaries.append(f"{crop['name']} ({seasons}, {water_req} water demand)")

    summary_verdict = (
        f"Comparative review of {', '.join(crop_names.values())}: "
        f"Each crop exhibits distinct ecological adaptations. "
        + "; ".join(crop_summaries) + ". "
        "Choice between these crops should depend on irrigation certainty, soil drainage, rotation history, and local market prices rather than a single compatibility metric."
    )

    tradeoffs = [
        "Water security trade-off: Higher yielding crops typically demand higher irrigation security and water table access.",
        "Input costs and fertilization: Legumes (Chickpea, Groundnut, Soybean) fix atmospheric nitrogen, lowering urea requirements, whereas Cereals and Sugarcane require heavy nitrogen supplementation.",
        "Market and pest resilience: Monocultures increase pest risks; intercropping compatible pulses with cereals can enhance systemic stability."
    ]

    return CropComparisonResponse(
        crop_ids=crop_ids,
        crop_names=crop_names,
        comparison_table=comparison_table,
        summary_verdict=summary_verdict,
        tradeoffs_and_limitations=tradeoffs,
        safety_notice=settings.safety_notice
    )
