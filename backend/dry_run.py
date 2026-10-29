"""
Dry run execution script to test all live FastAPI endpoints and engine workflows.
"""
from fastapi.testclient import TestClient
from app.main import app

def main():
    print("==================================================")
    print("STARTING SMART KRISHI ADVISOR LIVE DRY RUN")
    print("==================================================")
    
    client = TestClient(app)
    
    # 1. Health check
    print("\n[1/5] Testing Health Check Endpoint (/api/health)...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.status_code}"
    health_data = res.json()
    print(f" -> Status: {health_data.get('status')} | Version: {health_data.get('version')} | Crops in DB: {health_data.get('total_crops_loaded')}")
    
    # 2. Crops listing
    print("\n[2/5] Testing Crops Catalog Endpoint (/api/crops)...")
    res = client.get("/api/crops")
    assert res.status_code == 200, f"Crops list failed: {res.status_code}"
    crops = res.json()
    print(f" -> Successfully loaded {len(crops)} crops from catalog:")
    for c in crops[:4]:
        print(f"    - {c['name']} ({c['scientific_name']}) | Seasons: {c['growing_seasons']} | Water: {c['water_requirement_level']}")
    
    # 3. Test profiles listing
    print("\n[3/5] Testing Example Profiles (/api/profiles)...")
    res = client.get("/api/profiles")
    assert res.status_code == 200
    profiles = res.json()
    print(f" -> Found {len(profiles)} regional example profiles.")
    
    # 4. Test recommendation with Profile 1 (Rice Delta)
    profile_1 = profiles[0]
    print(f"\n[4/5] Testing Recommendation Engine with Profile 1: {profile_1['name']}...")
    payload = profile_1["input_data"]
    res = client.post("/api/recommend", json=payload)
    assert res.status_code == 200, f"Recommendation failed: {res.status_code} - {res.text}"
    rec_result = res.json()
    print(f" -> Status: {rec_result.get('status')} | Sufficient Data: {rec_result.get('is_sufficient_data')}")
    print(f" -> Overall Input Coverage: {rec_result.get('overall_coverage_pct')}%")
    print(f" -> Total Crops Evaluated: {len(rec_result.get('recommendations', []))}")
    print(" -> Top 3 Ranked Crops:")
    for idx, item in enumerate(rec_result.get("recommendations", [])[:3], 1):
        print(f"    {idx}. {item['crop_name']} ({item['scientific_name']})")
        print(f"       * Compatibility Score: {item['compatibility_score']}%")
        print(f"       * Suitability: {item['suitability_category']}")
        print(f"       * Matched Factors ({len(item['matched_factors'])}): {', '.join(item['matched_factors'])}")
        print(f"       * Why this crop: {item['why_this_crop'][:120]}...")
    
    # 5. Test crop comparison
    print("\n[5/5] Testing Side-by-Side Crop Comparison Endpoint (/api/compare)...")
    compare_payload = {
        "crop_ids": ["rice", "pearl_millet", "chickpea"],
        "user_context": payload
    }
    res = client.post("/api/compare", json=compare_payload)
    assert res.status_code == 200, f"Comparison failed: {res.status_code} - {res.text}"
    comp_result = res.json()
    print(f" -> Compared Crops: {list(comp_result.get('crop_names', {}).values())}")
    print(f" -> Comparison Matrix Dimensions: {len(comp_result.get('comparison_table', []))} parameters evaluated")
    for row in comp_result.get("comparison_table", [])[:4]:
        print(f"    * Factor: {row['factor_name']}")
        for cid, val in row.get("values_by_crop", {}).items():
            status_tag = row.get("status_by_crop", {}).get(cid, "")
            print(f"        - {cid}: {val} [{status_tag}]")
    print(f" -> Summary Verdict: {comp_result.get('summary_verdict')}")
    
    print("\n==================================================")
    print("SUCCESS: ALL API ENDPOINTS & LOGIC PASSED DRY RUN!")
    print("==================================================")

if __name__ == "__main__":
    main()
