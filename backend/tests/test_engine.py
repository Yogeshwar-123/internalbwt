"""
Automated unit tests for the recommendation engine.
Verifies score normalization, denominator adjustment, coverage indicator,
insufficient data handling, and explanation generation.
"""

import pytest
from app.config import settings
from app.data.loader import CropDataLoader
from app.schemas.input_schema import (
    CropRecommendationRequest,
    LocationContext,
    SoilContext,
    EnvironmentalContext,
    SeasonEnum,
    SoilTypeEnum,
    RainfallPeriodEnum,
    IrrigationEnum,
)
from app.engine.scoring import evaluate_crop_compatibility
from app.engine.recommender import run_crop_recommendation
from app.schemas.output_schema import FactorStatusEnum, SuitabilityCategoryEnum


@pytest.fixture
def sample_rice_crop():
    crop = CropDataLoader.get_crop_by_id("rice")
    assert crop is not None
    return crop


@pytest.fixture
def sample_wheat_crop():
    crop = CropDataLoader.get_crop_by_id("wheat")
    assert crop is not None
    return crop


def test_score_normalization_all_factors_present(sample_rice_crop):
    """When all factors are present and optimal, score should approach 100% and coverage 100%."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Andhra Pradesh",
            season=SeasonEnum.KHARIF,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.CLAY_LOAM,
            soil_ph=6.5,
            nitrogen=100.0,
            phosphorus=45.0,
            potassium=55.0,
            is_measured=True
        ),
        environment=EnvironmentalContext(
            temperature=28.0,
            rainfall=1500.0,
            rainfall_period=RainfallPeriodEnum.GROWING_SEASON,
            relative_humidity=80.0,
            is_measured=True
        )
    )
    score, coverage, evals, category = evaluate_crop_compatibility(
        sample_rice_crop, req, settings.weights
    )
    assert coverage == 100.0
    assert score >= 90.0
    assert category == SuitabilityCategoryEnum.HIGHLY_COMPATIBLE


def test_missing_npk_excluded_from_denominator(sample_rice_crop):
    """
    When NPK is null, NPK weights must be excluded from the denominator.
    Coverage should drop to 90%, but the score on the remaining factors should remain un-penalized.
    """
    req = CropRecommendationRequest(
        location=LocationContext(
            state="West Bengal",
            season=SeasonEnum.KHARIF,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.CLAY_LOAM,
            soil_ph=6.5,
            nitrogen=None,
            phosphorus=None,
            potassium=None,
            is_measured=False
        ),
        environment=EnvironmentalContext(
            temperature=28.0,
            rainfall=1500.0,
            rainfall_period=RainfallPeriodEnum.GROWING_SEASON,
            relative_humidity=80.0,
            is_measured=True
        )
    )
    score, coverage, evals, category = evaluate_crop_compatibility(
        sample_rice_crop, req, settings.weights
    )

    # N (3.33) + P (3.33) + K (3.34) = 10.0 weight
    # Remaining weight = 90.0
    assert coverage == 90.0
    assert score >= 90.0  # Perfect match on evaluated factors, NOT dragged down by missing NPK!
    
    # Check that NPK evaluations are marked UN_EVALUATED
    npk_evals = [e for e in evals if "Nitrogen" in e.factor_name or "Phosphorus" in e.factor_name or "Potassium" in e.factor_name]
    for e in npk_evals:
        assert e.status == FactorStatusEnum.UN_EVALUATED
        assert e.score_awarded == 0.0


def test_unsupported_season_causes_mismatch(sample_wheat_crop):
    """Wheat is a Rabi crop. Evaluating it in Kharif should trigger season mismatch."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Punjab",
            season=SeasonEnum.KHARIF,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.LOAM,
            soil_ph=7.0
        ),
        environment=EnvironmentalContext(
            temperature=32.0,
            rainfall=600.0
        )
    )
    score, coverage, evals, category = evaluate_crop_compatibility(
        sample_wheat_crop, req, settings.weights
    )
    season_eval = next(e for e in evals if e.factor_name == "Growing Season")
    assert season_eval.status == FactorStatusEnum.POTENTIAL_MISMATCH
    assert season_eval.score_awarded == 0.0


def test_ranking_consistency_across_crops():
    """Rice profile should rank Rice at the top, not Pearl Millet or Chickpea."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Odisha",
            season=SeasonEnum.KHARIF,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.CLAY,
            soil_ph=6.5
        ),
        environment=EnvironmentalContext(
            temperature=30.0,
            rainfall=1600.0,
            relative_humidity=85.0
        )
    )
    resp = run_crop_recommendation(req)
    assert resp.status == "SUCCESS"
    assert len(resp.recommendations) > 0
    top_crop = resp.recommendations[0]
    assert top_crop.crop_id == "rice"

    # Pearl millet should be ranked lower due to heavy rainfall
    millet = next(c for c in resp.recommendations if c.crop_id == "pearl_millet")
    assert top_crop.compatibility_score > millet.compatibility_score


def test_insufficient_data_trigger():
    """When only location is provided and all environmental and soil parameters are missing."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Karnataka",
            season=SeasonEnum.ZAID,
            irrigation=IrrigationEnum.UNKNOWN
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.UNKNOWN,
            soil_ph=None
        ),
        environment=EnvironmentalContext(
            temperature=None,
            rainfall=None,
            relative_humidity=None
        )
    )
    resp = run_crop_recommendation(req)
    assert resp.status == "INSUFFICIENT_DATA"
    assert resp.is_sufficient_data is False
    assert len(resp.insufficient_data_reasons) > 0
    assert len(resp.suggested_next_steps) > 0


def test_explanation_contains_specific_factor_details():
    """Explanation must cite specific measured values and crop requirements."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Haryana",
            season=SeasonEnum.RABI,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.LOAM,
            soil_ph=7.2
        ),
        environment=EnvironmentalContext(
            temperature=18.0,
            rainfall=400.0
        )
    )
    resp = run_crop_recommendation(req)
    wheat_rec = next(c for c in resp.recommendations if c.crop_id == "wheat")
    assert "18.0°C" in wheat_rec.why_this_crop or "temperature" in wheat_rec.why_this_crop.lower()
    assert "Rabi" in wheat_rec.why_this_crop
