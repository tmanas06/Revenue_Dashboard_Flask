import React, { useState, useEffect } from 'react';
import './AIRecommendations.css';

const AIRecommendations = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [marketingIdeas, setMarketingIdeas] = useState(null);
  const [businessType, setBusinessType] = useState('e-commerce');
  const [targetAudience, setTargetAudience] = useState('general consumers');
  const [marketingLoading, setMarketingLoading] = useState(false);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch('http://localhost:5000/api/ai/recommendations', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (data.status === 'error') {
        throw new Error(data.message || 'AI analysis failed');
      }
      
      setRecommendations(data);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError(err.message);
      
      // Retry logic with exponential backoff
      if (retryCount < 3) {
        setRetryCount(retryCount + 1);
        setTimeout(() => fetchRecommendations(), 2000 * retryCount);
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchMarketingIdeas = async () => {
    try {
      setMarketingLoading(true);
      setError(null);
      const response = await fetch(
        `http://localhost:5000/api/ai/marketing-ideas?business_type=${encodeURIComponent(businessType)}&target_audience=${encodeURIComponent(targetAudience)}`
      );
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.error || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.status === 'error') {
        throw new Error(data.message || 'Failed to generate marketing ideas');
      }
      
      setMarketingIdeas(data.marketing_ideas);
    } catch (err) {
      console.error('Error fetching marketing ideas:', err);
      setError(err.message);
    } finally {
      setMarketingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading recommendations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={fetchRecommendations} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="ai-recommendations">
      <h1>AI Business Recommendations</h1>

      {recommendations && (
        <>
          <div className="card">
            <h2>Revenue Analysis & Recommendations</h2>
            <div className="card-content">
              <h3>Key Observations</h3>
              <p>{recommendations.observations}</p>

              <div className="divider"></div>

              <h3>Price Recommendations</h3>
              <p>{recommendations.price_recommendations}</p>

              <div className="divider"></div>

              <h3>Product Focus</h3>
              <p>{recommendations.product_focus}</p>

              <div className="divider"></div>

              <h3>Growth Strategies</h3>
              <ul className="recommendation-list">
                {recommendations.growth_strategies.split('\n').filter(Boolean).map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>

              <div className="divider"></div>

              <h3>Potential Issues</h3>
              <ul className="recommendation-list">
                {recommendations.potential_issues.split('\n').filter(Boolean).map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}

      <div className="card">
        <h2>Generate Marketing Ideas</h2>
        
        <div className="form-group">
          <div className="input-group">
            <input
              type="text"
              placeholder="Business Type"
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              className="input-field"
            />
            
            <input
              type="text"
              placeholder="Target Audience"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              className="input-field"
            />
          </div>

          <button
            onClick={fetchMarketingIdeas}
            disabled={marketingLoading}
            className={`generate-button ${marketingLoading ? 'loading' : ''}`}
          >
            {marketingLoading ? 'Generating...' : 'Generate Ideas'}
          </button>

          {marketingIdeas && (
            <div className="marketing-ideas">
              <h3>Marketing Ideas for {businessType} targeting {targetAudience}:</h3>
              <ul className="ideas-list">
                {marketingIdeas.split('\n').filter(Boolean).map((idea, index) => (
                  <li key={index}>{idea}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIRecommendations;
