#!/usr/bin/env python3
"""
Load and process score files for data exploration
"""

import argparse
import json
import pandas as pd
import numpy as np
import sys
import os

def count_csv_rows(file_path):
    """Count rows in CSV file without loading all data"""
    try:
        # Read just to get the shape quickly
        df_sample = pd.read_csv(file_path, nrows=1)
        # Count total lines in file (subtract 1 for header)
        with open(file_path, 'r') as f:
            total_lines = sum(1 for _ in f) - 1
        return total_lines
    except Exception:
        return 0

def load_scores(file_path, max_rows=None):
    """Load scores from CSV file"""
    try:
        # Try to load as multi-index (opensoundscape format)
        df = pd.read_csv(file_path, index_col=[0, 1, 2])
        
        # If max_rows specified and data is too large, randomly sample
        if max_rows and len(df) > max_rows:
            df = df.sample(n=max_rows, random_state=42)
        
        # Convert to format suitable for frontend
        scores = {}
        for column in df.columns:
            scores[column] = df[column].values.tolist()
        
        # Calculate min and max scores
        all_scores = df.values.flatten()
        min_score = float(np.min(all_scores))
        max_score = float(np.max(all_scores))
        
        # Get file info
        file_info = []
        for idx in df.index:
            file_info.append({
                'file': idx[0],
                'start_time': idx[1],
                'end_time': idx[2]
            })
        
        result = {
            'scores': scores,
            'min_score': min_score,
            'max_score': max_score,
            'file_info': file_info,
            'shape': list(df.shape)
        }
        
        return result
        
    except Exception as e:
        # Try to load as simple CSV
        try:
            df = pd.read_csv(file_path)
            
            # If max_rows specified and data is too large, randomly sample
            if max_rows and len(df) > max_rows:
                df = df.sample(n=max_rows, random_state=42)
            
            # Assume first column is file path, rest are scores
            if 'file' in df.columns:
                file_col = 'file'
            else:
                file_col = df.columns[0]
            
            score_columns = [col for col in df.columns if col != file_col]
            
            scores = {}
            for column in score_columns:
                scores[column] = df[column].values.tolist()
            
            all_scores = df[score_columns].values.flatten()
            min_score = float(np.min(all_scores))
            max_score = float(np.max(all_scores))
            
            file_info = []
            for _, row in df.iterrows():
                file_info.append({
                    'file': row[file_col],
                    'start_time': 0,
                    'end_time': 0
                })
            
            result = {
                'scores': scores,
                'min_score': min_score,
                'max_score': max_score,
                'file_info': file_info,
                'shape': list(df.shape)
            }
            
            return result
            
        except Exception as e2:
            raise Exception(f"Could not load scores file: {e2}")

def main():
    parser = argparse.ArgumentParser(description='Load scores file')
    parser.add_argument('file_path', help='Path to scores CSV file')
    parser.add_argument('--max-rows', type=int, help='Maximum number of rows to load (random sample if exceeded)')
    parser.add_argument('--count-only', action='store_true', help='Only count rows, do not load data')
    
    args = parser.parse_args()
    
    try:
        if not os.path.exists(args.file_path):
            raise FileNotFoundError(f"File not found: {args.file_path}")
        
        if args.count_only:
            row_count = count_csv_rows(args.file_path)
            result = {'row_count': row_count}
        else:
            result = load_scores(args.file_path, max_rows=args.max_rows)
        
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            'error': str(e),
            'scores': {},
            'min_score': 0,
            'max_score': 1,
            'file_info': [],
            'shape': [0, 0]
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()