import type { CropItem, ExampleProfile } from './types';

export const CROPS_CATALOG: CropItem[] = [
  {
    id: "rice",
    name: "Rice",
    scientific_name: "Oryza sativa",
    category: "Cereal",
    compatible_soil_types: ["Clay", "Clay Loam", "Alluvial Soil", "Loam", "Black Soil"],
    soil_ph_range: { min: 5.0, max: 8.0, optimal_min: 6.0, optimal_max: 7.2 },
    temperature_range: { min: 18.0, max: 38.0, optimal_min: 22.0, optimal_max: 32.0, unit: "°C" },
    rainfall_range: { min: 900.0, max: 2500.0, optimal_min: 1200.0, optimal_max: 1800.0, unit: "mm" },
    humidity_range: { min: 55.0, max: 95.0, optimal_min: 70.0, optimal_max: 88.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 70.0, max: 160.0, unit: "mg/kg" },
      phosphorus: { min: 25.0, max: 65.0, unit: "mg/kg" },
      potassium: { min: 35.0, max: 90.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif", "Zaid"],
    irrigation_considerations: "Requires standing water (2-5 cm) during vegetative tillering phase. High water requirement.",
    water_requirement_level: "High",
    regional_applicability: ["West Bengal", "Uttar Pradesh", "Punjab", "Andhra Pradesh", "Telangana", "Tamil Nadu", "Odisha", "Bihar", "Assam", "Chhattisgarh"],
    description: "Primary staple cereal of India, thriving in humid, warm climates with clay or alluvial soil capable of holding water."
  },
  {
    id: "wheat",
    name: "Wheat",
    scientific_name: "Triticum aestivum",
    category: "Cereal",
    compatible_soil_types: ["Clay Loam", "Loam", "Alluvial Soil", "Sandy Loam"],
    soil_ph_range: { min: 5.8, max: 8.2, optimal_min: 6.2, optimal_max: 7.5 },
    temperature_range: { min: 10.0, max: 28.0, optimal_min: 14.0, optimal_max: 22.0, unit: "°C" },
    rainfall_range: { min: 300.0, max: 900.0, optimal_min: 450.0, optimal_max: 750.0, unit: "mm" },
    humidity_range: { min: 35.0, max: 75.0, optimal_min: 45.0, optimal_max: 65.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 60.0, max: 140.0, unit: "mg/kg" },
      phosphorus: { min: 30.0, max: 70.0, unit: "mg/kg" },
      potassium: { min: 30.0, max: 80.0, unit: "mg/kg" }
    },
    growing_seasons: ["Rabi"],
    irrigation_considerations: "Requires 4-6 critical irrigations: Crown Root Initiation (CRI) at 21 days is mandatory.",
    water_requirement_level: "Moderate",
    regional_applicability: ["Uttar Pradesh", "Punjab", "Haryana", "Madhya Pradesh", "Rajasthan", "Bihar", "Gujarat"],
    description: "Dominant Rabi winter cereal of north and central India requiring cool temperature during vegetative growth."
  },
  {
    id: "maize",
    name: "Maize",
    scientific_name: "Zea mays",
    category: "Cereal",
    compatible_soil_types: ["Loam", "Sandy Loam", "Clay Loam", "Alluvial Soil", "Red Soil"],
    soil_ph_range: { min: 5.5, max: 7.8, optimal_min: 6.0, optimal_max: 7.2 },
    temperature_range: { min: 15.0, max: 35.0, optimal_min: 21.0, optimal_max: 30.0, unit: "°C" },
    rainfall_range: { min: 500.0, max: 1100.0, optimal_min: 600.0, optimal_max: 900.0, unit: "mm" },
    humidity_range: { min: 45.0, max: 85.0, optimal_min: 55.0, optimal_max: 75.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 80.0, max: 160.0, unit: "mg/kg" },
      phosphorus: { min: 35.0, max: 75.0, unit: "mg/kg" },
      potassium: { min: 35.0, max: 80.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif", "Rabi", "Zaid"],
    irrigation_considerations: "Sensitive to waterlogging and moisture stress during tasseling and silking stages.",
    water_requirement_level: "Moderate",
    regional_applicability: ["Karnataka", "Madhya Pradesh", "Maharashtra", "Tamil Nadu", "Rajasthan", "Uttar Pradesh", "Telangana", "Bihar"],
    description: "Versatile industrial, feed, and food crop known as the 'queen of cereals' with wide seasonal adaptability."
  },
  {
    id: "cotton",
    name: "Cotton",
    scientific_name: "Gossypium hirsutum",
    category: "Fiber / Cash Crop",
    compatible_soil_types: ["Black Soil", "Alluvial Soil", "Clay Loam", "Red Soil"],
    soil_ph_range: { min: 6.0, max: 8.5, optimal_min: 6.5, optimal_max: 7.8 },
    temperature_range: { min: 20.0, max: 38.0, optimal_min: 24.0, optimal_max: 34.0, unit: "°C" },
    rainfall_range: { min: 500.0, max: 1200.0, optimal_min: 650.0, optimal_max: 1000.0, unit: "mm" },
    humidity_range: { min: 45.0, max: 80.0, optimal_min: 55.0, optimal_max: 70.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 60.0, max: 130.0, unit: "mg/kg" },
      phosphorus: { min: 25.0, max: 60.0, unit: "mg/kg" },
      potassium: { min: 30.0, max: 80.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif"],
    irrigation_considerations: "Critical irrigation needed at flowering and boll development. Highly susceptible to waterlogging.",
    water_requirement_level: "Moderate",
    regional_applicability: ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Rajasthan", "Karnataka", "Haryana", "Punjab"],
    description: "Major commercial fiber crop thriving in deep, moisture-retentive black basalt soils (Regur)."
  },
  {
    id: "chickpea",
    name: "Chickpea (Bengal Gram)",
    scientific_name: "Cicer arietinum",
    category: "Pulse",
    compatible_soil_types: ["Loam", "Clay Loam", "Black Soil", "Sandy Loam", "Alluvial Soil"],
    soil_ph_range: { min: 6.0, max: 8.4, optimal_min: 6.5, optimal_max: 7.6 },
    temperature_range: { min: 10.0, max: 30.0, optimal_min: 16.0, optimal_max: 24.0, unit: "°C" },
    rainfall_range: { min: 250.0, max: 700.0, optimal_min: 350.0, optimal_max: 550.0, unit: "mm" },
    humidity_range: { min: 30.0, max: 70.0, optimal_min: 40.0, optimal_max: 60.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 15.0, max: 40.0, unit: "mg/kg" },
      phosphorus: { min: 35.0, max: 75.0, unit: "mg/kg" },
      potassium: { min: 20.0, max: 55.0, unit: "mg/kg" }
    },
    growing_seasons: ["Rabi"],
    irrigation_considerations: "Primarily grown on residual soil moisture. Excess irrigation promotes vegetative growth at cost of yield.",
    water_requirement_level: "Low",
    regional_applicability: ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Karnataka", "Gujarat", "Andhra Pradesh"],
    description: "Leading pulse crop of India, fixing atmospheric nitrogen through Rhizobium symbiosis."
  },
  {
    id: "pearl_millet",
    name: "Pearl Millet (Bajra)",
    scientific_name: "Pennisetum glaucum",
    category: "Millet",
    compatible_soil_types: ["Sandy", "Sandy Loam", "Red Soil", "Loam", "Black Soil"],
    soil_ph_range: { min: 5.8, max: 8.6, optimal_min: 6.5, optimal_max: 8.2 },
    temperature_range: { min: 18.0, max: 42.0, optimal_min: 26.0, optimal_max: 36.0, unit: "°C" },
    rainfall_range: { min: 200.0, max: 650.0, optimal_min: 300.0, optimal_max: 500.0, unit: "mm" },
    humidity_range: { min: 30.0, max: 75.0, optimal_min: 40.0, optimal_max: 65.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 40.0, max: 90.0, unit: "mg/kg" },
      phosphorus: { min: 20.0, max: 50.0, unit: "mg/kg" },
      potassium: { min: 20.0, max: 50.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif", "Zaid"],
    irrigation_considerations: "Superbly drought hardy. Survives prolonged dry spells; responsive to 1-2 life-saving irrigations.",
    water_requirement_level: "Low",
    regional_applicability: ["Rajasthan", "Uttar Pradesh", "Gujarat", "Haryana", "Maharashtra", "Tamil Nadu", "Karnataka"],
    description: "Nutrient-dense, climate-resilient dryland cereal capable of producing reliable yields in sandy soils."
  },
  {
    id: "sugarcane",
    name: "Sugarcane",
    scientific_name: "Saccharum officinarum",
    category: "Commercial / Sugar Crop",
    compatible_soil_types: ["Clay Loam", "Loam", "Alluvial Soil", "Black Soil"],
    soil_ph_range: { min: 5.8, max: 8.4, optimal_min: 6.5, optimal_max: 7.8 },
    temperature_range: { min: 18.0, max: 38.0, optimal_min: 24.0, optimal_max: 34.0, unit: "°C" },
    rainfall_range: { min: 1000.0, max: 2500.0, optimal_min: 1400.0, optimal_max: 2000.0, unit: "mm" },
    humidity_range: { min: 50.0, max: 90.0, optimal_min: 65.0, optimal_max: 85.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 120.0, max: 250.0, unit: "mg/kg" },
      phosphorus: { min: 40.0, max: 90.0, unit: "mg/kg" },
      potassium: { min: 50.0, max: 130.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif", "Rabi"],
    irrigation_considerations: "Extremely heavy water requirement (1500-2500 mm). Requires 20-30 irrigations in tropical zones.",
    water_requirement_level: "High",
    regional_applicability: ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Bihar", "Gujarat", "Andhra Pradesh", "Punjab"],
    description: "Long-duration perennial cash crop requiring substantial irrigation, warm temperatures, and high solar radiation."
  },
  {
    id: "soybean",
    name: "Soybean",
    scientific_name: "Glycine max",
    category: "Oilseed / Pulse",
    compatible_soil_types: ["Black Soil", "Clay Loam", "Loam", "Alluvial Soil"],
    soil_ph_range: { min: 6.0, max: 7.8, optimal_min: 6.3, optimal_max: 7.2 },
    temperature_range: { min: 18.0, max: 35.0, optimal_min: 22.0, optimal_max: 30.0, unit: "°C" },
    rainfall_range: { min: 550.0, max: 1000.0, optimal_min: 650.0, optimal_max: 850.0, unit: "mm" },
    humidity_range: { min: 50.0, max: 85.0, optimal_min: 60.0, optimal_max: 78.0, unit: "%" },
    npk_ranges: {
      nitrogen: { min: 20.0, max: 50.0, unit: "mg/kg" },
      phosphorus: { min: 40.0, max: 80.0, unit: "mg/kg" },
      potassium: { min: 30.0, max: 70.0, unit: "mg/kg" }
    },
    growing_seasons: ["Kharif"],
    irrigation_considerations: "Typically rainfed during Kharif monsoon. Critical stages for moisture are pod initiation and bean filling.",
    water_requirement_level: "Moderate",
    regional_applicability: ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana", "Gujarat"],
    description: "Premier rainfed oilseed and protein crop cultivated across the vertisol black soils of Central India."
  }
];

export const EXAMPLE_PROFILES: ExampleProfile[] = [
  {
    id: "profile_rice_delta",
    name: "1. Rice-Oriented Delta (Kharif Monsoon)",
    description: "East Godavari, AP: High rainfall (1450mm), 29°C, 82% humidity, Clay Loam soil.",
    input_data: {
      location: { country: "India", state: "Andhra Pradesh", district: "East Godavari", season: "Kharif", irrigation: "Irrigated" },
      soil: { soil_type: "Clay Loam", soil_ph: 6.8, nitrogen: 110.0, phosphorus: 45.0, potassium: 60.0, is_measured: true },
      environment: { temperature: 29.0, rainfall: 1450.0, relative_humidity: 82.0, sunlight_hours: 6.5, is_measured: true }
    }
  },
  {
    id: "profile_pearl_millet_arid",
    name: "2. Millet-Oriented Semi-Arid (Dryland Kharif)",
    description: "Jodhpur, Rajasthan: Low rainfall (380mm), 32.5°C, 45% humidity, Sandy Loam.",
    input_data: {
      location: { country: "India", state: "Rajasthan", district: "Jodhpur", season: "Kharif", irrigation: "Rainfed" },
      soil: { soil_type: "Sandy Loam", soil_ph: 7.6, nitrogen: 45.0, phosphorus: 25.0, potassium: 35.0, is_measured: true },
      environment: { temperature: 32.5, rainfall: 380.0, relative_humidity: 45.0, sunlight_hours: 8.5, is_measured: true }
    }
  },
  {
    id: "profile_chickpea_rabi_pulse",
    name: "3. Pulse-Oriented Cool Winter (Rabi Central India)",
    description: "Ujjain, MP: Cool 19.5°C, 310mm, 48% humidity, Black Soil.",
    input_data: {
      location: { country: "India", state: "Madhya Pradesh", district: "Ujjain", season: "Rabi", irrigation: "Rainfed" },
      soil: { soil_type: "Black Soil", soil_ph: 7.4, nitrogen: 28.0, phosphorus: 50.0, potassium: 38.0, is_measured: true },
      environment: { temperature: 19.5, rainfall: 310.0, relative_humidity: 48.0, sunlight_hours: 7.5, is_measured: true }
    }
  },
  {
    id: "profile_missing_npk",
    name: "4. Missing NPK Lab Data (Deccan Plateau)",
    description: "Nagpur, Maharashtra: Black soil, 27.5°C, 780mm, soil test kit not yet used.",
    input_data: {
      location: { country: "India", state: "Maharashtra", district: "Nagpur", season: "Kharif", irrigation: "Irrigated" },
      soil: { soil_type: "Black Soil", soil_ph: 7.1, nitrogen: null, phosphorus: null, potassium: null, is_measured: false },
      environment: { temperature: 27.5, rainfall: 780.0, relative_humidity: 68.0, sunlight_hours: 6.0, is_measured: true }
    }
  }
];
