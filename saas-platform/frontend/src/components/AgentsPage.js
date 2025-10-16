import React, { useState, useEffect } from 'react';
import { ChevronLeft, MessageSquare, Code, Mic, Zap, Globe, Smartphone, Monitor, Search, Filter, Play, Download, Copy, ExternalLink } from 'lucide-react';

const AgentsPage = ({ onBack }) => {
  const [agents, setAgents] = useState([]);
  const [filteredAgents, setFilteredAgents] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedModality, setSelectedModality] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [loading, setLoading] = useState(true);

  // Mock data for internal AI agents
  const mockAgents = [
    {
      id: 1,
      name: 'Intent Classification Agent',
      description: 'Analyzes user queries to understand optimization goals and requirements',
      modality: 'Intent',
      status: 'active',
      capabilities: ['Natural Language Processing', 'Intent Recognition', 'Confidence Scoring', 'Context Analysis'],
      platforms: ['Claude 3.5 Sonnet', 'AI Platform'],
      icon: 'INT',
      color: 'bg-blue-500',
      features: ['Query understanding', 'Intent categorization', 'Confidence metrics', 'Reasoning explanation'],
      apiEndpoint: '/api/intent',
      documentation: 'https://docs.dcisionai.com/intent-agent',
      modelUsed: 'Claude 3.5 Sonnet',
      processingTime: '0.2-0.5s',
      accuracy: '95%'
    },
    {
      id: 2,
      name: 'Data Analysis Agent',
      description: 'Analyzes business data and assesses readiness for optimization',
      modality: 'Data',
      status: 'active',
      capabilities: ['Data Validation', 'Readiness Assessment', 'Entity Extraction', 'Assumption Generation'],
      platforms: ['Claude 3.5 Sonnet', 'AI Platform'],
      icon: 'DATA',
      color: 'bg-green-500',
      features: ['Data quality analysis', 'Readiness scoring', 'Entity identification', 'Assumption tracking'],
      apiEndpoint: '/api/data',
      documentation: 'https://docs.dcisionai.com/data-agent',
      modelUsed: 'Claude 3.5 Sonnet',
      processingTime: '0.3-0.8s',
      accuracy: '92%'
    },
    {
      id: 3,
      name: 'Model Building Agent',
      description: 'Creates mathematical optimization models based on intent and data analysis',
      modality: 'Model',
      status: 'active',
      capabilities: ['Mathematical Modeling', 'Variable Definition', 'Constraint Generation', 'Objective Setting'],
      platforms: ['Claude 3.5 Sonnet', 'AI Platform'],
      icon: 'MODEL',
      color: 'bg-purple-500',
      features: ['Model formulation', 'Variable creation', 'Constraint definition', 'Complexity assessment'],
      apiEndpoint: '/api/model',
      documentation: 'https://docs.dcisionai.com/model-agent',
      modelUsed: 'Claude 3.5 Sonnet',
      processingTime: '0.5-1.2s',
      accuracy: '88%'
    },
    {
      id: 4,
      name: 'Solver Agent',
      description: 'Executes mathematical optimization and provides decision recommendations',
      modality: 'Solver',
      status: 'active',
      capabilities: ['Mathematical Optimization', 'Solution Generation', 'Performance Analysis', 'Recommendation Engine'],
      platforms: ['PuLP CBC Solver', 'Claude 3.5 Sonnet'],
      icon: 'SOLVE',
      color: 'bg-orange-500',
      features: ['Optimization solving', 'Solution validation', 'Performance metrics', 'Recommendation generation'],
      apiEndpoint: '/api/solve',
      documentation: 'https://docs.dcisionai.com/solver-agent',
      modelUsed: 'PuLP CBC + Claude 3.5 Sonnet',
      processingTime: '0.1-2.0s',
      accuracy: '98%'
    },
    {
      id: 5,
      name: 'Agent Coordinator',
      description: 'Orchestrates the workflow between all agents and manages execution',
      modality: 'Coordination',
      status: 'active',
      capabilities: ['Workflow Orchestration', 'Agent Communication', 'Error Handling', 'Performance Monitoring'],
      platforms: ['Custom Logic', 'AI Platform'],
      icon: 'COORD',
      color: 'bg-indigo-500',
      features: ['Agent orchestration', 'Workflow management', 'Error recovery', 'Performance tracking'],
      apiEndpoint: '/api/coordinate',
      documentation: 'https://docs.dcisionai.com/coordinator-agent',
      modelUsed: 'Custom Logic',
      processingTime: '0.1-0.3s',
      accuracy: '99%'
    },
    {
      id: 6,
      name: 'Agent Memory Layer',
      description: 'Provides cross-session learning and pattern recognition capabilities',
      modality: 'Memory',
      status: 'active',
      capabilities: ['Pattern Recognition', 'Cross-session Learning', 'Insight Generation', 'Performance Optimization'],
      platforms: ['Custom Logic', 'AI Platform'],
      icon: 'MEM',
      color: 'bg-pink-500',
      features: ['Pattern caching', 'Learning algorithms', 'Insight generation', 'Performance optimization'],
      apiEndpoint: '/api/memory',
      documentation: 'https://docs.dcisionai.com/memory-agent',
      modelUsed: 'Custom Logic + Claude 3.5 Sonnet',
      processingTime: '0.05-0.2s',
      accuracy: '94%'
    },
    {
      id: 7,
      name: 'Predictive Model Cache',
      description: 'Intelligent caching system for 10-100x speed improvements',
      modality: 'Cache',
      status: 'active',
      capabilities: ['Intelligent Caching', 'Model Prediction', 'Speed Optimization', 'Cache Management'],
      platforms: ['Custom Logic', 'AI Platform'],
      icon: 'CACHE',
      color: 'bg-teal-500',
      features: ['Smart caching', 'Model prediction', 'Speed optimization', 'Cache invalidation'],
      apiEndpoint: '/api/cache',
      documentation: 'https://docs.dcisionai.com/cache-agent',
      modelUsed: 'Custom Logic',
      processingTime: '0.01-0.1s',
      accuracy: '96%'
    }
  ];

  const modalities = ['all', 'Intent', 'Data', 'Model', 'Solver', 'Coordination', 'Memory', 'Cache'];
  const statuses = ['all', 'active', 'beta', 'coming-soon'];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setAgents(mockAgents);
      setFilteredAgents(mockAgents);
      setLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    let filtered = agents;

    if (searchTerm) {
      filtered = filtered.filter(agent => 
        agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        agent.capabilities.some(cap => cap.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }

    if (selectedModality !== 'all') {
      filtered = filtered.filter(agent => agent.modality === selectedModality);
    }

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(agent => agent.status === selectedStatus);
    }

    setFilteredAgents(filtered);
  }, [searchTerm, selectedModality, selectedStatus, agents]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'beta': return 'bg-yellow-500/20 text-yellow-400';
      case 'coming-soon': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getModalityIcon = (modality) => {
    switch (modality) {
      case 'Chat': return 'CHAT';
      case 'SDK': return 'SDK';
      case 'Voice': return 'VOICE';
      case 'Mobile': return 'MOBILE';
      case 'Integration': return 'INTEG';
      case 'CLI': return 'CLI';
      default: return 'AGENT';
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e07a4a] mx-auto mb-4"></div>
          <p className="text-gray-400">Loading available agents...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white">AI Agents</h1>
            <p className="text-gray-400">Internal AI agents that power the decision support system</p>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search AI agents by name, capability, or modality..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
            />
          </div>
          <select
            value={selectedModality}
            onChange={(e) => setSelectedModality(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
          >
            {modalities.map(modality => (
              <option key={modality} value={modality}>
                {modality === 'all' ? 'All Modalities' : modality}
              </option>
            ))}
          </select>
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
          >
            {statuses.map(status => (
              <option key={status} value={status}>
                {status === 'all' ? 'All Status' : status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredAgents.map((agent) => (
          <div key={agent.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 min-h-[400px] flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-lg ${agent.color} flex items-center justify-center text-white text-xs font-bold`}>
                  {agent.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-2">{agent.name}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed break-words">{agent.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(agent.status)}`}>
                  {agent.status}
                </span>
                <span className="text-gray-500 text-xs">
                  {getModalityIcon(agent.modality)} {agent.modality}
                </span>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Capabilities:</div>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((capability, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                    {capability}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Platforms & Models:</div>
              <div className="flex flex-wrap gap-1">
                {agent.platforms.map((platform, index) => (
                  <span key={index} className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded">
                    {platform}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Performance Metrics:</div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="bg-gray-700 p-2 rounded text-center">
                  <div className="text-gray-400">Model</div>
                  <div className="text-white font-medium">{agent.modelUsed}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded text-center">
                  <div className="text-gray-400">Speed</div>
                  <div className="text-white font-medium">{agent.processingTime}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded text-center">
                  <div className="text-gray-400">Accuracy</div>
                  <div className="text-white font-medium">{agent.accuracy}</div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Features:</div>
              <ul className="text-xs text-gray-400 space-y-1">
                {agent.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="w-1 h-1 bg-gray-500 rounded-full"></span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-700 mt-auto">
              <div className="flex items-center gap-2">
                <span className="text-green-400 text-xs">ACTIVE</span>
                <span className="text-blue-400 text-xs">AI-POWERED</span>
                <span className="text-purple-400 text-xs">FAST</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(agent.apiEndpoint)}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  title="Copy API endpoint"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => window.open(agent.documentation, '_blank')}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  title="View documentation"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
                <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                  <Play className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredAgents.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-2">No agents found</div>
          <div className="text-gray-500 text-sm">Try adjusting your search or filter criteria</div>
        </div>
      )}
    </div>
  );
};

export default AgentsPage;
