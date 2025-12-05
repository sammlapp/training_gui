# Bioacoustics Training GUI - Design Document

## Overview

A desktop application for bioacoustics machine learning workflows that enables researchers to analyze audio recordings, detect species, train custom models, and iteratively improve detection accuracy through active learning.

## Core Purpose

Enable bioacoustics researchers to:
- Run automated species detection on large audio datasets
- Review and validate detection results
- Annotate audio data for training
- Train custom detection models
- Improve models through iterative feedback loops

## Application Architecture

### Desktop Application
- Cross-platform desktop app (Mac, Windows, Linux)
- Modern graphical interface with tabbed navigation
- Real-time progress monitoring and task management
- Offline operation with bundled ML environment

### Two-Tier Processing
- **Lightweight Frontend Server**: Handles UI interactions, file management, and data visualization
- **ML Processing Environment**: Executes compute-intensive model inference and training

## Primary Workflows

### 1. Inference Workflow
**Purpose**: Detect species in audio recordings using pre-trained or custom models

**Capabilities**:
- Select audio files via file picker, folder browser, or file lists
- Choose from multiple pre-trained bioacoustics models
- Configure detection parameters (batch size, overlap, confidence thresholds)
- Create and manage inference tasks
- Queue multiple inference jobs
- Monitor progress in real-time
- Export detection results as CSV files

**Outputs**: Time-stamped detection scores for each species across all analyzed audio

### 2. Exploration Workflow
**Purpose**: Visualize and filter detection results to identify patterns and high-confidence detections

**Capabilities**:
- Load inference results from CSV files
- Filter detections by species, score range, time, and location
- Visualize score distributions with interactive histograms
- Generate spectrograms for selected detections
- Play audio clips for verification
- Export filtered datasets for annotation

**Outputs**: Curated subsets of detections for review or training

### 3. Review & Annotation Workflow
**Purpose**: Listen to and annotate audio clips to create training data

**Capabilities**:
- Load detection results or custom annotation tasks
- Display spectrograms with playback controls
- Multi-class annotation with configurable label sets
- Batch annotation with keyboard shortcuts
- Stratified sampling strategies (random, score-weighted, high-confidence)
- Save annotations in standard formats
- Track annotation progress

**Outputs**: Validated annotations for model training

### 4. Training Workflow
**Purpose**: Train custom species detection models using annotated data

**Capabilities**:
- Load training and validation datasets
- Configure model architecture and hyperparameters
- Set up data augmentation strategies
- Monitor training metrics in real-time
- Save trained models for inference
- Export training history and performance metrics

**Outputs**: Trained models ready for deployment

## Data Flow

### Input Data
- Audio files (WAV, MP3, FLAC, OGG, M4A, AAC)
- Inference results (CSV with file paths, timestamps, and scores)
- Annotation files (CSV with labels and timestamps)
- Configuration files (JSON with settings)

### Intermediate Data
- Spectrograms (generated on-demand, cached for performance)
- Audio clips (extracted segments for review)
- Task definitions (queued inference jobs)

### Output Data
- Detection scores (CSV with predictions per file/time)
- Annotations (CSV with validated labels)
- Trained models (saved model weights and configurations)
- Visualizations (plots, charts, spectrograms)

## Task Management System

### Task Types
- Inference tasks (model predictions on audio files)
- Training tasks (model training sessions)
- Batch processing tasks (clip generation, data export)

### Task States
- Unstarted: Created but not queued
- Queued: Waiting to execute
- Running: Currently processing
- Completed: Finished successfully
- Failed: Encountered error
- Cancelled: Stopped by user

### Task Operations
- Create tasks with specific configurations
- Queue tasks for execution
- Monitor progress with real-time updates
- Cancel running tasks
- Review task history
- Rerun previous tasks with same settings

## Model Support

### Pre-trained Models
Integration with bioacoustics model zoo:
- Bird species detection (HawkEars, BirdNET, Perch)
- Frog call detection (RanaSierraeCNN)
- Custom PyTorch models

### Custom Models
- Train convolutional neural networks on user data
- Support for multi-class and multi-label classification
- Transfer learning from pre-trained architectures
- Model versioning and management

## Configuration Management

