import React, { useState } from 'react';

const Sidebar = ({ isCollapsed, onToggle, activeSection, onSectionChange, isMobile, onClose, onStartNewAnalysis }) => {
  const [pinnedItems, setPinnedItems] = useState(['Manufacturing', 'Finance']);

  const mainNavigation = [];

  const categories = [
    { id: 'manufacturing', label: 'Manufacturing' },
    { id: 'retail', label: 'Retail' },
    { id: 'finance', label: 'Finance' },
    { id: 'supply-chain', label: 'Supply Chain' },
    { id: 'pharma', label: 'Pharma' }
  ];

  const togglePin = (item) => {
    setPinnedItems(prev => 
      prev.includes(item) 
        ? prev.filter(p => p !== item)
        : [...prev, item]
    );
  };

  return (
    <div className={`bg-gray-900 border-r border-gray-800 transition-all duration-300 ease-in-out ${
      isCollapsed ? 'w-16' : 'w-64'
    } ${isMobile ? 'fixed top-0 left-0 h-full z-50' : ''} flex flex-col h-full`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-r from-[#e07a4a] to-[#d2691e] rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">D</span>
              </div>
              <span className="text-white font-semibold text-lg">DcisionAI</span>
            </div>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 bg-gradient-to-r from-[#e07a4a] to-[#d2691e] rounded-lg flex items-center justify-center mx-auto">
              <span className="text-white font-bold text-sm">D</span>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-1.5 hover:bg-gray-800 rounded-lg transition-colors text-gray-400 hover:text-white"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? '→' : '←'}
          </button>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="p-4">
        <button 
          onClick={onStartNewAnalysis}
          className="w-full bg-[#e07a4a] hover:bg-[#d2691e] text-white rounded-lg p-3 transition-all duration-200 hover:shadow-lg hover:shadow-[#e07a4a]/20 flex items-center justify-center gap-2"
        >
          {!isCollapsed ? (
            <>
              <span className="text-lg">+</span>
              <span className="text-sm font-medium">Start New Analysis</span>
            </>
          ) : (
            <span className="text-lg font-medium">+</span>
          )}
        </button>
      </div>

      {/* Pinned Items */}
      {pinnedItems.length > 0 && (
        <div className="px-4 pb-2">
          {!isCollapsed && (
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-gray-500 uppercase tracking-wide">Pinned</span>
              <button className="text-gray-500 hover:text-gray-400">
                +
              </button>
            </div>
          )}
          <div className="space-y-1">
            {pinnedItems.map((item) => (
              <div key={item} className="flex items-center justify-between group">
                <button 
                  className="flex items-center gap-2 text-sm text-gray-300 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800 transition-colors flex-1 text-left"
                  title={isCollapsed ? item : undefined}
                >
                  <span className="text-gray-500">📌</span>
                  {!isCollapsed && item}
                </button>
                {!isCollapsed && (
                  <button
                    onClick={() => togglePin(item)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-800 rounded transition-all text-gray-500 hover:text-white"
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}


      {/* Categories */}
      <div className="px-4 py-2 border-t border-gray-800">
        {!isCollapsed && (
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-gray-500 uppercase tracking-wide">Categories</span>
            <button className="text-gray-500 hover:text-gray-400">
              +
            </button>
          </div>
        )}
        <div className="space-y-1">
          {categories.map((category) => (
            <button
              key={category.id}
              className="w-full flex items-center gap-2 text-sm text-gray-400 hover:text-white px-2 py-1.5 rounded-lg hover:bg-gray-800 transition-colors"
              title={isCollapsed ? category.label : undefined}
            >
              {isCollapsed ? (
                <span className="text-gray-500">{category.label.charAt(0)}</span>
              ) : (
                category.label
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Actions */}
      <div className="p-4 border-t border-gray-800 space-y-2">
        <button 
          className="w-full flex items-center gap-3 text-gray-400 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          title={isCollapsed ? 'Notifications' : undefined}
        >
          {!isCollapsed && <span className="text-sm">Notifications</span>}
          {isCollapsed && <span className="text-sm">🔔</span>}
        </button>
        
        <button 
          className="w-full flex items-center gap-3 text-gray-400 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          title={isCollapsed ? 'Account' : undefined}
        >
          {!isCollapsed && (
            <div className="flex-1 text-left">
              <div className="text-sm">Account</div>
              <div className="text-xs text-gray-500">Settings & Profile</div>
            </div>
          )}
          {isCollapsed && <span className="text-sm">👤</span>}
        </button>
        
        <button 
          className="w-full flex items-center gap-3 text-gray-400 hover:text-white px-3 py-2 rounded-lg hover:bg-gray-800 transition-colors"
          title={isCollapsed ? 'Settings' : undefined}
        >
          {!isCollapsed && <span className="text-sm">Settings</span>}
          {isCollapsed && <span className="text-sm">⚙️</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
