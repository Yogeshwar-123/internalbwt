"""
Data loader module for crop reference data and example profiles.
Decoupled from engine logic to allow independent updates and tests.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any

DATA_DIR = Path(__file__).parent


class CropDataLoader:
    _crops_cache: Optional[List[Dict[str, Any]]] = None
    _profiles_cache: Optional[List[Dict[str, Any]]] = None

    @classmethod
    def load_crops(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load crop reference dataset from JSON file."""
        if cls._crops_cache is None or force_reload:
            crops_file = DATA_DIR / "crops.json"
            if not crops_file.exists():
                raise FileNotFoundError(f"Crop dataset not found at {crops_file}")
            with open(crops_file, "r", encoding="utf-8") as f:
                cls._crops_cache = json.load(f)
        return cls._crops_cache

    @classmethod
    def get_crop_by_id(cls, crop_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single crop by its unique identifier."""
        crops = cls.load_crops()
        for crop in crops:
            if crop.get("id") == crop_id:
                return crop
        return None

    @classmethod
    def load_profiles(cls, force_reload: bool = False) -> List[Dict[str, Any]]:
        """Load documented example profiles."""
        if cls._profiles_cache is None or force_reload:
            profiles_file = DATA_DIR / "example_profiles.json"
            if not profiles_file.exists():
                raise FileNotFoundError(f"Profiles file not found at {profiles_file}")
            with open(profiles_file, "r", encoding="utf-8") as f:
                cls._profiles_cache = json.load(f)
        return cls._profiles_cache

    @classmethod
    def get_profile_by_id(cls, profile_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve example profile by ID."""
        profiles = cls.load_profiles()
        for p in profiles:
            if p.get("id") == profile_id:
                return p
        return None
