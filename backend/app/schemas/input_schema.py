"""
Input validation schemas for Smart Krishi Advisor.
Uses Pydantic v2 with strict validation and documented bounds.
Never converts missing or null values into zero.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class SeasonEnum(str, Enum):
    KHARIF = "Kharif"
    RABI = "Rabi"
    ZAID = "Zaid"
    OTHER = "Other"


class IrrigationEnum(str, Enum):
    RAINFED = "Rainfed"
    IRRIGATED = "Irrigated"
    UNKNOWN = "Unknown"


class SoilTypeEnum(str, Enum):
    SANDY = "Sandy"
    SANDY_LOAM = "Sandy Loam"
    LOAM = "Loam"
    CLAY_LOAM = "Clay Loam"
    CLAY = "Clay"
    BLACK_SOIL = "Black Soil"
    RED_SOIL = "Red Soil"
    ALLUVIAL_SOIL = "Alluvial Soil"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class RainfallPeriodEnum(str, Enum):
    GROWING_SEASON = "Growing Season"
    ANNUAL = "Annual"


class MeasurementSourceEnum(str, Enum):
    LAB_MEASURED = "Lab Measured / Instrument"
    ESTIMATED = "Farmer Estimate / Historical Observation"
    WEATHER_API = "Live Weather Service"


class LocationContext(BaseModel):
    country: str = Field(default="India", description="Country name")
    state: str = Field(..., min_length=2, max_length=60, description="Indian state or union territory")
    district: Optional[str] = Field(default=None, max_length=80, description="District name (optional)")
    season: SeasonEnum = Field(..., description="Target agricultural season: Kharif, Rabi, Zaid, or Other")
    irrigation: IrrigationEnum = Field(default=IrrigationEnum.UNKNOWN, description="Irrigation availability")


class SoilContext(BaseModel):
    soil_type: SoilTypeEnum = Field(
        default=SoilTypeEnum.UNKNOWN,
        description="Soil texture or classification"
    )
    soil_ph: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=14.0,
        description="Soil pH value on a 0-14 scale. Must be between 0.0 and 14.0."
    )
    nitrogen: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=500.0,
        description="Available Nitrogen (N) in mg/kg or ppm. Sensible agricultural range 0-500."
    )
    phosphorus: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=300.0,
        description="Available Phosphorus (P) in mg/kg or ppm. Sensible agricultural range 0-300."
    )
    potassium: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=600.0,
        description="Available Potassium (K) in mg/kg or ppm. Sensible agricultural range 0-600."
    )
    npk_unit: str = Field(default="mg/kg", description="Unit of measurement for NPK values (mg/kg or ppm)")
    is_measured: bool = Field(
        default=False,
        description="True if values were measured via laboratory soil test, False if farmer estimated."
    )

    @field_validator("soil_ph")
    @classmethod
    def validate_ph(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0.0 or v > 14.0):
            raise ValueError("Soil pH must strictly be between 0.0 and 14.0")
        return v


class EnvironmentalContext(BaseModel):
    temperature: Optional[float] = Field(
        default=None,
        ge=-10.0,
        le=60.0,
        description="Average temperature in °C. Sensible terrestrial range -10°C to 60°C."
    )
    rainfall: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=6000.0,
        description="Rainfall depth in millimeters (mm). Sensible range 0 to 6000 mm."
    )
    rainfall_period: RainfallPeriodEnum = Field(
        default=RainfallPeriodEnum.GROWING_SEASON,
        description="Reference period for the specified rainfall amount."
    )
    relative_humidity: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Atmospheric relative humidity in percentage (0 to 100%)."
    )
    sunlight_hours: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=16.0,
        description="Average daily sunshine duration in hours (0 to 16)."
    )
    is_measured: bool = Field(
        default=False,
        description="True if environmental data is from a weather station/API, False if estimated."
    )

    @field_validator("relative_humidity")
    @classmethod
    def validate_humidity(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and (v < 0.0 or v > 100.0):
            raise ValueError("Relative humidity must strictly be between 0.0% and 100.0%")
        return v


class CropRecommendationRequest(BaseModel):
    """Complete user submission for crop recommendation."""
    location: LocationContext
    soil: SoilContext
    environment: EnvironmentalContext
    notes: Optional[str] = Field(default=None, max_length=500, description="Optional farmer field notes")


class CropComparisonRequest(BaseModel):
    """Request to compare two or more crops under the given input context."""
    crop_ids: list[str] = Field(..., min_length=2, max_length=5, description="List of 2 to 5 crop IDs to compare")
    user_inputs: Optional[CropRecommendationRequest] = Field(
        default=None,
        description="Optional input context to evaluate compatibility and highlights"
    )
