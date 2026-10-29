"""Example profiles API endpoints."""

from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from ..data.loader import CropDataLoader

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("", response_model=List[Dict[str, Any]])
def list_profiles() -> List[Dict[str, Any]]:
    """Retrieve all documented example profiles."""
    return CropDataLoader.load_profiles()


@router.get("/{profile_id}", response_model=Dict[str, Any])
def get_profile(profile_id: str) -> Dict[str, Any]:
    """Retrieve a single example profile by ID."""
    profile = CropDataLoader.get_profile_by_id(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{profile_id}' not found.")
    return profile
