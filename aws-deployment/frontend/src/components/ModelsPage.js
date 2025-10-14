import React, { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Search, Filter, Zap, Clock, Users, Brain } from 'lucide-react';

const ModelsPage = ({ onBack }) => {
  const [models, setModels] = useState([]);
  const [filteredModels, setFilteredModels] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  
  const modelsPerPage = 12;

  // Mock data for available models (in real implementation, this would come from an API)
  const mockModels = [
    // Anthropic Models
    { id: 1, name: 'Claude 3.5 Sonnet', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Most capable model for complex reasoning and analysis', capabilities: ['Text Generation', 'Analysis', 'Reasoning'], inputTokens: 200000, outputTokens: 8192, price: '$3.00/1M input, $15.00/1M output' },
    { id: 2, name: 'Claude 3.5 Haiku', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Fast and efficient model for quick tasks', capabilities: ['Text Generation', 'Quick Analysis'], inputTokens: 200000, outputTokens: 8192, price: '$0.25/1M input, $1.25/1M output' },
    { id: 3, name: 'Claude 3 Opus', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Most powerful model for complex tasks', capabilities: ['Text Generation', 'Complex Analysis', 'Code Generation'], inputTokens: 200000, outputTokens: 4096, price: '$15.00/1M input, $75.00/1M output' },
    { id: 4, name: 'Claude 3 Sonnet', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Balanced performance and cost', capabilities: ['Text Generation', 'Analysis'], inputTokens: 200000, outputTokens: 4096, price: '$3.00/1M input, $15.00/1M output' },
    { id: 5, name: 'Claude 3 Haiku', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Fast and cost-effective', capabilities: ['Text Generation', 'Quick Tasks'], inputTokens: 200000, outputTokens: 4096, price: '$0.25/1M input, $1.25/1M output' },
    { id: 6, name: 'Claude 2.1', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Previous generation model', capabilities: ['Text Generation', 'Analysis'], inputTokens: 200000, outputTokens: 4096, price: '$8.00/1M input, $24.00/1M output' },
    { id: 7, name: 'Claude 2.0', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Stable and reliable model', capabilities: ['Text Generation', 'Analysis'], inputTokens: 100000, outputTokens: 4096, price: '$8.00/1M input, $24.00/1M output' },
    { id: 8, name: 'Claude Instant 1.2', provider: 'Anthropic', category: 'Text Generation', status: 'active', description: 'Fast and lightweight model', capabilities: ['Text Generation', 'Quick Tasks'], inputTokens: 100000, outputTokens: 4096, price: '$0.80/1M input, $2.40/1M output' },

    // Amazon Models
    { id: 9, name: 'Titan Text G1 - Express', provider: 'Amazon', category: 'Text Generation', status: 'active', description: 'High-performance text generation', capabilities: ['Text Generation', 'Summarization'], inputTokens: 8000, outputTokens: 2048, price: '$0.0008/1K input, $0.0016/1K output' },
    { id: 10, name: 'Titan Text G1 - Lite', provider: 'Amazon', category: 'Text Generation', status: 'active', description: 'Lightweight text generation', capabilities: ['Text Generation', 'Quick Tasks'], inputTokens: 4000, outputTokens: 1024, price: '$0.0003/1K input, $0.0006/1K output' },
    { id: 11, name: 'Titan Text Embeddings G1 - Text', provider: 'Amazon', category: 'Embeddings', status: 'active', description: 'Text embedding generation', capabilities: ['Embeddings', 'Similarity Search'], inputTokens: 8000, outputTokens: 1536, price: '$0.0001/1K tokens' },
    { id: 12, name: 'Titan Multimodal Embeddings G1', provider: 'Amazon', category: 'Multimodal', status: 'active', description: 'Multimodal embedding generation', capabilities: ['Embeddings', 'Image Analysis'], inputTokens: 128, outputTokens: 1024, price: '$0.0001/1K tokens' },
    { id: 13, name: 'Titan Image Generator G1', provider: 'Amazon', category: 'Image Generation', status: 'active', description: 'AI image generation', capabilities: ['Image Generation', 'Creative Tasks'], inputTokens: 77, outputTokens: 1, price: '$0.008/image' },

    // AI21 Labs Models
    { id: 14, name: 'Jurassic-2 Ultra', provider: 'AI21 Labs', category: 'Text Generation', status: 'active', description: 'Most capable Jurassic model', capabilities: ['Text Generation', 'Complex Analysis'], inputTokens: 8000, outputTokens: 2048, price: '$12.50/1M input, $12.50/1M output' },
    { id: 15, name: 'Jurassic-2 Mid', provider: 'AI21 Labs', category: 'Text Generation', status: 'active', description: 'Balanced performance model', capabilities: ['Text Generation', 'Analysis'], inputTokens: 8000, outputTokens: 2048, price: '$8.75/1M input, $8.75/1M output' },
    { id: 16, name: 'Jurassic-2 Light', provider: 'AI21 Labs', category: 'Text Generation', status: 'active', description: 'Fast and efficient model', capabilities: ['Text Generation', 'Quick Tasks'], inputTokens: 8000, outputTokens: 2048, price: '$0.012/1K input, $0.012/1K output' },

    // Cohere Models
    { id: 17, name: 'Command', provider: 'Cohere', category: 'Text Generation', status: 'active', description: 'Instruction-following model', capabilities: ['Text Generation', 'Instructions'], inputTokens: 4000, outputTokens: 1024, price: '$1.00/1M input, $2.00/1M output' },
    { id: 18, name: 'Command Light', provider: 'Cohere', category: 'Text Generation', status: 'active', description: 'Lightweight command model', capabilities: ['Text Generation', 'Quick Commands'], inputTokens: 4000, outputTokens: 1024, price: '$0.30/1M input, $0.60/1M output' },
    { id: 19, name: 'Embed English', provider: 'Cohere', category: 'Embeddings', status: 'active', description: 'English text embeddings', capabilities: ['Embeddings', 'English Text'], inputTokens: 512, outputTokens: 1024, price: '$0.10/1M tokens' },
    { id: 20, name: 'Embed Multilingual', provider: 'Cohere', category: 'Embeddings', status: 'active', description: 'Multilingual text embeddings', capabilities: ['Embeddings', 'Multilingual'], inputTokens: 512, outputTokens: 1024, price: '$0.10/1M tokens' },

    // Meta Models
    { id: 21, name: 'Llama 2 70B Chat', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Large conversational model', capabilities: ['Text Generation', 'Chat', 'Analysis'], inputTokens: 4000, outputTokens: 2048, price: '$0.65/1M input, $0.65/1M output' },
    { id: 22, name: 'Llama 2 13B Chat', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Medium conversational model', capabilities: ['Text Generation', 'Chat'], inputTokens: 4000, outputTokens: 2048, price: '$0.35/1M input, $0.35/1M output' },
    { id: 23, name: 'Llama 2 7B Chat', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Small conversational model', capabilities: ['Text Generation', 'Chat'], inputTokens: 4000, outputTokens: 2048, price: '$0.20/1M input, $0.20/1M output' },
    { id: 24, name: 'Llama 2 70B', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Large base model', capabilities: ['Text Generation', 'Analysis'], inputTokens: 4000, outputTokens: 2048, price: '$0.65/1M input, $0.65/1M output' },
    { id: 25, name: 'Llama 2 13B', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Medium base model', capabilities: ['Text Generation'], inputTokens: 4000, outputTokens: 2048, price: '$0.35/1M input, $0.35/1M output' },
    { id: 26, name: 'Llama 2 7B', provider: 'Meta', category: 'Text Generation', status: 'active', description: 'Small base model', capabilities: ['Text Generation'], inputTokens: 4000, outputTokens: 2048, price: '$0.20/1M input, $0.20/1M output' },

    // Stability AI Models
    { id: 27, name: 'Stable Diffusion XL', provider: 'Stability AI', category: 'Image Generation', status: 'active', description: 'High-quality image generation', capabilities: ['Image Generation', 'Creative Tasks'], inputTokens: 77, outputTokens: 1, price: '$0.004/image' },
    { id: 28, name: 'Stable Diffusion XL Base', provider: 'Stability AI', category: 'Image Generation', status: 'active', description: 'Base image generation model', capabilities: ['Image Generation'], inputTokens: 77, outputTokens: 1, price: '$0.004/image' },

    // Add more models to reach 118...
    // ... (continuing with more models from various providers)
  ];

  const providers = ['all', 'Anthropic', 'Amazon', 'AI21 Labs', 'Cohere', 'Meta', 'Stability AI'];
  const categories = ['all', 'Text Generation', 'Embeddings', 'Image Generation', 'Multimodal'];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setModels(mockModels);
      setFilteredModels(mockModels);
      setLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    let filtered = models;

    if (searchTerm) {
      filtered = filtered.filter(model => 
        model.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        model.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (selectedProvider !== 'all') {
      filtered = filtered.filter(model => model.provider === selectedProvider);
    }

    if (selectedCategory !== 'all') {
      filtered = filtered.filter(model => model.category === selectedCategory);
    }

    setFilteredModels(filtered);
    setCurrentPage(1);
  }, [searchTerm, selectedProvider, selectedCategory, models]);

  const totalPages = Math.ceil(filteredModels.length / modelsPerPage);
  const startIndex = (currentPage - 1) * modelsPerPage;
  const endIndex = startIndex + modelsPerPage;
  const currentModels = filteredModels.slice(startIndex, endIndex);

  const getProviderColor = (provider) => {
    const colors = {
      'Anthropic': 'bg-orange-500',
      'Amazon': 'bg-yellow-500',
      'AI21 Labs': 'bg-blue-500',
      'Cohere': 'bg-purple-500',
      'Meta': 'bg-indigo-500',
      'Stability AI': 'bg-green-500'
    };
    return colors[provider] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#e07a4a] mx-auto mb-4"></div>
          <p className="text-gray-400">Loading available models...</p>
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
            <h1 className="text-2xl font-bold text-white">Available AI Models</h1>
            <p className="text-gray-400">Explore {filteredModels.length} advanced AI models</p>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search models..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
            />
          </div>
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-[#e07a4a] focus:ring-1 focus:ring-[#e07a4a]"
          >
            {providers.map(provider => (
              <option key={provider} value={provider}>
                {provider === 'all' ? 'All Providers' : provider}
              </option>
            ))}
          </select>
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
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {currentModels.map((model) => (
          <div key={model.id} className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors border border-gray-700 min-h-[350px] flex flex-col">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-8 h-8 rounded-lg ${getProviderColor(model.provider)} flex items-center justify-center text-white text-sm font-bold`}>
                  {model.provider.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-white font-semibold mb-1 break-words">{model.name}</h3>
                  <p className="text-gray-400 text-sm">{model.provider}</p>
                </div>
              </div>
              <div className={`px-2 py-1 rounded-full text-xs ${
                model.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
              }`}>
                {model.status}
              </div>
            </div>
            
            <p className="text-gray-300 text-sm mb-4 leading-relaxed break-words flex-1">{model.description}</p>
            
            <div className="space-y-2 mb-4">
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Brain className="w-3 h-3" />
                <span>{model.category}</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Clock className="w-3 h-3" />
                <span>{model.inputTokens.toLocaleString()} input tokens</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-gray-400">
                <Zap className="w-3 h-3" />
                <span>{model.outputTokens.toLocaleString()} output tokens</span>
              </div>
            </div>

            <div className="mb-4">
              <div className="text-xs text-gray-500 mb-1">Capabilities:</div>
              <div className="flex flex-wrap gap-1">
                {model.capabilities.map((capability, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-700 text-gray-300 text-xs rounded">
                    {capability}
                  </span>
                ))}
              </div>
            </div>

            <div className="text-xs text-gray-400">
              <strong>Pricing:</strong> {model.price}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            Showing {startIndex + 1}-{Math.min(endIndex, filteredModels.length)} of {filteredModels.length} models
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="p-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm">
              {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="p-2 bg-gray-800 border border-gray-700 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelsPage;
