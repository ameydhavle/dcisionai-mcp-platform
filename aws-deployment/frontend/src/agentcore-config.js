// AgentCore Gateway Configuration
export const AGENTCORE_CONFIG = {
  // Gateway URL for MCP protocol
  gatewayUrl: "https://dcisionai-gateway-0de1a655-ja1rhlcqjx.gateway.bedrock-agentcore.us-east-1.amazonaws.com/mcp",
  
  // OAuth access token (this should be refreshed periodically)
  accessToken: "eyJraWQiOiJLMWZEMFwvXC9qaGtJSHlZd2IyM2NsMkRSK0dEQ2tFaHVWZVd0djdFMERkOUk9IiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiI1cjdyaXJqdmI0OTZpam1rMDNtanNrNTNtOCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiRGNpc2lvbkFJLUdhdGV3YXktMGRlMWE2NTVcL2ludm9rZSIsImF1dGhfdGltZSI6MTc2MDU0MTM0MCwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfdjlDSmJRMWVKIiwiZXhwIjoxNzYwNTQ0OTQwLCJpYXQiOjE3NjA1NDEzNDAsInZlcnNpb24iOjIsImp0aSI6ImIwZWUxNTcwLTNkM2MtNDUxZS04NDk5LWMwMTRhODBjMDU3ZCIsImNsaWVudF9pZCI6IjVyN3Jpcmp2YjQ5NmlqbWswM21qc2s1M204In0.VaSKykBkYIVHJ4uiePNbu84IVNFkjt3zb8z2ZNu-CYicNwNgxMG-B_ys19bEbZoZayqS0VfDndbY4YJWm4fsP7wxFNcdbYWzv1RSfL6Z3ri1id7L4W5IBwfhtTPj5o-anEMWSxfHxuEtAD3C-ukFVRGVYJfvTnTCT1IUiNWyOENeJO4XwbnDESKiWCN0mrH30_P3HaGYMiQa63sC5MkLDvVBZH7n9yUeLAPoPQfuTee4yfkC_yEhEFYdmvAzTsXkwIRnT7wijCsKeWpn5K5cT8-hFaXl34y8uEwLEMgt7sLsYE3H76yTvhbFbbCgruUmqfFWx4FEJRB7vPWXxdU1Bg",
  
  // Client information for token refresh
  clientInfo: {
    clientId: "5r7rirjvb496ijmk03mjsk53m8",
    clientSecret: "l1ejvaalpnj9u3q33cfg4mp9u62nt789njlk2otti1eukhq8s44",
    userPoolId: "us-east-1_v9CJbQ1eJ",
    tokenEndpoint: "https://agentcore-22b5657e.auth.us-east-1.amazoncognito.com/oauth2/token",
    scope: "DcisionAI-Gateway-0de1a655/invoke",
    domainPrefix: "agentcore-22b5657e"
  },
  
  // Available tools in the Gateway
  tools: [
    "classify_intent",
    "analyze_data", 
    "build_model",
    "solve_optimization",
    "get_workflow_templates",
    "execute_workflow"
  ]
};

// Helper function to get headers for Gateway requests
export const getGatewayHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${AGENTCORE_CONFIG.accessToken}`
});

// Helper function to make Gateway tool calls
export const callGatewayTool = async (toolName, toolArguments) => {
  const response = await fetch(AGENTCORE_CONFIG.gatewayUrl, {
    method: 'POST',
    headers: getGatewayHeaders(),
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: toolArguments
      }
    })
  });
  
  if (!response.ok) {
    throw new Error(`Gateway request failed: ${response.status} ${response.statusText}`);
  }
  
  const result = await response.json();
  
  if (result.error) {
    throw new Error(`Gateway tool error: ${result.error.message}`);
  }
  
  // AgentCore Gateway wraps the actual Lambda response in a 'content' array
  // and the Lambda response itself is a stringified JSON in 'text'
  if (result.result && result.result.content && result.result.content.length > 0) {
    const content = result.result.content[0].text;
    try {
      const lambdaResponse = JSON.parse(content);
      // The Lambda function returns a body which is also a stringified JSON
      if (lambdaResponse.body) {
        return JSON.parse(lambdaResponse.body);
      }
      return lambdaResponse;
    } catch (e) {
      console.error("Failed to parse Lambda response from Gateway content:", e, content);
      return { status: "error", message: "Failed to parse Lambda response from Gateway" };
    }
  }
  
  return result.result;
};

// Helper function to list available tools
export const listGatewayTools = async () => {
  const response = await fetch(AGENTCORE_CONFIG.gatewayUrl, {
    method: 'POST',
    headers: getGatewayHeaders(),
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: Date.now(),
      method: 'tools/list',
      params: {}
    })
  });
  
  if (!response.ok) {
    throw new Error(`Gateway request failed: ${response.status} ${response.statusText}`);
  }
  
  const result = await response.json();
  
  if (result.error) {
    throw new Error(`Gateway tools list error: ${result.error.message}`);
  }
  
  return result.result;
};
