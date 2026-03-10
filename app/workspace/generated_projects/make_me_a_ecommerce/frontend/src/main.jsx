import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, info) {
    console.error('App Error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return React.createElement('div', {
        style: { padding: '40px', textAlign: 'center', fontFamily: 'Inter, sans-serif',
          background: '#fef2f2', minHeight: '100vh', display: 'flex',
          flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }
      },
        React.createElement('h2', { style: { color: '#dc2626', marginBottom: '16px' } },
          '\u26a0\ufe0f Something went wrong'),
        React.createElement('pre', {
          style: { background: '#fff', padding: '16px', borderRadius: '8px',
            maxWidth: '600px', overflow: 'auto', fontSize: '0.85rem',
            border: '1px solid #fecaca', textAlign: 'left' }
        }, String(this.state.error)),
        React.createElement('button', {
          onClick: () => window.location.reload(),
          style: { marginTop: '20px', padding: '10px 24px', background: '#667eea',
            color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer',
            fontSize: '1rem' }
        }, '\ud83d\udd04 Reload')
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  </React.StrictMode>
);