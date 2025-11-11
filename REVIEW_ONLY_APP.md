# Dipper Review - Review-Only Application

This is a lightweight, standalone version of Dipper that includes only the Review tab functionality. It's designed for users who only need to review and annotate audio clips without access to the inference, training, or extraction features.

## Features

- **Streamlined Interface**: No navigation drawer - just the Review tab
- **Smaller Bundle Size**: ~31KB smaller JavaScript bundle compared to full app
- **Same Review Functionality**: All review features including:
  - Binary and multi-class annotation
  - Focus and grid modes
  - Classifier-Guided Listening (CGL)
  - Filters and search
  - Auto-save
  - Progress tracking
  - Label counts
  - Keyboard shortcuts

## Building the Review-Only App

### Development Mode

To run the review-only app in development mode:

```bash
cd frontend
npm run electron-dev-review
```

This will:
1. Start the React dev server with `REACT_APP_REVIEW_ONLY=true`
2. Launch Electron with the review-only main process (`main-review.js`)

### Production Build

To build the review-only app for distribution:

#### macOS
```bash
cd frontend
npm run dist:review-mac
```

#### Windows
```bash
cd frontend
npm run dist:review
```

#### All Platforms
```bash
cd frontend
npm run dist:review
```

The built app will be output to `dist-review/` instead of `dist/`.

### Build Configuration

The review-only app uses:
- **App Name**: "Dipper Review"
- **App ID**: `com.bioacoustics.traininggui.review`
- **Main Process**: `src/main-review.js`
- **Build Config**: `electron-builder-review.json`
- **Output Directory**: `dist-review/`
- **Environment Variable**: `REACT_APP_REVIEW_ONLY=true`

## How It Works

### Conditional Rendering

The app uses an environment variable (`REACT_APP_REVIEW_ONLY`) to conditionally render:

```javascript
// In App.js
const isReviewOnly = process.env.REACT_APP_REVIEW_ONLY === 'true';

if (isReviewOnly) {
  return (
    <Box sx={{ display: 'flex', width: '100%' }}>
      <CssBaseline />
      <Box component="main" sx={{ flexGrow: 1, p: 0 }}>
        <ReviewTab />
      </Box>
    </Box>
  );
}
```

When `REACT_APP_REVIEW_ONLY=true`:
- No navigation drawer is rendered
- App starts directly in Review tab
- Full window width is used for the Review interface
- All other tabs (Inference, Training, etc.) are excluded from the bundle

### Separate Electron Configuration

The review-only app has its own:
1. **Main process file** (`main-review.js`):
   - Slightly larger default window (1400x900 vs 1200x800)
   - Title set to "Dipper Review"

2. **Electron builder config** (`electron-builder-review.json`):
   - Different app ID and product name
   - Separate output directory to avoid conflicts
   - Only includes necessary files

## Python Backend

The review-only app includes the full Python backend for:
- Audio file loading via HTTP server
- CSV processing
- Annotation export

The lightweight Python server is bundled the same way as the full app.

## Use Cases

The review-only app is perfect for:
- Annotation teams who only need to review clips
- Distributed annotation workflows
- Users with limited storage (smaller app size)
- Dedicated annotation workstations
- Simplified deployment in restricted environments

## Differences from Full App

**Included:**
- ✅ All Review tab features
- ✅ Binary and multi-class annotation
- ✅ Classifier-Guided Listening
- ✅ Focus and grid modes
- ✅ Python HTTP server for audio

**Excluded:**
- ❌ Inference tab
- ❌ Training tab
- ❌ Extraction tab
- ❌ Explore tab
- ❌ Task management
- ❌ Navigation drawer

## File Structure

```
frontend/
├── src/
│   ├── App.js                      # Modified to check REACT_APP_REVIEW_ONLY
│   ├── main-review.js              # Electron main process for review-only
│   ├── AppReviewOnly.js            # Standalone review-only component (alternative approach)
│   └── index-review.js             # Alternative index file (if needed)
├── electron-builder-review.json    # Electron builder config for review-only
└── package.json                    # Updated with review-only scripts
```

## Build Scripts

Added to `package.json`:

```json
{
  "scripts": {
    "build:review": "cross-env REACT_APP_REVIEW_ONLY=true react-scripts build",
    "build:review-all": "npm run build:review && npm run build:python-pyinstaller",
    "electron-dev-review": "concurrently \"cross-env BROWSER=none REACT_APP_REVIEW_ONLY=true npm start\" \"wait-on http://localhost:3000 && cross-env NODE_ENV=development electron src/main-review.js\"",
    "dist:review": "npm run build:review-all && electron-builder --config electron-builder-review.json",
    "dist:review-mac": "npm run build:review-all && electron-builder --mac --config electron-builder-review.json"
  }
}
```

## Future Enhancements

Potential improvements for the review-only app:
- Remove unused Python backend functionality to further reduce size
- Add app-specific branding/logo
- Simplified first-run experience
- Pre-configured review workflows
- Built-in tutorial for annotation
