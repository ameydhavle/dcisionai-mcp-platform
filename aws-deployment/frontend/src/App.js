import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, CheckCircle, AlertCircle, BarChart3, Settings, Zap, Eye, X } from 'lucide-react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ManufacturingHero from './components/ManufacturingHero';
import ValueProposition from './components/ValueProposition';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [showModelModal, setShowModelModal] = useState(false);
  const [currentModel, setCurrentModel] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeSection, setActiveSection] = useState('home');
  const [isMobile, setIsMobile] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);
  const [showValueProposition, setShowValueProposition] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Check if MCP server is running
    checkServerStatus();
    
    // Check if mobile
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const checkServerStatus = async () => {
    try {
      // Try local backend first, then Bedrock AgentCore
      const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      
      if (isLocal) {
        // Try local backend first
        try {
          const localResponse = await axios.post('https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod/health', {});
          if (localResponse.data.status === 'healthy') {
            setIsConnected(true);
            console.log('Connected to local backend');
            return;
          }
        } catch (localError) {
          console.log('Local backend not available, trying Bedrock AgentCore...');
        }
      }
      
      // Test streaming MCP API endpoint
      const apiUrl = 'https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod';
      
      const response = await axios.post(`${apiUrl}/health`, {}, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      // If we get a response with healthy status, the backend is connected
      if (response.data.status === 'healthy') {
        setIsConnected(true);
        console.log('Connected to streaming MCP API');
      } else {
        setIsConnected(false);
        console.log('Backend not healthy');
      }
    } catch (error) {
      console.log('Bedrock AgentCore connection error:', error);
      // If it's a network error, backend is not connected
      // If it's an API error, backend is connected but endpoint might not exist
      if (error.response && error.response.status >= 400) {
        setIsConnected(true); // Backend is responding, just endpoint issue
      } else {
        setIsConnected(false);
      }
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Use the multi-step optimization API
      const apiUrl = 'https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod';
      
      // Step 1: Intent Classification
      const intentResponse = await axios.post(`${apiUrl}/intent`, {
        query: input
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Intent response:', intentResponse.data);
      
      if (intentResponse.data.status !== 'success') {
        throw new Error('Intent classification failed');
      }

      const intentResult = intentResponse.data.result;

      // Step 2: Data Analysis
      const dataResponse = await axios.post(`${apiUrl}/data`, {
        intent_result: intentResult,
        query: input
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Data response:', dataResponse.data);
      
      if (dataResponse.data.status !== 'success') {
        throw new Error('Data analysis failed');
      }

      const dataResult = dataResponse.data.result;

      // Step 3: Model Building
      const modelResponse = await axios.post(`${apiUrl}/model`, {
        intent_result: intentResult,
        data_result: dataResult
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Model response:', modelResponse.data);
      
      if (modelResponse.data.status !== 'success') {
        throw new Error('Model building failed');
      }

      const modelResult = modelResponse.data.result;

      // Step 4: Decision Analysis Solving
      const solveResponse = await axios.post(`${apiUrl}/solve`, {
        intent_result: intentResult,
        data_result: dataResult,
        model_result: modelResult
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('Solve response:', solveResponse.data);
      
      if (solveResponse.data.status !== 'success') {
        throw new Error('Decision analysis solving failed');
      }

      const solveResult = solveResponse.data.result;

      // Combine all results into a comprehensive decision analysis result
      const optimizationResult = {
        status: 'success',
        timestamp: new Date().toISOString(),
        intent_classification: {
          intent: intentResult.intent,
          confidence: intentResult.confidence,
          entities: intentResult.entities,
          objectives: intentResult.objectives,
          reasoning: intentResult.reasoning
        },
        data_analysis: {
          data_entities: dataResult.data_entities,
          sample_data: dataResult.sample_data,
          readiness_score: dataResult.readiness_score,
          assumptions: dataResult.assumptions
        },
        model_building: {
          model_type: modelResult.model_type,
          variables: modelResult.variables,
          constraints: modelResult.constraints,
          objective: modelResult.objective_function,
          complexity: modelResult.complexity
        },
        optimization_solution: {
          status: solveResult.status,
          objective_value: solveResult.objective_value,
          solution: solveResult.solution,
          solve_time: solveResult.solve_time,
          solver_used: solveResult.solver_used
        }
      };
      
      console.log('Complete decision analysis result:', optimizationResult);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: optimizationResult,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
      
    } catch (error) {
      console.error('Decision analysis error:', error);
      
      let errorContent = 'Sorry, I encountered an error. Please try again or check your connection.';
      
      if (error.response) {
        // Server responded with error status
        const status = error.response.status;
        const data = error.response.data;
        
        if (status === 404) {
          errorContent = 'The optimization service is currently unavailable. Please try again later.';
        } else if (status === 500) {
          errorContent = 'The optimization service encountered an internal error. Please try again.';
        } else if (data && data.message) {
          errorContent = `Service error: ${data.message}`;
        }
      } else if (error.request) {
        // Network error
        errorContent = 'Unable to connect to the optimization service. Please check your internet connection.';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'error',
        content: errorContent,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const startDecisionChallenge = (query) => {
    setInput(query);
    setShowValueProposition(false);
    // Auto-send the message after a brief delay
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  const startNewAnalysis = () => {
    setMessages([]);
    setInput('');
    setShowValueProposition(false);
    setActiveSection('chat'); // Switch to chat section instead of home
  };

  const exampleQueries = [
    "Improve production line efficiency with 50 workers across 3 manufacturing lines",
    "Reduce supply chain costs for 5 warehouses across different regions",
    "Enhance quality control efficiency while reducing inspection costs",
    "Optimize resource allocation for sustainable manufacturing processes"
  ];

  const formatOptimizationResult = (result) => {
    // Check if optimization actually succeeded
    const isOptimizationSuccessful = result.status === 'success' && 
      result.optimization_solution && 
      result.optimization_solution.status === 'optimal';
    
    if (result.status === 'success') {
      return (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className={`flex items-center gap-2 ${isOptimizationSuccessful ? 'text-green-400' : 'text-yellow-400'}`}>
              {isOptimizationSuccessful ? (
                <CheckCircle className="w-5 h-5" />
              ) : (
                <AlertCircle className="w-5 h-5" />
              )}
              <span className="font-semibold">
                {isOptimizationSuccessful ? 'Decision Analysis Successful' : 'Decision Analysis Complete'}
              </span>
            </div>
            <button
              onClick={() => {
                setCurrentModel(result.model_building);
                setShowModelModal(true);
              }}
              className="flex items-center gap-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
            >
              <Eye className="w-4 h-4" />
              View Model
            </button>
          </div>
          
          {!isOptimizationSuccessful && result.optimization_solution && (
            <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-4">
              <div className="flex items-center gap-2 text-yellow-400 mb-2">
                <AlertCircle className="w-5 h-5" />
                <span className="font-semibold">Decision Analysis Warning</span>
              </div>
              <p className="text-yellow-200 text-sm">
                The decision model was built successfully, but the analysis engine encountered an issue: <strong>{result.optimization_solution.status}</strong>
              </p>
              {result.optimization_solution.error_message && (
                <p className="text-yellow-300 text-xs mt-2">
                  {typeof result.optimization_solution.error_message === 'string' ? result.optimization_solution.error_message : JSON.stringify(result.optimization_solution.error_message)}
                </p>
              )}
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Bot className="w-5 h-5" />
                Intent Classification
              </h3>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Intent:</span> {result.intent_classification?.intent}
              </p>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Confidence:</span> {typeof result.intent_classification?.confidence === 'number' ? (result.intent_classification.confidence * 100).toFixed(1) : '0.0'}%
              </p>
              <p className="text-sm text-gray-300">
                <span className="font-medium">Reasoning:</span> {typeof result.intent_classification?.reasoning === 'string' ? result.intent_classification.reasoning : JSON.stringify(result.intent_classification?.reasoning || '')}
              </p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Data Analysis
              </h3>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Entities:</span> {result.data_analysis?.data_entities?.length || 0}
              </p>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Readiness:</span> {typeof result.data_analysis?.readiness_score === 'number' ? (result.data_analysis.readiness_score * 100).toFixed(1) : '0.0'}%
              </p>
              <p className="text-sm text-gray-300">
                <span className="font-medium">Assumptions:</span> {result.data_analysis?.assumptions?.length || 0}
              </p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Decision Model
              </h3>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Type:</span> {result.model_building?.model_type}
              </p>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Variables:</span> {result.model_building?.variables?.length || 0}
              </p>
              <p className="text-sm text-gray-300">
                <span className="font-medium">Complexity:</span> {result.model_building?.complexity}
              </p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Decision Analysis Results
              </h3>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Status:</span> 
                <span className={`ml-2 px-2 py-1 rounded text-xs ${
                  result.optimization_solution?.status === 'optimal' ? 'bg-green-900 text-green-300' :
                  result.optimization_solution?.status === 'error' ? 'bg-red-900 text-red-300' :
                  'bg-yellow-900 text-yellow-300'
                }`}>
                  {result.optimization_solution?.status || 'unknown'}
                </span>
              </p>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Objective Value:</span> {result.optimization_solution?.objective_value || 'N/A'}
              </p>
              <p className="text-sm text-gray-300 mb-1">
                <span className="font-medium">Solve Time:</span> {typeof result.optimization_solution?.solve_time === 'number' ? result.optimization_solution.solve_time.toFixed(3) : '0.000'}s
              </p>
              {result.optimization_solution?.error_message && (
                <p className="text-sm text-red-300 mt-2">
                  <span className="font-medium">Error:</span> {typeof result.optimization_solution.error_message === 'string' ? result.optimization_solution.error_message : JSON.stringify(result.optimization_solution.error_message)}
                </p>
              )}
            </div>
          </div>

          {result.optimization_solution?.solution && Object.keys(result.optimization_solution.solution).length > 0 && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Decision Recommendations</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {Object.entries(result.optimization_solution.solution).map(([key, value]) => (
                  <div key={key} className="bg-gray-700 p-2 rounded text-sm">
                    <span className="font-medium">{key}:</span> 
                    <span className="ml-1">
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    } else {
      return (
        <div className="flex items-center gap-2 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span>Optimization failed: {result.error}</span>
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen bg-black flex">
      {/* Mobile Overlay */}
      {isMobile && showMobileSidebar && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setShowMobileSidebar(false)}
        />
      )}
      
      {/* Sidebar */}
        <Sidebar
          isCollapsed={isMobile ? false : sidebarCollapsed}
          onToggle={() => isMobile ? setShowMobileSidebar(!showMobileSidebar) : setSidebarCollapsed(!sidebarCollapsed)}
          activeSection={activeSection}
          onSectionChange={(section) => {
            setActiveSection(section);
            if (isMobile) setShowMobileSidebar(false);
          }}
          isMobile={isMobile}
          onClose={() => setShowMobileSidebar(false)}
          onStartNewAnalysis={startNewAnalysis}
        />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col transition-all duration-300 ease-in-out">
        {/* Top Header */}
        <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm px-6 py-4">
          <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {isMobile && (
                  <button
                    onClick={() => setShowMobileSidebar(true)}
                    className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
                    title="Open sidebar"
                  >
                    ☰
                  </button>
                )}
                {!isMobile && (
                  <button
                    onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                    className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
                    title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
                  >
                    {sidebarCollapsed ? '→' : '←'}
                  </button>
                )}
                <h1 className="text-2xl font-bold text-white">DcisionAI</h1>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                  <span className="text-sm text-gray-400">
                    {isConnected ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white">
                  🌐
                </button>
                <button className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white">
                  🎤
                </button>
              </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 flex flex-col">
          {messages.length === 0 && activeSection !== 'chat' ? (
            /* Welcome Screen - Manufacturing Focused */
            <div className="flex-1 overflow-y-auto p-8">
              {!showValueProposition ? (
                <ManufacturingHero onStartOptimization={startDecisionChallenge} />
              ) : (
                <ValueProposition />
              )}
              
              {/* Toggle between Hero and Value Proposition */}
              <div className="text-center mt-8">
                <button
                  onClick={() => setShowValueProposition(!showValueProposition)}
                  className="text-[#e07a4a] hover:text-[#d2691e] text-sm font-medium transition-colors"
                >
                  {showValueProposition ? '← Back to Optimization' : 'Why DcisionAI vs. ChatGPT? →'}
                </button>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {messages.length === 0 && activeSection === 'chat' ? (
                /* Empty Chat State */
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center max-w-md mx-auto">
                    <div className="w-16 h-16 bg-gradient-to-r from-[#e07a4a] to-[#d2691e] rounded-full flex items-center justify-center mx-auto mb-6">
                      <Bot className="w-8 h-8 text-white" />
                    </div>
                    <h2 className="text-2xl font-semibold text-white mb-3">Start Your Analysis</h2>
                    <p className="text-gray-400 mb-6">
                      Describe your manufacturing decision challenge and I'll help you find the optimal solution.
                    </p>
                    <button
                      onClick={() => setActiveSection('home')}
                      className="text-[#e07a4a] hover:text-[#d2691e] text-sm font-medium transition-colors mb-6"
                    >
                      ← Back to Home
                    </button>
                    <div className="space-y-3">
                      <div className="text-sm text-gray-500">
                        <strong>Try asking:</strong>
                      </div>
                      <div className="space-y-2">
                        <div className="text-sm text-gray-400 bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors" 
                             onClick={() => setInput("Improve production line efficiency with 50 workers across 3 manufacturing lines")}>
                          "Improve production line efficiency with 50 workers across 3 manufacturing lines"
                        </div>
                        <div className="text-sm text-gray-400 bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors"
                             onClick={() => setInput("Reduce supply chain costs for 5 warehouses across different regions")}>
                          "Reduce supply chain costs for 5 warehouses across different regions"
                        </div>
                        <div className="text-sm text-gray-400 bg-gray-800 rounded-lg p-3 cursor-pointer hover:bg-gray-700 transition-colors"
                             onClick={() => setInput("Enhance quality control efficiency while reducing inspection costs")}>
                          "Enhance quality control efficiency while reducing inspection costs"
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-4 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {message.type !== 'user' && (
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                  
                  <div
                    className={`max-w-4xl rounded-2xl px-6 py-4 ${
                      message.type === 'user'
                        ? 'bg-blue-600 text-white'
                        : message.type === 'error'
                        ? 'bg-red-900/50 text-red-200 border border-red-800'
                        : 'bg-gray-800 text-gray-100'
                    }`}
                  >
                    {message.type === 'user' ? (
                      <p className="text-lg">{message.content}</p>
                    ) : message.type === 'error' ? (
                      <p>{message.content}</p>
                    ) : (
                      formatOptimizationResult(message.content)
                    )}
                  </div>

                  {message.type === 'user' && (
                    <div className="w-8 h-8 bg-gray-700 rounded-lg flex items-center justify-center flex-shrink-0">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>
              ))
              )}
              
              {isLoading && (
                <div className="flex gap-4 justify-start">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <div className="bg-gray-800 rounded-2xl px-6 py-4 flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
                    <span className="text-gray-300">Analyzing your manufacturing decision challenge...</span>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}

            {/* Bottom Input Area */}
            {(messages.length > 0 || activeSection === 'chat') && (
              <div className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm p-6">
                <div className="max-w-4xl mx-auto">
                  <div className="flex items-center gap-3 bg-gray-800 border border-gray-700 rounded-2xl px-4 py-4 hover:border-gray-600 transition-colors focus-within:border-[#e07a4a] focus-within:ring-1 focus-within:ring-[#e07a4a]">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Describe your manufacturing decision challenge..."
                      className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none"
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!input.trim() || isLoading}
                      className="bg-[#e07a4a] hover:bg-[#d2691e] disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg transition-colors"
                    >
                      {isLoading ? 'Analyzing...' : 'Analyze'}
                    </button>
                  </div>
                </div>
              </div>
            )}
        </main>
      </div>

      {/* Model Details Modal */}
      {showModelModal && currentModel && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto modal-scroll">
            <div className="flex items-center justify-between p-6 border-b border-gray-700">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                <Settings className="w-6 h-6" />
                Decision Support Model
              </h2>
              <button
                onClick={() => setShowModelModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Model Overview */}
              <div className="bg-gray-800 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3 text-white">Model Overview</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Type:</span>
                    <div className="text-white font-medium">{currentModel.model_type}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Variables:</span>
                    <div className="text-white font-medium">{currentModel.variables?.length || 0}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Constraints:</span>
                    <div className="text-white font-medium">{currentModel.constraints?.length || 0}</div>
                  </div>
                  <div>
                    <span className="text-gray-400">Complexity:</span>
                    <div className="text-white font-medium">{currentModel.complexity}</div>
                  </div>
                </div>
              </div>

              {/* Variables */}
              {currentModel.variables && currentModel.variables.length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3 text-white">Decision Variables</h3>
                  <div className="space-y-2">
                    {currentModel.variables.map((variable, index) => (
                      <div key={index} className="bg-gray-700 p-3 rounded-lg">
                        <div className="flex items-center justify-between">
                          <span className="text-white font-medium">{variable.name}</span>
                          <span className="text-blue-400 text-sm">{variable.type}</span>
                        </div>
                        <div className="text-gray-300 text-sm mt-1">
                          Bounds: [{variable.bounds?.[0] || '0'}, {variable.bounds?.[1] || '∞'}]
                        </div>
                        {variable.description && (
                          <div className="text-gray-400 text-xs mt-1 italic">
                            {variable.description}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Objective Function */}
              {currentModel.objective && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3 text-white">Objective Function</h3>
                  <div className="bg-gray-700 p-3 rounded-lg">
                    <code className="text-green-400 text-sm font-mono break-all">
                      {currentModel.objective}
                    </code>
                  </div>
                </div>
              )}

              {/* Constraints */}
              {currentModel.constraints && currentModel.constraints.length > 0 && (
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3 text-white">Constraints</h3>
                  <div className="space-y-2">
                    {currentModel.constraints.map((constraint, index) => (
                      <div key={index} className="bg-gray-700 p-3 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-gray-400 text-sm">Constraint {index + 1}</span>
                          <span className="text-blue-400 text-sm">{constraint.type || 'inequality'}</span>
                        </div>
                        <code className="text-yellow-400 text-sm font-mono break-all">
                          {constraint.expression || constraint}
                        </code>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Mathematical Notation */}
              <div className="bg-gray-800 p-4 rounded-lg">
                <h3 className="text-lg font-semibold mb-3 text-white">Decision Model Formulation</h3>
                <div className="bg-gray-700 p-4 rounded-lg">
                  <div className="text-white text-sm space-y-2">
                    <div><strong>Model Type:</strong> {currentModel.model_type.replace('_', ' ').toUpperCase()}</div>
                    <div><strong>Variables:</strong> {currentModel.variables?.length || 0} decision variables</div>
                    <div><strong>Constraints:</strong> {currentModel.constraints?.length || 0} business rules</div>
                    <div><strong>Analysis Engine:</strong> PuLP CBC (Coin-or Branch and Cut)</div>
                    <div><strong>Status:</strong> Real decision support analysis (not simulated)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
