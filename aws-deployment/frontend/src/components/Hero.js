import React from 'react';

const Hero = ({ onStartOptimization }) => {
  const quickActions = [
    {
      title: "Operations",
      description: "Optimize resource allocation and throughput",
      query: "Optimize resource allocation and improve operational efficiency"
    },
    {
      title: "Supply Chain",
      description: "Minimize costs across multiple locations",
      query: "Minimize supply chain costs for 5 locations across different regions"
    },
    {
      title: "Quality Control",
      description: "Maximize efficiency while reducing operational costs",
      query: "Maximize quality control efficiency while reducing operational costs"
    },
    {
      title: "Resource Allocation",
      description: "Optimize for sustainable operations",
      query: "Optimize resource allocation for sustainable business processes"
    }
  ];

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

      {/* Quick Action Cards */}
      <div className="mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
          {quickActions.map((action, index) => (
            <button
              key={index}
              onClick={() => onStartOptimization(action.query)}
                className="group p-4 bg-gray-800 hover:bg-gray-700 rounded-xl text-left transition-all duration-200 border border-gray-700 hover:border-[#e07a4a] hover:shadow-lg hover:shadow-[#e07a4a]/20"
            >
              <h4 className="text-base font-semibold text-white mb-2 group-hover:text-[#e07a4a] transition-colors">
                {action.title}
              </h4>
              <p className="text-gray-400 text-sm mb-2">
                {action.description}
              </p>
              <div className="text-[#e07a4a] text-sm font-medium">
                Make Decision →
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Hero;
