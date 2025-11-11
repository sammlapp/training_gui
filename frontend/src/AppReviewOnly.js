import React from 'react';
import CssBaseline from '@mui/material/CssBaseline';
import './App.css';
import ReviewTab from './components/ReviewTab';

/**
 * Review-Only App - Simplified version with only the Review tab
 * No navigation drawer or other tabs
 */
function AppReviewOnly() {
  return (
    <div className="App">
      <CssBaseline />
      <ReviewTab />
    </div>
  );
}

export default AppReviewOnly;
