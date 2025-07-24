/**
 * Task Management System for Inference Tasks
 * Handles task CRUD operations, persistence, and queue management
 */

import { v4 as uuidv4 } from 'uuid';

export const TASK_STATUS = {
  UNSTARTED: 'unstarted',
  QUEUED: 'queued',
  RUNNING: 'running',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
};

class TaskManager {
  constructor() {
    this.tasks = new Map();
    this.queue = [];
    this.currentTask = null;
    this.listeners = new Set();
    this.loadTasks();
  }

  // Task CRUD Operations
  createTask(config, name = null) {
    const task = {
      id: uuidv4(),
      name: name || this.generateTaskName(config),
      status: TASK_STATUS.UNSTARTED,
      config: { ...config },
      created: Date.now(),
      started: null,
      completed: null,
      progress: '',
      result: null,
      processId: null
    };

    this.tasks.set(task.id, task);
    this.saveTasks();
    this.notifyListeners('taskCreated', task);
    return task;
  }

  getTask(taskId) {
    return this.tasks.get(taskId);
  }

  getAllTasks() {
    return Array.from(this.tasks.values()).sort((a, b) => b.created - a.created);
  }

  updateTask(taskId, updates) {
    const task = this.tasks.get(taskId);
    if (!task) return null;

    Object.assign(task, updates);
    this.tasks.set(taskId, task);
    this.saveTasks();
    this.notifyListeners('taskUpdated', task);
    return task;
  }

  deleteTask(taskId) {
    const task = this.tasks.get(taskId);
    if (!task) return false;

    // Can't delete running tasks
    if (task.status === TASK_STATUS.RUNNING) {
      return false;
    }

    // Remove from queue if present
    this.queue = this.queue.filter(id => id !== taskId);
    
    this.tasks.delete(taskId);
    this.saveTasks();
    this.notifyListeners('taskDeleted', { id: taskId });
    return true;
  }

  // Queue Management
  queueTask(taskId) {
    const task = this.getTask(taskId);
    if (!task || task.status === TASK_STATUS.RUNNING) return false;

    // Update task status to queued
    this.updateTask(taskId, { 
      status: TASK_STATUS.QUEUED,
      progress: 'Queued for execution'
    });

    // Add to queue if not already present
    if (!this.queue.includes(taskId)) {
      this.queue.push(taskId);
    }

    // Start immediately if no task is running
    if (!this.currentTask) {
      this.processQueue();
    }

    return true;
  }

  async processQueue() {
    if (this.currentTask || this.queue.length === 0) return;

    const taskId = this.queue.shift();
    const task = this.getTask(taskId);
    
    if (!task || task.status === TASK_STATUS.CANCELLED) {
      // Task was deleted or cancelled, process next
      this.processQueue();
      return;
    }

    this.currentTask = taskId;
    await this.executeTask(taskId);
  }

  async executeTask(taskId) {
    const task = this.getTask(taskId);
    if (!task) return;

    try {
      // Update task to running status
      this.updateTask(taskId, {
        status: TASK_STATUS.RUNNING,
        started: Date.now(),
        progress: 'Starting inference...'
      });

      // Execute the inference (this will be implemented separately)
      const result = await this.runInference(task);

      // Update task with results
      this.updateTask(taskId, {
        status: TASK_STATUS.COMPLETED,
        completed: Date.now(),
        progress: 'Completed successfully',
        result: result
      });

    } catch (error) {
      // Update task with error
      this.updateTask(taskId, {
        status: TASK_STATUS.FAILED,
        completed: Date.now(),
        progress: 'Failed',
        result: { error: error.message }
      });
    } finally {
      // Clear current task and process next in queue
      this.currentTask = null;
      setTimeout(() => this.processQueue(), 100);
    }
  }

