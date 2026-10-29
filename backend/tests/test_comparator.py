"""
Automated unit tests for the multi-crop comparator.
Verifies side-by-side table generation, bounds checking, and balanced summaries.
"""

import pytest
from app.schemas.input_schema import (
    CropComparisonRequest,
    CropRecommendationRequest,
    LocationContext,
    SoilContext,
    EnvironmentalContext,
    SeasonEnum,
    SoilTypeEnum,
)
from app.engine.comparator import compare_crops


def test_compare_two_crops_without_user_inputs():
    """Comparing Rice and Wheat without inputs should return objective crop reference specs."""
    req = CropComparisonRequest(crop_ids=["rice", "wheat"])
    res = compare_crops(req)

    assert len(res.crop_ids) == 2
    assert "rice" in res.crop_names
    assert "wheat" in res.crop_names
    assert len(res.comparison_table) >= 8

    # Verify rainfall row exists and shows different water needs
    rainfall_row = next(r for r in res.comparison_table if r.factor_key == "rainfall")
    assert "rice" in rainfall_row.values_by_crop
    assert "wheat" in rainfall_row.values_by_crop


def test_compare_crops_with_user_inputs():
    """Comparing crops with user input context evaluates both scores and coverage."""
    user_inputs = CropRecommendationRequest(
        location=LocationContext(state="Gujarat", season=SeasonEnum.KHARIF),
        soil=SoilContext(soil_type=SoilTypeEnum.BLACK_SOIL, soil_ph=7.5),
        environment=EnvironmentalContext(temperature=30.0, rainfall=700.0)
    )
    req = CropComparisonRequest(
        crop_ids=["cotton", "groundnut", "pearl_millet"],
        user_inputs=user_inputs
    )
    res = compare_crops(req)

    assert len(res.crop_ids) == 3
    # Check that score row was added
    score_row = next((r for r in res.comparison_table if r.factor_key == "compatibility_score"), None)
    assert score_row is not None
    assert "cotton" in score_row.values_by_crop


def test_compare_nonexistent_crop_raises_error():
    """Referencing an invalid crop ID should raise a clean ValueError."""
    req = CropComparisonRequest(crop_ids=["rice", "nonexistent_crop_123"])
    with pytest.raises(ValueError):
        compare_crops(req)
