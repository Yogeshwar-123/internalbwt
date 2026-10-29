"""
Output response schemas for Smart Krishi Advisor.
Includes explainability structures, factor-by-factor evaluations, and safety notices.
"""

from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class FactorStatusEnum(str, Enum):
    MATCHED = "Matched"
    POTENTIAL_MISMATCH = "Potential Mismatch"
    UN_EVALUATED = "Un-evaluated (Missing Data)"


class SuitabilityCategoryEnum(str, Enum):
    HIGHLY_COMPATIBLE = "Highly Compatible"
    MODERATELY_COMPATIBLE = "Moderately Compatible"
    MARGINAL_MISMATCH = "Marginally Compatible / Potential Mismatch"
    INSUFFICIENT_DATA = "Insufficient Data to Evaluate"


class FactorEvaluation(BaseModel):
    """Detailed evaluation of an individual agronomic factor."""
    factor_name: str
    user_value: Optional[Any] = None
    crop_requirement: str
    status: FactorStatusEnum
    weight: float
    score_awarded: float
    explanation: str


class CropRecommendationCard(BaseModel):
    """Detailed recommendation entry for a specific crop."""
    crop_id: str
    crop_name: str
    scientific_name: str
    category: str
    suitability_category: SuitabilityCategoryEnum
    compatibility_score: Optional[float] = Field(
        default=None,
        description="Prototype compatibility index (0-100) calculated solely over evaluated factors. Not a yield or probability prediction."
    )
    data_coverage_pct: float = Field(
        ...,
        description="Percentage of factor weight that could be evaluated based on provided inputs."
    )
    matched_factors: List[str]
    mismatched_factors: List[str]
    unevaluated_factors: List[str]
    factor_evaluations: List[FactorEvaluation]
    why_this_crop: str = Field(
        ...,
        description="Detailed, input-grounded explanation generated from actual factor evaluations."
    )
    key_risks_or_mismatches: List[str]
    irrigation_advice: str
    data_source: str
    reference_date: str
    is_verified_agronomic: bool


class RecommendationResponse(BaseModel):
    """Overall recommendation response payload."""
    request_id: str
    generation_date: str
    status: str
    is_sufficient_data: bool
    overall_coverage_pct: float
    user_inputs_summary: Dict[str, Any]
    insufficient_data_reasons: List[str] = Field(default_factory=list)
    suggested_next_steps: List[str] = Field(default_factory=list)
    recommendations: List[CropRecommendationCard] = Field(default_factory=list)
    dataset_version: str
    assumptions_and_limitations: List[str]
    safety_notice: str


class ComparisonRow(BaseModel):
    factor_name: str
    factor_key: str
    values_by_crop: Dict[str, Any]
    status_by_crop: Dict[str, str]
    notes: Optional[str] = None


class CropComparisonResponse(BaseModel):
    crop_ids: List[str]
    crop_names: Dict[str, str]
    comparison_table: List[ComparisonRow]
    summary_verdict: str
    tradeoffs_and_limitations: List[str]
    safety_notice: str


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    dataset_version: str
    total_crops_loaded: int
