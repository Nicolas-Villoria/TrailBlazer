#!/usr/bin/env python3
"""
Test script to debug monument downloading
"""

import sys
import os
from pathlib import Path

# Add the skeleton directory to the Python path
SKELETON_DIR = Path(__file__).parent.parent.parent / "skeleton"
sys.path.insert(0, str(SKELETON_DIR))

def main():
    print("🧪 Testing Monument Download")
    print("=" * 40)
    
    # Change to skeleton directory
    original_cwd = os.getcwd()
    os.chdir(str(SKELETON_DIR))
    
    try:
        from monuments import get_monuments, download_monuments
        
        print("📡 Testing direct download_monuments call...")
        
        # Test with the correct URL path
        monuments = download_monuments("edificacions-de-caracter-militar")
        print(f"✅ Downloaded {len(monuments)} military monuments")
        
        if monuments:
            print("📍 First few monuments:")
            for i, monument in enumerate(monuments[:3]):
                print(f"  {i+1}. {monument.name} at {monument.location}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()