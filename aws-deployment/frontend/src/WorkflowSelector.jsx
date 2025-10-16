import React, { useState, useEffect } from 'react';
import './WorkflowSelector.css';

const API_BASE_URL = 'https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod';

const WorkflowSelector = ({ onWorkflowSelect, onWorkflowExecute }) => {
  const [industries, setIndustries] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Industry icons mapping
  const industryIcons = {
    manufacturing: 'M',
    healthcare: 'H',
    retail: 'R',
    financial: 'F',
    logistics: 'L',
    energy: 'E'
  };

  // Load available industries on component mount
  useEffect(() => {
    loadIndustries();
  }, []);

  const loadIndustries = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/workflows`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setIndustries(data.industries);
      } else {
        setError('Failed to load industries');
      }
    } catch (err) {
      setError(`Error loading industries: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadWorkflows = async (industry) => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/workflows/${industry}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setWorkflows(data.workflows);
        setSelectedIndustry(industry);
      } else {
        setError(`Failed to load workflows for ${industry}`);
      }
    } catch (err) {
      setError(`Error loading workflows: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const executeWorkflow = async (workflow) => {
    try {
      setLoading(true);
      setError(null);
      
      // Call the workflow execution endpoint
      const response = await fetch(`${API_BASE_URL}/workflows/${selectedIndustry}/${workflow.id}/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          custom_parameters: {} // Can be customized later
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        // Pass the results to the parent component
        if (onWorkflowExecute) {
          onWorkflowExecute(data);
        }
      } else {
        setError(`Workflow execution failed: ${data.error || 'Unknown error'}`);
      }
    } catch (err) {
      setError(`Error executing workflow: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return '#4CAF50';
      case 'intermediate': return '#FF9800';
      case 'advanced': return '#F44336';
      default: return '#757575';
    }
  };

  if (loading && industries.length === 0) {
    return (
      <div className="workflow-selector">
        <div className="loading">Loading industries...</div>
      </div>
    );
  }

  return (
    <div className="workflow-selector">
      <h2>Industry-Specific Workflows</h2>
      <p>Choose an industry to see predefined optimization workflows</p>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}

      {/* Industry Selection */}
      <div className="industry-grid">
        {industries.map(industry => (
          <div 
            key={industry}
            className={`industry-card ${selectedIndustry === industry ? 'selected' : ''}`}
            onClick={() => loadWorkflows(industry)}
          >
            <div className="industry-icon">
              {industryIcons[industry] || '🏢'}
            </div>
            <div className="industry-name">
              {industry.charAt(0).toUpperCase() + industry.slice(1)}
            </div>
          </div>
        ))}
      </div>

      {/* Workflows for Selected Industry */}
      {selectedIndustry && (
        <div className="workflows-section">
          <h3>
            {industryIcons[selectedIndustry]} {selectedIndustry.charAt(0).toUpperCase() + selectedIndustry.slice(1)} Workflows
          </h3>
          
          {loading ? (
            <div className="loading">Loading workflows...</div>
          ) : (
            <div className="workflows-grid">
              {workflows.map(workflow => (
                <div key={workflow.id} className="workflow-card">
                  <div className="workflow-header">
                    <h4>{workflow.title}</h4>
                    <div className="workflow-meta">
                      <span 
                        className="difficulty-badge"
                        style={{ backgroundColor: getDifficultyColor(workflow.difficulty) }}
                      >
                        {workflow.difficulty}
                      </span>
                      <span className="time-estimate">
                        {workflow.estimated_time}
                      </span>
                    </div>
                  </div>
                  
                  <div className="workflow-description">
                    {workflow.description}
                  </div>
                  
                  <div className="workflow-actions">
                    <button 
                      className="try-workflow-btn"
                      onClick={() => executeWorkflow(workflow)}
                      disabled={loading}
                    >
                      {loading ? 'Executing...' : 'Try This Workflow →'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowSelector;
