#!/usr/bin/env python3
"""
DcisionAI Platform - Shared Configuration
========================================

Centralized configuration for the multi-domain DcisionAI platform.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PlatformConfig:
    """Platform-wide configuration settings."""
    platform_name: str = "DcisionAI Multi-Domain Platform"
    platform_version: str = "1.0.0"
    environment: str = "development"  # development, staging, production
    debug: bool = True
    log_level: str = "INFO"

@dataclass
class AWSConfig:
    """AWS configuration settings."""
    region: str = "us-east-1"
    account_id: str = "808953421331"
    default_role_arn: str = "arn:aws:iam::808953421331:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-3bddb2550f"
    ecr_base_url: str = "808953421331.dkr.ecr.us-east-1.amazonaws.com"

@dataclass
class DomainConfig:
    """Domain-specific configuration settings."""
    manufacturing: Dict[str, Any] = None
    finance: Dict[str, Any] = None
    pharma: Dict[str, Any] = None
    retail: Dict[str, Any] = None

class Settings:
    """
    Centralized settings manager for the DcisionAI platform.
    
    Provides configuration for all domains and platform components.
    """
    
    def __init__(self):
        """Initialize settings with environment variables and defaults."""
        # Platform configuration
        self.platform = PlatformConfig(
            platform_name=os.getenv("PLATFORM_NAME", "DcisionAI Multi-Domain Platform"),
            platform_version=os.getenv("PLATFORM_VERSION", "1.0.0"),
            environment=os.getenv("ENVIRONMENT", "development"),
            debug=os.getenv("DEBUG", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
        
        # AWS configuration
        self.aws = AWSConfig(
            region=os.getenv("AWS_REGION", "us-east-1"),
            account_id=os.getenv("AWS_ACCOUNT_ID", "808953421331"),
            default_role_arn=os.getenv("AWS_DEFAULT_ROLE_ARN", 
                "arn:aws:iam::808953421331:role/AmazonBedrockAgentCoreSDKRuntime-us-east-1-3bddb2550f"),
            ecr_base_url=os.getenv("AWS_ECR_BASE_URL", "808953421331.dkr.ecr.us-east-1.amazonaws.com")
        )
        
        # Domain configurations
        self.domains = DomainConfig(
            manufacturing=self._get_manufacturing_config(),
            finance=self._get_finance_config(),
            pharma=self._get_pharma_config(),
            retail=self._get_retail_config()
        )
    
    def _get_manufacturing_config(self) -> Dict[str, Any]:
        """Get manufacturing domain configuration."""
        return {
            "name": "manufacturing",
            "description": "Manufacturing optimization and production planning",
            "version": "1.0.0",
            "ecr_repo": f"{self.aws.ecr_base_url}/dcisionai-manufacturing-v1",
            "agent_runtime_prefix": "DcisionAI_Manufacturing_Agent_v1",
            "tools": {
                "intent": "manufacturing_intent_tool",
                "data": "manufacturing_data_tool", 
                "model": "manufacturing_model_tool",
                "solver": "manufacturing_solver_tool"
            },
            "workflow": ["intent", "data", "model", "solver"],
            "max_execution_time": 300,
            "supported_industries": ["automotive", "electronics", "aerospace", "chemicals"]
        }
    
    def _get_finance_config(self) -> Dict[str, Any]:
        """Get finance domain configuration."""
        return {
            "name": "finance",
            "description": "Financial analysis, risk assessment, and portfolio optimization",
            "version": "1.0.0",
            "ecr_repo": f"{self.aws.ecr_base_url}/dcisionai-finance-v1",
            "agent_runtime_prefix": "DcisionAI_Finance_Agent_v1",
            "tools": {
                "risk_assessment": "finance_risk_tool",
                "portfolio_optimization": "finance_portfolio_tool",
                "fraud_detection": "finance_fraud_tool",
                "compliance_checking": "finance_compliance_tool"
            },
            "workflow": ["risk_assessment", "portfolio_optimization", "fraud_detection"],
            "max_execution_time": 180,
            "supported_industries": ["banking", "insurance", "investment", "fintech"]
        }
    
    def _get_pharma_config(self) -> Dict[str, Any]:
        """Get pharma domain configuration."""
        return {
            "name": "pharma",
            "description": "Pharmaceutical research, clinical trials, and drug discovery",
            "version": "1.0.0",
            "ecr_repo": f"{self.aws.ecr_base_url}/dcisionai-pharma-v1",
            "agent_runtime_prefix": "DcisionAI_Pharma_Agent_v1",
            "tools": {
                "drug_discovery": "pharma_drug_tool",
                "clinical_trial_optimization": "pharma_trial_tool",
                "supply_chain_management": "pharma_supply_tool",
                "regulatory_compliance": "pharma_compliance_tool"
            },
            "workflow": ["drug_discovery", "clinical_trial_optimization", "supply_chain_management"],
            "max_execution_time": 600,
            "supported_industries": ["biotechnology", "pharmaceuticals", "medical_devices", "healthcare"]
        }
    
    def _get_retail_config(self) -> Dict[str, Any]:
        """Get retail domain configuration."""
        return {
            "name": "retail",
            "description": "Retail analytics, inventory management, and customer insights",
            "version": "1.0.0",
            "ecr_repo": f"{self.aws.ecr_base_url}/dcisionai-retail-v1",
            "agent_runtime_prefix": "DcisionAI_Retail_Agent_v1",
            "tools": {
                "inventory_management": "retail_inventory_tool",
                "demand_forecasting": "retail_demand_tool",
                "pricing_optimization": "retail_pricing_tool",
                "customer_analytics": "retail_customer_tool"
            },
            "workflow": ["inventory_management", "demand_forecasting", "pricing_optimization"],
            "max_execution_time": 240,
            "supported_industries": ["ecommerce", "brick_mortar", "fashion", "grocery"]
        }
    
    def get_domain_config(self, domain_name: str) -> Dict[str, Any]:
        """Get configuration for a specific domain."""
        domain_configs = {
            "manufacturing": self.domains.manufacturing,
            "finance": self.domains.finance,
            "pharma": self.domains.pharma,
            "retail": self.domains.retail
        }
        
        return domain_configs.get(domain_name, {})
    
    def get_all_domains(self) -> List[str]:
        """Get list of all configured domains."""
        return ["manufacturing", "finance", "pharma", "retail"]
    
    def get_platform_summary(self) -> Dict[str, Any]:
        """Get platform configuration summary."""
        return {
            "platform": {
                "name": self.platform.platform_name,
                "version": self.platform.platform_version,
                "environment": self.platform.environment,
                "debug": self.platform.debug,
                "log_level": self.platform.log_level
            },
            "aws": {
                "region": self.aws.region,
                "account_id": self.aws.account_id,
                "ecr_base_url": self.aws.ecr_base_url
            },
            "domains": {
                domain: self.get_domain_config(domain)
                for domain in self.get_all_domains()
            }
        }
    
    def update_domain_config(self, domain_name: str, config: Dict[str, Any]) -> bool:
        """Update configuration for a specific domain."""
        try:
            if domain_name == "manufacturing":
                self.domains.manufacturing.update(config)
            elif domain_name == "finance":
                self.domains.finance.update(config)
            elif domain_name == "pharma":
                self.domains.pharma.update(config)
            elif domain_name == "retail":
                self.domains.retail.update(config)
            else:
                return False
            
            return True
            
        except Exception:
            return False
    
    def get_ecr_repo(self, domain_name: str) -> str:
        """Get ECR repository URL for a specific domain."""
        domain_config = self.get_domain_config(domain_name)
        return domain_config.get("ecr_repo", "")
    
    def get_agent_runtime_prefix(self, domain_name: str) -> str:
        """Get agent runtime prefix for a specific domain."""
        domain_config = self.get_domain_config(domain_name)
        return domain_config.get("agent_runtime_prefix", f"DcisionAI_{domain_name.capitalize()}_Agent_v1")

# Global settings instance
settings = Settings()
