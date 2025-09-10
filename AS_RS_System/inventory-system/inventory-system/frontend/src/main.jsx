import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';

// Import CSS files in proper order
import './styles/theme.css';
import './index.css';
import './styles/animations.css';
import './styles/utility.css'; 
import './styles/components.css';
import './styles/effects.css';
import './styles/responsive.css';
import './styles/table-compact.css';
import './styles/layout-compact.css';
import './styles/visual-enhancements.css';
import './styles/micro-interactions.css';
import './styles/compact-enhanced.css';
import './styles/optimized-dashboard.css';
import './styles/optimized-size.css';  // Added for better screen space usage and table readability

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