### Inference Settings
- Model selection and parameters
- Audio processing settings (sample rate, window size, overlap)
- Batch processing configuration
- Output format and location

### Training Settings
- Model architecture and hyperparameters
- Optimizer and learning rate
- Data augmentation parameters
- Training/validation split ratios

### Display Settings
- Spectrogram visualization parameters
- Audio playback settings
- Color schemes and scales
- Default file locations

### Persistence
- Save configurations as JSON files
- Load previous configurations
- Session state persistence
- Default settings for new tasks

## Performance Optimization

### Efficient Data Loading
- In-memory caching of frequently accessed spectrograms
- Parallel processing of audio clips
- Asynchronous data streaming
- Progressive loading for large datasets

### Responsive UI
- Non-blocking task execution
- Background processing
- Real-time progress updates
- Smooth spectrogram rendering

### Resource Management
- Configurable batch sizes for memory control
- Worker process management
- Automatic cleanup of temporary files
- Efficient audio file scanning

## User Interface Design

### Navigation
- Tab-based interface for major workflows
- Persistent task status bar
- Quick access to recent files and tasks
- Contextual help and tooltips

### Visual Elements
- Material Design components
- Interactive spectrograms with playback
- Real-time charts and histograms
- Responsive layouts for different screen sizes

### Feedback
- Progress indicators for long operations
- Status messages for user actions
- Error notifications with recovery guidance
- Validation feedback for inputs

## Distribution & Deployment

### Packaging
- Standalone desktop application
- Bundled Python ML environment
- No external dependencies required
- Platform-specific installers

### Installation
- Simple drag-and-drop installation
- No admin privileges required
- Automatic environment setup
- Self-contained application bundle

### Updates
- Version checking capability
- Configuration migration support
- Backward compatibility with data files

## Extensibility

### Plugin Architecture
- Support for custom models
- Configurable label sets
- Custom preprocessing pipelines
- External tool integration

### Data Formats
- Standard CSV for interchange
- JSON for configurations
- Common audio formats
- Flexible metadata schemas

### Integration Points
- Command-line interface for scripting
- HTTP API for external tools
- File-based communication
- Standard ML frameworks (PyTorch)

## Quality & Reliability

### Error Handling
- Graceful degradation for missing files
- Recovery from processing errors
- Clear error messages
- Automatic retry for transient failures

### Data Validation
- Audio file format verification
- Configuration validation
- Input parameter checking
- File path resolution

### Testing
- Automated build verification
- Environment compatibility checks
- Performance benchmarking
- Integration testing

## Use Cases

### Research Workflows
- Large-scale acoustic monitoring surveys
- Species presence/absence studies
- Population monitoring over time
- Multi-site comparative studies

### Active Learning Loops
1. Run initial inference on unlabeled data
2. Filter to high-confidence detections
3. Review and annotate uncertain cases
4. Train improved model with new labels
5. Repeat to iteratively improve accuracy

### Data Curation
- Build training datasets from field recordings
- Quality control for existing annotations
- Generate examples for specific behaviors
- Create balanced class distributions

### Model Development
- Prototype new detection algorithms
- Test different architectures
- Compare model performance
- Fine-tune pre-trained models

## System Requirements

### Minimum Specifications
- Modern multi-core processor
- 8GB RAM
- 2GB disk space for application
- Additional storage for audio files and models

### Recommended Specifications
- Multi-core processor with 8+ cores
- 16GB+ RAM for large datasets
- SSD storage for performance
- GPU support for faster training (optional)

### Supported Platforms
- macOS 10.15 or later
- Windows 10 or later
- Linux (Ubuntu 18.04+ or equivalent)

## Design Principles

### Keep It Simple
- Intuitive workflows matching research needs
- Clear visual hierarchy
- Sensible defaults
- Progressive disclosure of advanced features

### Performance First
- Responsive UI even with large datasets
- Efficient resource usage
- Fast audio processing
- Optimized visualization rendering

### Researcher-Focused
- Workflows match scientific practices
- Export formats compatible with analysis tools
- Reproducible configurations
- Clear documentation and examples

### Reliable & Robust
- Handle edge cases gracefully
- Validate inputs thoroughly
- Recover from errors automatically
- Maintain data integrity
