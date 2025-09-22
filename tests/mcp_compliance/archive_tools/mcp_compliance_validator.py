#!/usr/bin/env python3
"""
MCP Compliance Validator
=======================

Production-ready MCP protocol compliance validation and reporting for DcisionAI Platform.
Provides comprehensive validation capabilities and generates detailed compliance reports.

This module implements:
- Compliance score calculation
- Detailed validation reporting
- Certification status determination
- Recommendations generation
- Export capabilities (JSON, YAML, HTML)
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from jinja2 import Template

logger = logging.getLogger(__name__)


@dataclass
class ComplianceRequirement:
    """Individual compliance requirement for MCP protocol."""
    
    id: str
    name: str
    description: str
    category: str
    priority: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
    weight: float  # 0.0 to 1.0 for scoring
    status: str = "PENDING"  # 'PASS', 'FAIL', 'SKIP', 'PENDING'
    score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ComplianceCategory:
    """Category of compliance requirements."""
    
    name: str
    description: str
    requirements: List[ComplianceRequirement] = field(default_factory=list)
    weight: float = 1.0
    
    @property
    def total_requirements(self) -> int:
        """Total number of requirements in this category."""
        return len(self.requirements)
    
    @property
    def passed_requirements(self) -> int:
        """Number of requirements that passed."""
        return len([r for r in self.requirements if r.status == 'PASS'])
    
    @property
    def failed_requirements(self) -> int:
        """Number of requirements that failed."""
        return len([r for r in self.requirements if r.status == 'FAIL'])
    
    @property
    def category_score(self) -> float:
        """Calculate category score based on weighted requirements."""
        if not self.requirements:
            return 0.0
        
        total_weight = sum(req.weight for req in self.requirements)
        if total_weight == 0:
            return 0.0
        
        weighted_score = sum(req.score * req.weight for req in self.requirements)
        return weighted_score / total_weight


@dataclass
class ComplianceValidationReport:
    """Comprehensive compliance validation report."""
    
    server_name: str
    server_version: str
    validation_date: datetime
    overall_score: float
    certification_status: str
    categories: List[ComplianceCategory] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    next_review_date: Optional[datetime] = None
    
    @property
    def total_requirements(self) -> int:
        """Total number of requirements across all categories."""
        return sum(cat.total_requirements for cat in self.categories)
    
    @property
    def passed_requirements(self) -> int:
        """Total number of requirements that passed."""
        return sum(cat.passed_requirements for cat in self.categories)
    
    @property
    def failed_requirements(self) -> int:
        """Total number of requirements that failed."""
        return sum(cat.failed_requirements for cat in self.categories)
    
    @property
    def compliance_percentage(self) -> float:
        """Percentage of requirements that passed."""
        if self.total_requirements == 0:
            return 0.0
        return (self.passed_requirements / self.total_requirements) * 100


class MCPComplianceValidator:
    """
    Production-ready MCP protocol compliance validator.
    
    This class provides comprehensive validation capabilities for MCP protocol compliance,
    ensuring DcisionAI Platform meets all requirements for private listing.
    """
    
    def __init__(self):
        """Initialize MCP compliance validator."""
        self.categories: List[ComplianceCategory] = []
        self.validation_results: List[ComplianceRequirement] = []
        
        # Setup compliance requirements
        self._setup_compliance_requirements()
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Setup logging for the compliance validator."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _setup_compliance_requirements(self) -> None:
        """Setup comprehensive compliance requirements."""
        logger.info("🔧 Setting up MCP compliance requirements")
        
        # Category 1: Core Protocol Compliance
        core_protocol = ComplianceCategory(
            name="Core Protocol Compliance",
            description="Basic MCP protocol requirements and version support",
            weight=0.25
        )
        
        core_protocol.requirements = [
            ComplianceRequirement(
                id="CP001",
                name="Protocol Version Support",
                description="Support latest MCP protocol version (2025-03-26)",
                category="core_protocol",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="CP002",
                name="Backward Compatibility",
                description="Support previous protocol versions",
                category="core_protocol",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="CP003",
                name="Version Negotiation",
                description="Proper version handshake implementation",
                category="core_protocol",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="CP004",
                name="Protocol Extensions",
                description="Support for protocol extensions and custom features",
                category="core_protocol",
                priority="MEDIUM",
                weight=0.6
            )
        ]
        
        # Category 2: Connection Management
        connection_mgmt = ComplianceCategory(
            name="Connection Management",
            description="Transport layer and connection handling",
            weight=0.20
        )
        
        connection_mgmt.requirements = [
            ComplianceRequirement(
                id="CM001",
                name="WebSocket Transport",
                description="Support for WebSocket transport layer",
                category="connection_mgmt",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="CM002",
                name="HTTP/2 Transport",
                description="Support for HTTP/2 transport layer",
                category="connection_mgmt",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="CM003",
                name="Connection Handshake",
                description="Proper connection establishment",
                category="connection_mgmt",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="CM004",
                name="Connection Termination",
                description="Graceful connection closure",
                category="connection_mgmt",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="CM005",
                name="Reconnection Logic",
                description="Automatic reconnection with backoff",
                category="connection_mgmt",
                priority="MEDIUM",
                weight=0.6
            )
        ]
        
        # Category 3: Tool Management
        tool_mgmt = ComplianceCategory(
            name="Tool Management",
            description="Tool registration, execution, and schema management",
            weight=0.25
        )
        
        tool_mgmt.requirements = [
            ComplianceRequirement(
                id="TM001",
                name="Tool Discovery",
                description="Implement tools/list method",
                category="tool_mgmt",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="TM002",
                name="Tool Execution",
                description="Implement tools/call method",
                category="tool_mgmt",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="TM003",
                name="Tool Metadata",
                description="Complete tool descriptions and capabilities",
                category="tool_mgmt",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="TM004",
                name="Tool Schemas",
                description="JSON Schema for tool inputs and outputs",
                category="tool_mgmt",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="TM005",
                name="Parameter Validation",
                description="Input parameter validation and type checking",
                category="tool_mgmt",
                priority="HIGH",
                weight=0.8
            )
        ]
        
        # Category 4: Security & Authentication
        security_auth = ComplianceCategory(
            name="Security & Authentication",
            description="Authentication methods and security features",
            weight=0.20
        )
        
        security_auth.requirements = [
            ComplianceRequirement(
                id="SA001",
                name="API Key Authentication",
                description="Secure API key handling",
                category="security_auth",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="SA002",
                name="OAuth 2.0 Support",
                description="OAuth 2.0 flow implementation",
                category="security_auth",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="SA003",
                name="JWT Token Support",
                description="JWT token validation and management",
                category="security_auth",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="SA004",
                name="Transport Security",
                description="TLS 1.3 encryption",
                category="security_auth",
                priority="CRITICAL",
                weight=1.0
            ),
            ComplianceRequirement(
                id="SA005",
                name="Rate Limiting",
                description="Request rate limiting and throttling",
                category="security_auth",
                priority="MEDIUM",
                weight=0.6
            )
        ]
        
        # Category 5: Error Handling & Resilience
        error_resilience = ComplianceCategory(
            name="Error Handling & Resilience",
            description="Error management and system resilience",
            weight=0.10
        )
        
        error_resilience.requirements = [
            ComplianceRequirement(
                id="ER001",
                name="Standard Error Codes",
                description="MCP standard error codes",
                category="error_resilience",
                priority="HIGH",
                weight=0.8
            ),
            ComplianceRequirement(
                id="ER002",
                name="Error Context",
                description="Detailed error information",
                category="error_resilience",
                priority="MEDIUM",
                weight=0.6
            ),
            ComplianceRequirement(
                id="ER003",
                name="Circuit Breaker",
                description="Circuit breaker pattern implementation",
                category="error_resilience",
                priority="MEDIUM",
                weight=0.6
            ),
            ComplianceRequirement(
                id="ER004",
                name="Retry Logic",
                description="Exponential backoff retry mechanisms",
                category="error_resilience",
                priority="MEDIUM",
                weight=0.6
            ),
            ComplianceRequirement(
                id="ER005",
                name="Health Checks",
                description="System health monitoring",
                category="error_resilience",
                priority="LOW",
                weight=0.4
            )
        ]
        
        # Add all categories
        self.categories = [
            core_protocol,
            connection_mgmt,
            tool_mgmt,
            security_auth,
            error_resilience
        ]
        
        logger.info(f"✅ Setup {len(self.categories)} compliance categories with {self.total_requirements} requirements")
    
    @property
    def total_requirements(self) -> int:
        """Total number of requirements across all categories."""
        return sum(cat.total_requirements for cat in self.categories)
    
    def validate_compliance(self, test_results: List[Dict[str, Any]]) -> ComplianceValidationReport:
        """
        Validate compliance based on test results.
        
        Args:
            test_results: List of test results from MCPComplianceTester
            
        Returns:
            Comprehensive compliance validation report
        """
        logger.info("🔍 Starting MCP compliance validation")
        
        start_time = time.time()
        
        # Initialize report
        report = ComplianceValidationReport(
            server_name="DcisionAI MCP Server",
            server_version="1.0.0",
            validation_date=datetime.utcnow(),
            overall_score=0.0,
            certification_status="PENDING"
        )
        
        try:
            # Map test results to requirements
            self._map_test_results_to_requirements(test_results)
            
            # Calculate category scores
            for category in self.categories:
                category_score = category.category_score
                logger.info(f"📊 {category.name}: {category_score:.2%}")
            
            # Calculate overall score
            overall_score = self._calculate_overall_score()
            report.overall_score = overall_score
            
            # Determine certification status
            report.certification_status = self._determine_certification_status(overall_score)
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations()
            
            # Set next review date
            report.next_review_date = datetime.utcnow() + timedelta(days=90)
            
            # Add categories to report
            report.categories = self.categories.copy()
            
        except Exception as e:
            logger.error(f"❌ Compliance validation failed: {e}")
            report.overall_score = 0.0
            report.certification_status = "FAILED"
            report.recommendations = [f"Validation failed: {str(e)}"]
        
        validation_time = time.time() - start_time
        logger.info(f"✅ MCP Compliance Validation completed in {validation_time:.2f}s")
        logger.info(f"📊 Overall Score: {report.overall_score:.2%}")
        logger.info(f"🏆 Certification Status: {report.certification_status}")
        
        return report
    
    def _map_test_results_to_requirements(self, test_results: List[Dict[str, Any]]) -> None:
        """Map test results to compliance requirements."""
        logger.info("🔗 Mapping test results to compliance requirements")
        
        # Create a mapping of test names to results
        test_result_map = {}
        for result in test_results:
            test_name = result.get('test_name', '')
            test_result_map[test_name] = result
        
        # Map test results to requirements
        for category in self.categories:
            for requirement in category.requirements:
                # Find matching test result
                matching_test = self._find_matching_test(requirement, test_result_map)
                
                if matching_test:
                    # Update requirement with test results
                    requirement.status = matching_test.get('status', 'FAIL')
                    requirement.score = matching_test.get('score', 0.0)
                    requirement.details = matching_test.get('details', {})
                    requirement.error_message = matching_test.get('error_message')
                    requirement.timestamp = datetime.utcnow()
                    
                    logger.debug(f"✅ Mapped {requirement.id} to test {matching_test.get('test_name')}")
                else:
                    # No matching test found
                    requirement.status = "SKIP"
                    requirement.score = 0.0
                    requirement.error_message = "No matching test found"
                    requirement.timestamp = datetime.utcnow()
                    
                    logger.warning(f"⚠️ No matching test found for {requirement.id}")
    
    def _find_matching_test(self, requirement: ComplianceRequirement, test_results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find matching test result for a requirement."""
        # Simple mapping logic - can be enhanced with more sophisticated matching
        test_name_mapping = {
            "protocol_version": "protocol_version",
            "connection_management": "connection_management",
            "tool_management": "tool_management",
            "authentication_security": "authentication_security",
            "message_format": "message_format",
            "resource_management": "resource_management",
            "prompt_management": "prompt_management",
            "error_handling": "error_handling",
            "resilience": "resilience"
        }
        
        # Try to find matching test by category
        for test_name, result in test_results.items():
            if requirement.category in test_name.lower():
                return result
        
        # Try to find by requirement ID
        for test_name, result in test_results.items():
            if requirement.id.lower() in test_name.lower():
                return result
        
        return None
    
    def _calculate_overall_score(self) -> float:
        """Calculate overall compliance score based on weighted categories."""
        if not self.categories:
            return 0.0
        
        total_weight = sum(cat.weight for cat in self.categories)
        if total_weight == 0:
            return 0.0
        
        weighted_score = sum(cat.category_score * cat.weight for cat in self.categories)
        return weighted_score / total_weight
    
    def _determine_certification_status(self, score: float) -> str:
        """Determine certification status based on score."""
        if score >= 0.95:
            return "COMPLIANT"
        elif score >= 0.90:
            return "MOSTLY_COMPLIANT"
        elif score >= 0.80:
            return "PARTIALLY_COMPLIANT"
        else:
            return "NON_COMPLIANT"
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        for category in self.categories:
            for requirement in category.requirements:
                if requirement.status == "FAIL" and requirement.priority in ["CRITICAL", "HIGH"]:
                    recommendations.append(
                        f"CRITICAL: Fix {requirement.name} ({requirement.id}) - {requirement.error_message or 'Requirement failed'}"
                    )
                elif requirement.status == "FAIL" and requirement.priority == "MEDIUM":
                    recommendations.append(
                        f"IMPROVE: Fix {requirement.name} ({requirement.id}) - {requirement.error_message or 'Requirement failed'}"
                    )
                elif requirement.status == "SKIP":
                    recommendations.append(
                        f"TEST: Add test coverage for {requirement.name} ({requirement.id})"
                    )
        
        if not recommendations:
            recommendations.append("All critical requirements passed - maintain current standards")
        
        return recommendations
    
    def export_report(self, report: ComplianceValidationReport, format: str = "json", output_path: Optional[str] = None) -> str:
        """
        Export compliance report in specified format.
        
        Args:
            report: Compliance validation report
            format: Output format ('json', 'yaml', 'html')
            output_path: Output file path (optional)
            
        Returns:
            Exported report content or file path
        """
        logger.info(f"📤 Exporting compliance report in {format.upper()} format")
        
        if format.lower() == "json":
            return self._export_json(report, output_path)
        elif format.lower() == "yaml":
            return self._export_yaml(report, output_path)
        elif format.lower() == "html":
            return self._export_html(report, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, report: ComplianceValidationReport, output_path: Optional[str] = None) -> str:
        """Export report in JSON format."""
        report_dict = asdict(report)
        
        # Convert datetime objects to ISO strings
        report_dict['validation_date'] = report.validation_date.isoformat()
        if report.next_review_date:
            report_dict['next_review_date'] = report.next_review_date.isoformat()
        
        for category in report_dict['categories']:
            for requirement in category['requirements']:
                requirement['timestamp'] = requirement['timestamp'].isoformat()
        
        json_content = json.dumps(report_dict, indent=2, default=str)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(json_content)
            return output_path
        else:
            return json_content
    
    def _export_yaml(self, report: ComplianceValidationReport, output_path: Optional[str] = None) -> str:
        """Export report in YAML format."""
        report_dict = asdict(report)
        
        # Convert datetime objects to ISO strings
        report_dict['validation_date'] = report.validation_date.isoformat()
        if report.next_review_date:
            report_dict['next_review_date'] = report.next_review_date.isoformat()
        
        for category in report_dict['categories']:
            for requirement in category['requirements']:
                requirement['timestamp'] = requirement['timestamp'].isoformat()
        
        yaml_content = yaml.dump(report_dict, default_flow_style=False, indent=2)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(yaml_content)
            return output_path
        else:
            return yaml_content
    
    def _export_html(self, report: ComplianceValidationReport, output_path: Optional[str] = None) -> str:
        """Export report in HTML format."""
        # HTML template for compliance report
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP Compliance Report - {{ report.server_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .category { margin: 20px 0; border: 1px solid #ddd; border-radius: 5px; }
        .category-header { background: #f8f8f8; padding: 10px; font-weight: bold; }
        .requirement { padding: 10px; border-bottom: 1px solid #eee; }
        .requirement.pass { background: #e8f5e8; }
        .requirement.fail { background: #ffe8e8; }
        .requirement.skip { background: #fff8e8; }
        .status { font-weight: bold; }
        .status.pass { color: green; }
        .status.fail { color: red; }
        .status.skip { color: orange; }
        .score { font-size: 1.2em; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>MCP Protocol Compliance Report</h1>
        <h2>{{ report.server_name }} v{{ report.server_version }}</h2>
        <p><strong>Validation Date:</strong> {{ report.validation_date.strftime('%Y-%m-%d %H:%M:%S UTC') }}</p>
    </div>
    
    <div class="summary">
        <h3>Compliance Summary</h3>
        <p><strong>Overall Score:</strong> <span class="score">{{ "%.1f"|format(report.overall_score * 100) }}%</span></p>
        <p><strong>Certification Status:</strong> <span class="status">{{ report.certification_status }}</span></p>
        <p><strong>Total Requirements:</strong> {{ report.total_requirements }}</p>
        <p><strong>Passed:</strong> {{ report.passed_requirements }} | <strong>Failed:</strong> {{ report.failed_requirements }}</p>
        {% if report.next_review_date %}
        <p><strong>Next Review:</strong> {{ report.next_review_date.strftime('%Y-%m-%d') }}</p>
        {% endif %}
    </div>
    
    {% for category in report.categories %}
    <div class="category">
        <div class="category-header">
            {{ category.name }} (Score: {{ "%.1f"|format(category.category_score * 100) }}%)
        </div>
        {% for requirement in category.requirements %}
        <div class="requirement {{ requirement.status }}">
            <div class="status {{ requirement.status }}">{{ requirement.status.upper() }}</div>
            <h4>{{ requirement.name }} ({{ requirement.id }})</h4>
            <p><strong>Priority:</strong> {{ requirement.priority }} | <strong>Score:</strong> {{ "%.1f"|format(requirement.score * 100) }}%</p>
            <p>{{ requirement.description }}</p>
            {% if requirement.error_message %}
            <p><strong>Error:</strong> {{ requirement.error_message }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
    {% if report.recommendations %}
    <div class="category">
        <div class="category-header">Recommendations</div>
        {% for recommendation in report.recommendations %}
        <div class="requirement">
            <p>{{ recommendation }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(report=report)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(html_content)
            return output_path
        else:
            return html_content
