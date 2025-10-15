"""Explore Tab - Data exploration and visualization"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict
from nicegui import ui
from .audio_utils import create_spectrogram


class AudioClipViewer:
    """Component for displaying audio clip with spectrogram"""
    
    def __init__(self, clip_data: dict):
        self.clip_data = clip_data
        self.spectrogram_base64 = None
        self.audio_base64 = None
        self.is_playing = False
        self.audio_element = None
        
    def render(self):
        """Render the audio clip viewer"""
        with ui.card().classes('w-full mb-2'):
            # Header with file info
            with ui.row().classes('w-full items-center justify-between mb-2'):
                ui.label(f"File: {Path(self.clip_data.get('file', 'Unknown')).name}").classes('text-caption')
                ui.label(f"Time: {self.clip_data.get('start_time', 0):.2f}s - {self.clip_data.get('end_time', 0):.2f}s").classes('text-caption')
            
            # Spectrogram and audio
            with ui.column().classes('w-full'):
                # Load button
                if not self.spectrogram_base64:
                    ui.button('Load Clip', icon='play_circle', on_click=self.load_clip)
                else:
                    # Spectrogram image
                    ui.image(f'data:image/png;base64,{self.spectrogram_base64}').classes('w-full')
                    
                    # Audio player
                    if self.audio_base64:
                        with ui.row().classes('w-full items-center gap-2'):
                            ui.button(
                                icon='play_arrow' if not self.is_playing else 'pause',
                                on_click=self.toggle_play
                            ).props('flat round')
                            
                            # HTML audio element (hidden)
                            ui.html(f'''
                                <audio id="audio_{id(self)}" src="data:audio/wav;base64,{self.audio_base64}">
                                </audio>
                            ''')
    
    def load_clip(self):
        """Load and display the audio clip"""
        try:
            file_path = self.clip_data.get('file')
            start_time = self.clip_data.get('start_time', 0)
            end_time = self.clip_data.get('end_time', 3)
            
            # Create spectrogram and audio
            spec_base64, audio_base64, sr = create_spectrogram(
                file_path,
                start_time,
                end_time
            )
            
            self.spectrogram_base64 = spec_base64
            self.audio_base64 = audio_base64
            
            # Re-render
            ui.notify('Clip loaded', type='positive')
        except Exception as e:
            ui.notify(f'Error loading clip: {e}', type='negative')
    
    def toggle_play(self):
        """Toggle audio playback"""
        self.is_playing = not self.is_playing
        # Use JavaScript to control audio
        if self.is_playing:
            ui.run_javascript(f'document.getElementById("audio_{id(self)}").play()')
        else:
            ui.run_javascript(f'document.getElementById("audio_{id(self)}").pause()')


class ExploreTab:
    """Explore tab for data visualization"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.selected_file = ''
        self.score_threshold = 0.1
        self.selected_species = []
        self.available_species = []
        self.clips_to_display = []
        
    def render(self):
        """Render the explore tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Explore Data').classes('text-h4 mb-4')
            
            # File loading section
            with ui.card().classes('w-full mb-4'):
                ui.label('Load Detection Results').classes('text-h6 mb-2')
                with ui.row().classes('w-full gap-2'):
                    ui.input(
                        label='CSV File Path',
                        placeholder='Enter path to CSV file...'
                    ).classes('flex-grow').on('change', self.load_csv_file)
                    ui.button('Load', icon='upload_file', on_click=lambda: ui.notify('Enter a file path'))
            
            # Data summary
            with ui.card().classes('w-full mb-4').bind_visibility_from(self, 'data', lambda d: d is not None):
                ui.label('Data Summary').classes('text-h6 mb-2')
                with ui.grid(columns=4).classes('w-full gap-4'):
                    with ui.column():
                        ui.label('Total Detections')
                        ui.label().classes('text-h5').bind_text_from(
                            self, 'data',
                            lambda d: str(len(d)) if d is not None else '0'
                        )
                    
                    with ui.column():
                        ui.label('Unique Files')
                        ui.label().classes('text-h5').bind_text_from(
                            self, 'data',
                            lambda d: str(d['file'].nunique()) if d is not None and 'file' in d.columns else '0'
                        )
                    
                    with ui.column():
                        ui.label('Species Found')
                        ui.label().classes('text-h5').bind_text_from(
                            self, 'available_species',
                            lambda s: str(len(s))
                        )
                    
                    with ui.column():
                        ui.label('Filtered Results')
                        ui.label().classes('text-h5').bind_text_from(
                            self, 'clips_to_display',
                            lambda c: str(len(c))
                        )
            
            # Filters
            with ui.card().classes('w-full mb-4').bind_visibility_from(self, 'data', lambda d: d is not None):
                ui.label('Filters').classes('text-h6 mb-2')
                
                # Score threshold
                with ui.row().classes('w-full items-center gap-4 mb-4'):
                    ui.label('Score Threshold:')
                    ui.slider(min=0, max=1, step=0.01, value=0.1).classes('flex-grow').bind_value(
                        self, 'score_threshold'
                    ).on('change', self.apply_filters)
                    ui.label().bind_text_from(self, 'score_threshold', lambda t: f'{t:.2f}')
                
                # Species selection
                with ui.row().classes('w-full gap-2'):
                    ui.label('Species:')
                    ui.select(
                        options=[],
                        multiple=True,
                        value=[]
                    ).classes('flex-grow').bind_value(self, 'selected_species').bind_options_from(
                        self, 'available_species'
                    ).on('update:model-value', self.apply_filters)
                
                ui.button('Apply Filters', icon='filter_alt', on_click=self.apply_filters)
            
            # Results display
            with ui.column().classes('w-full').bind_visibility_from(self, 'clips_to_display', lambda c: len(c) > 0):
                ui.label('Detection Results').classes('text-h6 mb-2')
                
                # Clips container
                with ui.column().classes('w-full gap-2') as self.clips_container:
                    pass
    
    def load_csv_file(self, e):
        """Load CSV file"""
        file_path = e.sender.value if hasattr(e, 'sender') else e.args
        
        try:
            # Load CSV
            self.data = pd.read_csv(file_path)
            ui.notify(f'Loaded {len(self.data)} detections', type='positive')
            
            # Extract available species
            if 'species' in self.data.columns:
                self.available_species = sorted(self.data['species'].unique().tolist())
            elif 'class' in self.data.columns:
                self.available_species = sorted(self.data['class'].unique().tolist())
            
            # Apply initial filters
            self.apply_filters()
            
        except Exception as e:
            ui.notify(f'Error loading CSV: {e}', type='negative')
            self.data = None
    
    def apply_filters(self, e=None):
        """Apply filters to the data"""
        if self.data is None:
            return
        
        # Filter by score threshold
        filtered = self.data.copy()
        if 'score' in filtered.columns:
            filtered = filtered[filtered['score'] >= self.score_threshold]
        
        # Filter by selected species
        if self.selected_species and len(self.selected_species) > 0:
            if 'species' in filtered.columns:
                filtered = filtered[filtered['species'].isin(self.selected_species)]
            elif 'class' in filtered.columns:
                filtered = filtered[filtered['class'].isin(self.selected_species)]
        
        # Convert to clip data
        self.clips_to_display = []
        for idx, row in filtered.head(20).iterrows():  # Limit to first 20 for performance
            clip = {
                'file': row.get('file', ''),
                'start_time': row.get('start_time', 0),
                'end_time': row.get('end_time', 3),
                'species': row.get('species', row.get('class', 'Unknown')),
                'score': row.get('score', 0)
            }
            self.clips_to_display.append(clip)
        
        # Update display
        self.update_clips_display()
        
        ui.notify(f'Showing {len(self.clips_to_display)} detections', type='info')
    
    def update_clips_display(self):
        """Update the clips display"""
        self.clips_container.clear()
        
        with self.clips_container:
            if len(self.clips_to_display) == 0:
                ui.label('No detections match the current filters').classes('text-caption text-gray-500')
            else:
                for clip_data in self.clips_to_display:
                    viewer = AudioClipViewer(clip_data)
                    viewer.render()
