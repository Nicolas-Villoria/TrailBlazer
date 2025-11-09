#!/usr/bin/env python3
"""
Quick test script to verify TrailBlazer API endpoints
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test health endpoint"""
    print_section("Testing Health Endpoint")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_monument_types():
    """Test monument types endpoint"""
    print_section("Testing Monument Types")
    response = requests.get(f"{BASE_URL}/monument-types")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data.get('types', []))} monument types")
        for t in data.get('types', []):
            print(f"  - {t.get('name')}: {t.get('count', 0)} monuments")
    return response.status_code == 200

def test_monuments():
    """Test monuments endpoint"""
    print_section("Testing Monuments Endpoint")
    # Small area around Barcelona
    params = {
        "monument_type": "militars",
        "bottom_left_lat": 41.3,
        "bottom_left_lon": 2.0,
        "top_right_lat": 41.5,
        "top_right_lon": 2.3
    }
    response = requests.get(f"{BASE_URL}/monuments", params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {data.get('count', 0)} monuments in area")
        if data.get('monuments'):
            print(f"First monument: {data['monuments'][0].get('name')}")
    return response.status_code == 200

def test_segment_stats():
    """Test segment stats endpoint"""
    print_section("Testing Segment Stats")
    params = {
        "bottom_left_lat": 41.3,
        "bottom_left_lon": 2.0,
        "top_right_lat": 41.35,
        "top_right_lon": 2.1
    }
    response = requests.get(f"{BASE_URL}/segments/stats", params=params)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Segments cached: {data.get('segments_cached')}")
        print(f"Segment count: {data.get('segment_count')}")
    return response.status_code == 200

def test_route_calculation():
    """Test route calculation endpoint"""
    print_section("Testing Route Calculation (Async)")
    
    # Small test area
    payload = {
        "start_point": {
            "lat": 41.35,
            "lon": 2.05
        },
        "monument_type": "militars",
        "search_box": {
            "bottom_left": {
                "lat": 41.3,
                "lon": 2.0
            },
            "top_right": {
                "lat": 41.4,
                "lon": 2.1
            }
        }
    }
    
    print("Starting route calculation...")
    response = requests.post(f"{BASE_URL}/routes/calculate", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        job_id = data.get("job_id")
        print(f"Job ID: {job_id}")
        print(f"Message: {data.get('message')}")
        
        # Poll for job completion
        print("\nPolling for job completion...")
        max_attempts = 60
        for attempt in range(max_attempts):
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/routes/job/{job_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                status = status_data.get("status")
                progress = status_data.get("progress", 0)
                print(f"  Attempt {attempt + 1}: Status={status}, Progress={progress*100:.0f}%")
                
                if status == "completed":
                    print("\n✅ Route calculation completed!")
                    result = status_data.get("result", {})
                    print(f"  Reachable monuments: {result.get('reachable_monuments', 0)}")
                    print(f"  Unreachable monuments: {result.get('unreachable_monuments', 0)}")
                    if result.get("png_url"):
                        print(f"  PNG URL: {result.get('png_url')}")
                    if result.get("kml_url"):
                        print(f"  KML URL: {result.get('kml_url')}")
                    return True
                elif status == "failed":
                    print(f"\n❌ Job failed: {status_data.get('error')}")
                    return False
        
        print("\n⚠️  Job did not complete within timeout")
        return False
    
    return False

def main():
    """Run all tests"""
    print("\n🧪 TrailBlazer API Test Suite")
    print("="*60)
    
    tests = [
        ("Health Check", test_health),
        ("Monument Types", test_monument_types),
        ("Monuments Query", test_monuments),
        ("Segment Stats", test_segment_stats),
        # Uncomment to test full route calculation (takes time):
        # ("Route Calculation", test_route_calculation),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results[name] = False
    
    # Summary
    print_section("Test Summary")
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server at http://localhost:8000")
        print("   Please make sure the server is running with: python3 app.py")
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
