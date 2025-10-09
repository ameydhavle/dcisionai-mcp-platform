#!/usr/bin/env python3
"""
DcisionAI Platform - Domains
============================

Multi-domain implementations for the DcisionAI platform.
"""

# Lazy imports to avoid instantiation during import
def _get_manufacturing_agent():
    from .manufacturing import DcisionAI_Manufacturing_Agent_v1
    return DcisionAI_Manufacturing_Agent_v1

def _get_finance_placeholder():
    from .finance import FinanceDomainPlaceholder
    return FinanceDomainPlaceholder

def _get_pharma_placeholder():
    from .pharma import PharmaDomainPlaceholder
    return PharmaDomainPlaceholder

__version__ = "1.0.0"
__all__ = [
    "DcisionAI_Manufacturing_Agent_v1",
    "FinanceDomainPlaceholder", 
    "PharmaDomainPlaceholder"
]

# Domain registry with lazy loading
AVAILABLE_DOMAINS = {
    "manufacturing": {
        "name": "manufacturing",
        "description": "Manufacturing optimization and production planning",
        "status": "active",
        "agent_class": _get_manufacturing_agent,
        "version": "1.0.0"
    },
    "finance": {
        "name": "finance", 
        "description": "Financial analysis and risk assessment",
        "status": "planned",
        "agent_class": _get_finance_placeholder,
        "version": "1.0.0"
    },
    "pharma": {
        "name": "pharma",
        "description": "Pharmaceutical research and drug discovery", 
        "status": "planned",
        "agent_class": _get_pharma_placeholder,
        "version": "1.0.0"
    }
}

def get_domain_info(domain_name: str):
    """Get information about a specific domain."""
    return AVAILABLE_DOMAINS.get(domain_name)

def list_available_domains():
    """List all available domains and their status."""
    return AVAILABLE_DOMAINS

def get_active_domains():
    """Get only the active domains."""
    return {
        name: info for name, info in AVAILABLE_DOMAINS.items() 
        if info["status"] == "active"
    }
