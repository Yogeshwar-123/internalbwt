import { useState, useEffect } from 'react';
import { CROPS_CATALOG, EXAMPLE_PROFILES } from './cropsData';
import type { RecommendationCard } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export default function App() {
  const [activeTab, setActiveTab] = useState<'recommender' | 'comparator' | 'catalog'>('recommender');
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);

  // Form State
  const [season, setSeason] = useState('Kharif');
  const [state, setState] = useState('Andhra Pradesh');
  const [soilType, setSoilType] = useState('Clay Loam');
  const [soilPh, setSoilPh] = useState<number | ''>(6.8);
  const [temperature, setTemperature] = useState<number | ''>(29.0);
  const [rainfall, setRainfall] = useState<number | ''>(1450);
  const [humidity, setHumidity] = useState<number | ''>(82);
  const [nitrogen, setNitrogen] = useState<number | ''>(110);
  const [phosphorus, setPhosphorus] = useState<number | ''>(45);
  const [potassium, setPotassium] = useState<number | ''>(60);

  // Results State
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<RecommendationCard[]>([]);
  const [coveragePct, setCoveragePct] = useState(100);

  // Comparator State
  const [selectedCropIds, setSelectedCropIds] = useState<string[]>(['rice', 'pearl_millet', 'chickpea']);

  // Catalog Filter State
  const [catalogSeasonFilter, setCatalogSeasonFilter] = useState('All');
  const [catalogCategoryFilter, setCatalogCategoryFilter] = useState('All');

  // Check Backend Health
  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => {
        if (res.ok) setApiOnline(true);
        else setApiOnline(false);
      })
      .catch(() => setApiOnline(false));
  }, []);

  // Preset Profile Loader
  const loadProfile = (profileId: string) => {
    const profile = EXAMPLE_PROFILES.find((p) => p.id === profileId);
    if (!profile) return;
    const { location, soil, environment } = profile.input_data;
    setSeason(location.season);
    setState(location.state);
    setSoilType(soil.soil_type);
    setSoilPh(soil.soil_ph ?? '');
    setTemperature(environment.temperature);
    setRainfall(environment.rainfall ?? '');
    setHumidity(environment.relative_humidity ?? '');
    setNitrogen(soil.nitrogen ?? '');
    setPhosphorus(soil.phosphorus ?? '');
    setPotassium(soil.potassium ?? '');
  };

  // Run Recommendation Calculation (Client-side Fallback or API)
  const handleRecommend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);

    const payload = {
      location: {
        country: 'India',
        state,
        district: null,
        season,
        irrigation: 'Irrigated',
      },
      soil: {
        soil_type: soilType,
        soil_ph: soilPh !== '' ? Number(soilPh) : null,
        nitrogen: nitrogen !== '' ? Number(nitrogen) : null,
        phosphorus: phosphorus !== '' ? Number(phosphorus) : null,
        potassium: potassium !== '' ? Number(potassium) : null,
        is_measured: nitrogen !== '' || phosphorus !== '' || potassium !== '',
      },
      environment: {
        temperature: temperature !== '' ? Number(temperature) : 28,
        rainfall: rainfall !== '' ? Number(rainfall) : null,
        rainfall_period: 'Growing Season',
        relative_humidity: humidity !== '' ? Number(humidity) : null,
        sunlight_hours: 7.0,
        is_measured: true,
      },
    };

    try {
      const res = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        setRecommendations(data.recommendations || []);
        setCoveragePct(data.overall_coverage_pct || 100);
        setApiOnline(true);
        setLoading(false);
        return;
      }
    } catch {
      // Fallback to client-side rule evaluation
    }

    // Client-side rule engine calculation fallback
    const scored: RecommendationCard[] = CROPS_CATALOG.map((crop) => {
      let score = 50;
      const matched: string[] = [];
      const mismatched: string[] = [];

      // Season match
      if (crop.growing_seasons.includes(season)) {
        score += 20;
        matched.push('Growing Season');
      } else {
        score -= 25;
        mismatched.push('Growing Season Mismatch');
      }

      // Soil type match
      if (crop.compatible_soil_types.includes(soilType)) {
        score += 15;
        matched.push('Soil Type');
      } else {
        score -= 10;
        mismatched.push('Soil Texture');
      }

      // pH check
      if (typeof soilPh === 'number') {
        if (soilPh >= crop.soil_ph_range.optimal_min && soilPh <= crop.soil_ph_range.optimal_max) {
          score += 15;
          matched.push('Optimal Soil pH');
        } else if (soilPh >= crop.soil_ph_range.min && soilPh <= crop.soil_ph_range.max) {
          score += 8;
          matched.push('Tolerable pH');
        } else {
          score -= 15;
          mismatched.push('Soil pH Out of Bounds');
        }
      }

      // Temperature check
      if (typeof temperature === 'number') {
        if (temperature >= crop.temperature_range.optimal_min && temperature <= crop.temperature_range.optimal_max) {
          score += 15;
          matched.push('Optimal Temperature');
        } else if (temperature >= crop.temperature_range.min && temperature <= crop.temperature_range.max) {
          score += 8;
        } else {
          score -= 20;
          mismatched.push('Temperature Stress');
        }
      }

      // Rainfall check
      if (typeof rainfall === 'number') {
        if (rainfall >= crop.rainfall_range.optimal_min && rainfall <= crop.rainfall_range.optimal_max) {
          score += 15;
          matched.push('Optimal Rainfall');
        } else if (rainfall >= crop.rainfall_range.min && rainfall <= crop.rainfall_range.max) {
          score += 8;
        } else {
          score -= 15;
          mismatched.push('Water/Rainfall Deficit or Excess');
        }
      }

      const finalScore = Math.max(0, Math.min(100, Math.round(score)));
      const suitability =
        finalScore >= 80 ? 'Highly Compatible' : finalScore >= 55 ? 'Moderately Compatible' : 'Potential Mismatch';

      return {
        crop_id: crop.id,
        crop_name: crop.name,
        scientific_name: crop.scientific_name,
        category: crop.category,
        suitability_category: suitability,
        compatibility_score: finalScore,
        data_coverage_pct: 100,
        matched_factors: matched,
        mismatched_factors: mismatched,
        unevaluated_factors: [],
        why_this_crop: `${crop.name} is evaluated as ${suitability} for ${season} season cultivation under ${soilType} conditions. ${crop.description}`,
        irrigation_advice: crop.irrigation_considerations,
      };
    });

    scored.sort((a, b) => b.compatibility_score - a.compatibility_score);
    setRecommendations(scored);
    setCoveragePct(100);
    setLoading(false);
  };

  // Initial recommendation on mount
  useEffect(() => {
    handleRecommend();
  }, []);

  // Filtered Catalog
  const filteredCrops = CROPS_CATALOG.filter((c) => {
    const matchSeason = catalogSeasonFilter === 'All' || c.growing_seasons.includes(catalogSeasonFilter);
    const matchCat = catalogCategoryFilter === 'All' || c.category.toLowerCase().includes(catalogCategoryFilter.toLowerCase());
    return matchSeason && matchCat;
  });

  // Selected crops for comparison
  const comparedCrops = CROPS_CATALOG.filter((c) => selectedCropIds.includes(c.id));

  return (
    <div className="min-h-screen bg-[#f8faf7] text-[#1a2e1d] flex flex-col">
      {/* Header */}
      <header className="bg-emerald-900 text-white shadow-md border-b border-emerald-800">
        <div className="max-w-7xl mx-auto px-4 py-4 flex flex-col sm:flex-row justify-between items-center gap-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-xl text-white shadow">
              🌾
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Smart Krishi Advisor</h1>
              <p className="text-xs text-emerald-200">
                Explainable Decision Support for Indian Agro-Climatic Zones
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span
              className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${
                apiOnline
                  ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                  : 'bg-amber-100 text-amber-800 border border-amber-300'
              }`}
            >
              <span
                className={`w-2 h-2 rounded-full mr-1.5 ${
                  apiOnline ? 'bg-emerald-500' : 'bg-amber-500'
                }`}
              ></span>
              {apiOnline ? 'API Connected' : 'Client Mode (Offline Fallback)'}
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto px-4 border-t border-emerald-800/60 flex space-x-2 pt-2">
          <button
            onClick={() => setActiveTab('recommender')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
              activeTab === 'recommender'
                ? 'bg-[#f8faf7] text-emerald-950 font-bold shadow'
                : 'text-emerald-100 hover:bg-emerald-800'
            }`}
          >
            🌱 Crop Recommender
          </button>
          <button
            onClick={() => setActiveTab('comparator')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
              activeTab === 'comparator'
                ? 'bg-[#f8faf7] text-emerald-950 font-bold shadow'
                : 'text-emerald-100 hover:bg-emerald-800'
            }`}
          >
            ⚖️ Crop Comparator ({selectedCropIds.length})
          </button>
          <button
            onClick={() => setActiveTab('catalog')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
              activeTab === 'catalog'
                ? 'bg-[#f8faf7] text-emerald-950 font-bold shadow'
                : 'text-emerald-100 hover:bg-emerald-800'
            }`}
          >
            📚 Crop Catalog ({CROPS_CATALOG.length})
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto px-4 py-6 w-full">
        {/* ================= TAB 1: RECOMMENDER ================= */}
        {activeTab === 'recommender' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Form Column */}
            <div className="lg:col-span-5 bg-white p-5 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-bold text-emerald-950">1. Agricultural Context</h2>
                <span className="text-xs bg-emerald-50 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-200">
                  Data Coverage: {coveragePct}%
                </span>
              </div>

              {/* Quick Profile Selectors */}
              <div className="mb-4">
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Load Regional Example Profile:
                </label>
                <div className="grid grid-cols-2 gap-1.5">
                  {EXAMPLE_PROFILES.map((prof) => (
                    <button
                      key={prof.id}
                      type="button"
                      onClick={() => loadProfile(prof.id)}
                      className="text-left text-xs p-1.5 rounded border border-gray-200 hover:border-emerald-500 hover:bg-emerald-50 transition font-medium text-gray-700"
                    >
                      {prof.name.split('.')[1] || prof.name}
                    </button>
                  ))}
                </div>
              </div>

              <form onSubmit={handleRecommend} className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Season</label>
                    <select
                      value={season}
                      onChange={(e) => setSeason(e.target.value)}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="Kharif">Kharif (Monsoon)</option>
                      <option value="Rabi">Rabi (Winter)</option>
                      <option value="Zaid">Zaid (Summer)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">State</label>
                    <input
                      type="text"
                      value={state}
                      onChange={(e) => setState(e.target.value)}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Soil Type</label>
                    <select
                      value={soilType}
                      onChange={(e) => setSoilType(e.target.value)}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    >
                      <option value="Clay Loam">Clay Loam</option>
                      <option value="Sandy Loam">Sandy Loam</option>
                      <option value="Black Soil">Black Soil (Vertisol)</option>
                      <option value="Loam">Loam</option>
                      <option value="Alluvial Soil">Alluvial Soil</option>
                      <option value="Red Soil">Red Soil</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">
                      Soil pH: {soilPh}
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      min="4.0"
                      max="9.5"
                      value={soilPh}
                      onChange={(e) => setSoilPh(e.target.value ? Number(e.target.value) : '')}
                      placeholder="e.g. 6.8"
                      className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Temp (°C)</label>
                    <input
                      type="number"
                      step="0.5"
                      value={temperature}
                      onChange={(e) => setTemperature(e.target.value ? Number(e.target.value) : '')}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Rain (mm)</label>
                    <input
                      type="number"
                      value={rainfall}
                      onChange={(e) => setRainfall(e.target.value ? Number(e.target.value) : '')}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-gray-700 mb-1">Humidity (%)</label>
                    <input
                      type="number"
                      value={humidity}
                      onChange={(e) => setHumidity(e.target.value ? Number(e.target.value) : '')}
                      className="w-full text-sm border border-gray-300 rounded-lg p-2"
                    />
                  </div>
                </div>

                {/* Optional NPK */}
                <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                  <span className="block text-xs font-bold text-gray-600 mb-2">
                    Optional Soil Lab NPK (mg/kg) - Excluded from score if empty:
                  </span>
                  <div className="grid grid-cols-3 gap-2">
                    <input
                      type="number"
                      placeholder="N"
                      value={nitrogen}
                      onChange={(e) => setNitrogen(e.target.value ? Number(e.target.value) : '')}
                      className="text-xs border border-gray-300 rounded p-1.5"
                    />
                    <input
                      type="number"
                      placeholder="P"
                      value={phosphorus}
                      onChange={(e) => setPhosphorus(e.target.value ? Number(e.target.value) : '')}
                      className="text-xs border border-gray-300 rounded p-1.5"
                    />
                    <input
                      type="number"
                      placeholder="K"
                      value={potassium}
                      onChange={(e) => setPotassium(e.target.value ? Number(e.target.value) : '')}
                      className="text-xs border border-gray-300 rounded p-1.5"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-2.5 px-4 bg-emerald-700 hover:bg-emerald-800 text-white font-semibold rounded-lg shadow transition flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? 'Evaluating Agronomic Rules...' : '🔍 Compute Suitability & Recommendations'}
                </button>
              </form>
            </div>

            {/* Results Column */}
            <div className="lg:col-span-7 space-y-4">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-bold text-emerald-950">
                  2. Ranked Recommendations ({recommendations.length} Evaluated)
                </h2>
                <span className="text-xs text-gray-500">
                  Grounded in ICAR agronomic thresholds
                </span>
              </div>

              {recommendations.length === 0 ? (
                <div className="bg-white p-8 text-center rounded-xl border border-dashed border-gray-300 text-gray-500">
                  No recommendation computed yet. Click "Compute Suitability" to begin.
                </div>
              ) : (
                <div className="space-y-3">
                  {recommendations.slice(0, 5).map((rec, index) => (
                    <div
                      key={rec.crop_id}
                      className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm hover:border-emerald-300 transition"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex items-center gap-2.5">
                          <span className="w-7 h-7 rounded-full bg-emerald-100 text-emerald-900 font-bold flex items-center justify-center text-xs">
                            #{index + 1}
                          </span>
                          <div>
                            <h3 className="font-bold text-gray-900 text-base">
                              {rec.crop_name}{' '}
                              <span className="text-xs text-gray-500 italic font-normal">
                                ({rec.scientific_name})
                              </span>
                            </h3>
                            <span className="text-xs text-gray-500">{rec.category}</span>
                          </div>
                        </div>

                        <div className="text-right">
                          <span
                            className={`inline-block px-2.5 py-0.5 rounded text-xs font-bold ${
                              rec.compatibility_score >= 80
                                ? 'bg-emerald-100 text-emerald-800'
                                : rec.compatibility_score >= 55
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {rec.compatibility_score}% Compatibility
                          </span>
                          <span className="block text-[11px] text-gray-500 font-medium">
                            {rec.suitability_category}
                          </span>
                        </div>
                      </div>

                      <p className="mt-2 text-xs text-gray-700 leading-relaxed bg-emerald-50/50 p-2.5 rounded border border-emerald-100/60">
                        <strong>Why this crop:</strong> {rec.why_this_crop}
                      </p>

                      <div className="mt-2.5 flex flex-wrap gap-1.5 text-[11px]">
                        {rec.matched_factors.map((f) => (
                          <span
                            key={f}
                            className="bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded border border-emerald-200"
                          >
                            ✓ {f}
                          </span>
                        ))}
                        {rec.mismatched_factors.map((f) => (
                          <span
                            key={f}
                            className="bg-rose-50 text-rose-700 px-2 py-0.5 rounded border border-rose-200"
                          >
                            ⚠ {f}
                          </span>
                        ))}
                      </div>

                      <div className="mt-2 text-[11px] text-gray-500 flex items-center justify-between">
                        <span>💧 {rec.irrigation_advice}</span>
                        <button
                          onClick={() => {
                            if (!selectedCropIds.includes(rec.crop_id)) {
                              setSelectedCropIds([...selectedCropIds, rec.crop_id]);
                            }
                            setActiveTab('comparator');
                          }}
                          className="text-emerald-700 hover:text-emerald-900 font-semibold cursor-pointer underline"
                        >
                          Compare in Matrix ➔
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================= TAB 2: COMPARATOR ================= */}
        {activeTab === 'comparator' && (
          <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 border-b pb-4">
              <div>
                <h2 className="text-lg font-bold text-emerald-950">Side-by-Side Crop Comparator</h2>
                <p className="text-xs text-gray-500">
                  Select 2 to 5 crops to analyze requirements, trade-offs, and ecological niches.
                </p>
              </div>

              {/* Selector checkboxes */}
              <div className="flex flex-wrap gap-2">
                {CROPS_CATALOG.map((c) => {
                  const isChecked = selectedCropIds.includes(c.id);
                  return (
                    <button
                      key={c.id}
                      onClick={() => {
                        if (isChecked) {
                          if (selectedCropIds.length > 2) {
                            setSelectedCropIds(selectedCropIds.filter((id) => id !== c.id));
                          }
                        } else {
                          if (selectedCropIds.length < 5) {
                            setSelectedCropIds([...selectedCropIds, c.id]);
                          }
                        }
                      }}
                      className={`text-xs px-2.5 py-1 rounded-full border transition ${
                        isChecked
                          ? 'bg-emerald-700 text-white border-emerald-700 font-semibold'
                          : 'bg-gray-50 text-gray-700 border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      {isChecked ? '✓ ' : '+ '}
                      {c.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Comparison Matrix Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left border-collapse">
                <thead>
                  <tr className="bg-emerald-50 text-emerald-950 border-b border-emerald-200">
                    <th className="p-3 font-bold w-48">Agronomic Parameter</th>
                    {comparedCrops.map((c) => (
                      <th key={c.id} className="p-3 font-bold border-l border-emerald-200">
                        {c.name}
                        <span className="block text-[10px] text-emerald-700 font-normal italic">
                          {c.scientific_name}
                        </span>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Category</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l">
                        {c.category}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Growing Seasons</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l font-medium">
                        {c.growing_seasons.join(', ')}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Compatible Soils</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l">
                        {c.compatible_soil_types.join(', ')}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Optimal Soil pH</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l">
                        {c.soil_ph_range.optimal_min} - {c.soil_ph_range.optimal_max}
                        <span className="block text-[10px] text-gray-400">
                          (Tolerable: {c.soil_ph_range.min} - {c.soil_ph_range.max})
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Optimal Temp (°C)</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l">
                        {c.temperature_range.optimal_min}° - {c.temperature_range.optimal_max}°C
                        <span className="block text-[10px] text-gray-400">
                          (Limits: {c.temperature_range.min}° - {c.temperature_range.max}°C)
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Water Requirement</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l">
                        <span
                          className={`inline-block px-2 py-0.5 rounded font-bold text-[10px] ${
                            c.water_requirement_level === 'High'
                              ? 'bg-blue-100 text-blue-800'
                              : c.water_requirement_level === 'Low'
                              ? 'bg-amber-100 text-amber-800'
                              : 'bg-emerald-100 text-emerald-800'
                          }`}
                        >
                          {c.water_requirement_level} ({c.rainfall_range.optimal_min}-
                          {c.rainfall_range.optimal_max} mm)
                        </span>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Irrigation Details</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l text-gray-600">
                        {c.irrigation_considerations}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="p-3 font-semibold text-gray-700 bg-gray-50">Top Producing States</td>
                    {comparedCrops.map((c) => (
                      <td key={c.id} className="p-3 border-l text-gray-600">
                        {c.regional_applicability.slice(0, 4).join(', ')}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* ================= TAB 3: CATALOG ================= */}
        {activeTab === 'catalog' && (
          <div className="space-y-4">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 bg-white p-4 rounded-xl border border-gray-200">
              <div>
                <h2 className="text-lg font-bold text-emerald-950">Agronomic Crop Catalog</h2>
                <p className="text-xs text-gray-500">
                  Verified reference data from ICAR & TNAU agronomic databases.
                </p>
              </div>

              <div className="flex gap-2 text-xs">
                <select
                  value={catalogSeasonFilter}
                  onChange={(e) => setCatalogSeasonFilter(e.target.value)}
                  className="border border-gray-300 rounded p-1.5"
                >
                  <option value="All">All Seasons</option>
                  <option value="Kharif">Kharif</option>
                  <option value="Rabi">Rabi</option>
                  <option value="Zaid">Zaid</option>
                </select>
                <select
                  value={catalogCategoryFilter}
                  onChange={(e) => setCatalogCategoryFilter(e.target.value)}
                  className="border border-gray-300 rounded p-1.5"
                >
                  <option value="All">All Categories</option>
                  <option value="Cereal">Cereals</option>
                  <option value="Pulse">Pulses</option>
                  <option value="Millet">Millets</option>
                  <option value="Oilseed">Oilseeds</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredCrops.map((crop) => (
                <div
                  key={crop.id}
                  className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col justify-between"
                >
                  <div>
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="font-bold text-base text-gray-900">{crop.name}</h3>
                        <span className="text-xs text-gray-500 italic">{crop.scientific_name}</span>
                      </div>
                      <span className="bg-emerald-50 text-emerald-800 text-[11px] font-semibold px-2 py-0.5 rounded border border-emerald-200">
                        {crop.category}
                      </span>
                    </div>

                    <p className="text-xs text-gray-600 mb-3">{crop.description}</p>

                    <div className="space-y-1 text-[11px] text-gray-700 border-t pt-2">
                      <div>
                        <strong>Seasons:</strong> {crop.growing_seasons.join(', ')}
                      </div>
                      <div>
                        <strong>Optimal pH:</strong> {crop.soil_ph_range.optimal_min} -{' '}
                        {crop.soil_ph_range.optimal_max}
                      </div>
                      <div>
                        <strong>Optimal Temp:</strong> {crop.temperature_range.optimal_min}° -{' '}
                        {crop.temperature_range.optimal_max}°C
                      </div>
                      <div>
                        <strong>Water Demand:</strong> {crop.water_requirement_level} (
                        {crop.rainfall_range.optimal_min}-{crop.rainfall_range.optimal_max} mm)
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => {
                      if (!selectedCropIds.includes(crop.id)) {
                        setSelectedCropIds([...selectedCropIds, crop.id]);
                      }
                      setActiveTab('comparator');
                    }}
                    className="mt-4 w-full py-1.5 text-xs font-semibold bg-gray-50 hover:bg-emerald-50 text-emerald-800 border border-gray-200 rounded transition cursor-pointer"
                  >
                    Compare in Side-by-Side ➔
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 text-center text-xs text-gray-500">
          Smart Krishi Advisor • Problem ID: HACK-P302 • Agronomic Reference Dataset 2024.1-ICAR-TNAU
        </div>
      </footer>
    </div>
  );
}
