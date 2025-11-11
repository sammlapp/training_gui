#!/usr/bin/env python3
"""Test audio utilities to ensure spectrogram generation works"""

import numpy as np
import soundfile as sf
from tabs.audio_utils import create_spectrogram, audio_to_base64, generate_placeholder_spectrogram

# Create a test audio file with a sine wave
def create_test_audio():
    """Create a simple test audio file"""
    sample_rate = 22050
    duration = 3  # seconds
    frequency = 440  # Hz (A4 note)
    
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t)
    
    # Add some harmonics for more interesting spectrogram
    audio += 0.5 * np.sin(2 * np.pi * frequency * 2 * t)
    audio += 0.3 * np.sin(2 * np.pi * frequency * 3 * t)
    
    # Normalize
    audio = audio / np.max(np.abs(audio))
    
    # Save to file
    test_file = 'test_audio_sine.wav'
    sf.write(test_file, audio, sample_rate)
    
    return test_file, sample_rate

if __name__ == '__main__':
    print("Testing audio utilities...")
    
    # Test placeholder generation
    print("1. Testing placeholder spectrogram generation...")
    placeholder = generate_placeholder_spectrogram(400, 200)
    print(f"   ✓ Placeholder generated: {len(placeholder)} characters")
    
    # Test audio file creation
    print("2. Creating test audio file...")
    test_file, sr = create_test_audio()
    print(f"   ✓ Test audio created: {test_file} at {sr} Hz")
    
    # Test spectrogram generation
    print("3. Testing spectrogram generation...")
    try:
        spec_b64, audio_b64, sample_rate = create_spectrogram(
            test_file,
            0.0,
            3.0,
            settings={
                'image_width': 400,
                'image_height': 200,
                'spec_window_size': 512,
                'spectrogram_colormap': 'viridis'
            }
        )
        print(f"   ✓ Spectrogram generated: {len(spec_b64)} characters")
        print(f"   ✓ Audio base64 generated: {len(audio_b64)} characters")
        print(f"   ✓ Sample rate: {sample_rate} Hz")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nAll tests completed!")
