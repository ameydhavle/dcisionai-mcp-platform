import React from 'react'

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🚀 DcisionAI Customer Portal</h1>
        <p>Welcome to the DcisionAI Manufacturing MCP Server Portal</p>
        <div className="features">
          <h2>Available Features:</h2>
          <ul>
            <li>🔍 MCP Server Discovery</li>
            <li>🔑 API Key Management</li>
            <li>📊 Usage Dashboard</li>
            <li>🛠️ Tool Documentation</li>
            <li>🆘 Support Center</li>
          </ul>
        </div>
        <div className="quick-start">
          <h2>Quick Start:</h2>
          <ol>
            <li>Get your API key from the portal</li>
            <li>Install the Python SDK: <code>pip install dcisionai-mcp</code></li>
            <li>Start using manufacturing optimization tools</li>
          </ol>
        </div>
      </header>
    </div>
  )
}

export default App
