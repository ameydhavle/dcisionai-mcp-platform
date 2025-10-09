#!/usr/bin/env python3
"""
DcisionAI Multi-Domain Platform - Main Entry Point
=================================================

Main entry point for the DcisionAI multi-domain platform.
Demonstrates the platform architecture and domain management.
"""

import logging
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main platform demonstration."""
    logger.info("🚀 Starting DcisionAI Multi-Domain Platform")
    
    try:
        # Import platform components
        from platform_core import platform_manager
        from domains import AVAILABLE_DOMAINS, get_active_domains
        
        logger.info("✅ Platform components imported successfully")
        
        # Display platform summary
        logger.info("\n" + "="*60)
        logger.info("🏗️  PLATFORM ARCHITECTURE OVERVIEW")
        logger.info("="*60)
        
        platform_summary = platform_manager.get_platform_summary()
        logger.info(f"Platform: {platform_summary['platform']['name']}")
        logger.info(f"Version: {platform_summary['platform']['version']}")
        logger.info(f"Environment: {platform_summary['platform']['environment']}")
        logger.info(f"Total Domains: {platform_summary['domains']['total_domains']}")
        logger.info(f"Total Agents: {platform_summary['domains']['total_agents']}")
        logger.info(f"Total Tools: {platform_summary['domains']['total_tools']}")
        
        # Display domain information
        logger.info("\n" + "="*60)
        logger.info("🌐 AVAILABLE DOMAINS")
        logger.info("="*60)
        
        for domain_name, domain_info in AVAILABLE_DOMAINS.items():
            status_emoji = "✅" if domain_info["status"] == "active" else "🔄"
            logger.info(f"{status_emoji} {domain_name.upper()}: {domain_info['description']}")
            logger.info(f"   Status: {domain_info['status']}")
            logger.info(f"   Version: {domain_info['version']}")
            logger.info("")  # Empty line for readability
        
        # Display active domains
        logger.info("="*60)
        logger.info("🎯 ACTIVE DOMAINS")
        logger.info("="*60)
        
        active_domains = get_active_domains()
        for domain_name, domain_info in active_domains.items():
            logger.info(f"✅ {domain_name.upper()}: {domain_info['description']}")
            logger.info(f"   Agent Class: {domain_info['agent_class']().__name__}")
            logger.info("")  # Empty line for readability
        
        # Display cross-domain capabilities
        logger.info("="*60)
        logger.info("🔗 CROSS-DOMAIN CAPABILITIES")
        logger.info("="*60)
        
        cross_domain_capabilities = platform_manager.get_cross_domain_capabilities()
        for domain_name, capabilities in cross_domain_capabilities["cross_domain_capabilities"].items():
            logger.info(f"🌐 {domain_name.upper()}:")
            logger.info(f"   Tools: {', '.join(capabilities['tools'])}")
            logger.info(f"   Workflow: {' → '.join(capabilities['workflow'])}")
            logger.info(f"   Industries: {', '.join(capabilities['supported_industries'])}")
            logger.info("")  # Empty line for readability
        
        # Display platform statistics
        logger.info("="*60)
        logger.info("📊 PLATFORM STATISTICS")
        logger.info("="*60)
        
        platform_stats = platform_manager.get_platform_statistics()
        logger.info(f"Total Domains: {platform_stats['total_domains']}")
        logger.info(f"Total Agents: {platform_stats['total_agents']}")
        logger.info(f"Total Tools: {platform_stats['total_tools']}")
        logger.info(f"Environment: {platform_stats['environment']}")
        logger.info(f"Version: {platform_stats['version']}")
        logger.info(f"Last Activity: {platform_stats['last_activity']}")
        
        # Display shared framework components
        logger.info("\n" + "="*60)
        logger.info("🔧 SHARED FRAMEWORK COMPONENTS")
        logger.info("="*60)
        
        logger.info("✅ Base Agent Framework")
        logger.info("✅ Base Tool Framework") 
        logger.info("✅ Domain Manager")
        logger.info("✅ Platform Manager")
        logger.info("✅ Shared Configuration")
        logger.info("✅ Base Deployment Framework")
        
        logger.info("\n" + "="*60)
        logger.info("🎉 PLATFORM INITIALIZATION COMPLETE")
        logger.info("="*60)
        
        # Export platform configuration
        config_export = platform_manager.export_platform_config()
        export_filename = f"platform_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_filename, 'w') as f:
            json.dump(config_export, f, indent=2, default=str)
        
        logger.info(f"📁 Platform configuration exported to: {export_filename}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to import platform components: {e}")
        logger.error("Please ensure all dependencies are installed and paths are correct")
        return False
        
    except Exception as e:
        logger.error(f"❌ Platform initialization failed: {e}")
        logger.error("Please check the platform configuration and dependencies")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ Platform demonstration completed successfully")
    else:
        logger.error("❌ Platform demonstration failed")
        exit(1)
