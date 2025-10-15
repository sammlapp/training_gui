"""Review Tab - Annotation review interface"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from nicegui import ui
from .audio_utils import create_spectrogram


class FocusViewClip:
    """Focus view component for reviewing a single clip"""
    
    def __init__(self, clip_data: dict, on_annotation_change, on_next, on_prev):
        self.clip_data = clip_data
        self.on_annotation_change = on_annotation_change
        self.on_next = on_next
        self.on_prev = on_prev
        self.spectrogram_base64 = None
        self.audio_base64 = None
        self.is_playing = False
        self.annotation = clip_data.get('annotation', 'unlabeled')
        
    def render(self):
        """Render the focus view clip"""
        with ui.column().classes('w-full items-center'):
            # File info
            ui.label(f"File: {Path(self.clip_data.get('file', 'Unknown')).name}").classes('text-h6 mb-2')
            ui.label(
                f"Time: {self.clip_data.get('start_time', 0):.2f}s - {self.clip_data.get('end_time', 0):.2f}s"
            ).classes('text-caption mb-4')
            
            # Load clip button or spectrogram
            if not self.spectrogram_base64:
                ui.button('Load Clip', icon='play_circle', on_click=self.load_clip).classes('mb-4')
            else:
                # Spectrogram
                with ui.card().classes('mb-4'):
                    ui.image(f'data:image/png;base64,{self.spectrogram_base64}').props('fit=contain').style('max-width: 900px; max-height: 400px')
                
                # Audio controls
                with ui.row().classes('items-center gap-4 mb-4'):
                    ui.button(
                        icon='play_arrow' if not self.is_playing else 'pause',
                        on_click=self.toggle_play
                    ).props('round')
                    ui.button(icon='replay', on_click=self.restart_audio).props('round flat')
                    
                    # Hidden audio element
                    ui.html(f'''
                        <audio id="audio_focus_{id(self)}" src="data:audio/wav;base64,{self.audio_base64}">
                        </audio>
                    ''')
            
            # Annotation controls
            with ui.card().classes('w-full p-4 mb-4'):
                ui.label('Annotation').classes('text-h6 mb-2')
                
                with ui.row().classes('w-full gap-2 justify-center'):
                    ui.button('Yes', icon='check', on_click=lambda: self.set_annotation('yes')).props('color=positive')
                    ui.button('No', icon='close', on_click=lambda: self.set_annotation('no')).props('color=negative')
                    ui.button('Uncertain', icon='help', on_click=lambda: self.set_annotation('uncertain')).props('color=warning')
                    ui.button('Unlabeled', icon='remove', on_click=lambda: self.set_annotation('unlabeled'))
                
                ui.label().classes('text-caption mt-2').bind_text_from(
                    self, 'annotation',
                    lambda a: f'Current: {a.upper()}'
                )
            
            # Navigation controls
            with ui.row().classes('gap-4 mb-4'):
                ui.button('Previous (J)', icon='navigate_before', on_click=self.on_prev)
                ui.button('Next (K)', icon='navigate_next', on_click=self.on_next).props('color=primary')
            
            # Keyboard shortcuts help
            with ui.card().classes('w-full p-4'):
                ui.label('Keyboard Shortcuts').classes('text-caption font-bold mb-2')
                ui.markdown('''
- **A**: Mark as Yes
- **S**: Mark as No
- **D**: Mark as Uncertain
- **F**: Mark as Unlabeled
- **Space**: Play/Pause
- **J**: Previous clip
- **K**: Next clip
                ''').classes('text-caption')
    
    def load_clip(self):
        """Load the audio clip and spectrogram"""
        try:
            spec_base64, audio_base64, sr = create_spectrogram(
                self.clip_data.get('file'),
                self.clip_data.get('start_time', 0),
                self.clip_data.get('end_time', 3),
                settings={'image_width': 900, 'image_height': 400}
            )
            
            self.spectrogram_base64 = spec_base64
            self.audio_base64 = audio_base64
            
            ui.notify('Clip loaded', type='positive')
            
        except Exception as e:
            ui.notify(f'Error loading clip: {e}', type='negative')
    
    def toggle_play(self):
        """Toggle audio playback"""
        self.is_playing = not self.is_playing
        if self.is_playing:
            ui.run_javascript(f'document.getElementById("audio_focus_{id(self)}").play()')
        else:
            ui.run_javascript(f'document.getElementById("audio_focus_{id(self)}").pause()')
    
    def restart_audio(self):
        """Restart audio playback"""
        ui.run_javascript(f'''
            var audio = document.getElementById("audio_focus_{id(self)}");
            audio.currentTime = 0;
            audio.play();
        ''')
        self.is_playing = True
    
    def set_annotation(self, value: str):
        """Set annotation value"""
        self.annotation = value
        if self.on_annotation_change:
            self.on_annotation_change(value)


class ReviewTab:
    """Review tab for annotation review"""
    
    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.current_index = 0
        self.review_mode = 'binary'
        self.focus_view = None
        self.annotations_changed = False
        
    def render(self):
        """Render the review tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Review Annotations').classes('text-h4 mb-4')
            
            # File loading section
            with ui.card().classes('w-full mb-4'):
                ui.label('Load Annotation Data').classes('text-h6 mb-2')
                with ui.row().classes('w-full gap-2'):
                    ui.input(
                        label='CSV File Path',
                        placeholder='Enter path to CSV file with annotations...'
                    ).classes('flex-grow').on('change', self.load_annotation_file)
                    ui.button('Load', icon='upload_file')
            
            # Settings
            with ui.card().classes('w-full mb-4').bind_visibility_from(self, 'data', lambda d: d is not None):
                ui.label('Settings').classes('text-h6 mb-2')
                with ui.row().classes('w-full gap-4'):
                    ui.select(
                        ['binary', 'multiclass'],
                        label='Review Mode',
                        value='binary'
                    ).bind_value(self, 'review_mode')
            
            # Progress indicator
            with ui.row().classes('w-full items-center gap-4 mb-4').bind_visibility_from(self, 'data', lambda d: d is not None):
                ui.label().bind_text_from(
                    self, 'current_index',
                    lambda i: f'Clip {i + 1} of {len(self.data) if self.data is not None else 0}'
                ).classes('text-h6')
                ui.space()
                ui.button('Save Annotations', icon='save', on_click=self.save_annotations).props('color=primary')
            
            # Focus view container
            with ui.column().classes('w-full items-center') as self.focus_container:
                ui.label('Load a file to start reviewing').classes('text-caption text-gray-500')
    
    def load_annotation_file(self, e):
        """Load annotation file"""
        file_path = e.sender.value if hasattr(e, 'sender') else e.args
        
        try:
            self.data = pd.read_csv(file_path)
            ui.notify(f'Loaded {len(self.data)} clips for review', type='positive')
            
            # Initialize annotations if not present
            if 'annotation' not in self.data.columns:
                self.data['annotation'] = 'unlabeled'
            
            # Start with first clip
            self.current_index = 0
            self.show_current_clip()
            
        except Exception as e:
            ui.notify(f'Error loading file: {e}', type='negative')
    
    def show_current_clip(self):
        """Show the current clip in focus view"""
        if self.data is None or len(self.data) == 0:
            return
        
        # Get current clip data
        row = self.data.iloc[self.current_index]
        clip_data = {
            'file': row.get('file', ''),
            'start_time': row.get('start_time', 0),
            'end_time': row.get('end_time', 3),
            'annotation': row.get('annotation', 'unlabeled'),
            'species': row.get('species', row.get('class', 'Unknown'))
        }
        
        # Clear and recreate focus view
        self.focus_container.clear()
        
        with self.focus_container:
            self.focus_view = FocusViewClip(
                clip_data,
                on_annotation_change=self.update_annotation,
                on_next=self.next_clip,
                on_prev=self.prev_clip
            )
            self.focus_view.render()
    
    def update_annotation(self, value: str):
        """Update annotation for current clip"""
        if self.data is not None:
            self.data.at[self.current_index, 'annotation'] = value
            self.annotations_changed = True
    
    def next_clip(self):
        """Go to next clip"""
        if self.data is not None and self.current_index < len(self.data) - 1:
            self.current_index += 1
            self.show_current_clip()
    
    def prev_clip(self):
        """Go to previous clip"""
        if self.data is not None and self.current_index > 0:
            self.current_index -= 1
            self.show_current_clip()
    
    def save_annotations(self):
        """Save annotations to file"""
        if self.data is None:
            return
        
        # Save to same file with _annotated suffix
        output_path = Path('annotations_reviewed.csv')
        self.data.to_csv(output_path, index=False)
        ui.notify(f'Annotations saved to {output_path}', type='positive')
        self.annotations_changed = False
