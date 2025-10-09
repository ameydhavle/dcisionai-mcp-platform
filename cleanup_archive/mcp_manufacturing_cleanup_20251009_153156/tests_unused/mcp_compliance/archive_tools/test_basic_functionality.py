#!/usr/bin/env python3
"""
Basic Functionality Tests for MCP Compliance Testing Framework
============================================================

Tests to verify that the MCP compliance testing framework components
are working correctly and can be imported and initialized.
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.mcp_compliance.mcp_compliance_tester import MCPComplianceTester
from tests.mcp_compliance.mcp_compliance_validator import MCPComplianceValidator
from tests.mcp_compliance.mcp_compliance_tester import MCPTestResult, MCPComplianceReport
from tests.mcp_compliance.mcp_compliance_validator import ComplianceRequirement, ComplianceCategory, ComplianceValidationReport
from datetime import datetime


class TestMCPComplianceFramework:
    """Test basic functionality of MCP compliance testing framework."""
    
    def test_imports(self):
        """Test that all required modules can be imported."""
        assert MCPComplianceTester is not None
        assert MCPComplianceValidator is not None
        assert MCPTestResult is not None
        assert MCPComplianceReport is not None
        assert ComplianceRequirement is not None
        assert ComplianceCategory is not None
        assert ComplianceValidationReport is not None
    
    def test_mcp_test_result_creation(self):
        """Test MCPTestResult creation and properties."""
        result = MCPTestResult(
            test_name="test_protocol_version",
            status="PASS",
            score=1.0,
            execution_time=0.5,
            details={"version": "2025-03-26"}
        )
        
        assert result.test_name == "test_protocol_version"
        assert result.status == "PASS"
        assert result.score == 1.0
        assert result.execution_time == 0.5
        assert result.details["version"] == "2025-03-26"
    
    def test_mcp_compliance_report_creation(self):
        """Test MCPComplianceReport creation and properties."""
        report = MCPComplianceReport(
            server_name="Test Server",
            server_version="1.0.0",
            test_date=datetime.utcnow(),
            overall_score=0.95
        )
        
        assert report.server_name == "Test Server"
        assert report.server_version == "1.0.0"
        assert report.overall_score == 0.95
        assert report.total_tests == 0
        assert report.passed_tests == 0
        assert report.failed_tests == 0
    
    def test_compliance_requirement_creation(self):
        """Test ComplianceRequirement creation and properties."""
        requirement = ComplianceRequirement(
            id="CP001",
            name="Protocol Version Support",
            description="Support latest MCP protocol version",
            category="core_protocol",
            priority="CRITICAL",
            weight=1.0
        )
        
        assert requirement.id == "CP001"
        assert requirement.name == "Protocol Version Support"
        assert requirement.category == "core_protocol"
        assert requirement.priority == "CRITICAL"
        assert requirement.weight == 1.0
        assert requirement.status == "PENDING"
        assert requirement.score == 0.0
    
    def test_compliance_category_creation(self):
        """Test ComplianceCategory creation and properties."""
        category = ComplianceCategory(
            name="Core Protocol",
            description="Basic MCP protocol requirements",
            weight=0.25
        )
        
        # Add a requirement
        requirement = ComplianceRequirement(
            id="CP001",
            name="Protocol Version Support",
            description="Support latest MCP protocol version",
            category="core_protocol",
            priority="CRITICAL",
            weight=1.0
        )
        
        category.requirements.append(requirement)
        
        assert category.name == "Core Protocol"
        assert category.weight == 0.25
        assert category.total_requirements == 1
        assert category.passed_requirements == 0
        assert category.failed_requirements == 0
        assert category.category_score == 0.0  # No tests run yet
    
    def test_compliance_validator_initialization(self):
        """Test MCPComplianceValidator initialization."""
        validator = MCPComplianceValidator()
        
        assert validator is not None
        assert len(validator.categories) > 0
        assert validator.total_requirements > 0
        
        # Check that we have the expected categories
        category_names = [cat.name for cat in validator.categories]
        expected_categories = [
            "Core Protocol Compliance",
            "Connection Management", 
            "Tool Management",
            "Security & Authentication",
            "Error Handling & Resilience"
        ]
        
        for expected in expected_categories:
            assert expected in category_names
    
    def test_compliance_validator_categories(self):
        """Test that compliance validator has proper category structure."""
        validator = MCPComplianceValidator()
        
        for category in validator.categories:
            assert category.name is not None
            assert category.description is not None
            assert category.weight > 0
            assert category.weight <= 1.0
            assert len(category.requirements) > 0
            
            for requirement in category.requirements:
                assert requirement.id is not None
                assert requirement.name is not None
                assert requirement.description is not None
                assert requirement.category is not None
                assert requirement.priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
                assert requirement.weight > 0
                assert requirement.weight <= 1.0
    
    def test_compliance_validator_scoring(self):
        """Test compliance validator scoring logic."""
        validator = MCPComplianceValidator()
        
        # Test with empty test results
        test_results = []
        report = validator.validate_compliance(test_results)
        
        assert report is not None
        assert report.overall_score == 0.0
        assert report.certification_status == "NON_COMPLIANT"
        assert len(report.recommendations) > 0
    
    def test_mcp_compliance_tester_initialization(self):
        """Test MCPComplianceTester initialization."""
        tester = MCPComplianceTester(
            server_url="ws://localhost:8080/mcp",
            auth_token="test-token",
            timeout=30,
            max_retries=3
        )
        
        assert tester.server_url == "ws://localhost:8080/mcp"
        assert tester.auth_token == "test-token"
        assert tester.timeout == 30
        assert tester.max_retries == 3
        assert tester.protocol_version == "2025-03-26"
        assert len(tester.supported_versions) > 0
    
    def test_certification_status_determination(self):
        """Test certification status determination logic."""
        validator = MCPComplianceValidator()
        
        # Test different score thresholds
        assert validator._determine_certification_status(0.95) == "COMPLIANT"
        assert validator._determine_certification_status(0.90) == "MOSTLY_COMPLIANT"
        assert validator._determine_certification_status(0.80) == "PARTIALLY_COMPLIANT"
        assert validator._determine_certification_status(0.75) == "NON_COMPLIANT"
    
    def test_recommendations_generation(self):
        """Test recommendations generation logic."""
        validator = MCPComplianceValidator()
        
        # Test with no test results (all requirements will be SKIP)
        test_results = []
        report = validator.validate_compliance(test_results)
        
        assert len(report.recommendations) > 0
        
        # Should have recommendations for skipped tests
        skip_recommendations = [r for r in report.recommendations if "TEST:" in r]
        assert len(skip_recommendations) > 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
