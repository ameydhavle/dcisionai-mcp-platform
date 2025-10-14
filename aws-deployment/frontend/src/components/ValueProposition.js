import React from 'react';

const ValueProposition = () => {
  const differentiators = [
    {
      title: "Intelligent Decision Layer",
      description: "Transforms business complexity into optimized, explainable decisions",
      highlight: "vs. ChatGPT's general responses"
    },
    {
      title: "Enterprise Decision Intelligence",
      description: "Built for crew allocation, delivery routing, and complex business decisions",
      highlight: "vs. Generic AI knowledge"
    },
    {
      title: "Explainable Results",
      description: "Every decision comes with transparent reasoning you can trust",
      highlight: "vs. Black-box AI responses"
    },
    {
      title: "Democratized Decision Making",
      description: "Makes optimization accessible to every decision-maker",
      highlight: "vs. Complex enterprise software"
    }
  ];

  return (
    <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl p-8 border border-gray-700">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-white mb-4">
          Why DcisionAI vs. Generic AI?
        </h2>
        <p className="text-gray-300 text-lg max-w-2xl mx-auto">
          We don't just provide information - we deliver <span className="text-[#e07a4a] font-semibold">Decision Intelligence</span> with explainable results you can trust.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {differentiators.map((item, index) => (
          <div key={index} className="bg-gray-800/50 rounded-xl p-6 border border-gray-700 hover:border-[#e07a4a] transition-colors">
            <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
            <p className="text-gray-300 mb-3">{item.description}</p>
            <div className="flex items-center gap-2 text-sm">
              <span className="text-gray-500">vs.</span>
              <span className="text-red-400 font-medium">{item.highlight}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 text-center">
        <div className="inline-block bg-[#e07a4a]/20 text-[#e07a4a] px-4 py-2 rounded-lg border border-[#e07a4a]/30">
          <span className="font-medium">Real AI Platform Integration</span>
        </div>
        <p className="text-gray-400 text-sm mt-2">
          Powered by enterprise-grade AI with decision intelligence expertise
        </p>
      </div>
    </div>
  );
};

export default ValueProposition;
