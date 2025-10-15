"""Task Management for NiceGUI App"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from nicegui import ui


class TaskStatus:
    """Task status constants"""
    UNSTARTED = 'unstarted'
    QUEUED = 'queued'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class TaskManager:
    """Manages inference/training/extraction tasks"""
    
    def __init__(self, server_url='http://localhost:8000'):
        self.server_url = server_url
        self.tasks: Dict[str, dict] = {}
        self.current_task = None
        self.queue = []
        self.monitoring_task = None
        
    def create_task(self, task_type: str, config: dict, name: str = None) -> dict:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = {
            'id': task_id,
            'type': task_type,
            'name': name or f'{task_type}_task_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            'status': TaskStatus.UNSTARTED,
            'config': config,
            'created': datetime.now().isoformat(),
            'started': None,
            'completed': None,
            'progress': '',
            'result': None,
            'job_id': None,
            'system_pid': None
        }
        
        self.tasks[task_id] = task
        return task
    
    def get_task(self, task_id: str) -> Optional[dict]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[dict]:
        """Get all tasks sorted by creation date"""
        return sorted(self.tasks.values(), key=lambda t: t['created'], reverse=True)
    
    def update_task(self, task_id: str, updates: dict):
        """Update task fields"""
        if task_id in self.tasks:
            self.tasks[task_id].update(updates)
    
    async def queue_task(self, task_id: str):
        """Add task to queue and start processing"""
        task = self.get_task(task_id)
        if not task or task['status'] == TaskStatus.RUNNING:
            return False
        
        self.update_task(task_id, {
            'status': TaskStatus.QUEUED,
            'progress': 'Queued for execution'
        })
        
        if task_id not in self.queue:
            self.queue.append(task_id)
        
        # Start processing if no current task
        if not self.current_task:
            await self.process_queue()
        
        return True
    
    async def process_queue(self):
        """Process tasks in queue"""
        if self.current_task or not self.queue:
            return
        
        task_id = self.queue.pop(0)
        task = self.get_task(task_id)
        
        if not task or task['status'] == TaskStatus.CANCELLED:
            # Task was deleted or cancelled, process next
            await self.process_queue()
            return
        
        self.current_task = task_id
        await self.execute_task(task_id)
    
    async def execute_task(self, task_id: str):
        """Execute a task"""
        task = self.get_task(task_id)
        if not task:
            return
        
        try:
            self.update_task(task_id, {
                'status': TaskStatus.RUNNING,
                'started': datetime.now().isoformat(),
                'progress': f'Starting {task["type"]}...'
            })
            
            # Execute based on task type
            if task['type'] == 'inference':
                await self.run_inference(task)
            elif task['type'] == 'training':
                await self.run_training(task)
            elif task['type'] == 'extraction':
                await self.run_extraction(task)
            
        except Exception as e:
            self.update_task(task_id, {
                'status': TaskStatus.FAILED,
                'completed': datetime.now().isoformat(),
                'progress': 'Failed',
                'result': {'error': str(e)}
            })
        finally:
            self.current_task = None
            # Process next task
            await self.process_queue()
    
    async def run_inference(self, task: dict):
        """Run inference task"""
        config = task['config']
        
        # Create job folder name
        job_folder_name = f"{task['name']}_{task['id'][:8]}"
        job_folder = f"{config.get('output_dir', '/tmp')}/{job_folder_name}"
        
        # Prepare config for backend
        backend_config = {
            'model_source': config.get('model_source', 'bmz'),
            'model': config.get('model', 'BirdSetEfficientNetB1'),
            'files': config.get('files', []),
            'file_globbing_patterns': config.get('file_globbing_patterns', []),
            'file_list': config.get('file_list', ''),
            'output_dir': config.get('output_dir', ''),
            'sparse_save_threshold': config.get('sparse_save_threshold'),
            'job_folder': job_folder,
            'config_output_path': f'{job_folder}/{task["name"]}_config.json',
            'log_file_path': f'{job_folder}/inference_log.txt',
            'split_by_subfolder': config.get('split_by_subfolder', False),
            'subset_size': config.get('subset_size') if config.get('testing_mode_enabled') else None,
            'inference_settings': {
                'clip_overlap': config.get('overlap', 0.0),
                'batch_size': config.get('batch_size', 1),
                'num_workers': config.get('worker_count', 1)
            }
        }
        
        # Determine Python environment
        if config.get('use_custom_python_env') and config.get('custom_python_env_path'):
            python_env = config['custom_python_env_path']
        else:
            python_env = '/usr/bin/python3'  # Default system Python
        
        try:
            # Save config to temp file
            temp_config_path = f'/tmp/inference_config_{task["id"]}.json'
            Path(temp_config_path).write_text(json.dumps(backend_config, indent=2))
            
            # Start inference via backend server
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f'{self.server_url}/inference/run',
                    json={
                        'job_id': task['id'],
                        'config_path': temp_config_path,
                        'python_env_path': python_env
                    }
                )
                
                result = response.json()
                
                if result.get('status') == 'started':
                    self.update_task(task['id'], {
                        'job_id': result.get('job_id'),
                        'system_pid': result.get('system_pid'),
                        'progress': 'Inference running...'
                    })
                    
                    # Start monitoring
                    await self.monitor_task(task['id'], 'inference')
                else:
                    raise Exception(result.get('error', 'Failed to start inference'))
                    
        except Exception as e:
            self.update_task(task['id'], {
                'status': TaskStatus.FAILED,
                'completed': datetime.now().isoformat(),
                'progress': 'Failed',
                'result': {'error': str(e)}
            })
    
    async def run_training(self, task: dict):
        """Run training task"""
        # Similar to run_inference but for training
        ui.notify('Training not yet implemented', type='warning')
    
    async def run_extraction(self, task: dict):
        """Run extraction task"""
        # Similar to run_inference but for extraction
        ui.notify('Extraction not yet implemented', type='warning')
    
    async def monitor_task(self, task_id: str, task_type: str):
        """Monitor task status"""
        task = self.get_task(task_id)
        if not task or not task.get('job_id'):
            return
        
        endpoint = f'/{task_type}/status'
        max_attempts = 3600  # 1 hour max (checking every second)
        attempt = 0
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                while attempt < max_attempts:
                    if task['status'] in [TaskStatus.CANCELLED, TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        break
                    
                    try:
                        response = await client.get(
                            f'{self.server_url}{endpoint}',
                            params={'job_id': task['job_id']}
                        )
                        
                        result = response.json()
                        status = result.get('status')
                        
                        if status == 'running':
                            self.update_task(task_id, {
                                'progress': result.get('message', 'Running...')
                            })
                        elif status == 'completed':
                            self.update_task(task_id, {
                                'status': TaskStatus.COMPLETED,
                                'completed': datetime.now().isoformat(),
                                'progress': 'Completed successfully',
                                'result': result
                            })
                            break
                        elif status in ['failed', 'error']:
                            self.update_task(task_id, {
                                'status': TaskStatus.FAILED,
                                'completed': datetime.now().isoformat(),
                                'progress': 'Failed',
                                'result': result
                            })
                            break
                        elif status == 'cancelled':
                            self.update_task(task_id, {
                                'status': TaskStatus.CANCELLED,
                                'completed': datetime.now().isoformat(),
                                'progress': 'Cancelled',
                                'result': result
                            })
                            break
                        
                    except Exception as e:
                        print(f'Error monitoring task: {e}')
                    
                    await asyncio.sleep(1)
                    attempt += 1
                    
        except Exception as e:
            print(f'Monitor task error: {e}')
    
    async def cancel_task(self, task_id: str):
        """Cancel a running task"""
        task = self.get_task(task_id)
        if not task or not task.get('job_id'):
            return False
        
        try:
            endpoint = f'/{task["type"]}/cancel'
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f'{self.server_url}{endpoint}',
                    json={'job_id': task['job_id']}
                )
                
                result = response.json()
                if result.get('status') == 'cancelled':
                    self.update_task(task_id, {
                        'status': TaskStatus.CANCELLED,
                        'completed': datetime.now().isoformat(),
                        'progress': 'Cancelled by user'
                    })
                    return True
                    
        except Exception as e:
            print(f'Cancel task error: {e}')
        
        return False
    
    def delete_task(self, task_id: str):
        """Delete a task"""
        task = self.get_task(task_id)
        if task and task['status'] != TaskStatus.RUNNING:
            del self.tasks[task_id]
            if task_id in self.queue:
                self.queue.remove(task_id)
            return True
        return False


# Global task manager instance
task_manager = TaskManager()
