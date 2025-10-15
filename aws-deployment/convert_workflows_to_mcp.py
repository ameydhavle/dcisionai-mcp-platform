#!/usr/bin/env python3
"""
Convert DcisionAI Workflow APIs to MCP-Compatible Tools
====================================================

This script converts the existing workflow templates and APIs into
MCP-compatible tools for AgentCore Gateway integration.
"""

import json
import yaml
from typing import Dict, Any, List
from datetime import datetime

class WorkflowToMCPConverter:
    def __init__(self):
        self.mcp_tools = []
        self.workflow_templates = self.load_workflow_templates()
    
    def load_workflow_templates(self) -> Dict[str, Any]:
        """Load existing workflow templates."""
        try:
            # Import the workflow templates
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            
            from workflow_templates import WORKFLOW_TEMPLATES
            return WORKFLOW_TEMPLATES
        except ImportError:
            print("⚠️  Could not import workflow templates, using mock data")
            return self.get_mock_workflow_templates()
    
    def get_mock_workflow_templates(self) -> Dict[str, Any]:
        """Get mock workflow templates for testing."""
        return {
            "manufacturing": {
                "production_planning": {
                    "id": "production_planning",
                    "title": "Advanced Production Planning",
                    "description": "Optimize multi-product production with capacity, labor, and material constraints",
                    "problem_description": "Optimize production for 5 products across 3 production lines...",
                    "expected_intent": "production_optimization",
                    "expected_entities": ["products", "production_lines", "capacity", "labor", "materials"],
                    "industry": "manufacturing",
                    "category": "production_planning",
                    "difficulty": "advanced",
                    "estimated_time": "4-5 minutes"
                }
            },
            "marketing": {
                "comprehensive_marketing_optimization": {
                    "id": "comprehensive_marketing_optimization",
                    "title": "Comprehensive Marketing Spend Optimization",
                    "description": "Optimize marketing budget allocation across channels, campaigns, and customer segments",
                    "problem_description": "Optimize $50,000 monthly marketing budget across 6 channels...",
                    "expected_intent": "marketing_optimization",
                    "expected_entities": ["channels", "segments", "budget", "roi", "lifetime_value"],
                    "industry": "marketing",
                    "category": "marketing_spend_optimization",
                    "difficulty": "advanced",
                    "estimated_time": "5-6 minutes"
                }
            }
        }
    
    def convert_workflow_to_mcp_tool(self, industry: str, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a single workflow to MCP tool format."""
        
        # Create tool name
        tool_name = f"optimize_{workflow_id}"
        
        # Create input schema
        input_schema = {
            "type": "object",
            "properties": {
                "problem_description": {
                    "type": "string",
                    "description": f"Detailed description of the {workflow_data['title']} problem",
                    "default": workflow_data.get('problem_description', '')
                },
                "custom_parameters": {
                    "type": "object",
                    "description": "Custom parameters for the optimization",
                    "properties": {},
                    "additionalProperties": True
                },
                "industry": {
                    "type": "string",
                    "description": "Industry context for the optimization",
                    "enum": [industry],
                    "default": industry
                },
                "workflow_id": {
                    "type": "string",
                    "description": "Unique identifier for the workflow",
                    "enum": [workflow_id],
                    "default": workflow_id
                }
            },
            "required": ["problem_description"]
        }
        
        # Create MCP tool
        mcp_tool = {
            "name": tool_name,
            "description": f"{workflow_data['description']} - {workflow_data.get('difficulty', 'intermediate')} difficulty, estimated time: {workflow_data.get('estimated_time', '5 minutes')}",
            "inputSchema": input_schema,
            "metadata": {
                "industry": industry,
                "category": workflow_data.get('category', 'general'),
                "difficulty": workflow_data.get('difficulty', 'intermediate'),
                "estimated_time": workflow_data.get('estimated_time', '5 minutes'),
                "expected_intent": workflow_data.get('expected_intent', 'general_optimization'),
                "expected_entities": workflow_data.get('expected_entities', []),
                "workflow_id": workflow_id,
                "title": workflow_data.get('title', workflow_id)
            }
        }
        
        return mcp_tool
    
    def convert_all_workflows(self) -> List[Dict[str, Any]]:
        """Convert all workflows to MCP tools."""
        print("🔄 Converting workflows to MCP tools...")
        
        mcp_tools = []
        
        for industry, workflows in self.workflow_templates.items():
            print(f"   Processing {industry} industry...")
            
            for workflow_id, workflow_data in workflows.items():
                mcp_tool = self.convert_workflow_to_mcp_tool(industry, workflow_id, workflow_data)
                mcp_tools.append(mcp_tool)
                print(f"   ✅ Converted: {mcp_tool['name']}")
        
        self.mcp_tools = mcp_tools
        print(f"✅ Converted {len(mcp_tools)} workflows to MCP tools")
        return mcp_tools
    
    def create_mcp_server_spec(self) -> Dict[str, Any]:
        """Create MCP server specification for the workflows."""
        
        mcp_spec = {
            "mcpServers": {
                "dcisionai-optimization-workflows": {
                    "command": "python",
                    "args": ["-m", "dcisionai_mcp_server"],
                    "env": {
                        "WORKFLOW_TEMPLATES_PATH": "./workflow_templates.py",
                        "LAMBDA_FUNCTION_ARN": "arn:aws:lambda:us-east-1:808953421331:function:dcisionai-enhanced-workflows"
                    }
                }
            }
        }
        
        return mcp_spec
    
    def create_openapi_spec(self) -> Dict[str, Any]:
        """Create OpenAPI specification for the optimization workflows."""
        
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "DcisionAI Optimization Workflows API",
                "version": "1.0.0",
                "description": "API for executing optimization workflows across various industries"
            },
            "servers": [
                {
                    "url": "https://h5w9r03xkf.execute-api.us-east-1.amazonaws.com/prod",
                    "description": "DcisionAI Production API"
                }
            ],
            "paths": {},
            "components": {
                "schemas": {
                    "OptimizationRequest": {
                        "type": "object",
                        "properties": {
                            "problem_description": {"type": "string"},
                            "custom_parameters": {"type": "object"},
                            "industry": {"type": "string"},
                            "workflow_id": {"type": "string"}
                        },
                        "required": ["problem_description"]
                    },
                    "OptimizationResponse": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "timestamp": {"type": "string"},
                            "workflow": {"type": "object"},
                            "optimization_pipeline": {"type": "object"},
                            "execution_summary": {"type": "object"}
                        }
                    }
                }
            }
        }
        
        # Add paths for each workflow
        for tool in self.mcp_tools:
            workflow_id = tool['metadata']['workflow_id']
            industry = tool['metadata']['industry']
            
            path = f"/workflows/{industry}/{workflow_id}/execute"
            openapi_spec["paths"][path] = {
                "post": {
                    "summary": tool['metadata']['title'],
                    "description": tool['description'],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/OptimizationRequest"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Optimization completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OptimizationResponse"}
                                }
                            }
                        },
                        "400": {
                            "description": "Bad request - invalid parameters"
                        },
                        "500": {
                            "description": "Internal server error"
                        }
                    },
                    "tags": [industry, tool['metadata']['category']]
                }
            }
        
        return openapi_spec
    
    def generate_gateway_target_config(self) -> Dict[str, Any]:
        """Generate Gateway target configuration for the workflows."""
        
        # Create OpenAPI spec
        openapi_spec = self.create_openapi_spec()
        
        target_config = {
            "mcp": {
                "openApiSchema": {
                    "inline": openapi_spec
                }
            }
        }
        
        return target_config
    
    def save_mcp_tools(self, filename: str = None) -> str:
        """Save MCP tools to file."""
        if filename is None:
            filename = f"dcisionai_mcp_tools_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.mcp_tools, f, indent=2)
        
        print(f"💾 MCP tools saved to: {filename}")
        return filename
    
    def save_openapi_spec(self, filename: str = None) -> str:
        """Save OpenAPI specification to file."""
        if filename is None:
            filename = f"dcisionai_openapi_spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        openapi_spec = self.create_openapi_spec()
        
        with open(filename, 'w') as f:
            json.dump(openapi_spec, f, indent=2)
        
        print(f"💾 OpenAPI spec saved to: {filename}")
        return filename
    
    def save_gateway_config(self, filename: str = None) -> str:
        """Save Gateway target configuration to file."""
        if filename is None:
            filename = f"dcisionai_gateway_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        gateway_config = {
            "target_configuration": self.generate_gateway_target_config(),
            "mcp_tools": self.mcp_tools,
            "openapi_spec": self.create_openapi_spec(),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_workflows": len(self.mcp_tools),
                "industries": list(set(tool['metadata']['industry'] for tool in self.mcp_tools)),
                "categories": list(set(tool['metadata']['category'] for tool in self.mcp_tools))
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(gateway_config, f, indent=2)
        
        print(f"💾 Gateway configuration saved to: {filename}")
        return filename

def main():
    """Main function to convert workflows to MCP tools."""
    print("🔄 DcisionAI Workflow to MCP Conversion")
    print("=" * 50)
    
    converter = WorkflowToMCPConverter()
    
    # Convert all workflows
    mcp_tools = converter.convert_all_workflows()
    
    # Save outputs
    mcp_tools_file = converter.save_mcp_tools()
    openapi_spec_file = converter.save_openapi_spec()
    gateway_config_file = converter.save_gateway_config()
    
    print("\n" + "=" * 50)
    print("🎉 Conversion Complete!")
    print("=" * 50)
    print(f"Total workflows converted: {len(mcp_tools)}")
    print(f"MCP tools file: {mcp_tools_file}")
    print(f"OpenAPI spec file: {openapi_spec_file}")
    print(f"Gateway config file: {gateway_config_file}")
    
    print("\n📋 Next Steps:")
    print("1. Use the Gateway config file to create Gateway targets")
    print("2. Test the MCP tools with AgentCore Gateway")
    print("3. Update frontend to use semantic search")
    print("4. Deploy the optimized workflow system")

if __name__ == "__main__":
    main()
