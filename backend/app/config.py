"""
Configuration settings for Smart Krishi Advisor recommendation engine and API.
All scoring weights and evaluation parameters are documented and configurable.
"""

from typing import Dict
from pydantic import BaseModel, Field


class FactorWeights(BaseModel):
    """
    Weights for each factor contributing to the total compatibility score.
    Total maximum sum = 100.
    When a factor is missing from the user input, its weight is excluded from the denominator,
    ensuring unmeasured parameters never unfairly penalize the crop score.
    """
    season: float = Field(default=20.0, description="Weight for growing season alignment")
    soil_type: float = Field(default=15.0, description="Weight for soil texture and classification compatibility")
    soil_ph: float = Field(default=15.0, description="Weight for soil pH tolerance")
    temperature: float = Field(default=15.0, description="Weight for temperature range suitability")
    rainfall: float = Field(default=15.0, description="Weight for rainfall requirement alignment")
    humidity: float = Field(default=10.0, description="Weight for relative atmospheric humidity")
    nitrogen: float = Field(default=3.33, description="Weight for Nitrogen (N) content")
    phosphorus: float = Field(default=3.33, description="Weight for Phosphorus (P) content")
    potassium: float = Field(default=3.34, description="Weight for Potassium (K) content")

    @property
    def total_possible_weight(self) -> float:
        return (
            self.season
            + self.soil_type
            + self.soil_ph
            + self.temperature
            + self.rainfall
            + self.humidity
            + self.nitrogen
            + self.phosphorus
            + self.potassium
        )


class EngineConfig(BaseModel):
    """Core recommendation engine thresholds and settings."""
    app_name: str = "Smart Krishi Advisor"
    version: str = "1.0.0"
    dataset_version: str = "2024.1-ICAR-TNAU"
    weights: FactorWeights = Field(default_factory=FactorWeights)
    
    # Coverage threshold: Minimum percentage of evaluated weight required for confident recommendation
    min_coverage_threshold_pct: float = Field(
        default=35.0,
        description="Minimum coverage % required to provide ranked recommendations. Below this, insufficient data status is flagged."
    )
    
    # Score thresholds for categorical suitability
    high_compatibility_threshold: float = Field(
        default=75.0,
        description="Score >= 75 is Highly Compatible"
    )
    moderate_compatibility_threshold: float = Field(
        default=55.0,
        description="Score between 55 and 74.9 is Moderately Compatible"
    )
    marginal_compatibility_threshold: float = Field(
        default=40.0,
        description="Score between 40 and 54.9 is Marginally Compatible / Potential Mismatch"
    )

    # Partial score parameters for soft boundaries
    tolerance_buffer_pct: float = Field(
        default=0.15,
        description="Buffer percentage outside optimal min/max where partial score is still awarded rather than sharp cutoff"
    )

    safety_notice: str = (
        "Smart Krishi Advisor provides preliminary crop compatibility guidance for educational "
        "and decision-support purposes. Recommendations depend on input accuracy, reference-data quality, "
        "regional conditions, irrigation, weather, pests, and other factors. Compatibility scores are "
        "not probabilities of crop success or yield predictions. Consult a local agricultural extension "
        "officer or qualified agronomist before making significant farming decisions."
    )


settings = EngineConfig()
