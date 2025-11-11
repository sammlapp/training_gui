"""Extraction Tab - Audio extraction interface"""

from nicegui import ui


class ExtractionTab:
    """Extraction tab for extracting audio clips"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render the extraction tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Audio Extraction').classes('text-h4 mb-4')
            ui.label('Extraction interface will be implemented here').classes('text-caption')
            
            # Placeholder content
            with ui.card().classes('w-full'):
                ui.label('Coming soon...').classes('text-h6')
