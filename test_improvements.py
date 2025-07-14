#!/usr/bin/env python3
"""
Test script to verify the background removal improvements
"""

import time
import requests
import base64
from PIL import Image
import io
import json
import os

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "test_api_key"  # Replace with your actual API key

def test_background_removal():
    """Test the improved background removal functionality"""
    
    # First, let's create a test API key
    create_api_key_response = requests.post(
        f"{API_BASE_URL}/api-keys",
        json={"name": "Test Key for Improvements"},
        headers={"Content-Type": "application/json"}
    )
    
    if create_api_key_response.status_code == 200:
        api_data = create_api_key_response.json()
        api_key = api_data["key"]
        print(f"✅ Created test API key: {api_key[:8]}...")
    else:
        print(f"❌ Failed to create API key: {create_api_key_response.status_code}")
        return
    
    # Test with different scenarios
    test_scenarios = [
        {
            "name": "Auto-detection with quality enhancement",
            "params": {"enhance_quality": True}
        },
        {
            "name": "Human-focused model",
            "params": {"model_hint": "human", "enhance_quality": True}
        },
        {
            "name": "Object-focused model",
            "params": {"model_hint": "object", "enhance_quality": True}
        },
        {
            "name": "General model",
            "params": {"model_hint": "general", "enhance_quality": True}
        },
        {
            "name": "No enhancement (baseline)",
            "params": {"enhance_quality": False}
        }
    ]
    
    # You would need to have a test image file
    test_image_path = "test_image.jpg"
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        print("Please add a test image file to run the tests")
        return
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    print("\n🧪 Testing Background Removal Improvements")
    print("=" * 50)
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        
        try:
            # Prepare the request
            with open(test_image_path, "rb") as f:
                files = {"file": (test_image_path, f, "image/jpeg")}
                data = {"return_json": True}
                data.update(scenario["params"])
                
                # Make the request
                start_time = time.time()
                response = requests.post(
                    f"{API_BASE_URL}/remove-background",
                    files=files,
                    data=data,
                    headers=headers
                )
                request_time = time.time() - start_time
                
                if response.status_code == 200:
                    result = response.json()
                    processing_time = result.get("processing_time", 0)
                    
                    print(f"  ✅ Success!")
                    print(f"  ⏱️  Request time: {request_time:.2f}s")
                    print(f"  ⚡ Processing time: {processing_time:.2f}s")
                    print(f"  📊 Success: {result.get('success', False)}")
                    print(f"  💬 Message: {result.get('message', 'No message')}")
                    
                    # Check if we have image data
                    if "processed_image_url" in result:
                        image_data = result["processed_image_url"]
                        if image_data.startswith("data:image/png;base64,"):
                            print(f"  🖼️  Image data received: {len(image_data)} chars")
                        else:
                            print(f"  ⚠️  Unexpected image data format")
                    
                else:
                    print(f"  ❌ Failed with status: {response.status_code}")
                    print(f"  💥 Error: {response.text}")
                    
        except Exception as e:
            print(f"  ❌ Exception: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Test completed!")

def test_api_status():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Background Removal Improvements Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if test_api_status():
        test_background_removal()
    else:
        print("\n❌ API is not running. Please start the server first:")
        print("   python -m uvicorn main:app --reload")
