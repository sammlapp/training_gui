"""Help Tab - Help and documentation"""

from nicegui import ui


class HelpTab:
    """Help tab with documentation"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render the help tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Help & Documentation').classes('text-h4 mb-4')
            
            with ui.card().classes('w-full mb-4'):
                ui.label('Quick Start').classes('text-h6 mb-2')
                ui.markdown('''
## Getting Started

1. **Inference Tab**: Run pre-trained models on your audio files
2. **Training Tab**: Train custom models with your own data
3. **Extraction Tab**: Extract audio clips from detections
4. **Explore Tab**: Visualize and explore detection results
5. **Review Tab**: Review and annotate detections

## Features

- Species detection using bioacoustics model zoo
- Custom model training with active learning
- Interactive spectrogram visualization
- Audio playback with progress tracking
- Batch processing capabilities

## Keyboard Shortcuts

### Review Tab
- **Space**: Play/Pause audio
- **J**: Previous clip
- **K**: Next clip
- **A**: Mark as "Yes" (binary mode)
- **S**: Mark as "No" (binary mode)
- **D**: Mark as "Uncertain"
- **F**: Mark as "Unlabeled"
                ''')
            
            with ui.card().classes('w-full'):
                ui.label('About').classes('text-h6 mb-2')
                ui.markdown('''
**Bioacoustics Training GUI**

A cross-platform application for bioacoustics machine learning with active learning capabilities.

Built with NiceGUI and Python for seamless integration with ML workflows.
                ''')
