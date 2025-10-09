#!/usr/bin/env python3
"""
Simple test script to verify the TrailBlazer web backend is working
"""

import sys
import os
from pathlib import Path

# Add the skeleton directory to the Python path
SKELETON_DIR = Path(__file__).parent.parent.parent / "skeleton"
sys.path.insert(0, str(SKELETON_DIR))

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        from segments import get_segments, Box, Point, Segment, Segments
        print("✅ segments module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing segments: {e}")
        return False
    
    try:
        from graphmaker import make_graph, simplify_graph
        print("✅ graphmaker module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing graphmaker: {e}")
        return False
    
    try:
        from monuments import get_monuments, Monument, Monuments
        print("✅ monuments module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing monuments: {e}")
        return False
    
    try:
        from routes import find_routes, export_PNG_routes, export_KML_routes
        print("✅ routes module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing routes: {e}")
        return False
    
    try:
        from viewer import export_PNG, export_KML
        print("✅ viewer module imported successfully")
    except ImportError as e:
        print(f"❌ Error importing viewer: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality of the modules"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from segments import Box, Point
        from monuments import get_monuments
        
        # Test creating basic data structures
        point = Point(41.3851, 2.1734)  # Barcelona
        print(f"✅ Created point: {point}")
        
        box = Box(Point(41.3, 2.1), Point(41.4, 2.2))
        print(f"✅ Created box: {box}")
        
        # Test getting monuments (this might take a moment)
        print("📡 Testing monument retrieval (this may take a moment)...")
        monuments = get_monuments("militars")
        print(f"✅ Retrieved {len(monuments)} military monuments")
        
        if monuments:
            print(f"   Example: {monuments[0].name} at {monuments[0].location}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

def test_web_dependencies():
    """Test web-specific dependencies"""
    print("\n🧪 Testing web dependencies...")
    
    try:
        import fastapi
        print("✅ FastAPI available")
    except ImportError:
        print("❌ FastAPI not installed. Run: pip3 install fastapi")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn available")
    except ImportError:
        print("❌ Uvicorn not installed. Run: pip3 install uvicorn")
        return False
    
    try:
        import pydantic
        print("✅ Pydantic available")
    except ImportError:
        print("❌ Pydantic not installed. Run: pip3 install pydantic")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 TrailBlazer Web Backend Test Suite")
    print("=" * 50)
    
    # Check if skeleton directory exists
    if not SKELETON_DIR.exists():
        print(f"❌ Skeleton directory not found at: {SKELETON_DIR}")
        print("   Make sure you're running this from the web/backend directory")
        return False
    
    print(f"📁 Using skeleton directory: {SKELETON_DIR}")
    
    # Run tests
    tests = [
        test_imports,
        test_web_dependencies,
        test_basic_functionality
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Summary
    print("=" * 50)
    if passed == len(tests):
        print("🎉 All tests passed! The web backend should work correctly.")
        print("\nNext steps:")
        print("1. Start the backend: python3 app.py")
        print("2. Open the frontend: web/frontend/index.html")
        print("3. Or use the startup script: ./start_web.sh")
    else:
        print(f"⚠️  {len(tests) - passed} test(s) failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install missing dependencies: pip3 install fastapi uvicorn pydantic")
        print("- Make sure you're in the correct directory")
        print("- Check that the skeleton modules exist and are working")
    
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)