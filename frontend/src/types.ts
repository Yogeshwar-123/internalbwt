export interface CropItem {
  id: string;
  name: string;
  scientific_name: string;
  category: string;
  compatible_soil_types: string[];
  soil_ph_range: {
    min: number;
    max: number;
    optimal_min: number;
    optimal_max: number;
  };
  temperature_range: {
    min: number;
    max: number;
    optimal_min: number;
    optimal_max: number;
    unit: string;
  };
  rainfall_range: {
    min: number;
    max: number;
    optimal_min: number;
    optimal_max: number;
    unit: string;
    reference_period?: string;
  };
  humidity_range: {
    min: number;
    max: number;
    optimal_min: number;
    optimal_max: number;
    unit: string;
  };
  npk_ranges: {
    nitrogen: { min: number; max: number; unit: string };
    phosphorus: { min: number; max: number; unit: string };
    potassium: { min: number; max: number; unit: string };
  };
  growing_seasons: string[];
  irrigation_considerations: string;
  water_requirement_level: string;
  regional_applicability: string[];
  description: string;
}

export interface RecommendationCard {
  crop_id: string;
  crop_name: string;
  scientific_name: string;
  category: string;
  suitability_category: string;
  compatibility_score: number;
  data_coverage_pct: number;
  matched_factors: string[];
  mismatched_factors: string[];
  unevaluated_factors: string[];
  why_this_crop: string;
  irrigation_advice: string;
}

export interface ExampleProfile {
  id: string;
  name: string;
  description: string;
  input_data: {
    location: {
      country: string;
      state: string;
      district: string | null;
      season: string;
      irrigation: string;
    };
    soil: {
      soil_type: string;
      soil_ph: number | null;
      nitrogen: number | null;
      phosphorus: number | null;
      potassium: number | null;
      is_measured: boolean;
    };
    environment: {
      temperature: number;
      rainfall: number | null;
      relative_humidity: number | null;
      sunlight_hours: number | null;
      is_measured: boolean;
    };
  };
}
