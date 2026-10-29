"""
Automated unit tests for input schemas and validation constraints.
Verifies pH bounds, humidity bounds, missing value allowances, and error handling.
"""

import pytest
from pydantic import ValidationError
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


def test_valid_form_submission():
    """Test full valid input model creation."""
    req = CropRecommendationRequest(
        location=LocationContext(
            state="Punjab",
            season=SeasonEnum.RABI,
            irrigation=IrrigationEnum.IRRIGATED
        ),
        soil=SoilContext(
            soil_type=SoilTypeEnum.ALLUVIAL_SOIL,
            soil_ph=7.2,
            nitrogen=120.0,
            phosphorus=50.0,
            potassium=55.0,
            is_measured=True
        ),
        environment=EnvironmentalContext(
            temperature=18.0,
            rainfall=400.0,
            rainfall_period=RainfallPeriodEnum.GROWING_SEASON,
            relative_humidity=60.0,
            is_measured=True
        )
    )
    assert req.location.state == "Punjab"
    assert req.soil.soil_ph == 7.2
    assert req.soil.nitrogen == 120.0
    assert req.environment.temperature == 18.0


def test_missing_optional_npk_not_coerced_to_zero():
    """Ensure missing NPK values remain None and are never silently converted to 0."""
    soil = SoilContext(
        soil_type=SoilTypeEnum.BLACK_SOIL,
        soil_ph=7.5,
        nitrogen=None,
        phosphorus=None,
        potassium=None,
        is_measured=False
    )
    assert soil.nitrogen is None
    assert soil.phosphorus is None
    assert soil.potassium is None
    assert soil.nitrogen != 0.0


def test_invalid_ph_raises_validation_error():
    """pH outside [0, 14] must fail validation."""
    with pytest.raises(ValidationError):
        SoilContext(soil_ph=-0.5)

    with pytest.raises(ValidationError):
        SoilContext(soil_ph=14.5)


def test_boundary_ph_values():
    """Boundary pH values (0.0 and 14.0) should be accepted."""
    soil_min = SoilContext(soil_ph=0.0)
    soil_max = SoilContext(soil_ph=14.0)
    assert soil_min.soil_ph == 0.0
    assert soil_max.soil_ph == 14.0


def test_invalid_humidity_raises_validation_error():
    """Humidity outside [0, 100] must fail validation."""
    with pytest.raises(ValidationError):
        EnvironmentalContext(relative_humidity=-1.0)

    with pytest.raises(ValidationError):
        EnvironmentalContext(relative_humidity=105.0)


def test_boundary_humidity_values():
    """Humidity boundary values (0.0 and 100.0) should be accepted."""
    env_min = EnvironmentalContext(relative_humidity=0.0)
    env_max = EnvironmentalContext(relative_humidity=100.0)
    assert env_min.relative_humidity == 0.0
    assert env_max.relative_humidity == 100.0


def test_unknown_soil_type_accepted():
    """Soil type Unknown must be valid and distinct from known types."""
    soil = SoilContext(soil_type=SoilTypeEnum.UNKNOWN)
    assert soil.soil_type == SoilTypeEnum.UNKNOWN


def test_invalid_temperature_bounds():
    """Extreme out-of-range temperatures should be rejected by bounds."""
    with pytest.raises(ValidationError):
        EnvironmentalContext(temperature=-25.0)  # below -10°C sensible limit

    with pytest.raises(ValidationError):
        EnvironmentalContext(temperature=75.0)   # above 60°C sensible limit
