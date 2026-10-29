"""
Scoring module for the Explainable Recommendation Engine.
Calculates factor-level compatibility scores, normalized totals, and data coverage indicators.
Guarantees:
- Unavailable factors are excluded from the denominator.
- Missing values are never converted to zero.
- Transparent, documented weights and buffer calculations.
"""

from typing import Dict, Any, Tuple, Optional
from ..config import settings, FactorWeights
from ..schemas.input_schema import (
    CropRecommendationRequest,
    SoilTypeEnum,
    IrrigationEnum,
    SeasonEnum,
    RainfallPeriodEnum,
)
from ..schemas.output_schema import (
    FactorEvaluation,
    FactorStatusEnum,
    SuitabilityCategoryEnum,
)


def evaluate_season(
    user_season: SeasonEnum,
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """Evaluate season alignment."""
    crop_seasons = crop_data.get("growing_seasons", [])
    season_str = user_season.value
    
    if season_str in crop_seasons:
        return FactorEvaluation(
            factor_name="Growing Season",
            user_value=season_str,
            crop_requirement=", ".join(crop_seasons),
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"Requested {season_str} season is an ideal growing period for {crop_data['name']}."
        )
    elif user_season == SeasonEnum.OTHER:
        # Partial match if season is unclassified but possible in controlled conditions
        awarded = round(weight * 0.4, 2)
        return FactorEvaluation(
            factor_name="Growing Season",
            user_value=season_str,
            crop_requirement=", ".join(crop_seasons),
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=f"Custom/Other season selected. Standard seasons are: {', '.join(crop_seasons)}."
        )
    else:
        return FactorEvaluation(
            factor_name="Growing Season",
            user_value=season_str,
            crop_requirement=", ".join(crop_seasons),
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=0.0,
            explanation=f"Seasonal mismatch: {season_str} is outside standard growing seasons ({', '.join(crop_seasons)})."
        )


def evaluate_soil_type(
    user_soil: SoilTypeEnum,
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """Evaluate soil texture compatibility."""
    crop_soils = crop_data.get("compatible_soil_types", [])
    user_val = user_soil.value

    if user_soil == SoilTypeEnum.UNKNOWN or not user_val:
        return FactorEvaluation(
            factor_name="Soil Type",
            user_value="Unknown / Not Specified",
            crop_requirement=", ".join(crop_soils),
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation="Soil type was not provided. Excluded from scoring denominator."
        )

    if user_val in crop_soils:
        return FactorEvaluation(
            factor_name="Soil Type",
            user_value=user_val,
            crop_requirement=", ".join(crop_soils),
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"{user_val} is well-suited for root aeration and water retention for {crop_data['name']}."
        )
    else:
        # Partial compatibility for 'Other' or intermediate textures
        awarded = round(weight * 0.25, 2)
        return FactorEvaluation(
            factor_name="Soil Type",
            user_value=user_val,
            crop_requirement=", ".join(crop_soils),
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=f"{user_val} is not commonly recommended. {crop_data['name']} prefers: {', '.join(crop_soils)}."
        )


def evaluate_soil_ph(
    user_ph: Optional[float],
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """Evaluate soil pH compatibility."""
    ph_data = crop_data.get("soil_ph_range", {})
    min_ph = ph_data.get("min", 5.5)
    max_ph = ph_data.get("max", 8.5)
    opt_min = ph_data.get("optimal_min", min_ph)
    opt_max = ph_data.get("optimal_max", max_ph)
    req_str = f"Optimal: {opt_min} - {opt_max} (Tolerable: {min_ph} - {max_ph})"

    if user_ph is None:
        return FactorEvaluation(
            factor_name="Soil pH",
            user_value=None,
            crop_requirement=req_str,
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation="Soil pH value was not provided. Excluded from scoring denominator."
        )

    if opt_min <= user_ph <= opt_max:
        return FactorEvaluation(
            factor_name="Soil pH",
            user_value=user_ph,
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"pH {user_ph} falls squarely in the optimal nutrient availability range ({opt_min} - {opt_max})."
        )
    elif min_ph <= user_ph <= max_ph:
        # Tolerable range: awards 70% of points
        awarded = round(weight * 0.70, 2)
        return FactorEvaluation(
            factor_name="Soil pH",
            user_value=user_ph,
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=awarded,
            explanation=f"pH {user_ph} is within tolerable limits ({min_ph} - {max_ph}), though slightly outside optimal ({opt_min} - {opt_max})."
        )
    else:
        diff = min_ph - user_ph if user_ph < min_ph else user_ph - max_ph
        if diff <= 0.5:
            # Borderline: small partial credit
            awarded = round(weight * 0.30, 2)
            msg = f"pH {user_ph} is borderline ({'acidic' if user_ph < min_ph else 'alkaline'} stress). Soil amendment like {'lime' if user_ph < min_ph else 'gypsum'} may be needed."
        else:
            awarded = 0.0
            msg = f"Significant pH mismatch ({user_ph}). Crop requires {min_ph} - {max_ph}. Severe nutrient lockout likely."
            
        return FactorEvaluation(
            factor_name="Soil pH",
            user_value=user_ph,
            crop_requirement=req_str,
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=msg
        )


def evaluate_temperature(
    user_temp: Optional[float],
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """Evaluate temperature compatibility."""
    t_data = crop_data.get("temperature_range", {})
    min_t = t_data.get("min", 15.0)
    max_t = t_data.get("max", 35.0)
    opt_min = t_data.get("optimal_min", min_t)
    opt_max = t_data.get("optimal_max", max_t)
    req_str = f"Optimal: {opt_min}°C - {opt_max}°C (Tolerable: {min_t}°C - {max_t}°C)"

    if user_temp is None:
        return FactorEvaluation(
            factor_name="Temperature",
            user_value=None,
            crop_requirement=req_str,
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation="Temperature was not specified. Excluded from scoring denominator."
        )

    if opt_min <= user_temp <= opt_max:
        return FactorEvaluation(
            factor_name="Temperature",
            user_value=f"{user_temp}°C",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"Temperature {user_temp}°C is within optimal physiological growth zone ({opt_min}°C - {opt_max}°C)."
        )
    elif min_t <= user_temp <= max_t:
        awarded = round(weight * 0.70, 2)
        return FactorEvaluation(
            factor_name="Temperature",
            user_value=f"{user_temp}°C",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=awarded,
            explanation=f"{user_temp}°C is tolerable ({min_t}°C - {max_t}°C), though development may deviate slightly from peak rate."
        )
    else:
        diff = min_t - user_temp if user_temp < min_t else user_temp - max_t
        if diff <= 3.0:
            awarded = round(weight * 0.25, 2)
            issue = "chilling/cold" if user_temp < min_t else "heat"
            msg = f"{user_temp}°C is near threshold with moderate {issue} stress potential."
        else:
            awarded = 0.0
            issue = "extreme cold" if user_temp < min_t else "severe thermal"
            msg = f"{user_temp}°C causes {issue} stress. Range for {crop_data['name']} is {min_t}°C - {max_t}°C."

        return FactorEvaluation(
            factor_name="Temperature",
            user_value=f"{user_temp}°C",
            crop_requirement=req_str,
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=msg
        )


def evaluate_rainfall(
    user_rain: Optional[float],
    rainfall_period: RainfallPeriodEnum,
    user_irrigation: IrrigationEnum,
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """
    Evaluate rainfall requirement.
    Considers rainfall period and irrigation availability:
    If rainfall is below crop requirement, irrigation can bridge the gap.
    """
    r_data = crop_data.get("rainfall_range", {})
    min_r = r_data.get("min", 400.0)
    max_r = r_data.get("max", 1200.0)
    opt_min = r_data.get("optimal_min", min_r)
    opt_max = r_data.get("optimal_max", max_r)
    ref_period = r_data.get("reference_period", "Growing Season")
    req_str = f"Optimal: {opt_min} - {opt_max} mm ({ref_period})"

    if user_rain is None:
        return FactorEvaluation(
            factor_name="Rainfall",
            user_value=None,
            crop_requirement=req_str,
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation="Rainfall was not specified. Excluded from scoring denominator."
        )

    # If user provided Annual rainfall but crop expects Growing Season (or vice-versa),
    # apply a conservative scaling factor for comparability
    adjusted_user_rain = user_rain
    period_note = ""
    if rainfall_period == RainfallPeriodEnum.ANNUAL and ref_period == "Growing Season":
        adjusted_user_rain = user_rain * 0.65  # approx 65% annual rain occurs during growing season in India
        period_note = " (approx. converted to growing season equivalent)"
    elif rainfall_period == RainfallPeriodEnum.GROWING_SEASON and ref_period == "Annual":
        adjusted_user_rain = user_rain / 0.65
        period_note = " (scaled to annual equivalent)"

    if opt_min <= adjusted_user_rain <= opt_max:
        return FactorEvaluation(
            factor_name="Rainfall",
            user_value=f"{user_rain} mm ({rainfall_period.value}){period_note}",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"Rainfall of {user_rain} mm satisfies optimal moisture demand ({opt_min} - {opt_max} mm)."
        )
    elif min_r <= adjusted_user_rain <= max_r:
        awarded = round(weight * 0.75, 2)
        return FactorEvaluation(
            factor_name="Rainfall",
            user_value=f"{user_rain} mm ({rainfall_period.value}){period_note}",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=awarded,
            explanation=f"Rainfall ({user_rain} mm) meets tolerable range ({min_r} - {max_r} mm)."
        )
    elif adjusted_user_rain < min_r:
        # Rainfall deficit
        if user_irrigation == IrrigationEnum.IRRIGATED:
            # Irrigation bridges deficit
            awarded = round(weight * 0.85, 2)
            return FactorEvaluation(
                factor_name="Rainfall & Irrigation",
                user_value=f"{user_rain} mm (Irrigated field)",
                crop_requirement=req_str,
                status=FactorStatusEnum.MATCHED,
                weight=weight,
                score_awarded=awarded,
                explanation=f"Natural rainfall ({user_rain} mm) is below optimal, but active irrigation effectively compensates for water demand."
            )
        else:
            awarded = round(weight * 0.20, 2)
            return FactorEvaluation(
                factor_name="Rainfall",
                user_value=f"{user_rain} mm ({user_irrigation.value})",
                crop_requirement=req_str,
                status=FactorStatusEnum.POTENTIAL_MISMATCH,
                weight=weight,
                score_awarded=awarded,
                explanation=f"Moisture deficit: {user_rain} mm is below required {min_r} mm for rainfed cultivation."
            )
    else:
        # Excessive rainfall
        awarded = round(weight * 0.25, 2)
        return FactorEvaluation(
            factor_name="Rainfall",
            user_value=f"{user_rain} mm",
            crop_requirement=req_str,
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=f"High rainfall ({user_rain} mm exceeds {max_r} mm). Risk of waterlogging, fungal diseases, or root asphyxiation."
        )


def evaluate_humidity(
    user_hum: Optional[float],
    crop_data: Dict[str, Any],
    weight: float,
) -> FactorEvaluation:
    """Evaluate atmospheric relative humidity."""
    h_data = crop_data.get("humidity_range", {})
    min_h = h_data.get("min", 30.0)
    max_h = h_data.get("max", 85.0)
    opt_min = h_data.get("optimal_min", min_h)
    opt_max = h_data.get("optimal_max", max_h)
    req_str = f"Optimal: {opt_min}% - {opt_max}% (Tolerable: {min_h}% - {max_h}%)"

    if user_hum is None:
        return FactorEvaluation(
            factor_name="Relative Humidity",
            user_value=None,
            crop_requirement=req_str,
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation="Relative humidity was not specified. Excluded from scoring denominator."
        )

    if opt_min <= user_hum <= opt_max:
        return FactorEvaluation(
            factor_name="Relative Humidity",
            user_value=f"{user_hum}%",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"Humidity {user_hum}% supports healthy transpiration without excessive disease pressure."
        )
    elif min_h <= user_hum <= max_h:
        awarded = round(weight * 0.70, 2)
        return FactorEvaluation(
            factor_name="Relative Humidity",
            user_value=f"{user_hum}%",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=awarded,
            explanation=f"Humidity {user_hum}% is tolerable ({min_h}% - {max_h}%)."
        )
    else:
        awarded = round(weight * 0.20, 2)
        condition = "very dry air / excessive vapor pressure deficit" if user_hum < min_h else "excessive dampness favoring foliar pathogens"
        return FactorEvaluation(
            factor_name="Relative Humidity",
            user_value=f"{user_hum}%",
            crop_requirement=req_str,
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=f"Humidity {user_hum}% is outside optimal range ({opt_min}% - {opt_max}%), causing {condition}."
        )


def evaluate_nutrient(
    nutrient_name: str,
    user_val: Optional[float],
    crop_data: Dict[str, Any],
    weight: float,
    unit: str = "mg/kg",
) -> FactorEvaluation:
    """Evaluate individual soil macronutrient (N, P, or K)."""
    key = nutrient_name.lower()
    symbol = "N" if nutrient_name == "Nitrogen" else ("P" if nutrient_name == "Phosphorus" else "K")
    factor_label = f"{nutrient_name} ({symbol})"
    ranges = crop_data.get("npk_ranges", {}).get(key, {})
    min_val = ranges.get("min", 20.0)
    max_val = ranges.get("max", 100.0)
    req_str = f"{min_val} - {max_val} {unit}"

    if user_val is None:
        return FactorEvaluation(
            factor_name=factor_label,
            user_value=None,
            crop_requirement=req_str,
            status=FactorStatusEnum.UN_EVALUATED,
            weight=weight,
            score_awarded=0.0,
            explanation=f"{nutrient_name} was not tested/provided. Excluded from scoring denominator."
        )

    if min_val <= user_val <= max_val:
        return FactorEvaluation(
            factor_name=factor_label,
            user_value=f"{user_val} {unit}",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=weight,
            explanation=f"{nutrient_name} level ({user_val} {unit}) satisfies expected soil fertility benchmarks."
        )
    elif user_val > max_val:
        # High nutrient level is generally acceptable (except extreme toxicity), slight partial discount
        awarded = round(weight * 0.85, 2)
        return FactorEvaluation(
            factor_name=factor_label,
            user_value=f"{user_val} {unit}",
            crop_requirement=req_str,
            status=FactorStatusEnum.MATCHED,
            weight=weight,
            score_awarded=awarded,
            explanation=f"High {nutrient_name} level ({user_val} {unit}). Ample nutrient reserve present."
        )
    else:
        # Nutrient deficit
        ratio = user_val / min_val if min_val > 0 else 0
        awarded = round(weight * max(0.2, min(0.7, ratio)), 2)
        return FactorEvaluation(
            factor_name=factor_label,
            user_value=f"{user_val} {unit}",
            crop_requirement=req_str,
            status=FactorStatusEnum.POTENTIAL_MISMATCH,
            weight=weight,
            score_awarded=awarded,
            explanation=f"Soil {nutrient_name} deficit ({user_val} {unit} vs min requirement {min_val} {unit}). Supplemental fertilizer will be necessary."
        )


def evaluate_crop_compatibility(
    crop_data: Dict[str, Any],
    request: CropRecommendationRequest,
    weights: FactorWeights,
) -> Tuple[float, float, list[FactorEvaluation], SuitabilityCategoryEnum]:
    """
    Evaluate crop against user input.
    Returns:
    (normalized_score, data_coverage_pct, factor_evaluations, suitability_category)
    """
    evaluations: list[FactorEvaluation] = []

    # 1. Season (20%)
    evaluations.append(evaluate_season(request.location.season, crop_data, weights.season))

    # 2. Soil Type (15%)
    evaluations.append(evaluate_soil_type(request.soil.soil_type, crop_data, weights.soil_type))

    # 3. Soil pH (15%)
    evaluations.append(evaluate_soil_ph(request.soil.soil_ph, crop_data, weights.soil_ph))

    # 4. Temperature (15%)
    evaluations.append(evaluate_temperature(request.environment.temperature, crop_data, weights.temperature))

    # 5. Rainfall & Irrigation (15%)
    evaluations.append(evaluate_rainfall(
        request.environment.rainfall,
        request.environment.rainfall_period,
        request.location.irrigation,
        crop_data,
        weights.rainfall
    ))

    # 6. Humidity (10%)
    evaluations.append(evaluate_humidity(request.environment.relative_humidity, crop_data, weights.humidity))

    # 7. Nitrogen (3.33%)
    evaluations.append(evaluate_nutrient(
        "Nitrogen",
        request.soil.nitrogen,
        crop_data,
        weights.nitrogen,
        request.soil.npk_unit
    ))

    # 8. Phosphorus (3.33%)
    evaluations.append(evaluate_nutrient(
        "Phosphorus",
        request.soil.phosphorus,
        crop_data,
        weights.phosphorus,
        request.soil.npk_unit
    ))

    # 9. Potassium (3.34%)
    evaluations.append(evaluate_nutrient(
        "Potassium",
        request.soil.potassium,
        crop_data,
        weights.potassium,
        request.soil.npk_unit
    ))

    # Calculate evaluated weights and awarded score
    evaluated_weight = 0.0
    awarded_points = 0.0

    for ev in evaluations:
        if ev.status != FactorStatusEnum.UN_EVALUATED:
            evaluated_weight += ev.weight
            awarded_points += ev.score_awarded

    total_possible = weights.total_possible_weight
    data_coverage_pct = round((evaluated_weight / total_possible) * 100.0, 1)

    if evaluated_weight > 0:
        normalized_score = round((awarded_points / evaluated_weight) * 100.0, 1)
    else:
        normalized_score = 0.0

    # Categorize suitability
    if data_coverage_pct < settings.min_coverage_threshold_pct:
        category = SuitabilityCategoryEnum.INSUFFICIENT_DATA
    elif normalized_score >= settings.high_compatibility_threshold:
        category = SuitabilityCategoryEnum.HIGHLY_COMPATIBLE
    elif normalized_score >= settings.moderate_compatibility_threshold:
        category = SuitabilityCategoryEnum.MODERATELY_COMPATIBLE
    else:
        category = SuitabilityCategoryEnum.MARGINAL_MISMATCH

    return normalized_score, data_coverage_pct, evaluations, category
