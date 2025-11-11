# Testing Instructions for NiceGUI Implementation

## Quick Start Test

1. **Install Dependencies**
   ```bash
   pip install -r requirements-nicegui.txt
   ```

2. **Run the Application**
   ```bash
   python3 app.py
   ```

3. **Access the Application**
   - Open your browser to http://localhost:8080
   - You should see the Bioacoustics Training GUI with tab navigation

## Testing Each Tab

### 1. Help Tab
- Navigate to the Help tab
- Verify documentation is displayed
- Check that keyboard shortcuts are listed

### 2. Inference Tab
- Enter a task name
- Select file/folder mode
- Enter a valid audio file path (e.g., `/path/to/audio.wav`)
- Configure model settings
- Click "Create Task"
- Verify notification appears

### 3. Explore Tab
- Navigate to Explore tab
- Enter path to CSV file: `test_data/sample_detections.csv`
- Click in the input field and press Enter
- Verify data summary appears
- Adjust score threshold slider
- Select species from dropdown
- Click "Apply Filters"
- Click "Load Clip" on a detection
- Verify spectrogram appears
- Click play button to test audio

### 4. Review Tab
- Navigate to Review tab  
- Enter path to CSV file with annotations
- File should have columns: `file`, `start_time`, `end_time`, `species`, `annotation`
- Click "Load Clip" on the displayed clip
- Verify spectrogram loads
- Click annotation buttons (Yes/No/Uncertain)
- Navigate with Previous/Next buttons
- Click "Save Annotations"
- Verify file is saved

## Unit Tests

### Test Audio Processing
```bash
python3 test_audio_utils.py
```

Expected output:
- Placeholder generation: ✓
- Test audio creation: ✓
- Spectrogram generation: ✓
- Audio base64 encoding: ✓

## Known Limitations

1. **File Selection**: Uses text input fields instead of native file dialogs (web-based limitation)
2. **Training/Extraction Tabs**: Stub implementations (coming soon)
3. **Keyboard Shortcuts**: Review tab shortcuts guide shown but not yet implemented
4. **Task Monitoring**: Task execution not yet integrated with backend scripts

## Verifying Core Features

### ✅ Working Features
- [x] Tab navigation
- [x] Form inputs and controls
- [x] Data binding and reactivity
- [x] CSV loading and parsing
- [x] Data filtering (threshold, species)
- [x] Spectrogram generation from audio files
- [x] Audio encoding to base64
- [x] HTML5 audio playback
- [x] Annotation state management
- [x] Configuration save/load
- [x] Notifications and user feedback

### 🚧 In Progress
- [ ] Backend task execution integration
- [ ] Keyboard event handlers
- [ ] Training tab implementation
- [ ] Extraction tab implementation
- [ ] Batch processing

## Testing with Real Data

To test with real bioacoustics data:

1. **Prepare Audio Files**
   - Place audio files (WAV, MP3, FLAC) in a test directory
   - Note the full paths

2. **Prepare Detection CSV**
   Create a CSV file with this structure:
   ```csv
   file,start_time,end_time,species,score
   /path/to/audio.wav,0.0,3.0,Species1,0.85
   /path/to/audio.wav,5.0,8.0,Species2,0.72
   ```

3. **Test Explore Tab**
   - Load the CSV file
   - Filter by score and species
   - Load clips and verify spectrograms
   - Test audio playback

4. **Test Review Tab**
   - Load the same CSV
   - Review clips in focus mode
   - Add annotations
   - Save and verify output file

## Troubleshooting

### Application won't start
- Check Python version (3.8+)
- Verify all dependencies installed: `pip list | grep nicegui`
- Check port 8080 is available: `lsof -i :8080`

### Blank page in browser
- Check browser console for errors (F12)
- Verify app is running: `curl http://localhost:8080`
- Try different browser

### Spectrogram won't load
- Verify audio file exists and is readable
- Check file format is supported (WAV, MP3, FLAC)
- Check console output for errors
- Run `test_audio_utils.py` to verify audio processing works

### CSV won't load
- Verify file exists and is readable
- Check CSV has required columns
- Verify file paths in CSV are absolute paths
- Check for special characters in file paths

## Performance Testing

For large datasets:
- Test with 100+ detections
- Monitor memory usage
- Check UI responsiveness
- Verify filtering performance

## Browser Compatibility

Tested browsers:
- Chrome/Chromium: ✓
- Firefox: ✓
- Safari: ✓
- Edge: ✓

## Reporting Issues

When reporting issues, include:
1. Browser and version
2. Python version
3. Error messages from console
4. Steps to reproduce
5. Sample data if relevant
