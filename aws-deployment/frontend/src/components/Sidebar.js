import React, { useState } from 'react';

const Sidebar = ({ isCollapsed, onToggle, activeSection, onSectionChange, isMobile, onClose, onStartNewAnalysis }) => {

  return (
    <div className={`bg-gradient-to-b from-gray-900 via-gray-900 to-gray-800 border-r border-gray-700/50 shadow-2xl transition-all duration-300 ease-in-out ${
      isCollapsed ? 'w-16' : 'w-72'
    } ${isMobile ? 'fixed top-0 left-0 h-full z-50' : ''} flex flex-col h-full backdrop-blur-sm`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-700/30 bg-gradient-to-r from-gray-900/50 to-gray-800/30">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-[#e07a4a] via-[#d2691e] to-[#b8860b] rounded-xl flex items-center justify-center shadow-lg ring-1 ring-white/10">
                <span className="text-white font-bold text-lg">D</span>
              </div>
              <div>
                <span className="text-white font-bold text-xl tracking-tight">DcisionAI</span>
                <div className="text-xs text-gray-400 font-medium tracking-wide">ENTERPRISE</div>
              </div>
            </div>
          )}
          {isCollapsed && (
            <div className="w-10 h-10 bg-gradient-to-br from-[#e07a4a] via-[#d2691e] to-[#b8860b] rounded-xl flex items-center justify-center mx-auto shadow-lg ring-1 ring-white/10">
              <span className="text-white font-bold text-lg">D</span>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-2 hover:bg-gray-700/50 rounded-lg transition-all duration-200 text-gray-400 hover:text-white hover:shadow-md"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <span className="text-sm font-medium">{isCollapsed ? '→' : '←'}</span>
          </button>
        </div>
      </div>

      {/* New Analysis Button */}
      <div className="p-6">
        <button 
          onClick={onStartNewAnalysis}
          className="w-full bg-gradient-to-r from-[#e07a4a] to-[#d2691e] hover:from-[#d2691e] hover:to-[#b8860b] text-white rounded-xl p-4 transition-all duration-300 hover:shadow-xl hover:shadow-[#e07a4a]/25 flex items-center justify-center gap-3 group"
        >
          {!isCollapsed ? (
            <>
              <div className="w-6 h-6 bg-white/20 rounded-lg flex items-center justify-center group-hover:bg-white/30 transition-colors">
                <span className="text-white font-bold text-sm">+</span>
              </div>
              <span className="text-sm font-semibold tracking-wide">Start New Analysis</span>
            </>
          ) : (
            <div className="w-6 h-6 bg-white/20 rounded-lg flex items-center justify-center group-hover:bg-white/30 transition-colors">
              <span className="text-white font-bold text-sm">+</span>
            </div>
          )}
        </button>
      </div>



      {/* Available Models */}
      <div className="px-6 py-4 border-t border-gray-700/30">
        {!isCollapsed && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full"></div>
              <span className="text-xs text-gray-300 uppercase tracking-wider font-semibold">Available Models</span>
            </div>
            <div className="text-xs text-gray-500 ml-4 leading-relaxed">
              Advanced AI models at your disposal
            </div>
          </div>
        )}
        <div className="space-y-1">
          <button
            onClick={() => onSectionChange('models')}
            className="w-full flex items-center gap-3 text-sm text-gray-300 hover:text-white px-4 py-3 rounded-xl hover:bg-gradient-to-r hover:from-gray-700/50 hover:to-gray-600/30 transition-all duration-200 group border border-transparent hover:border-gray-600/30"
            title={isCollapsed ? "View All Available Models (28)" : undefined}
          >
            {isCollapsed ? (
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-lg flex items-center justify-center mx-auto group-hover:from-blue-500/30 group-hover:to-blue-600/30 transition-all">
                <span className="text-blue-400 text-xs font-bold">M</span>
              </div>
            ) : (
              <>
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-lg flex items-center justify-center group-hover:from-blue-500/30 group-hover:to-blue-600/30 transition-all">
                  <span className="text-blue-400 text-xs font-bold">M</span>
                </div>
                <div className="flex-1 text-left min-w-0">
                  <div className="text-sm font-semibold break-words group-hover:text-white transition-colors">View All Models</div>
                  <div className="text-xs text-gray-500 break-words group-hover:text-gray-300 transition-colors">28 models available</div>
                </div>
                <div className="w-5 h-5 bg-gray-600/50 rounded-md flex items-center justify-center group-hover:bg-gray-500/50 transition-colors">
                  <span className="text-gray-400 text-xs group-hover:text-white transition-colors">→</span>
                </div>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Knowledge Base */}
      <div className="px-6 py-4 border-t border-gray-700/30">
        {!isCollapsed && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-gradient-to-r from-green-400 to-green-500 rounded-full"></div>
              <span className="text-xs text-gray-300 uppercase tracking-wider font-semibold">Knowledge Base</span>
            </div>
            <div className="text-xs text-gray-500 ml-4 leading-relaxed">
              Manage your data sources and documents
            </div>
          </div>
        )}
        <div className="space-y-1">
          <button
            onClick={() => onSectionChange('knowledgebase')}
            className="w-full flex items-center gap-3 text-sm text-gray-300 hover:text-white px-4 py-3 rounded-xl hover:bg-gradient-to-r hover:from-gray-700/50 hover:to-gray-600/30 transition-all duration-200 group border border-transparent hover:border-gray-600/30"
            title={isCollapsed ? "Manage Knowledge Bases" : undefined}
          >
            {isCollapsed ? (
              <div className="w-8 h-8 bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-lg flex items-center justify-center mx-auto group-hover:from-green-500/30 group-hover:to-green-600/30 transition-all">
                <span className="text-green-400 text-xs font-bold">K</span>
              </div>
            ) : (
              <>
                <div className="w-8 h-8 bg-gradient-to-br from-green-500/20 to-green-600/20 rounded-lg flex items-center justify-center group-hover:from-green-500/30 group-hover:to-green-600/30 transition-all">
                  <span className="text-green-400 text-xs font-bold">K</span>
                </div>
                <div className="flex-1 text-left min-w-0">
                  <div className="text-sm font-semibold break-words group-hover:text-white transition-colors">Manage Knowledge Bases</div>
                  <div className="text-xs text-gray-500 break-words group-hover:text-gray-300 transition-colors">Create, upload, and organize data</div>
                </div>
                <div className="w-5 h-5 bg-gray-600/50 rounded-md flex items-center justify-center group-hover:bg-gray-500/50 transition-colors">
                  <span className="text-gray-400 text-xs group-hover:text-white transition-colors">→</span>
                </div>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Agents */}
      <div className="px-6 py-4 border-t border-gray-700/30">
        {!isCollapsed && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 bg-gradient-to-r from-purple-400 to-purple-500 rounded-full"></div>
              <span className="text-xs text-gray-300 uppercase tracking-wider font-semibold">Agents</span>
            </div>
            <div className="text-xs text-gray-500 ml-4 leading-relaxed">
              Internal AI agents powering the system
            </div>
          </div>
        )}
        <div className="space-y-1">
          <button
            onClick={() => onSectionChange('agents')}
            className="w-full flex items-center gap-3 text-sm text-gray-300 hover:text-white px-4 py-3 rounded-xl hover:bg-gradient-to-r hover:from-gray-700/50 hover:to-gray-600/30 transition-all duration-200 group border border-transparent hover:border-gray-600/30"
            title={isCollapsed ? "View All Agents" : undefined}
          >
            {isCollapsed ? (
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-lg flex items-center justify-center mx-auto group-hover:from-purple-500/30 group-hover:to-purple-600/30 transition-all">
                <span className="text-purple-400 text-xs font-bold">A</span>
              </div>
            ) : (
              <>
                <div className="w-8 h-8 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-lg flex items-center justify-center group-hover:from-purple-500/30 group-hover:to-purple-600/30 transition-all">
                  <span className="text-purple-400 text-xs font-bold">A</span>
                </div>
                <div className="flex-1 text-left min-w-0">
                  <div className="text-sm font-semibold break-words group-hover:text-white transition-colors">View All Agents</div>
                  <div className="text-xs text-gray-500 break-words group-hover:text-gray-300 transition-colors">Intent, Data, Model, Solver, and more</div>
                </div>
                <div className="w-5 h-5 bg-gray-600/50 rounded-md flex items-center justify-center group-hover:bg-gray-500/50 transition-colors">
                  <span className="text-gray-400 text-xs group-hover:text-white transition-colors">→</span>
                </div>
              </>
            )}
          </button>
        </div>
      </div>

    </div>
  );
};

export default Sidebar;
