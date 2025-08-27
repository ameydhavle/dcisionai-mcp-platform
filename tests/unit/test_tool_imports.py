#!/usr/bin/env python3
"""
Test Tool Imports - Check if manufacturing tools can be imported
==============================================================

Simple test to verify that all manufacturing tools can be imported
and initialized without hanging.
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger("Tool Import Test")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def test_tool_imports():
    """Test importing all manufacturing tools"""
    
    logger.info("🔍 Testing Manufacturing Tool Imports")
    logger.info("=" * 50)
    
    tools_to_test = [
        ("Intent Tool", "mcp_server.tools.manufacturing.intent.DcisionAI_Intent_Tool"),
        ("Data Tool", "mcp_server.tools.manufacturing.data.DcisionAI_Data_Tool"),
        ("Model Builder", "mcp_server.tools.manufacturing.model.DcisionAI_Model_Builder"),
        ("Solver Tool", "mcp_server.tools.manufacturing.solver"),
    ]
    
    for tool_name, module_path in tools_to_test:
        try:
            logger.info(f"📦 Testing import: {tool_name}")
            module = __import__(module_path, fromlist=['*'])
            logger.info(f"✅ {tool_name} imported successfully")
            
            # Try to create tool instance
            if tool_name == "Intent Tool":
                tool = module.create_dcisionai_intent_tool_v6()
                logger.info(f"✅ {tool_name} instance created")
            elif tool_name == "Data Tool":
                tool = module.create_dcisionai_data_tool_v3()
                logger.info(f"✅ {tool_name} instance created")
            elif tool_name == "Model Builder":
                tool = module.create_model_builder_tool()
                logger.info(f"✅ {tool_name} instance created")
            elif tool_name == "Solver Tool":
                tool = module.create_shared_solver_tool()
                logger.info(f"✅ {tool_name} instance created")
                
        except Exception as e:
            logger.error(f"❌ {tool_name} failed: {e}")
            return False
    
    return True

def test_fastmcp_server():
    """Test FastMCP server creation"""
    
    logger.info("\n🔍 Testing FastMCP Server Creation")
    logger.info("=" * 50)
    
    try:
        from mcp_server.fastmcp_server import create_fastmcp_server
        logger.info("📦 FastMCP server module imported")
        
        server = create_fastmcp_server()
        logger.info("✅ FastMCP server created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ FastMCP server failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Tool Import Tests")
    logger.info("=" * 60)
    
    # Test tool imports
    tools_ok = test_tool_imports()
    
    # Test FastMCP server
    server_ok = test_fastmcp_server()
    
    if tools_ok and server_ok:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.error("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
