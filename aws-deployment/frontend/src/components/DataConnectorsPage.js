import React, { useState, useEffect } from 'react';
import { ChevronLeft, Plus, Search, Filter, Database, Globe, Zap, Settings, CheckCircle, AlertCircle, Clock, ExternalLink, Copy, Play, Trash2 } from 'lucide-react';

const DataConnectorsPage = ({ onBack }) => {
  const [connectors, setConnectors] = useState([]);
  const [filteredConnectors, setFilteredConnectors] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [loading, setLoading] = useState(true);
  const [showNewConnectorModal, setShowNewConnectorModal] = useState(false);

  // Mock data for data connectors
  const mockConnectors = [
    {
      id: 1,
      name: 'Salesforce CRM',
      description: 'Customer relationship management data and analytics',
      category: 'CRM',
      status: 'connected',
      type: 'API',
      icon: 'SF',
      color: 'bg-blue-500',
      lastSync: '2 minutes ago',
      dataPoints: 1250,
      endpoints: ['/api/accounts', '/api/contacts', '/api/opportunities'],
      features: ['Real-time sync', 'Custom fields', 'Bulk operations'],
      documentation: 'https://docs.dcisionai.com/salesforce-connector'
    },
    {
      id: 2,
      name: 'MySQL Database',
      description: 'Production database with operational data',
      category: 'Database',
      status: 'connected',
      type: 'Database',
      icon: 'DB',
      color: 'bg-orange-500',
      lastSync: '5 minutes ago',
      dataPoints: 50000,
      endpoints: ['production_db', 'analytics_db'],
      features: ['Query optimization', 'Data validation', 'Backup sync'],
      documentation: 'https://docs.dcisionai.com/mysql-connector'
    },
    {
      id: 3,
      name: 'Google Analytics',
      description: 'Website traffic and user behavior analytics',
      category: 'Analytics',
      status: 'connected',
      type: 'API',
      icon: 'GA',
      color: 'bg-green-500',
      lastSync: '1 hour ago',
      dataPoints: 8500,
      endpoints: ['/api/analytics', '/api/reports'],
      features: ['Real-time data', 'Custom metrics', 'Historical data'],
      documentation: 'https://docs.dcisionai.com/google-analytics-connector'
    },
    {
      id: 4,
      name: 'Slack Workspace',
      description: 'Team communication and collaboration data',
      category: 'Communication',
      status: 'connected',
      type: 'API',
      icon: 'SL',
      color: 'bg-purple-500',
      lastSync: '30 minutes ago',
      dataPoints: 3200,
      endpoints: ['/api/messages', '/api/channels', '/api/users'],
      features: ['Message analysis', 'Channel insights', 'User activity'],
      documentation: 'https://docs.dcisionai.com/slack-connector'
    },
    {
      id: 5,
      name: 'AWS S3 Bucket',
      description: 'Cloud storage with business documents and files',
      category: 'Storage',
      status: 'connected',
      type: 'Storage',
      icon: 'S3',
      color: 'bg-yellow-500',
      lastSync: '15 minutes ago',
      dataPoints: 1200,
      endpoints: ['documents-bucket', 'reports-bucket'],
      features: ['File processing', 'Metadata extraction', 'Version control'],
      documentation: 'https://docs.dcisionai.com/s3-connector'
    },
    {
      id: 6,
      name: 'HubSpot Marketing',
      description: 'Marketing automation and lead management',
      category: 'Marketing',
      status: 'error',
      type: 'API',
      icon: 'HS',
      color: 'bg-red-500',
      lastSync: '2 hours ago',
      dataPoints: 0,
      endpoints: ['/api/contacts', '/api/campaigns'],
      features: ['Lead scoring', 'Campaign tracking', 'Email analytics'],
      documentation: 'https://docs.dcisionai.com/hubspot-connector',
      errorMessage: 'API key expired - please update credentials'
    },
    {
      id: 7,
      name: 'PostgreSQL Analytics',
      description: 'Data warehouse with business intelligence data',
      category: 'Database',
      status: 'pending',
      type: 'Database',
      icon: 'PG',
      color: 'bg-indigo-500',
      lastSync: 'Never',
      dataPoints: 0,
      endpoints: ['analytics_db'],
      features: ['Complex queries', 'Data modeling', 'Performance monitoring'],
      documentation: 'https://docs.dcisionai.com/postgresql-connector'
    },
    {
      id: 8,
      name: 'Microsoft Excel',
      description: 'Spreadsheet data and business reports',
      category: 'File',
      status: 'connected',
      type: 'File',
      icon: 'XL',
      color: 'bg-green-600',
      lastSync: '1 day ago',
      dataPoints: 450,
      endpoints: ['reports.xlsx', 'data.xlsx'],
      features: ['Sheet parsing', 'Formula evaluation', 'Chart data'],
      documentation: 'https://docs.dcisionai.com/excel-connector'
    }
  ];

  const categories = ['all', 'CRM', 'Database', 'Analytics', 'Communication', 'Storage', 'Marketing', 'File'];
  const statuses = ['all', 'connected', 'error', 'pending'];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setConnectors(mockConnectors);
      setFilteredConnectors(mockConnectors);
      setLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    let filtered = connectors;

    if (searchTerm) {
      filtered = filtered.filter(connector => 
        connector.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        connector.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        connector.category.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(connector => connector.category === selectedCategory);
    }

    if (selectedStatus !== 'all') {
      filtered = filtered.filter(connector => connector.status === selectedStatus);
    }

    setFilteredConnectors(filtered);
  }, [searchTerm, selectedCategory, selectedStatus, connectors]);

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected': return 'bg-green-500/20 text-green-400';
      case 'error': return 'bg-red-500/20 text-red-400';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return <CheckCircle className="w-4 h-4" />;
      case 'error': return <AlertCircle className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e07a4a] mx-auto mb-4"></div>
          <p className="text-gray-400">Loading data connectors...</p>
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
            <h1 className="text-2xl font-bold text-white">Data Connectors</h1>
            <p className="text-gray-400">Connect external data sources and APIs to power your decisions</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowNewConnectorModal(true)}
              className="bg-gradient-to-r from-[#e07a4a] to-[#d2691e] hover:from-[#d2691e] hover:to-[#b8860b] text-white px-4 py-2 rounded-lg transition-all duration-200 hover:shadow-lg hover:shadow-[#e07a4a]/25 flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Connector
            </button>
            <button className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Configure
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search connectors by name, description, or category..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
          >
            {categories.map(category => (
              <option key={category} value={category}>
                {category === 'all' ? 'All Categories' : category}
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

      {/* Connectors Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredConnectors.map((connector) => (
          <div key={connector.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 min-h-[400px] flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-12 h-12 rounded-lg ${connector.color} flex items-center justify-center text-white text-xs font-bold`}>
                  {connector.icon}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 break-words">{connector.name}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed break-words">{connector.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs flex items-center gap-1 ${getStatusColor(connector.status)}`}>
                  {getStatusIcon(connector.status)}
                  {connector.status}
                </span>
                <span className="text-gray-500 text-xs">
                  {connector.type}
                </span>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Connection Details:</div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-gray-700 p-2 rounded text-center">
                  <div className="text-gray-400">Data Points</div>
                  <div className="text-white font-medium">{connector.dataPoints.toLocaleString()}</div>
                </div>
                <div className="bg-gray-700 p-2 rounded text-center">
                  <div className="text-gray-400">Last Sync</div>
                  <div className="text-white font-medium">{connector.lastSync}</div>
                </div>
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Endpoints:</div>
              <div className="flex flex-wrap gap-1">
                {connector.endpoints.map((endpoint, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                    {endpoint}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-2">Features:</div>
              <ul className="text-xs text-gray-400 space-y-1">
                {connector.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <span className="w-1 h-1 bg-gray-500 rounded-full"></span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>

            {connector.errorMessage && (
              <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded-lg">
                <div className="text-red-400 text-xs font-medium mb-1">Connection Error:</div>
                <div className="text-red-300 text-xs">{connector.errorMessage}</div>
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-gray-700 mt-auto">
              <div className="flex items-center gap-2">
                <span className="text-blue-400 text-xs">API</span>
                <span className="text-green-400 text-xs">SYNC</span>
                <span className="text-purple-400 text-xs">REAL-TIME</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(connector.documentation)}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  title="Copy documentation URL"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => window.open(connector.documentation, '_blank')}
                  className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white"
                  title="View documentation"
                >
                  <ExternalLink className="w-4 h-4" />
                </button>
                <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                  <Play className="w-4 h-4" />
                </button>
                <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredConnectors.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-lg mb-2">No connectors found</div>
          <div className="text-gray-500 text-sm">Try adjusting your search or filter criteria</div>
        </div>
      )}
    </div>
  );
};

export default DataConnectorsPage;
