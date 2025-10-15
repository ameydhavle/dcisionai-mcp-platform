import React, { useState, useEffect } from 'react';
import { ChevronRight, Clock, Zap, TrendingUp } from 'lucide-react';
import { callGatewayTool } from '../agentcore-config';

const Hero = ({ onStartOptimization, onExecuteWorkflow }) => {
  const [industries, setIndustries] = useState([]);
  const [selectedIndustry, setSelectedIndustry] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(false);

  // Industry icons mapping
  const industryIcons = {
    manufacturing: 'M',
    healthcare: 'H',
    retail: 'R',
    marketing: 'M',
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
      console.log('Loading industries from AgentCore Gateway...');
      const result = await callGatewayTool('DcisionAI-Optimization-Tools-Fixed___get_workflow_templates', {});
      console.log('Industries result:', result);
      
      if (result.status === 'success') {
        console.log('Setting industries:', result.industries);
        setIndustries(result.industries);
      } else {
        console.error('Failed to load industries:', result);
        // Fallback: set some default industries for testing
        console.log('Setting fallback industries for testing');
        setIndustries(['manufacturing', 'healthcare', 'retail', 'marketing', 'financial', 'logistics', 'energy']);
      }
    } catch (err) {
      console.error('Error loading industries:', err);
      // Fallback: set some default industries for testing
      console.log('Setting fallback industries due to error');
      setIndustries(['manufacturing', 'healthcare', 'retail', 'marketing', 'financial', 'logistics', 'energy']);
    } finally {
      setLoading(false);
    }
  };

  const loadWorkflows = async (industry) => {
    try {
      setLoading(true);
      console.log(`Loading workflows for industry: ${industry}`);
      const result = await callGatewayTool('DcisionAI-Optimization-Tools-Fixed___get_workflow_templates', { industry });
      console.log('Workflows result:', result);
      
      if (result.status === 'success') {
        console.log('Setting workflows:', result.workflows);
        setWorkflows(result.workflows);
        setSelectedIndustry(industry);
      } else {
        console.error('Failed to load workflows:', result);
        // Fallback: set some default workflows for testing
        console.log('Setting fallback workflows for testing');
        const fallbackWorkflows = getFallbackWorkflows(industry);
        setWorkflows(fallbackWorkflows);
        setSelectedIndustry(industry);
      }
    } catch (err) {
      console.error('Error loading workflows:', err);
      // Fallback: set some default workflows for testing
      console.log('Setting fallback workflows due to error');
      const fallbackWorkflows = getFallbackWorkflows(industry);
      setWorkflows(fallbackWorkflows);
      setSelectedIndustry(industry);
    } finally {
      setLoading(false);
    }
  };

  const getFallbackWorkflows = (industry) => {
    const fallbackWorkflows = {
      manufacturing: [
        { id: 'production_planning', title: 'Advanced Production Planning', description: 'Optimize multi-product production with capacity, labor, and material constraints', estimated_time: '4-5 minutes', category: 'production_planning', industry: 'manufacturing' },
        { id: 'supply_chain', title: 'Global Supply Chain Optimization', description: 'Optimize multi-tier supply chain with transportation and inventory costs', estimated_time: '5-6 minutes', category: 'supply_chain', industry: 'manufacturing' },
        { id: 'quality_control', title: 'Quality Control & Process Optimization', description: 'Optimize quality control processes with cost-benefit analysis', estimated_time: '4-5 minutes', category: 'quality_control', industry: 'manufacturing' }
      ],
      healthcare: [
        { id: 'patient_flow', title: 'Patient Flow Optimization', description: 'Optimize patient scheduling and resource allocation', estimated_time: '3-4 minutes', category: 'patient_flow', industry: 'healthcare' },
        { id: 'equipment_utilization', title: 'Equipment Utilization Optimization', description: 'Maximize equipment efficiency and minimize downtime', estimated_time: '4-5 minutes', category: 'equipment_utilization', industry: 'healthcare' },
        { id: 'staff_scheduling', title: 'Staff Scheduling Optimization', description: 'Optimize staff schedules for maximum efficiency', estimated_time: '3-4 minutes', category: 'staff_scheduling', industry: 'healthcare' }
      ],
      retail: [
        { id: 'pricing_strategy', title: 'Dynamic Pricing Strategy', description: 'Optimize pricing strategies for maximum revenue', estimated_time: '4-5 minutes', category: 'pricing_strategy', industry: 'retail' },
        { id: 'marketing', title: 'Marketing Campaign Optimization', description: 'Optimize marketing campaigns for maximum ROI', estimated_time: '3-4 minutes', category: 'marketing', industry: 'retail' },
        { id: 'inventory_management', title: 'Inventory Management Optimization', description: 'Optimize inventory levels and distribution', estimated_time: '4-5 minutes', category: 'inventory_management', industry: 'retail' }
      ],
      marketing: [
        { id: 'campaign_management', title: 'Campaign Management Optimization', description: 'Optimize marketing campaign performance', estimated_time: '3-4 minutes', category: 'campaign_management', industry: 'marketing' },
        { id: 'marketing_spend_optimization', title: 'Marketing Spend Optimization', description: 'Optimize marketing budget allocation', estimated_time: '4-5 minutes', category: 'marketing_spend_optimization', industry: 'marketing' },
        { id: 'customer_acquisition', title: 'Customer Acquisition Optimization', description: 'Optimize customer acquisition strategies', estimated_time: '3-4 minutes', category: 'customer_acquisition', industry: 'marketing' }
      ],
      financial: [
        { id: 'credit_risk', title: 'Credit Risk Assessment', description: 'Optimize credit risk evaluation processes', estimated_time: '4-5 minutes', category: 'credit_risk', industry: 'financial' },
        { id: 'fraud_detection', title: 'Fraud Detection Optimization', description: 'Optimize fraud detection algorithms', estimated_time: '3-4 minutes', category: 'fraud_detection', industry: 'financial' },
        { id: 'portfolio_management', title: 'Portfolio Management Optimization', description: 'Optimize investment portfolio allocation', estimated_time: '4-5 minutes', category: 'portfolio_management', industry: 'financial' }
      ],
      logistics: [
        { id: 'route_planning', title: 'Route Planning Optimization', description: 'Optimize delivery routes for efficiency', estimated_time: '4-5 minutes', category: 'route_planning', industry: 'logistics' },
        { id: 'warehouse_operations', title: 'Warehouse Operations Optimization', description: 'Optimize warehouse layout and operations', estimated_time: '3-4 minutes', category: 'warehouse_operations', industry: 'logistics' },
        { id: 'fleet_management', title: 'Fleet Management Optimization', description: 'Optimize fleet utilization and maintenance', estimated_time: '4-5 minutes', category: 'fleet_management', industry: 'logistics' }
      ],
      energy: [
        { id: 'renewable_energy', title: 'Renewable Energy Optimization', description: 'Optimize renewable energy generation and storage', estimated_time: '4-5 minutes', category: 'renewable_energy', industry: 'energy' },
        { id: 'grid_management', title: 'Grid Management Optimization', description: 'Optimize power grid operations and distribution', estimated_time: '3-4 minutes', category: 'grid_management', industry: 'energy' },
        { id: 'maintenance', title: 'Maintenance Optimization', description: 'Optimize equipment maintenance schedules', estimated_time: '3-4 minutes', category: 'maintenance', industry: 'energy' }
      ]
    };
    return fallbackWorkflows[industry] || [];
  };

  const executeWorkflow = async (workflow) => {
    if (onExecuteWorkflow) {
      onExecuteWorkflow(workflow);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'beginner': return 'text-green-400 bg-green-400/20';
      case 'intermediate': return 'text-yellow-400 bg-yellow-400/20';
      case 'advanced': return 'text-red-400 bg-red-400/20';
      default: return 'text-gray-400 bg-gray-400/20';
    }
  };


  return (
    <div className="text-center max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="mb-8">
        <div className="mb-4">
          <h1 className="text-6xl sm:text-5xl font-bold text-white mb-2 leading-tight" style={{fontSize: '4rem', lineHeight: '1.05', letterSpacing: '-0.04em'}}>
            The Intelligent{' '}
            <span className="bg-gradient-to-r from-white via-[#e07a4a] to-white bg-clip-text text-transparent">
              Enterprise Decision
            </span>
            <br />
            Layer
          </h1>
        </div>
        
        <p className="text-gray-300 text-lg max-w-4xl mx-auto mb-6 leading-relaxed" style={{fontSize: '1.125rem', lineHeight: '1.5', letterSpacing: '-0.01em'}}>
          Between AI chatbots and spreadsheets, there's a missing layer —{' '}
          <span className="bg-gradient-to-r from-white via-[#e07a4a] to-white bg-clip-text text-transparent">
            the Intelligent Decision Layer
          </span>
          {' '}— that transforms business complexity into optimized, explainable decisions.
        </p>
        

      </div>

      {/* Demo Section */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-700 rounded-xl p-4 border border-gray-600 mb-8">
        <h3 className="text-lg font-semibold text-white mb-3 text-center">See DcisionAI in Action</h3>
        <p className="text-gray-300 mb-3 text-center">
          Watch how we transform business complexity into optimized, explainable decisions you can trust.
        </p>
        <div className="flex items-center justify-center gap-4 text-sm">
          <span className="text-green-400">Intent Classification</span>
          <span className="text-gray-400">→</span>
          <span className="text-blue-400">Data Analysis</span>
          <span className="text-gray-400">→</span>
          <span className="text-purple-400">Model Building</span>
          <span className="text-gray-400">→</span>
          <span className="text-orange-400">Decision Solver</span>
        </div>
      </div>

      {/* Industry Selection */}
      <div className="mb-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-5xl mx-auto">
          {industries.map((industry) => (
            <button
              key={industry}
              onClick={() => loadWorkflows(industry)}
              className={`group p-4 rounded-xl text-center transition-all duration-200 border ${
                selectedIndustry === industry
                  ? 'bg-[#e07a4a] border-[#e07a4a] text-white'
                  : 'bg-gray-800 hover:bg-gray-700 border-gray-700 hover:border-[#e07a4a] text-gray-300 hover:text-white'
              } hover:shadow-lg hover:shadow-[#e07a4a]/20`}
            >
              <div className="text-2xl font-bold mb-2 bg-gray-700 rounded-full w-12 h-12 flex items-center justify-center mx-auto">{industryIcons[industry]}</div>
              <h4 className="text-sm font-semibold capitalize">
                {industry}
              </h4>
              <div className="text-xs mt-1 opacity-75">
                {industry === 'manufacturing' && '3 workflows'}
                {industry === 'healthcare' && '3 workflows'}
                {industry === 'retail' && '3 workflows'}
                {industry === 'marketing' && '3 workflows'}
                {industry === 'financial' && '3 workflows'}
                {industry === 'logistics' && '3 workflows'}
                {industry === 'energy' && '3 workflows'}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Workflow Selection */}
      {selectedIndustry && workflows.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-center mb-6">
            <div className="text-xl font-bold mr-3 bg-gray-700 rounded-full w-10 h-10 flex items-center justify-center">{industryIcons[selectedIndustry]}</div>
            <h3 className="text-2xl font-bold text-white capitalize">
              {selectedIndustry} Workflows
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl mx-auto">
            {workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="group p-6 bg-gray-800 hover:bg-gray-700 rounded-xl text-left transition-all duration-200 border border-gray-700 hover:border-[#e07a4a] hover:shadow-lg hover:shadow-[#e07a4a]/20"
              >
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-lg font-semibold text-white group-hover:text-[#e07a4a] transition-colors">
                    {workflow.title}
                  </h4>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(workflow.difficulty)}`}>
                    {workflow.difficulty}
                  </span>
                </div>
                
                <p className="text-gray-400 text-sm mb-4 line-clamp-3">
                  {workflow.description}
                </p>
                
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center text-gray-500 text-sm">
                    <Clock className="w-4 h-4 mr-1" />
                    {workflow.estimated_time}
                  </div>
                  <div className="flex items-center text-gray-500 text-sm">
                    <Zap className="w-4 h-4 mr-1" />
                    {workflow.category.replace(/_/g, ' ')}
                  </div>
                </div>
                
                <button
                  onClick={() => executeWorkflow(workflow)}
                  className="w-full bg-[#e07a4a] hover:bg-[#d4693a] text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center"
                >
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Execute Workflow
                  <ChevronRight className="w-4 h-4 ml-2" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#e07a4a]"></div>
          <span className="ml-3 text-gray-300">Loading workflows...</span>
        </div>
      )}

      {/* Fallback to Generic Actions if No Workflows */}
      {!selectedIndustry && !loading && (
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-white mb-6">Quick Start</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
            <button
              onClick={() => onStartOptimization("Optimize resource allocation and improve operational efficiency")}
              className="group p-4 bg-gray-800 hover:bg-gray-700 rounded-xl text-left transition-all duration-200 border border-gray-700 hover:border-[#e07a4a] hover:shadow-lg hover:shadow-[#e07a4a]/20"
            >
              <h4 className="text-base font-semibold text-white mb-2 group-hover:text-[#e07a4a] transition-colors">
                Operations Optimization
              </h4>
              <p className="text-gray-400 text-sm mb-2">
                Optimize resource allocation and throughput
              </p>
              <div className="text-[#e07a4a] text-sm font-medium">
                Make Decision →
              </div>
            </button>
            <button
              onClick={() => onStartOptimization("Minimize supply chain costs for 5 locations across different regions")}
              className="group p-4 bg-gray-800 hover:bg-gray-700 rounded-xl text-left transition-all duration-200 border border-gray-700 hover:border-[#e07a4a] hover:shadow-lg hover:shadow-[#e07a4a]/20"
            >
              <h4 className="text-base font-semibold text-white mb-2 group-hover:text-[#e07a4a] transition-colors">
                Supply Chain Optimization
              </h4>
              <p className="text-gray-400 text-sm mb-2">
                Minimize costs across multiple locations
              </p>
              <div className="text-[#e07a4a] text-sm font-medium">
                Make Decision →
              </div>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Hero;
