"""
DcisionAI Platform - A2A Model Validation Consensus Swarm
========================================================

Shared validation swarm that coordinates between Model Builder and Solver tools
for robust model validation with consensus building.

Copyright (c) 2025 DcisionAI. All rights reserved.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Platform throttling imports
from src.shared.throttling import (
    ThrottleAwareSwarm,
    BedrockThrottleConfig,
    BedrockThrottleException,
    get_platform_throttle_manager
)

logger = logging.getLogger(__name__)


class ValidationTier(Enum):
    """Validation tiers based on model complexity"""
    BASIC = "basic"        # Single validation - $0.02
    STANDARD = "standard"  # Dual validation - $0.04
    PREMIUM = "premium"    # Consensus validation - $0.08


class ValidationStatus(Enum):
    """Validation status codes"""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_IMPROVEMENT = "needs_improvement"
    UNCERTAIN = "uncertain"


@dataclass
class ValidationResult:
    """Comprehensive validation result with consensus metrics"""
    status: ValidationStatus
    consensus_score: float
    model_builder_score: float
    solver_score: float
    issues: List[str]
    recommendations: List[str]
    confidence: float
    validation_tier: ValidationTier
    timestamp: datetime


class A2AModelValidatorSwarm:
    """
    A2A Consensus Model Validation Swarm
    ====================================
    
    Coordinates validation between Model Builder and Solver tools
    using consensus building for robust model validation.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.A2AValidator")
        
        # Platform throttling
        self.throttle_manager = get_platform_throttle_manager()
        
        # Validation agents
        self.model_builder_validator = None
        self.solver_validator = None
        self.consensus_builder = None
        
        # Performance tracking
        self.validation_history = []
    
    async def initialize(self) -> bool:
        """Initialize A2A validation swarm"""
        try:
            # Initialize model builder validator
            self.model_builder_validator = ThrottleAwareSwarm("model_validator", "model_builder_validator")
            self.model_builder_validator.add_agent(
                name="model_builder_agent",
                system_prompt="""You are a MODEL BUILDER VALIDATOR. Your ONLY job is to validate optimization models from a model building perspective.

                DO NOT execute solvers. DO NOT modify models. DO NOT solve optimization problems.
                ONLY validate that the model structure is correct for optimization.

                Validate from model building perspective:
                - Variable definitions: All variables properly defined with types and bounds
                - Constraint structure: Constraints are mathematically sound and complete
                - Objective function: Objective is well-formed and appropriate
                - Model completeness: All necessary components are present
                - Mathematical correctness: Model follows optimization principles

                Respond ONLY with JSON:
                {
                    "validation_score": 0.95,
                    "variable_validation": 0.98,
                    "constraint_validation": 0.92,
                    "objective_validation": 0.96,
                    "completeness_check": 0.90,
                    "issues": ["issue_1", "issue_2"],
                    "recommendations": ["recommendation_1", "recommendation_2"],
                    "confidence": 0.94
                }

                REMEMBER: You are ONLY validating model structure, NOT executing solvers."""
            )
            
            # Initialize solver validator
            self.solver_validator = ThrottleAwareSwarm("model_validator", "solver_validator")
            self.solver_validator.add_agent(
                name="solver_agent",
                system_prompt="""You are a SOLVER VALIDATOR. Your ONLY job is to validate optimization models from a solver execution perspective.

                DO NOT build models. DO NOT modify models. DO NOT solve optimization problems.
                ONLY validate that the model can be executed by optimization solvers.

                Validate from solver execution perspective:
                - Solver compatibility: Model format is compatible with common solvers
                - Numerical stability: Model won't cause numerical issues
                - Execution feasibility: Model can be solved within reasonable time
                - Constraint feasibility: Constraints don't create infeasible problems
                - Variable bounds: Bounds are reasonable and don't cause issues

                Respond ONLY with JSON:
                {
                    "validation_score": 0.93,
                    "solver_compatibility": 0.95,
                    "numerical_stability": 0.90,
                    "execution_feasibility": 0.88,
                    "constraint_feasibility": 0.92,
                    "issues": ["issue_1", "issue_2"],
                    "recommendations": ["recommendation_1", "recommendation_2"],
                    "confidence": 0.91
                }

                REMEMBER: You are ONLY validating solver compatibility, NOT building models."""
            )
            
            # Initialize consensus builder
            self.consensus_builder = ThrottleAwareSwarm("model_validator", "consensus_builder")
            self.consensus_builder.add_agent(
                name="consensus_agent",
                system_prompt="""You are a CONSENSUS BUILDER. Your ONLY job is to build consensus between model builder and solver validation results.

                DO NOT build models. DO NOT execute solvers. DO NOT modify validation results.
                ONLY synthesize consensus from multiple validation perspectives.

                Build consensus by:
                - Analyzing agreement between validators
                - Resolving conflicts between perspectives
                - Weighting validation scores appropriately
                - Providing unified recommendations
                - Calculating overall confidence

                Respond ONLY with JSON:
                {
                    "consensus_status": "valid|invalid|needs_improvement|uncertain",
                    "consensus_score": 0.94,
                    "agreement_level": 0.92,
                    "model_builder_score": 0.95,
                    "solver_score": 0.93,
                    "unified_issues": ["issue_1", "issue_2"],
                    "unified_recommendations": ["recommendation_1", "recommendation_2"],
                    "confidence": 0.94,
                    "validation_tier": "basic|standard|premium"
                }

                REMEMBER: You are ONLY building consensus, NOT performing validation."""
            )
            
            self.logger.info("A2A Model Validator Swarm initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"A2A Model Validator Swarm initialization failed: {e}")
            return False
    
    async def validate_model_consensus(self, model_result: Dict[str, Any], 
                                     validation_tier: ValidationTier = ValidationTier.STANDARD) -> ValidationResult:
        """
        Perform A2A consensus validation between Model Builder and Solver tools
        
        Args:
            model_result: Complete model building result
            validation_tier: Validation complexity tier
            
        Returns:
            Consensus validation result
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting A2A consensus validation for tier: {validation_tier.value}")
            
            # Step 1: Model Builder validation
            model_builder_result = await self._validate_from_model_builder_perspective(model_result)
            
            # Step 2: Solver validation
            solver_result = await self._validate_from_solver_perspective(model_result)
            
            # Step 3: Build consensus (only for standard+ tiers)
            consensus_result = {}
            if validation_tier != ValidationTier.BASIC:
                consensus_result = await self._build_consensus(model_builder_result, solver_result, validation_tier)
            
            # Step 4: Compile final result
            final_result = self._compile_validation_result(
                model_builder_result, solver_result, consensus_result, validation_tier
            )
            
            # Track performance
            execution_time = (datetime.now() - start_time).total_seconds()
            await self._track_validation_performance(final_result, execution_time)
            
            self.logger.info(f"A2A consensus validation completed: {final_result.status.value}, "
                           f"confidence: {final_result.confidence:.2f}, time: {execution_time:.2f}s")
            
            return final_result
            
        except Exception as e:
            self.logger.error(f"A2A consensus validation failed: {e}")
            # Return uncertain result on failure
            return ValidationResult(
                status=ValidationStatus.UNCERTAIN,
                consensus_score=0.0,
                model_builder_score=0.0,
                solver_score=0.0,
                issues=[f"Validation failed: {e}"],
                recommendations=["Retry validation with simpler tier"],
                confidence=0.0,
                validation_tier=validation_tier,
                timestamp=datetime.now()
            )
    
    async def _validate_from_model_builder_perspective(self, model_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model from model building perspective"""
        try:
            async with self.throttle_manager.request_context("model_validator", estimated_tokens=600):
                
                validation_request = {
                    "model_result": model_result,
                    "perspective": "model_builder"
                }
                
                response = await self.model_builder_validator.execute_single_agent(
                    0, json.dumps(validation_request)
                )
                
                return self._parse_validation_response(response)
                
        except Exception as e:
            self.logger.error(f"Model builder validation failed: {e}")
            return {
                "validation_score": 0.5,
                "variable_validation": 0.5,
                "constraint_validation": 0.5,
                "objective_validation": 0.5,
                "completeness_check": 0.5,
                "issues": [f"Model builder validation failed: {e}"],
                "recommendations": ["Retry validation"],
                "confidence": 0.0
            }
    
    async def _validate_from_solver_perspective(self, model_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate model from solver execution perspective"""
        try:
            async with self.throttle_manager.request_context("model_validator", estimated_tokens=600):
                
                validation_request = {
                    "model_result": model_result,
                    "perspective": "solver"
                }
                
                response = await self.solver_validator.execute_single_agent(
                    0, json.dumps(validation_request)
                )
                
                return self._parse_validation_response(response)
                
        except Exception as e:
            self.logger.error(f"Solver validation failed: {e}")
            return {
                "validation_score": 0.5,
                "solver_compatibility": 0.5,
                "numerical_stability": 0.5,
                "execution_feasibility": 0.5,
                "constraint_feasibility": 0.5,
                "issues": [f"Solver validation failed: {e}"],
                "recommendations": ["Retry validation"],
                "confidence": 0.0
            }
    
    async def _build_consensus(self, model_builder_result: Dict[str, Any], 
                             solver_result: Dict[str, Any],
                             validation_tier: ValidationTier) -> Dict[str, Any]:
        """Build consensus between validation perspectives"""
        try:
            async with self.throttle_manager.request_context("model_validator", estimated_tokens=500):
                
                consensus_request = {
                    "model_builder_result": model_builder_result,
                    "solver_result": solver_result,
                    "validation_tier": validation_tier.value
                }
                
                response = await self.consensus_builder.execute_single_agent(
                    0, json.dumps(consensus_request)
                )
                
                return self._parse_validation_response(response)
                
        except Exception as e:
            self.logger.error(f"Consensus building failed: {e}")
            return {
                "consensus_status": "uncertain",
                "consensus_score": 0.5,
                "agreement_level": 0.5,
                "model_builder_score": model_builder_result.get("validation_score", 0.5),
                "solver_score": solver_result.get("validation_score", 0.5),
                "unified_issues": ["Consensus building failed"],
                "unified_recommendations": ["Retry consensus validation"],
                "confidence": 0.0,
                "validation_tier": validation_tier.value
            }
    
    def _compile_validation_result(self, model_builder_result: Dict[str, Any],
                                 solver_result: Dict[str, Any],
                                 consensus_result: Dict[str, Any],
                                 validation_tier: ValidationTier) -> ValidationResult:
        """Compile final validation result from all perspectives"""
        
        # Extract scores
        model_builder_score = model_builder_result.get("validation_score", 0.0)
        solver_score = solver_result.get("validation_score", 0.0)
        
        # Calculate consensus score
        if consensus_result:
            consensus_score = consensus_result.get("consensus_score", 0.0)
            agreement_level = consensus_result.get("agreement_level", 0.0)
            status_str = consensus_result.get("consensus_status", "uncertain")
        else:
            # Basic tier: simple average
            consensus_score = (model_builder_score + solver_score) / 2
            agreement_level = 1.0 - abs(model_builder_score - solver_score)
            status_str = self._determine_status(consensus_score)
        
        # Determine final status
        status = self._map_status_string(status_str)
        
        # Compile issues and recommendations
        all_issues = []
        all_recommendations = []
        
        all_issues.extend(model_builder_result.get("issues", []))
        all_issues.extend(solver_result.get("issues", []))
        if consensus_result:
            all_issues.extend(consensus_result.get("unified_issues", []))
        
        all_recommendations.extend(model_builder_result.get("recommendations", []))
        all_recommendations.extend(solver_result.get("recommendations", []))
        if consensus_result:
            all_recommendations.extend(consensus_result.get("unified_recommendations", []))
        
        # Calculate confidence
        confidence = consensus_result.get("confidence", 0.0) if consensus_result else (model_builder_score + solver_score) / 2
        
        return ValidationResult(
            status=status,
            consensus_score=consensus_score,
            model_builder_score=model_builder_score,
            solver_score=solver_score,
            issues=all_issues,
            recommendations=all_recommendations,
            confidence=confidence,
            validation_tier=validation_tier,
            timestamp=datetime.now()
        )
    
    def _determine_status(self, score: float) -> str:
        """Determine status based on validation score"""
        if score >= 0.9:
            return "valid"
        elif score >= 0.7:
            return "needs_improvement"
        else:
            return "invalid"
    
    def _map_status_string(self, status_str: str) -> ValidationStatus:
        """Map status string to ValidationStatus enum"""
        status_map = {
            "valid": ValidationStatus.VALID,
            "invalid": ValidationStatus.INVALID,
            "needs_improvement": ValidationStatus.NEEDS_IMPROVEMENT,
            "uncertain": ValidationStatus.UNCERTAIN
        }
        return status_map.get(status_str, ValidationStatus.UNCERTAIN)
    
    def _parse_validation_response(self, response: str) -> Dict[str, Any]:
        """Parse agent response to extract validation info"""
        try:
            import re
            
            # Handle Strands AgentResult format
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                raise ValueError("No JSON found in agent response")
                
        except Exception as e:
            self.logger.error(f"Failed to parse validation response: {e}")
            raise Exception(f"Validation response parsing failed - NO FALLBACKS: {e}")
    
    async def _track_validation_performance(self, result: ValidationResult, execution_time: float):
        """Track validation performance"""
        
        self.validation_history.append({
            "timestamp": datetime.utcnow(),
            "validation_tier": result.validation_tier.value,
            "status": result.status.value,
            "consensus_score": result.consensus_score,
            "confidence": result.confidence,
            "execution_time": execution_time,
            "issues_count": len(result.issues)
        })
    
    async def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation performance statistics"""
        
        if len(self.validation_history) < 5:
            return {"status": "insufficient_data"}
        
        recent = self.validation_history[-50:]  # Last 50 validations
        
        return {
            "total_validations": len(recent),
            "average_consensus_score": sum(r["consensus_score"] for r in recent) / len(recent),
            "average_confidence": sum(r["confidence"] for r in recent) / len(recent),
            "average_execution_time": sum(r["execution_time"] for r in recent) / len(recent),
            "status_distribution": {
                "valid": len([r for r in recent if r["status"] == "valid"]) / len(recent),
                "invalid": len([r for r in recent if r["status"] == "invalid"]) / len(recent),
                "needs_improvement": len([r for r in recent if r["status"] == "needs_improvement"]) / len(recent),
                "uncertain": len([r for r in recent if r["status"] == "uncertain"]) / len(recent)
            },
            "tier_distribution": {
                "basic": len([r for r in recent if r["validation_tier"] == "basic"]) / len(recent),
                "standard": len([r for r in recent if r["validation_tier"] == "standard"]) / len(recent),
                "premium": len([r for r in recent if r["validation_tier"] == "premium"]) / len(recent)
            }
        }


# Global instance for shared access
_global_validator = None

async def get_global_validator() -> A2AModelValidatorSwarm:
    """Get global A2A validator instance"""
    global _global_validator
    if _global_validator is None:
        _global_validator = A2AModelValidatorSwarm()
        await _global_validator.initialize()
    return _global_validator