  async runInference(task) {
    const config = task.config;
    
    // Generate unique process ID for this task
    const processId = `task_${task.id}_${Date.now()}`;
    
    // Update task with process ID
    this.updateTask(task.id, { processId });

    try {
      // Update progress
      this.updateTask(task.id, { progress: 'Preparing configuration...' });

      // Create job folder and output paths
      const jobFolderName = task.name.replace(/[^a-zA-Z0-9\-_\s]/g, '').replace(/\s+/g, '_');
      const jobFolder = config.output_dir ? `${config.output_dir}/${jobFolderName}` : '';
      const outputCsvPath = jobFolder ? `${jobFolder}/predictions.csv` : '';
      const configJsonPath = jobFolder ? `${jobFolder}/${task.name}_${task.id}.json` : '';

      // Create temporary config file
      const tempConfigPath = `/tmp/inference_config_${processId}.json`;
      const configData = {
        model: config.model || 'BirdNET',
        files: config.files || [],
        output_file: outputCsvPath,
        job_folder: jobFolder,
        config_output_path: configJsonPath,
        inference_settings: {
          clip_overlap: config.overlap || 0.0,
          batch_size: config.batch_size || 1,
          num_workers: config.worker_count || 1
        }
      };

      // Save temporary config file using HTTP API
      const saveResponse = await fetch('http://localhost:8000/config/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config_data: configData,
          output_path: tempConfigPath
        })
      });

      const saveResult = await saveResponse.json();
      if (saveResult.status !== 'success') {
        throw new Error(`Failed to save configuration: ${saveResult.error}`);
      }

      // Update progress
      this.updateTask(task.id, { progress: 'Setting up ML environment...' });

      // Get environment paths using Electron userData directory
      const envPathResult = await window.electronAPI.getEnvironmentPath('dipper_pytorch_env');
      const archivePathResult = await window.electronAPI.getArchivePath('dipper_pytorch_env.tar.gz');

      if (!envPathResult.success || !archivePathResult.success) {
        throw new Error('Failed to get environment paths');
      }

      const envPath = envPathResult.path;
      const archivePath = archivePathResult.path;

      // Update progress
      this.updateTask(task.id, { progress: 'Running inference...' });

      // Run inference via HTTP API
      const inferenceResponse = await fetch('http://localhost:8000/inference/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          config_path: tempConfigPath,
          env_path: envPath,
          archive_path: archivePath
        })
      });

      const inferenceResult = await inferenceResponse.json();

      if (inferenceResult.status === 'success') {
        return {
          success: true,
          output_path: configData.output_file,
          job_folder: configData.job_folder,
          config_path: configData.config_output_path,
          total_files: config.files.length,
          message: 'Inference completed successfully'
        };
      } else {
        // Show detailed error information
        let errorMessage = inferenceResult.error || 'Inference failed';

        if (inferenceResult.details) {
          errorMessage += '\n\nDetails:\n' + inferenceResult.details;
        } else if (inferenceResult.stderr) {
          errorMessage += '\n\nError output:\n' + inferenceResult.stderr;
        }

        if (inferenceResult.stdout) {
          errorMessage += '\n\nStandard output:\n' + inferenceResult.stdout;
        }

        throw new Error(errorMessage);
      }
    } catch (error) {
      throw new Error(`Inference failed: ${error.message}`);
    }
  }

  cancelTask(taskId) {
    const task = this.getTask(taskId);
    if (!task) return false;

    if (task.status === TASK_STATUS.RUNNING) {
      // Cancel the running process
      if (task.processId && window.electronAPI) {
        window.electronAPI.killPythonProcess(task.processId);
      }
    }

    // Remove from queue
    this.queue = this.queue.filter(id => id !== taskId);

    // Update task status
    this.updateTask(taskId, {
      status: TASK_STATUS.CANCELLED,
      completed: Date.now(),
      progress: 'Cancelled by user'
    });

    // If this was the current task, process next
    if (this.currentTask === taskId) {
      this.currentTask = null;
      setTimeout(() => this.processQueue(), 100);
    }

    return true;
  }

  // Utility Methods
  generateTaskName(config) {
    const modelName = config.model || 'Unknown';
    const fileCount = config.files ? config.files.length : 0;
    const timestamp = new Date().toLocaleString();
    return `${modelName} - ${fileCount} files - ${timestamp}`;
  }

  // Persistence
  saveTasks() {
    try {
      const tasksData = Array.from(this.tasks.entries());
      localStorage.setItem('inference_tasks', JSON.stringify(tasksData));
    } catch (error) {
      console.error('Failed to save tasks:', error);
    }
  }

  loadTasks() {
    try {
      const tasksData = localStorage.getItem('inference_tasks');
      if (tasksData) {
        const entries = JSON.parse(tasksData);
        this.tasks = new Map(entries);
        
        // Rebuild queue from queued tasks
        this.rebuildQueue();
      }
    } catch (error) {
      console.error('Failed to load tasks:', error);
      this.tasks = new Map();
    }
  }

  rebuildQueue() {
    // On startup, rebuild queue from tasks that were queued or running
    const queuedTasks = this.getAllTasks()
      .filter(task => task.status === TASK_STATUS.QUEUED || task.status === TASK_STATUS.RUNNING)
      .sort((a, b) => a.created - b.created);

    this.queue = queuedTasks.map(task => {
      // Reset running tasks to queued on startup
      if (task.status === TASK_STATUS.RUNNING) {
        this.updateTask(task.id, { 
          status: TASK_STATUS.QUEUED,
          progress: 'Reconnected - queued for execution'
        });
      }
      return task.id;
    });

    // Start processing if there are queued tasks
    if (this.queue.length > 0) {
      setTimeout(() => this.processQueue(), 1000);
    }
  }

  // Event System
  addListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  notifyListeners(event, data) {
    this.listeners.forEach(callback => {
      try {
        callback(event, data);
      } catch (error) {
        console.error('Task listener error:', error);
      }
    });
  }

  // Queue Info
  getQueueInfo() {
    return {
      currentTask: this.currentTask ? this.getTask(this.currentTask) : null,
      queueLength: this.queue.length,
      nextTasks: this.queue.slice(0, 3).map(id => this.getTask(id))
    };
  }
}

// Singleton instance
export const taskManager = new TaskManager();
export default taskManager;