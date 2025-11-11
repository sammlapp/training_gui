#!/usr/bin/env python3
"""Test script to verify Review tab rendering with sample data"""

import pandas as pd
from pathlib import Path
import sys

# Create sample data
sample_audio = '/home/runner/work/training_gui/training_gui/backend/opensoundscape_sample_data/birds_10s.wav'

# Check if sample file exists, otherwise use placeholder
if not Path(sample_audio).exists():
    print(f"Sample audio file not found: {sample_audio}")
    print("Will use placeholder data for testing rendering")
    sample_audio = '/path/to/sample.wav'  # Placeholder

# Create sample detection CSV
sample_data = pd.DataFrame({
    'file': [sample_audio] * 5,
    'start_time': [0.0, 1.0, 2.0, 3.0, 4.0],
    'end_time': [1.0, 2.0, 3.0, 4.0, 5.0],
    'annotation': ['unlabeled'] * 5,
    'labels': [''] * 5,
    'comments': [''] * 5
})

# Save to CSV
csv_path = '/tmp/test_review_data.csv'
sample_data.to_csv(csv_path, index=False)
print(f"Created sample CSV: {csv_path}")
print(f"Rows: {len(sample_data)}")
print("\nSample data:")
print(sample_data)

print("\nTo test:")
print(f"1. Load CSV in Review tab: {csv_path}")
print(f"2. Click 'Load' button on any clip card")
print(f"3. Verify spectrogram renders")
print(f"4. Click spectrogram to play audio")
print(f"5. Click annotation buttons to change labels")
