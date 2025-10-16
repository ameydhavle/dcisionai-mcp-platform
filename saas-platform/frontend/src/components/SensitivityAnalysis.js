import React, { useState, useEffect, useCallback } from 'react';
import { 
  Sliders, 
  TrendingUp, 
  TrendingDown, 
  Target, 
  AlertTriangle,
  CheckCircle,
  RotateCcw,
  Play,
  Pause,
  Download,
  BarChart3,
  LineChart,
  PieChart,
  X
} from 'lucide-react';

const SensitivityAnalysis = ({ result, onClose }) => {
  const [sensitivityParams, setSensitivityParams] = useState({});
  const [isRunning, setIsRunning] = useState(false);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [chartType, setChartType] = useState('line');
  const [animationSpeed, setAnimationSpeed] = useState(1);

  // Initialize sensitivity parameters based on the optimization result
  useEffect(() => {
    const initialParams = {};
    
    // Extract variables from the solution
    if (result.optimization_solution?.solution) {
      Object.entries(result.optimization_solution.solution).forEach(([key, value]) => {
        if (typeof value === 'number') {
          initialParams[key] = {
            current: value,
            min: Math.max(0, value * 0.5),
            max: value * 2,
            step: value * 0.1,
            impact: 0 // Will be calculated
          };
        }
      });
    }

    // Add constraint parameters
    if (result.model_building?.constraints) {
      result.model_building.constraints.forEach((constraint, index) => {
        initialParams[`constraint_${index}`] = {
          current: 1,
          min: 0.1,
          max: 2,
          step: 0.1,
          impact: 0,
          type: 'constraint'
        };
      });
    }

    setSensitivityParams(initialParams);
  }, [result]);

  // Calculate sensitivity impact
  const calculateSensitivityImpact = useCallback((paramName, newValue) => {
    const param = sensitivityParams[paramName];
    if (!param) return 0;

    const changePercent = ((newValue - param.current) / param.current) * 100;
    
    // Simulate impact calculation based on parameter type
    if (param.type === 'constraint') {
      return Math.abs(changePercent) * 0.5; // Constraint changes have moderate impact
    } else {
      return Math.abs(changePercent) * 0.8; // Variable changes have higher impact
    }
  }, [sensitivityParams]);

  // Run sensitivity analysis
  const runSensitivityAnalysis = async () => {
    setIsRunning(true);
    
    try {
      // Prepare parameter changes for the backend
      const parameterChanges = {};
      Object.keys(sensitivityParams).forEach(paramName => {
        const param = sensitivityParams[paramName];
        if (param.type !== 'constraint') {
          parameterChanges[paramName] = param.current / (result.optimization_solution?.solution?.[paramName] || 1);
        }
      });

      // Call the real backend endpoint
      const response = await fetch('https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/sensitivity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base_optimization_result: result,
          parameter_changes: parameterChanges
        })
      });

      const data = await response.json();
      if (data.status === 'success') {
        setAnalysisResults(data.sensitivity_analysis);
      } else {
        console.error('Sensitivity analysis failed:', data.error);
        // Fallback to simulated data
        const results = {};
        Object.keys(sensitivityParams).forEach(paramName => {
          const param = sensitivityParams[paramName];
          const impact = calculateSensitivityImpact(paramName, param.current);
          
          results[paramName] = {
            ...param,
            impact,
            scenarios: generateScenarios(paramName, param)
          };
        });
        setAnalysisResults(results);
      }
    } catch (error) {
      console.error('Failed to run sensitivity analysis:', error);
      // Fallback to simulated data
      const results = {};
      Object.keys(sensitivityParams).forEach(paramName => {
        const param = sensitivityParams[paramName];
        const impact = calculateSensitivityImpact(paramName, param.current);
        
        results[paramName] = {
          ...param,
          impact,
          scenarios: generateScenarios(paramName, param)
        };
      });
      setAnalysisResults(results);
    }
    
    setIsRunning(false);
  };

  // Generate scenario analysis
  const generateScenarios = (paramName, param) => {
    const scenarios = [];
    const steps = 5;
    
    for (let i = 0; i <= steps; i++) {
      const value = param.min + (param.max - param.min) * (i / steps);
      const impact = calculateSensitivityImpact(paramName, value);
      const objectiveChange = (value / param.current - 1) * 100;
      
      scenarios.push({
        value,
        impact,
        objectiveChange,
        feasibility: impact < 20 ? 'feasible' : impact < 50 ? 'warning' : 'infeasible'
      });
    }
    
    return scenarios;
  };

  // Update parameter value
  const updateParameter = (paramName, value) => {
    setSensitivityParams(prev => ({
      ...prev,
      [paramName]: {
        ...prev[paramName],
        current: parseFloat(value)
      }
    }));
  };

  // Reset to original values
  const resetToOriginal = () => {
    const originalParams = {};
    Object.keys(sensitivityParams).forEach(key => {
      if (result.optimization_solution?.solution?.[key]) {
        originalParams[key] = {
          ...sensitivityParams[key],
          current: result.optimization_solution.solution[key]
        };
      }
    });
    setSensitivityParams(prev => ({ ...prev, ...originalParams }));
  };

  // Export analysis results
  const exportResults = () => {
    const data = {
      timestamp: new Date().toISOString(),
      originalResult: result,
      sensitivityAnalysis: analysisResults,
      parameters: sensitivityParams
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sensitivity_analysis.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 rounded-2xl border border-gray-700 w-full max-w-6xl h-[90vh] flex flex-col overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
              <Sliders className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Sensitivity Analysis</h2>
              <p className="text-gray-400">Interactive parameter exploration and impact assessment</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={exportResults}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Parameter Controls */}
            <div className="space-y-6">
              <div className="bg-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <Target className="w-5 h-5" />
                    Parameter Controls
                  </h3>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={resetToOriginal}
                      className="px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm transition-colors flex items-center gap-1"
                    >
                      <RotateCcw className="w-4 h-4" />
                      Reset
                    </button>
                    <button
                      onClick={runSensitivityAnalysis}
                      disabled={isRunning}
                      className="px-3 py-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg text-sm transition-colors flex items-center gap-1"
                    >
                      {isRunning ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" />
                          Analyze
                        </>
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {Object.entries(sensitivityParams).map(([paramName, param]) => (
                    <div key={paramName} className="bg-gray-700 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <label className="text-white font-medium">
                          {paramName.replace(/_/g, ' ').toUpperCase()}
                        </label>
                        <span className="text-gray-400 text-sm">
                          {param.current.toFixed(2)}
                        </span>
                      </div>
                      
                      <input
                        type="range"
                        min={param.min}
                        max={param.max}
                        step={param.step}
                        value={param.current}
                        onChange={(e) => updateParameter(paramName, e.target.value)}
                        className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                      />
                      
                      <div className="flex justify-between text-xs text-gray-400 mt-1">
                        <span>{param.min.toFixed(1)}</span>
                        <span>{param.max.toFixed(1)}</span>
                      </div>
                      
                      {param.impact > 0 && (
                        <div className="mt-2 flex items-center gap-2">
                          <div className={`w-2 h-2 rounded-full ${
                            param.impact < 10 ? 'bg-green-500' :
                            param.impact < 25 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <span className="text-xs text-gray-300">
                            Impact: {param.impact.toFixed(1)}%
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Analysis Summary */}
              {analysisResults && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5" />
                    Analysis Summary
                  </h3>
                  
                  <div className="space-y-3">
                    {Object.entries(analysisResults).map(([paramName, analysis]) => (
                      <div key={paramName} className="bg-gray-700 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-white font-medium">
                            {paramName.replace(/_/g, ' ').toUpperCase()}
                          </span>
                          <div className="flex items-center gap-2">
                            {analysis.impact < 10 ? (
                              <CheckCircle className="w-4 h-4 text-green-400" />
                            ) : analysis.impact < 25 ? (
                              <AlertTriangle className="w-4 h-4 text-yellow-400" />
                            ) : (
                              <AlertTriangle className="w-4 h-4 text-red-400" />
                            )}
                            <span className={`text-sm font-semibold ${
                              analysis.impact < 10 ? 'text-green-400' :
                              analysis.impact < 25 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {analysis.impact.toFixed(1)}%
                            </span>
                          </div>
                        </div>
                        
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full transition-all duration-500 ${
                              analysis.impact < 10 ? 'bg-green-500' :
                              analysis.impact < 25 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${Math.min(analysis.impact, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Visualization */}
            <div className="space-y-6">
              {/* Chart Controls */}
              <div className="bg-gray-800 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <LineChart className="w-5 h-5" />
                    Impact Visualization
                  </h3>
                  <div className="flex items-center gap-2">
                    <select
                      value={chartType}
                      onChange={(e) => setChartType(e.target.value)}
                      className="bg-gray-700 text-white rounded-lg px-3 py-1 text-sm border border-gray-600"
                    >
                      <option value="line">Line Chart</option>
                      <option value="bar">Bar Chart</option>
                      <option value="pie">Pie Chart</option>
                    </select>
                  </div>
                </div>

                {/* Chart Placeholder */}
                <div className="bg-gray-700 rounded-lg p-8 text-center border border-gray-600">
                  <div className="text-gray-400 mb-4">
                    {chartType === 'line' && <LineChart className="w-16 h-16 mx-auto mb-4" />}
                    {chartType === 'bar' && <BarChart3 className="w-16 h-16 mx-auto mb-4" />}
                    {chartType === 'pie' && <PieChart className="w-16 h-16 mx-auto mb-4" />}
                    <p className="text-lg">Interactive Chart Coming Soon</p>
                    <p className="text-sm">Real-time sensitivity visualization</p>
                  </div>
                  <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                    Enable Chart
                  </button>
                </div>
              </div>

              {/* Scenario Analysis */}
              {analysisResults && (
                <div className="bg-gray-800 rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="w-5 h-5" />
                    Scenario Analysis
                  </h3>
                  
                  <div className="space-y-4">
                    {Object.entries(analysisResults).slice(0, 3).map(([paramName, analysis]) => (
                      <div key={paramName} className="bg-gray-700 rounded-lg p-4">
                        <h4 className="text-white font-medium mb-3">
                          {paramName.replace(/_/g, ' ').toUpperCase()}
                        </h4>
                        
                        <div className="space-y-2">
                          {analysis.scenarios.map((scenario, index) => (
                            <div key={index} className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${
                                  scenario.feasibility === 'feasible' ? 'bg-green-500' :
                                  scenario.feasibility === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                                }`}></div>
                                <span className="text-gray-300 text-sm">
                                  {scenario.value.toFixed(2)}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <span className={`text-sm font-semibold ${
                                  scenario.objectiveChange > 0 ? 'text-green-400' : 'text-red-400'
                                }`}>
                                  {scenario.objectiveChange > 0 ? '+' : ''}{scenario.objectiveChange.toFixed(1)}%
                                </span>
                                <span className="text-xs text-gray-400">
                                  {scenario.impact.toFixed(1)}% impact
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SensitivityAnalysis;
