"""Crop catalog and information endpoints."""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from ..data.loader import CropDataLoader

router = APIRouter(prefix="/crops", tags=["Crops"])


@router.get("", response_model=List[Dict[str, Any]])
def list_crops(
    season: Optional[str] = Query(None, description="Filter by growing season"),
    category: Optional[str] = Query(None, description="Filter by crop category (Cereal, Pulse, etc.)")
) -> List[Dict[str, Any]]:
    """Retrieve full catalog of crops with optional season or category filter."""
    crops = CropDataLoader.load_crops()
    filtered = crops

    if season:
        season_clean = season.strip().capitalize()
        filtered = [c for c in filtered if season_clean in c.get("growing_seasons", [])]

    if category:
        cat_clean = category.strip().lower()
        filtered = [c for c in filtered if c.get("category", "").lower() == cat_clean]

    return filtered


@router.get("/{crop_id}", response_model=Dict[str, Any])
def get_crop(crop_id: str) -> Dict[str, Any]:
    """Retrieve details for a single crop by ID."""
    crop = CropDataLoader.get_crop_by_id(crop_id)
    if not crop:
        raise HTTPException(status_code=404, detail=f"Crop with ID '{crop_id}' not found.")
    return crop
