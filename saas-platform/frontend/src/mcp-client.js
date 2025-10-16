// MCP Client Configuration for Direct MCP Server Integration
export const MCP_CONFIG = {
  // MCP Server URL (Flask backend)
  serverUrl: "http://localhost:5001/api/mcp",
  
  // Available tools in the MCP server
  tools: [
    "classify_intent",
    "analyze_data", 
    "build_model",
    "solve_optimization",
    "get_workflow_templates",
    "execute_workflow"
  ]
};

// Helper function to get headers for MCP requests
export const getMCPHeaders = () => ({
  'Content-Type': 'application/json'
});

// Helper function to make MCP tool calls
export const callMCPTool = async (toolName, toolArguments) => {
  const endpoint = getMCPEndpoint(toolName);
  
  const response = await fetch(`${MCP_CONFIG.serverUrl}/${endpoint}`, {
    method: 'POST',
    headers: getMCPHeaders(),
    body: JSON.stringify(toolArguments)
  });
  
  if (!response.ok) {
    throw new Error(`MCP request failed: ${response.status} ${response.statusText}`);
  }
  
  const result = await response.json();
  
  if (result.error) {
    throw new Error(`MCP tool error: ${result.error.message}`);
  }
  
  return result;
};

// Helper function to get the correct endpoint for each tool
export const getMCPEndpoint = (toolName) => {
  const endpointMap = {
    'classify_intent': 'classify-intent',
    'analyze_data': 'analyze-data',
    'build_model': 'build-model',
    'solve_optimization': 'solve-optimization',
    'get_workflow_templates': 'workflow-templates',
    'execute_workflow': 'execute-workflow'
  };
  
  return endpointMap[toolName] || toolName;
};

// Helper function to list available tools
export const listMCPTools = async () => {
  try {
    const response = await fetch(`${MCP_CONFIG.serverUrl}/health-check`);
    
    if (!response.ok) {
      throw new Error(`MCP health check failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    
    return {
      tools: MCP_CONFIG.tools,
      status: result.status,
      message: result.message
    };
  } catch (error) {
    throw new Error(`MCP tools list error: ${error.message}`);
  }
};

// Helper function to test MCP connection
export const testMCPConnection = async () => {
  try {
    const response = await fetch(`${MCP_CONFIG.serverUrl}/health-check`);
    
    if (response.ok) {
      const result = await response.json();
      return {
        connected: true,
        status: result.status,
        message: result.message
      };
    } else {
      return {
        connected: false,
        status: 'error',
        message: `HTTP ${response.status}: ${response.statusText}`
      };
    }
  } catch (error) {
    return {
      connected: false,
      status: 'error',
      message: error.message
    };
  }
};
