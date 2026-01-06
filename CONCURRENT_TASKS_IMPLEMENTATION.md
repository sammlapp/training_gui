# Concurrent Task Execution - Implementation Summary

## Overview
Implemented configurable concurrent task execution allowing users to run multiple background tasks (inference, training, extraction) simultaneously. Users can configure the maximum number of concurrent tasks and optionally exempt extraction tasks from the concurrency limit.

## Implementation Date
January 2026

## Files Created

### 1. frontend/src/components/SettingsTab.js
**Purpose:** New Settings tab for global application configuration

**Features:**
- Material-UI form with TextField for max concurrent tasks (1-10)
- Checkbox to exempt extraction tasks from concurrent limit
- Save/Reset buttons with success/error feedback
- Informational cards explaining the settings and recommended values
- Settings persist to localStorage as 'dipper_settings'
- Dispatches 'settingsChanged' event when settings are saved

**Key Components:**
- Max Concurrent Tasks: Number input (1-10), default 1
- Exempt Extraction Tasks: Checkbox, default false
- About section with recommended values based on system RAM

## Files Modified

### 2. frontend/src/utils/TaskManager.js
**Major Changes:**

**Constructor:**
- Replaced `this.currentTask = null` with `this.runningTasks = new Set()`
- Added `this.loadSettings()` to load configuration from localStorage
- Added event listener for 'settingsChanged' to dynamically reload settings

**New Methods:**
- `loadSettings()`: Loads maxConcurrentTasks and exemptExtractionTasks from localStorage
- `getCountedRunningTasks()`: Returns count of running tasks, optionally excluding extraction tasks

**Updated Methods:**
- `queueTask()`: Always calls processQueue() to try starting available tasks
- `processQueue()`: Now uses while loop to start multiple tasks up to the concurrent limit
- `executeTask()`: Finally block deletes from runningTasks Set and triggers processQueue
- `cancelTask()`: Checks runningTasks Set instead of currentTask
- `getQueueInfo()`: Returns array of runningTasks plus backward-compatible currentTask

**Concurrency Logic:**
```javascript
async processQueue() {
  while (this.queue.length > 0) {
    const countedRunning = this.getCountedRunningTasks();
    if (countedRunning >= this.maxConcurrentTasks) {
      break; // At capacity
    }
    // Start task without awaiting (parallel execution)
    this.runningTasks.add(taskId);
    this.executeTask(taskId);
  }
}
```

### 3. frontend/src/App.js
**Changes:**

**Imports:**
- Added `SettingsIcon` from '@mui/icons-material/Settings'
- Added `SettingsTab` component

**Tab List:**
- Added Settings tab between Review and Help tabs

**State:**
- Added `runningTasks` state array to track multiple running tasks

**Effect Hook:**
- Updated to set runningTasks from queueInfo.runningTasks

**Status Bar:**
- Now displays multiple running tasks when more than one
- Shows "Running 1 task" or "Running N tasks: task1, task2..."
- Truncates long task lists at 80 characters

**Rendering:**
- Added SettingsTab component rendering when activeTab === 'settings'

## Settings Structure

Settings stored in localStorage as JSON:
```json
{
  "maxConcurrentTasks": 1,      // 1-10
  "exemptExtractionTasks": false // boolean
}
```

## User Experience

### Settings Tab
1. User navigates to Settings tab via sidebar
2. Adjusts max concurrent tasks (1-10) using number input
3. Optionally checks "Do not count extraction tasks" checkbox
4. Clicks "Save Settings" button
5. Settings immediately apply (TaskManager reloads via event)
6. Can reset to defaults (1 task, no exemptions) without saving

### Task Execution
**Without Exemption (default):**
- Max 1 task runs at a time (inference, training, or extraction)
- Additional tasks queue and wait

**With Max = 3, No Exemption:**
- Up to 3 tasks run simultaneously (any combination)
- 4th task waits in queue

**With Max = 2, Exemption Enabled:**
- Up to 2 inference/training tasks run
- Unlimited extraction tasks run without counting toward limit
- Example: 2 inference + 5 extraction tasks can all run simultaneously

### Status Bar Display
**Single Task:**
```
🔄 Running: Inference BirdNET - 50 files - 1/5/2026
   Processing 50 audio files
```

**Multiple Tasks:**
```
🔄 Running 3 tasks: Inference BirdNET - 50 files, Training HawkEars - 4 cl...
```

**Idle:**
```
✅ Ready • 5 completed tasks • 2 queued • Backend: port 8000
```

## Technical Details

### Concurrency Model
- **Frontend-enforced:** TaskManager controls concurrency via queue processing
- **Backend-agnostic:** Backend spawns subprocesses as requested
- **Non-blocking:** Tasks execute in parallel via fire-and-forget pattern
- **Status polling:** Each running task polls backend every 2 seconds

### Extraction Task Exemption
When enabled:
- Extraction tasks add to `runningTasks` Set
- `getCountedRunningTasks()` filters them out of the count
- They can start even when inference/training slots are full
- Useful because extraction is less resource-intensive

### Backward Compatibility
- `getQueueInfo()` still returns `currentTask` (first running task)
- Existing code expecting single task continues to work
- New code can use `runningTasks` array for full visibility

## Resource Considerations

**Recommended Settings:**
- **1 task (default):** Safe for all systems, prevents conflicts
- **2-3 tasks:** Good for 16GB+ RAM systems
- **4-5 tasks:** For 32GB+ RAM, many CPU cores
- **Extraction exemption:** Enable if running many extraction tasks

**Memory Usage:**
- Each inference/training task: ~2GB RAM per subprocess
- Each extraction task: ~500MB RAM (less intensive)

## Future Enhancements

Potential additions:
- Backend-side concurrency limit as safety measure
- Per-task-type limits (e.g., max 2 inference, max 1 training)
- Resource monitoring (show RAM/CPU usage)
- Queue priority system
- WebSocket for real-time updates instead of polling
- Task affinity (e.g., extraction always runs on CPU, inference on GPU)

## Testing Checklist

- [x] Settings tab renders correctly
- [x] Settings save to localStorage
- [x] Settings reload when changed
- [ ] Single task execution (max=1)
- [ ] Multiple tasks execution (max=2,3,4)
- [ ] Extraction exemption works correctly
- [ ] Status bar shows correct running task count
- [ ] Queued tasks start when slots become available
- [ ] Task cancellation works with multiple running tasks
- [ ] App reload preserves settings

## Related Files
- Server mode plan: `/Users/SML161/.claude/plans/quiet-conjuring-pike.md`
- TaskManager backup: `/Users/SML161/training_gui/frontend/src/utils/TaskManager.js.backup`
