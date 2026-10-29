"""Crop comparison endpoint."""

from fastapi import APIRouter, HTTPException, status
from ..schemas.input_schema import CropComparisonRequest
from ..schemas.output_schema import CropComparisonResponse
from ..engine.comparator import compare_crops

router = APIRouter(tags=["Comparison"])


@router.post(
    "/compare",
    response_model=CropComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare two or more crops side-by-side"
)
def create_comparison(request: CropComparisonRequest) -> CropComparisonResponse:
    """
    Compares 2 to 5 crops across agronomic parameters, soil requirements, and scores.
    """
    if len(request.crop_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Must provide at least 2 crops to compare."
        )
    if len(request.crop_ids) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot compare more than 5 crops at once."
        )

    try:
        response = compare_crops(request)
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while comparing crops: {str(e)}"
        )
