"""Inference Tab - Model inference interface"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional
from nicegui import ui, events
import uuid


class InferenceTab:
    """Inference tab for running model predictions"""
    
    def __init__(self):
        self.task_name = ''
        self.file_selection_mode = 'files'
        self.selected_files = []
        self.selected_folder = None
        self.selected_extensions = ['wav', 'mp3', 'flac']
        self.file_count = 0
        self.config = {
            'model_source': 'bmz',
            'model': 'BirdSetEfficientNetB1',
            'overlap': 0.0,
            'batch_size': 1,
            'worker_count': 1,
            'output_dir': '',
            'sparse_outputs_enabled': False,
            'sparse_save_threshold': -3.0,
            'split_by_subfolder': False,
            'use_custom_python_env': False,
            'custom_python_env_path': '',
            'testing_mode_enabled': False,
            'subset_size': 10
        }
        self.running_tasks = {}
        
    def render(self):
        """Render the inference tab UI"""
        with ui.column().classes('w-full p-4'):
            ui.label('Model Inference').classes('text-h4 mb-4')
            
            # Task name
            with ui.row().classes('w-full items-center gap-4 mb-4'):
                ui.label('Task Name:').classes('text-bold')
                ui.input(placeholder='Enter task name...').classes('flex-grow').bind_value(self, 'task_name')
            
            # File selection mode
            with ui.card().classes('w-full mb-4'):
                ui.label('File Selection').classes('text-h6 mb-2')
                
                with ui.row().classes('w-full gap-2 mb-2'):
                    ui.radio(
                        ['files', 'folder', 'patterns'],
                        value='files',
                        on_change=lambda e: setattr(self, 'file_selection_mode', e.value)
                    ).props('inline').bind_value(self, 'file_selection_mode')
                
                # File selection buttons
                with ui.row().classes('w-full gap-2'):
                    # File path input (manual entry)
                    ui.input(
                        label='File/Folder Path',
                        placeholder='Enter path to files or folder...'
                    ).classes('flex-grow').on('change', self.on_path_change)
                    
                    # For folder mode, show extension checkboxes
                    if self.file_selection_mode == 'folder':
                        with ui.row().classes('gap-2 ml-4'):
                            for ext in ['wav', 'mp3', 'flac']:
                                ui.checkbox(ext.upper(), value=ext in self.selected_extensions).on(
                                    'update:model-value',
                                    lambda e, ext=ext: self.toggle_extension(ext, e.args)
                                )
                
                # File count display
                with ui.row().classes('w-full mt-2'):
                    ui.label().bind_text_from(self, 'file_count', lambda c: f'Files found: {c}')
            
            # Model configuration
            with ui.card().classes('w-full mb-4'):
                ui.label('Model Configuration').classes('text-h6 mb-2')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    # Model source
                    with ui.column():
                        ui.label('Model Source:')
                        ui.select(
                            ['bmz', 'local', 'custom'],
                            value='bmz'
                        ).bind_value(self.config, 'model_source')
                    
                    # Model selection
                    with ui.column():
                        ui.label('Model:')
                        ui.select(
                            [
                                'BirdSetEfficientNetB1',
                                'BirdNET',
                                'Perch',
                                'HawkEars',
                                'RanaSierraeCNN'
                            ],
                            value='BirdSetEfficientNetB1'
                        ).bind_value(self.config, 'model')
                    
                    # Overlap
                    with ui.column():
                        ui.label('Overlap:')
                        ui.number(
                            value=0.0,
                            min=0.0,
                            max=0.9,
                            step=0.1
                        ).bind_value(self.config, 'overlap')
                    
                    # Batch size
                    with ui.column():
                        ui.label('Batch Size:')
                        ui.number(
                            value=1,
                            min=1,
                            max=64,
                            step=1
                        ).bind_value(self.config, 'batch_size')
                    
                    # Worker count
                    with ui.column():
                        ui.label('Worker Count:')
                        ui.number(
                            value=1,
                            min=1,
                            max=16,
                            step=1
                        ).bind_value(self.config, 'worker_count')
                    
                    # Output directory
                    with ui.column().classes('col-span-2'):
                        ui.label('Output Directory:')
                        with ui.row().classes('w-full gap-2'):
                            ui.input(placeholder='Select output directory...').classes('flex-grow').bind_value(self.config, 'output_dir')
                            ui.button('Browse', icon='folder', on_click=self.select_output_dir)
            
            # Advanced settings
            with ui.expansion('Advanced Settings').classes('w-full mb-4'):
                with ui.column().classes('w-full gap-2 p-4'):
                    ui.checkbox('Sparse Outputs Enabled').bind_value(self.config, 'sparse_outputs_enabled')
                    ui.number(
                        label='Sparse Save Threshold',
                        value=-3.0,
                        step=0.1
                    ).bind_value(self.config, 'sparse_save_threshold')
                    ui.checkbox('Split by Subfolder').bind_value(self.config, 'split_by_subfolder')
                    ui.checkbox('Testing Mode (Limit Files)').bind_value(self.config, 'testing_mode_enabled')
                    ui.number(
                        label='Subset Size (Testing Mode)',
                        value=10,
                        min=1,
                        max=1000,
                        step=1
                    ).bind_value(self.config, 'subset_size')
            
            # Action buttons
            with ui.row().classes('w-full gap-2 mb-4'):
                ui.button('Create Task', icon='add', on_click=self.create_task)
                ui.button('Create and Run', icon='play_arrow', on_click=self.create_and_run_task).props('color=primary')
                ui.button('Save Config', icon='save', on_click=self.save_config)
                ui.button('Load Config', icon='folder_open', on_click=self.load_config)
            
            # Task monitor
            with ui.card().classes('w-full'):
                ui.label('Running Tasks').classes('text-h6 mb-2')
                with ui.column().classes('w-full gap-2') as self.task_container:
                    ui.label('No active tasks').classes('text-caption text-gray-500')
    
    def toggle_extension(self, ext: str, checked: bool):
        """Toggle extension selection"""
        if checked and ext not in self.selected_extensions:
            self.selected_extensions.append(ext)
        elif not checked and ext in self.selected_extensions:
            self.selected_extensions.remove(ext)
    
    def on_path_change(self, e):
        """Handle path input change"""
        path = e.args if isinstance(e.args, str) else e.sender.value
        if not path:
            return
        
        path_obj = Path(path)
        if self.file_selection_mode == 'files':
            # Check if it's a file
            if path_obj.is_file():
                self.selected_files = [str(path_obj)]
                self.file_count = 1
                ui.notify(f'Selected 1 file')
            else:
                ui.notify('Invalid file path', type='warning')
        elif self.file_selection_mode == 'folder':
            # Check if it's a folder
            if path_obj.is_dir():
                self.selected_folder = str(path_obj)
                self.count_files_in_folder_sync()
                ui.notify(f'Selected folder with {self.file_count} files')
            else:
                ui.notify('Invalid folder path', type='warning')
    
    def count_files_in_folder_sync(self):
        """Count files in selected folder with selected extensions"""
        if not self.selected_folder:
            return
        
        count = 0
        folder_path = Path(self.selected_folder)
        for ext in self.selected_extensions:
            count += len(list(folder_path.rglob(f'*.{ext}')))
            count += len(list(folder_path.rglob(f'*.{ext.upper()}')))
        
        self.file_count = count
    
    def find_files_from_patterns(self):
        """Find files from glob patterns"""
        ui.notify('Pattern matching not yet implemented')
    
    def select_output_dir(self, e):
        """Handle output directory input"""
        path = e.sender.value
        if path and Path(path).is_dir():
            self.config['output_dir'] = path
            ui.notify('Output directory set')
        else:
            ui.notify('Invalid directory path', type='warning')
    
    def create_task(self):
        """Create inference task"""
        if not self.task_name:
            ui.notify('Please enter a task name', type='warning')
            return
        
        if self.file_count == 0:
            ui.notify('Please select files first', type='warning')
            return
        
        ui.notify(f'Task "{self.task_name}" created', type='positive')
    
    def create_and_run_task(self):
        """Create and run inference task"""
        self.create_task()
        # TODO: Implement task execution
        ui.notify('Starting inference...', type='info')
    
    def save_config(self):
        """Save configuration to file"""
        # For now, just save to default location
        config_path = Path('configs/inference_config.json')
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        ui.notify(f'Configuration saved to {config_path}', type='positive')
    
    def load_config(self):
        """Load configuration from file"""
        config_path = Path('configs/inference_config.json')
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            ui.notify('Configuration loaded', type='positive')
        else:
            ui.notify('No configuration file found', type='warning')
