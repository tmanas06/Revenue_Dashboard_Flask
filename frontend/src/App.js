import React from 'react';
import { Route, Routes, Link } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import AIRecommendations from './components/AIRecommendations';

import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Revenue Analytics Dashboard</h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/ai-recommendations">AI Recommendations</Link>
        </nav>
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/ai-recommendations" element={<AIRecommendations />} />
        </Routes>
      </main>
      <footer className="app-footer">
        <p> {new Date().getFullYear()} Revenue Analytics Dashboard</p>
      </footer>
    </div>
  );
}

export default App;