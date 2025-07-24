import React, { useState } from 'react';

function TaskCreationForm({ onTaskCreate, onTaskCreateAndRun }) {
  const [taskName, setTaskName] = useState('');
  const [config, setConfig] = useState({
    files: [],
    model: 'BirdNET',
    overlap: 0.0,
    batch_size: 1,
    worker_count: 1,
    output_dir: ''
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

  const saveInferenceConfig = async () => {
    try {
      if (!window.electronAPI) {
        alert('Electron API not available - running in browser mode');
        return;
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const defaultName = `inference_config_${timestamp}.json`;
      const configPath = await window.electronAPI.saveFile(defaultName);

      if (configPath) {
        const configData = {
          task_name: taskName,
          model: config.model,
          files: config.files,
          output_dir: config.output_dir,
          inference_settings: {
            clip_overlap: config.overlap,
            batch_size: config.batch_size,
            num_workers: config.worker_count
          }
        };

        // Use HTTP API to save config
        const response = await fetch('http://localhost:8000/config/save', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            config_data: configData,
            output_path: configPath
          })
        });

        const result = await response.json();
        if (result.status === 'success') {
          alert(`Config saved to: ${configPath.split('/').pop()}`);
        } else {
          alert(`Failed to save config: ${result.error}`);
        }
      }
    } catch (err) {
      alert('Failed to save config: ' + err.message);
    }
  };

  const loadInferenceConfig = async () => {
    try {
      if (!window.electronAPI) {
        alert('Electron API not available - running in browser mode');
        return;
      }

      const configFile = await window.electronAPI.selectJSONFiles();
      if (configFile && configFile.length > 0) {
        // Use HTTP API to load config
        const response = await fetch('http://localhost:8000/config/load', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            config_path: configFile[0]
          })
        });

        const result = await response.json();
        if (result.status === 'success') {
          const configData = result.config;
          setTaskName(configData.task_name || '');
          setConfig(prev => ({
            ...prev,
            model: configData.model || 'BirdNET',
            files: configData.files || [],
            output_dir: configData.output_dir || '',
            overlap: configData.inference_settings?.clip_overlap || 0.0,
            batch_size: configData.inference_settings?.batch_size || 1,
            worker_count: configData.inference_settings?.num_workers || 1
          }));
          alert(`Config loaded from: ${configFile[0].split('/').pop()}`);
        } else {
          alert(`Failed to load config: ${result.error}`);
        }
      }
    } catch (err) {
      alert('Failed to load config: ' + err.message);
    }
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


      </div>

      {/* Config Management and Task Launch Buttons */}
      <div className="config-actions" style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid var(--border)' }}>
        <div className="button-group" style={{ display: 'flex', gap: '8px', justifyContent: 'flex-start' }}>
          <button
            type="button"
            className="button-secondary"
            onClick={saveInferenceConfig}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            Save Config
          </button>
          <button
            type="button"
            className="button-secondary"
            onClick={loadInferenceConfig}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            Load Config
          </button>


          <button
            className="button-secondary"
            onClick={() => handleSubmit(false)}
            disabled={config.files.length === 0 || !config.output_dir}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}
          >
            Create Task
          </button>
          <button
            className="button-primary"
            onClick={() => handleSubmit(true)}
            disabled={config.files.length === 0 || !config.output_dir}
            style={{ fontSize: '0.8rem', padding: '6px 12px' }}

          >
            Create and Run Task
          </button>

        </div>
      </div>

      {/* Action Buttons
      <div className="form-actions">
        
      </div> */}
    </div>
  );
}

export default TaskCreationForm;