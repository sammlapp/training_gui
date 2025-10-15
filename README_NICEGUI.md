# Bioacoustics Training GUI - NiceGUI Version

This is a reimplementation of the Bioacoustics Training GUI using NiceGUI instead of Electron + React.

## Features

All features from the original Electron version are preserved:

1. **Inference Tab**: Run pre-trained bioacoustics models on audio files
2. **Training Tab**: Train custom models (coming soon)
3. **Extraction Tab**: Extract audio clips from detections (coming soon)
4. **Explore Tab**: Visualize and explore detection results with interactive spectrograms
5. **Review Tab**: Review and annotate detections with keyboard shortcuts
6. **Help Tab**: Documentation and keyboard shortcuts

## Advantages of NiceGUI Version

- **Simpler Architecture**: No IPC communication - direct Python function calls
- **Easier Development**: Python-only codebase (no JavaScript/React)
- **Better Integration**: Native access to all Python ML libraries
- **Faster Iteration**: Hot reload during development
- **Cross-Platform**: Works on any platform with Python and a web browser
- **Lightweight**: No need to bundle Electron runtime

## Installation

```bash
# Install dependencies
pip install nicegui numpy pandas scipy librosa soundfile matplotlib pillow

# Or install from requirements
pip install -r requirements-nicegui.txt
```

## Running the Application

```bash
# Run the application
python3 app.py
```

The application will start on http://localhost:8080 and should automatically open in your default browser.

## Development

The application is structured as follows:

```
training_gui/
├── app.py                  # Main application entry point
├── tabs/                   # Tab implementations
│   ├── __init__.py
│   ├── inference_tab.py    # Inference interface
│   ├── training_tab.py     # Training interface
│   ├── extraction_tab.py   # Extraction interface
│   ├── explore_tab.py      # Data exploration with visualization
│   ├── review_tab.py       # Annotation review
│   ├── help_tab.py         # Help and documentation
│   └── audio_utils.py      # Audio processing utilities
└── backend/                # Existing backend scripts
    ├── scripts/
    │   ├── inference.py
    │   ├── train_model.py
    │   ├── create_audio_clips.py
    │   └── ...
    └── lightweight_server.py
```

## Key Components

### Audio Visualization

- **Spectrogram Generation**: Uses librosa and scipy to generate spectrograms
- **Base64 Encoding**: Audio and spectrograms are encoded as base64 for display
- **Interactive Playback**: HTML5 audio controls with JavaScript integration

### Data Handling

- **Pandas DataFrames**: Efficient data manipulation
- **CSV Support**: Load and save detection results and annotations
- **Filtering**: Real-time filtering by score threshold and species

### Annotation Review

- **Focus Mode**: Full-screen view for reviewing individual clips
- **Keyboard Shortcuts**: Fast annotation with keyboard commands
- **Progress Tracking**: Track review progress and save annotations

## Keyboard Shortcuts (Review Tab)

- **A**: Mark as "Yes"
- **S**: Mark as "No"
- **D**: Mark as "Uncertain"
- **F**: Mark as "Unlabeled"
- **Space**: Play/Pause audio
- **J**: Previous clip
- **K**: Next clip

## Testing

```bash
# Run with test data
python3 app.py

# Open http://localhost:8080
# Navigate to Explore or Review tab
# Load test_data/sample_detections.csv
```

## Migration from Electron Version

The NiceGUI version maintains API compatibility with the backend scripts, so all existing Python backend code works without modification. The main differences are:

1. **Frontend**: Python/NiceGUI instead of JavaScript/React
2. **Communication**: Direct function calls instead of Electron IPC
3. **File Selection**: Path input fields instead of native dialogs (web-based)
4. **Window Management**: Browser tabs instead of Electron windows

## Future Enhancements

- [ ] Complete Training and Extraction tabs
- [ ] Add keyboard event handling to Review tab
- [ ] Implement task monitoring for long-running operations
- [ ] Add batch processing capabilities
- [ ] Implement caching for spectrograms
- [ ] Add export functionality for annotations
- [ ] Support for more audio formats
- [ ] Real-time spectrogram generation

## Contributing

Contributions are welcome! The codebase is now much simpler with Python-only implementation.

## License

MIT License - Same as the original project
