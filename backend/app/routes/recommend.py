"""Recommendation endpoint."""

from fastapi import APIRouter, HTTPException, status
from ..schemas.input_schema import CropRecommendationRequest
from ..schemas.output_schema import RecommendationResponse
from ..engine.recommender import run_crop_recommendation

router = APIRouter(tags=["Recommendations"])


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    status_code=status.HTTP_200_OK,
    summary="Compute crop suitability recommendations"
)
def create_recommendation(request: CropRecommendationRequest) -> RecommendationResponse:
    """
    Submits user agricultural context and receives explainable crop recommendations.
    Never coerces missing values into zero. Excludes unavailable factors from denominator.
    """
    try:
        response = run_crop_recommendation(request)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while computing recommendations: {str(e)}"
        )
