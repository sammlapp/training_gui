# Backend API Endpoints Needed

The enhanced file selection system requires these new backend endpoints in `lightweight_server.py`:

## File Counting APIs

### 1. Count Files from Glob Patterns
```
POST /files/count-glob
Content-Type: application/json

{
  "patterns": [
    "/Users/name/data/project1/**/*.WAV",
    "/Users/name/data/project2/**/*.mp3"
  ]
}

Response:
{
  "status": "success",
  "count": 1234,
  "patterns_processed": 2
}
```

### 2. Count Files from File List
```
POST /files/count-list
Content-Type: application/json

{
  "file_path": "/path/to/filelist.txt"
}

Response:
{
  "status": "success", 
  "count": 567,
  "valid_files": 567,
  "invalid_files": 0
}
```

## Implementation Notes

- Use Python's `glob.glob()` with `recursive=True` for `**` patterns
- For file lists, read each line and validate file existence
- Filter for valid audio extensions: .wav, .WAV, .mp3, .MP3, .flac, .FLAC, .ogg, .m4a, .aac
- Return error status if patterns are invalid or file paths don't exist
- The inference script should handle these new config fields:
  - `file_globbing_patterns: str[]` - Array of glob patterns
  - `file_list: str` - Path to text file with one file per line
  - Legacy `files: str[]` still supported for individual file selection

## Config Structure Updates

The inference config JSON now supports these modes:

```json
{
  "model": "BirdNET",
  "files": [],  // Individual files (legacy)
  "file_globbing_patterns": [  // Glob patterns
    "/Users/name/data/**/*.wav"
  ],
  "file_list": "",  // Path to file list
  "output_file": "/path/to/output.csv",
  "inference_settings": {
    "clip_overlap": 0.0,
    "batch_size": 1,
    "num_workers": 1
  }
}
```

The inference script should use files in this priority:
1. `files` array (if not empty)
2. `file_globbing_patterns` (if not empty) 
3. `file_list` (if specified)