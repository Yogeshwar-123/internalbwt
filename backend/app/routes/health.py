"""Health check endpoint."""

from fastapi import APIRouter
from ..config import settings
from ..data.loader import CropDataLoader
from ..schemas.output_schema import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    crops = CropDataLoader.load_crops()
    return HealthResponse(
        status="HEALTHY",
        app_name=settings.app_name,
        version=settings.version,
        dataset_version=settings.dataset_version,
        total_crops_loaded=len(crops)
    )
