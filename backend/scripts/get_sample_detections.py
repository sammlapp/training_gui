#!/usr/bin/env python3
"""
Get sample detections for a specific species
"""

import argparse
import json
import pandas as pd
import numpy as np
import sys
import os
import tempfile
from pathlib import Path
import librosa
import soundfile as sf
from PIL import Image
import scipy.signal
from io import BytesIO
import base64

def spec_to_image(spectrogram, range=[-80, -20], colormap='greys_r', channels=3, shape=None):
    """Convert spectrogram to image array"""
    # Normalize to range
    spec_normalized = np.clip((spectrogram - range[0]) / (range[1] - range[0]), 0, 1)
    
    # Convert to 0-255 range
    spec_uint8 = (spec_normalized * 255).astype(np.uint8)
    
    # Flip vertically (frequency axis)
    spec_uint8 = np.flipud(spec_uint8)
    
    if channels == 3:
        # Convert to RGB by repeating grayscale values
        img_array = np.stack([spec_uint8, spec_uint8, spec_uint8], axis=-1)
    else:
        img_array = spec_uint8
    
    # Resize if shape specified
    if shape is not None:
        img = Image.fromarray(img_array)
        img = img.resize((shape[1], shape[0]), Image.Resampling.LANCZOS)
        img_array = np.array(img)
    
    return img_array

def create_spectrogram_for_detection(file_path, start_time, end_time):
    """Create spectrogram using librosa and PIL instead of opensoundscape"""
    try:
        # Load audio segment
        duration = end_time - start_time if end_time > start_time else None
        offset = start_time if start_time > 0 else 0
        
        samples, sr = librosa.load(file_path, sr=None, offset=offset, duration=duration)
        
        # Normalize audio
        if len(samples) > 0:
            samples = samples / (np.max(np.abs(samples)) + 1e-8)
        
        # Create spectrogram
        frequencies, times, spectrogram = scipy.signal.spectrogram(
            x=samples,
            fs=sr,
            nperseg=512,
            noverlap=256,  # 50% overlap
            nfft=512,
        )
        
        # Convert to decibels
        spectrogram = 10 * np.log10(
            spectrogram,
            where=spectrogram > 0,
            out=np.full(spectrogram.shape, -np.inf),
        )
        
        # Convert spectrogram to image array
        img_array = spec_to_image(
            spectrogram,
            range=[-80, -20],
            colormap='greys_r',
            channels=3,
            shape=(224, 224)
        )
        
        # Convert to PIL Image and save to temporary file
        pil_image = Image.fromarray(img_array, mode='RGB')
        
        # Save to temporary file
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, f"spec_{hash(file_path + str(start_time))}.png")
        pil_image.save(temp_file)
        
        return temp_file
        
    except Exception as e:
        print(f"Error creating spectrogram for {file_path}: {e}")
        return None

def get_sample_detections(score_data, species, score_range, num_samples=12):
    """Get sample detections for a species within score range"""
    try:
        if species not in score_data['scores']:
            raise ValueError(f"Species {species} not found in scores")
        
        scores = score_data['scores'][species]
        file_info = score_data['file_info']
        
        # Find detections within score range
        filtered_detections = []
        for i, score in enumerate(scores):
            if score_range[0] <= score <= score_range[1]:
                detection = {
                    'score': score,
                    'file_path': file_info[i]['file'],
                    'start_time': file_info[i]['start_time'],
                    'end_time': file_info[i]['end_time'],
                    'index': i
                }
                filtered_detections.append(detection)
        
        # Sort by score (highest first)
        filtered_detections.sort(key=lambda x: x['score'], reverse=True)
        
        # Take top samples
        sample_detections = filtered_detections[:num_samples]
        
        # Generate spectrograms for each sample
        for detection in sample_detections:
            try:
                # Create spectrogram using librosa and PIL
                audio_path = detection['file_path']
                start_time = detection['start_time']
                end_time = detection['end_time']
                
                # Handle full file case
                if start_time == 0 and end_time == 0:
                    # For full file, we'll load a segment from the beginning
                    end_time = start_time + 5.0  # 5 second segment
                
                # Create spectrogram
                temp_file = create_spectrogram_for_detection(audio_path, start_time, end_time)
                
                # Add info to detection
                detection['spectrogram_path'] = temp_file
                detection['file_name'] = os.path.basename(audio_path)
                
            except Exception as e:
                # If spectrogram generation fails, create placeholder
                detection['spectrogram_path'] = None
                detection['file_name'] = os.path.basename(detection['file_path'])
                detection['error'] = str(e)
        
        return sample_detections
        
    except Exception as e:
        raise Exception(f"Error getting sample detections: {e}")

def main():
    parser = argparse.ArgumentParser(description='Get sample detections')
    parser.add_argument('score_data', help='JSON score data')
    parser.add_argument('species', help='Species name')
    parser.add_argument('score_range', help='JSON score range [min, max]')
    parser.add_argument('num_samples', type=int, help='Number of samples to return')
    
    args = parser.parse_args()
    
    try:
        score_data = json.loads(args.score_data)
        score_range = json.loads(args.score_range)
        
        samples = get_sample_detections(score_data, args.species, score_range, args.num_samples)
        print(json.dumps(samples))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'samples': []
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()