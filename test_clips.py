#!/usr/bin/env python3
"""Test script to verify clips endpoint is working"""

import requests
import json

# Test data - simple clip request
test_clip_data = {
    "clips": [
        {
            "file_path": "/Users/SML161/training_gui/frontend/python-env/lib/python3.9/site-packages/opensoundscape/sample_data/birds_10s.wav",
            "start_time": 0.0,
            "end_time": 3.0,
            "species": "Test Species"
        }
    ],
    "settings": {
        "include_spectrogram": True,
        "include_audio": False,
        "spectrogram_settings": {
            "height": 128,
            "width": 256
        }
    }
}

try:
    response = requests.post(
        "http://localhost:8000/clips/batch",
        json=test_clip_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("results"):
            for result in response_data["results"]:
                print(f"Result status: {result.get('status')}")
                if result.get('error'):
                    print(f"Result error: {result.get('error')}")
                if result.get('spectrogram_base64'):
                    print(f"Spectrogram generated: {len(result['spectrogram_base64'])} characters")
    
except Exception as e:
    print(f"Error: {e}")