"""Training Tab - Model training interface"""

from nicegui import ui


class TrainingTab:
    """Training tab for training custom models"""
    
    def __init__(self):
        pass
    
    def render(self):
        """Render the training tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Model Training').classes('text-h4 mb-4')
            ui.label('Training interface will be implemented here').classes('text-caption')
            
            # Placeholder content
            with ui.card().classes('w-full'):
                ui.label('Coming soon...').classes('text-h6')
