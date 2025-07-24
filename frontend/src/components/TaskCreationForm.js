import React, { useState } from 'react';

function TaskCreationForm({ onTaskCreate, onTaskCreateAndRun }) {
  const [taskName, setTaskName] = useState('');
  const [config, setConfig] = useState({
    files: [],
    model: 'BirdNET',
    overlap: 0.0,
    batch_size: 1,
    worker_count: 1,
    output_dir: '',
    save_clips: false
  });

  const handleFileSelection = async () => {
    try {
      const files = await window.electronAPI.selectFiles();
      if (files && files.length > 0) {
        setConfig(prev => ({ ...prev, files }));
      }
    } catch (error) {
      console.error('Failed to select files:', error);
    }
  };

  const handleOutputDirSelection = async () => {
    try {
      const dir = await window.electronAPI.selectFolder();
      if (dir) {
        setConfig(prev => ({ ...prev, output_dir: dir }));
      }
    } catch (error) {
      console.error('Failed to select output directory:', error);
    }
  };

  const handleSubmit = (createAndRun = false) => {
    if (config.files.length === 0) {
      alert('Please select audio files first');
      return;
    }

    if (!config.output_dir) {
      alert('Please select an output directory');
      return;
    }

    const taskConfig = { ...config };
    const finalTaskName = taskName.trim() || null; // Let TaskManager generate name if empty

    if (createAndRun) {
      onTaskCreateAndRun(taskConfig, finalTaskName);
    } else {
      onTaskCreate(taskConfig, finalTaskName);
    }

    // Reset form
    setTaskName('');
    setConfig(prev => ({ 
      ...prev, 
      files: [], 
      output_dir: '' 
    }));
  };

  return (
    <div className="task-creation-form">
      <h3>Create Inference Task</h3>
      
      <div className="form-grid">
        {/* Task Name */}
        <div className="form-group full-width">
          <label>Task Name (optional)</label>
          <input
            type="text"
            value={taskName}
            onChange={(e) => setTaskName(e.target.value)}
            placeholder="Leave empty for auto-generated name"
          />
        </div>

        {/* Files */}
        <div className="form-group full-width">
          <label>Audio Files</label>
          <div className="file-selection">
            <button onClick={handleFileSelection}>
              Select Audio Files
            </button>
            {config.files.length > 0 && (
              <span className="file-count">
                {config.files.length} files selected
              </span>
            )}
          </div>
        </div>

        {/* Output Directory */}
        <div className="form-group full-width">
          <label>Output Directory</label>
          <div className="file-selection">
            <button onClick={handleOutputDirSelection}>
              Select Output Directory
            </button>
            {config.output_dir && (
              <span className="selected-path">
                {config.output_dir}
              </span>
            )}
          </div>
        </div>

        {/* Model */}
        <div className="form-group">
          <label>Model</label>
          <select
            value={config.model}
            onChange={(e) => setConfig(prev => ({ ...prev, model: e.target.value }))}
          >
            <option value="BirdNET">BirdNET</option>
            <option value="Perch">Perch</option>
            <option value="HawkEars">HawkEars</option>
            <option value="RanaSierraeCNN">RanaSierraeCNN</option>
          </select>
        </div>

        {/* Overlap */}
        <div className="form-group">
          <label>Overlap</label>
          <input
            type="number"
            min="0"
            max="1"
            step="0.1"
            value={config.overlap}
            onChange={(e) => setConfig(prev => ({ ...prev, overlap: parseFloat(e.target.value) }))}
          />
        </div>

        {/* Batch Size */}
        <div className="form-group">
          <label>Batch Size</label>
          <input
            type="number"
            min="1"
            max="32"
            value={config.batch_size}
            onChange={(e) => setConfig(prev => ({ ...prev, batch_size: parseInt(e.target.value) }))}
          />
        </div>

        {/* Worker Count */}
        <div className="form-group">
          <label>Workers</label>
          <input
            type="number"
            min="1"
            max="8"
            value={config.worker_count}
            onChange={(e) => setConfig(prev => ({ ...prev, worker_count: parseInt(e.target.value) }))}
          />
        </div>


        {/* Save Clips */}
        <div className="form-group full-width">
          <label>
            <input
              type="checkbox"
              checked={config.save_clips}
              onChange={(e) => setConfig(prev => ({ ...prev, save_clips: e.target.checked }))}
            />
            Save Audio Clips
          </label>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="form-actions">
        <button
          className="button-secondary"
          onClick={() => handleSubmit(false)}
          disabled={config.files.length === 0 || !config.output_dir}
        >
          Create Task
        </button>
        <button
          className="button-primary"
          onClick={() => handleSubmit(true)}
          disabled={config.files.length === 0 || !config.output_dir}
        >
          Create and Run Task
        </button>
      </div>
    </div>
  );
}

export default TaskCreationForm;