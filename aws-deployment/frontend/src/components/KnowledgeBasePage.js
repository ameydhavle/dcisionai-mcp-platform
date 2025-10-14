import React, { useState, useEffect } from 'react';
import { ChevronLeft, Plus, Upload, FileText, Database, Settings, Trash2, Edit, Eye, Search, Filter, Calendar, Users, HardDrive } from 'lucide-react';

const KnowledgeBasePage = ({ onBack }) => {
  const [knowledgeBases, setKnowledgeBases] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedKB, setSelectedKB] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  // Mock data for knowledge bases
  const mockKnowledgeBases = [
    {
      id: 1,
      name: 'Business Operations Manual',
      description: 'Complete business procedures and best practices',
      status: 'active',
      documents: 45,
      size: '2.3 GB',
      lastUpdated: '2025-10-13',
      createdBy: 'John Smith',
      embeddings: 125000,
      dataSource: 'Cloud Storage',
      region: 'us-east-1'
    },
    {
      id: 2,
      name: 'Quality Control Standards',
      description: 'ISO standards and quality control procedures',
      status: 'active',
      documents: 23,
      size: '890 MB',
      lastUpdated: '2025-10-12',
      createdBy: 'Sarah Johnson',
      embeddings: 67000,
      dataSource: 'Cloud Storage',
      region: 'us-east-1'
    },
    {
      id: 3,
      name: 'Supply Chain Documentation',
      description: 'Vendor contracts and supply chain procedures',
      status: 'processing',
      documents: 12,
      size: '456 MB',
      lastUpdated: '2025-10-11',
      createdBy: 'Mike Chen',
      embeddings: 34000,
      dataSource: 'Cloud Storage',
      region: 'us-east-1'
    },
    {
      id: 4,
      name: 'Financial Reports Archive',
      description: 'Historical financial data and reports',
      status: 'active',
      documents: 78,
      size: '1.8 GB',
      lastUpdated: '2025-10-10',
      createdBy: 'Lisa Wang',
      embeddings: 89000,
      dataSource: 'Cloud Storage',
      region: 'us-east-1'
    },
    {
      id: 5,
      name: 'Safety Protocols',
      description: 'Workplace safety guidelines and incident reports',
      status: 'error',
      documents: 8,
      size: '234 MB',
      lastUpdated: '2025-10-09',
      createdBy: 'David Brown',
      embeddings: 12000,
      dataSource: 'Cloud Storage',
      region: 'us-east-1'
    }
  ];

  const [newKB, setNewKB] = useState({
    name: '',
    description: '',
    dataSource: 'cloud',
    bucketName: '',
    region: 'us-east-1'
  });

  const [uploadData, setUploadData] = useState({
    knowledgeBaseId: '',
    files: null,
    dataSource: 'upload'
  });

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setKnowledgeBases(mockKnowledgeBases);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredKBs = knowledgeBases.filter(kb => {
    const matchesSearch = kb.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         kb.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || kb.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'processing': return 'bg-yellow-500/20 text-yellow-400';
      case 'error': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return '🟢';
      case 'processing': return '🟡';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  const handleCreateKB = () => {
    // Simulate API call
    const newKBData = {
      id: knowledgeBases.length + 1,
      ...newKB,
      status: 'processing',
      documents: 0,
      size: '0 MB',
      lastUpdated: new Date().toISOString().split('T')[0],
      createdBy: 'Current User',
      embeddings: 0,
      dataSource: newKB.dataSource === 'cloud' ? 'Cloud Storage' : 'Upload',
      region: newKB.region
    };
    
    setKnowledgeBases([...knowledgeBases, newKBData]);
    setShowCreateModal(false);
    setNewKB({ name: '', description: '', dataSource: 'cloud', bucketName: '', region: 'us-east-1' });
  };

  const handleUploadFiles = () => {
    setUploading(true);
    // Simulate upload process
    setTimeout(() => {
      setUploading(false);
      setShowUploadModal(false);
      setUploadData({ knowledgeBaseId: '', files: null, dataSource: 'upload' });
    }, 2000);
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e07a4a] mx-auto mb-4"></div>
          <p className="text-gray-400">Loading knowledge bases...</p>
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
            <h1 className="text-2xl font-bold text-white">Knowledge Base Management</h1>
            <p className="text-gray-400">Manage your data sources and documents for AI analysis</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-[#e07a4a] hover:bg-[#d2691e] text-white rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Knowledge Base
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors border border-gray-700"
          >
            <Upload className="w-4 h-4" />
            Upload Documents
          </button>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search knowledge bases..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
            />
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="processing">Processing</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {/* Knowledge Bases Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredKBs.map((kb) => (
          <div key={kb.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 min-h-[300px] flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-r from-[#e07a4a] to-[#d2691e] rounded-lg flex items-center justify-center">
                  <Database className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 break-words">{kb.name}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed break-words">{kb.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(kb.status)}`}>
                  {getStatusIcon(kb.status)} {kb.status}
                </span>
                <div className="flex gap-1">
                  <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1 hover:bg-gray-700 rounded text-gray-400 hover:text-white">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <FileText className="w-4 h-4" />
                <span>{kb.documents} documents</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <HardDrive className="w-4 h-4" />
                <span>{kb.size}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Database className="w-4 h-4" />
                <span>{kb.embeddings.toLocaleString()} embeddings</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <Calendar className="w-4 h-4" />
                <span>{kb.lastUpdated}</span>
              </div>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-gray-700">
              <div className="text-xs text-gray-500">
                Created by {kb.createdBy} • {kb.dataSource} • {kb.region}
              </div>
              <button className="text-red-400 hover:text-red-300 text-sm">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Knowledge Base Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-white mb-4">Create Knowledge Base</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Name</label>
                <input
                  type="text"
                  value={newKB.name}
                  onChange={(e) => setNewKB({...newKB, name: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                  placeholder="Enter knowledge base name"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-300 mb-2">Description</label>
                <textarea
                  value={newKB.description}
                  onChange={(e) => setNewKB({...newKB, description: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                  rows="3"
                  placeholder="Describe the knowledge base"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-300 mb-2">Data Source</label>
                <select
                  value={newKB.dataSource}
                  onChange={(e) => setNewKB({...newKB, dataSource: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                >
                  <option value="cloud">Cloud Storage</option>
                  <option value="upload">File Upload</option>
                </select>
              </div>
              
              {newKB.dataSource === 'cloud' && (
                <>
                  <div>
                    <label className="block text-sm text-gray-300 mb-2">Storage Bucket Name</label>
                    <input
                      type="text"
                      value={newKB.bucketName}
                      onChange={(e) => setNewKB({...newKB, bucketName: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                      placeholder="my-knowledge-base-bucket"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm text-gray-300 mb-2">Cloud Region</label>
                    <select
                      value={newKB.region}
                      onChange={(e) => setNewKB({...newKB, region: e.target.value})}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                    >
                      <option value="us-east-1">US East (N. Virginia)</option>
                      <option value="us-west-2">US West (Oregon)</option>
                      <option value="eu-west-1">Europe (Ireland)</option>
                      <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                    </select>
                  </div>
                </>
              )}
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateKB}
                disabled={!newKB.name || !newKB.description}
                className="flex-1 px-4 py-2 bg-[#e07a4a] hover:bg-[#d2691e] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Upload Documents Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
            <h2 className="text-xl font-bold text-white mb-4">Upload Documents</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-300 mb-2">Knowledge Base</label>
                <select
                  value={uploadData.knowledgeBaseId}
                  onChange={(e) => setUploadData({...uploadData, knowledgeBaseId: e.target.value})}
                  className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
                >
                  <option value="">Select knowledge base</option>
                  {knowledgeBases.filter(kb => kb.status === 'active').map(kb => (
                    <option key={kb.id} value={kb.id}>{kb.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-300 mb-2">Files</label>
                <div className="border-2 border-dashed border-gray-600 rounded-lg p-6 text-center">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">Drop files here or click to browse</p>
                  <p className="text-gray-500 text-xs mt-1">Supports PDF, DOC, TXT, CSV</p>
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt,.csv"
                    onChange={(e) => setUploadData({...uploadData, files: e.target.files})}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <span className="text-[#e07a4a] hover:text-[#d2691e] text-sm">Browse files</span>
                  </label>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowUploadModal(false)}
                className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleUploadFiles}
                disabled={!uploadData.knowledgeBaseId || !uploadData.files || uploading}
                className="flex-1 px-4 py-2 bg-[#e07a4a] hover:bg-[#d2691e] text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default KnowledgeBasePage;
