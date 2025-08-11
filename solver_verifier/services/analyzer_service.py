"""Analyzer service - equivalent to Solver role in Gemini's approach."""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..models.business_requirement import (
    BusinessRequirement, 
    HypothesisRequirement,
    Citation,
    SourceLocation,
    AcceptanceCriteria,
    VerificationIssue,
    RequirementType,
    Priority
)
from ..models.agent_config import SystemSettings
from .llm_service import LLMService


class AnalyzerService:
    """
    Analyzer service responsible for extracting and refining business requirements.
    Equivalent to the Solver role in Gemini's mathematical problem-solving approach.
    """
    
    def __init__(self, settings: SystemSettings):
        self.settings = settings
        self.system_prompt = settings.analyzer_system_prompt
        self.llm_service = LLMService(settings)
        
    async def generate_initial_draft(self, documents: Dict[str, str]) -> Dict[str, Any]:
        """
        Stage 1: Generate initial BR draft with direct citations and location info.
        
        This method would integrate with an LLM service to:
        - Extract business requirements from RFP documents
        - Include direct citations with location information
        - Apply clarity, completeness, consistency, verifiability principles
        - Separate confirmed requirements from hypotheses
        
        Args:
            documents: Dict mapping document names to their content
            
        Returns:
            Dict containing 'requirements' and 'hypotheses' lists
        """
        
        try:
            # Build prompt for initial requirement extraction
            user_prompt = self._build_stage1_prompt(documents)
            
            # Call LLM service
            llm_response = await self.llm_service.call_llm_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse LLM response and convert to our models
            requirements = []
            hypotheses = []
            
            # Extract requirements from LLM response
            if 'data' in llm_response and 'requirements' in llm_response['data']:
                for req_data in llm_response['data']['requirements']:
                    try:
                        # Convert LLM response to BusinessRequirement model
                        requirement = self._convert_llm_to_requirement(req_data)
                        requirements.append(requirement)
                    except Exception as e:
                        print(f"Error converting requirement: {e}")
                        continue
            
            # Extract hypotheses if present
            if 'hypotheses' in llm_response:
                for hyp_data in llm_response['hypotheses']:
                    try:
                        hypothesis = HypothesisRequirement(
                            hypothesis_id=hyp_data.get('hypothesis_id', f"HYP_{uuid.uuid4().hex[:8]}"),
                            description=hyp_data.get('description', ''),
                            rationale=hyp_data.get('rationale', ''),
                            confidence_level=hyp_data.get('confidence_level', 0.5),
                            evidence_needed=hyp_data.get('evidence_needed', [])
                        )
                        hypotheses.append(hypothesis)
                    except Exception as e:
                        print(f"Error converting hypothesis: {e}")
                        continue
            
            return {
                'requirements': requirements,
                'hypotheses': hypotheses
            }
            
        except Exception as e:
            # Fallback to sample data if LLM call fails
            print(f"LLM call failed, using sample data: {e}")
            
            example_requirements = []
            if documents:
                doc_name = list(documents.keys())[0]
                sample_requirement = BusinessRequirement(
                    br_id=f"BR_{uuid.uuid4().hex[:8]}",
                    title="Sample Requirement (LLM Failed)",
                    description=f"Failed to extract from {doc_name}. Please check LLM configuration.",
                    requirement_type=RequirementType.FUNCTIONAL,
                    priority=Priority.MEDIUM,
                    citations=[
                        Citation(
                            text="LLM service not available",
                            location=SourceLocation(
                                document=doc_name,
                                section="N/A"
                            )
                        )
                    ],
                    stakeholders=["System"],
                    acceptance_criteria=[]
                )
                example_requirements.append(sample_requirement)
            
            return {
                'requirements': example_requirements,
                'hypotheses': []
            }
    
    async def self_improvement_pass(
        self, 
        current_requirements: List[BusinessRequirement],
        current_hypotheses: List[HypothesisRequirement],
        documents: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Stage 2: Self-improvement pass to enhance the initial draft.
        
        - Search for missing, ambiguous, or duplicate requirements
        - Deep rescan by document sections (strategy, service, data, regulations, constraints)
        - Decompose atomic violations (multiple requirements in one statement)
        - Review incomplete traceability (missing citations/locations)
        
        Args:
            current_requirements: Current list of business requirements
            current_hypotheses: Current list of hypothesis requirements
            documents: Source documents content
            
        Returns:
            Dict containing improved 'requirements' and 'hypotheses' lists
        """
        
        try:
            # Build prompt for self-improvement
            user_prompt = self._build_stage2_prompt(current_requirements, current_hypotheses, documents)
            
            # Call LLM service for improvement suggestions
            llm_response = await self.llm_service.call_llm_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse improved requirements
            improved_requirements = current_requirements.copy()  # Start with current
            improved_hypotheses = current_hypotheses.copy()
            
            # Apply improvements from LLM response
            if 'data' in llm_response and 'requirements' in llm_response['data']:
                improved_requirements = []
                for req_data in llm_response['data']['requirements']:
                    try:
                        requirement = self._convert_llm_to_requirement(req_data)
                        improved_requirements.append(requirement)
                    except Exception as e:
                        print(f"Error converting improved requirement: {e}")
                        continue
            
            return {
                'requirements': improved_requirements,
                'hypotheses': improved_hypotheses
            }
            
        except Exception as e:
            print(f"Self-improvement LLM call failed: {e}")
            # Return original requirements if improvement fails
            return {
                'requirements': current_requirements,
                'hypotheses': current_hypotheses
            }
    
    async def fix_verification_issues(
        self,
        requirements: List[BusinessRequirement],
        issues: List[VerificationIssue],
        documents: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Stage 5: Fix requirements based on verification issues from Verifier.
        
        - Address each issue in the bug report
        - Fix critical errors immediately or discard BR
        - Enhance justification gaps with better evidence and explanations
        
        Args:
            requirements: Current business requirements
            issues: List of verification issues to fix
            documents: Source documents for reference
            
        Returns:
            Dict containing fixed 'requirements' list
        """
        
        # Group issues by BR ID for efficient processing
        issues_by_br = {}
        for issue in issues:
            if issue.br_id not in issues_by_br:
                issues_by_br[issue.br_id] = []
            issues_by_br[issue.br_id].append(issue)
        
        fixed_requirements = []
        
        for req in requirements:
            if req.br_id in issues_by_br:
                # Apply fixes for this requirement
                req_issues = issues_by_br[req.br_id]
                
                # Check for critical errors
                critical_errors = [i for i in req_issues if i.error_type == "critical_error"]
                
                if critical_errors:
                    try:
                        # Try to fix critical errors with LLM
                        fixed_req = await self._fix_critical_errors(req, critical_errors, documents)
                        if fixed_req:
                            fixed_requirements.append(fixed_req)
                        # else: discard requirement if unfixable
                    except Exception as e:
                        print(f"Failed to fix critical errors for {req.br_id}: {e}")
                        # Discard requirement if fixing fails
                        continue
                else:
                    try:
                        # Fix justification gaps
                        improved_req = await self._fix_justification_gaps(req, req_issues, documents)
                        fixed_requirements.append(improved_req)
                    except Exception as e:
                        print(f"Failed to fix justification gaps for {req.br_id}: {e}")
                        # Keep original requirement if fixing fails
                        fixed_requirements.append(req)
            else:
                # No issues with this requirement
                fixed_requirements.append(req)
        
        return {
            'requirements': fixed_requirements
        }
    
    def _build_stage1_prompt(self, documents: Dict[str, str]) -> str:
        """Build prompt for stage 1 initial draft generation."""
        prompt = f"""
        Extract business requirements from the provided RFP documents.
        
        For each requirement:
        1. Include direct citations with exact text and location information
        2. Apply principles of clarity, completeness, consistency, and verifiability
        3. If evidence is insufficient, classify as hypothesis rather than requirement
        
        Documents:
        """
        
        for doc_name, content in documents.items():
            prompt += f"\n--- {doc_name} ---\n{content[:2000]}...\n"  # Truncate for example
        
        return prompt
    
    def _build_stage2_prompt(
        self, 
        requirements: List[BusinessRequirement],
        hypotheses: List[HypothesisRequirement], 
        documents: Dict[str, str]
    ) -> str:
        """Build prompt for stage 2 self-improvement."""
        prompt = f"""
        Improve the following initial requirements draft by:
        
        1. Identifying missing, ambiguous, or duplicate requirements
        2. Scanning documents by section (strategy, services, data, regulations, constraints)
        3. Decomposing compound requirements into atomic ones
        4. Improving traceability and citations
        
        Current Requirements: {len(requirements)} items
        Current Hypotheses: {len(hypotheses)} items
        
        Review and improve these systematically.
        """
        
        return prompt
    
    def _convert_llm_to_requirement(self, req_data: Dict[str, Any]) -> BusinessRequirement:
        """Convert LLM response data to BusinessRequirement model."""
        
        # Extract citations
        citations = []
        for citation_data in req_data.get('근거인용', []):
            citation = Citation(
                text=citation_data.get('quote', ''),
                location=SourceLocation(
                    document=citation_data.get('doc_id', ''),
                    section=citation_data.get('loc', ''),
                    page_number=None,
                    paragraph=None
                ),
                context=citation_data.get('context')
            )
            citations.append(citation)
        
        # Extract acceptance criteria
        acceptance_criteria = []
        if req_data.get('수용기준(초안)'):
            criteria = AcceptanceCriteria(
                criterion_id=f"AC_{uuid.uuid4().hex[:6]}",
                description=req_data['수용기준(초안)'],
                testable=True
            )
            acceptance_criteria.append(criteria)
        
        # Determine requirement type and priority
        req_type = RequirementType.FUNCTIONAL  # Default
        priority = Priority.MEDIUM  # Default
        
        if req_data.get('우선순위'):
            priority_str = req_data['우선순위'].lower()
            if 'high' in priority_str or '높음' in priority_str:
                priority = Priority.HIGH
            elif 'low' in priority_str or '낮음' in priority_str:
                priority = Priority.LOW
            elif 'critical' in priority_str or '중요' in priority_str:
                priority = Priority.CRITICAL
        
        return BusinessRequirement(
            br_id=req_data.get('요구사항 ID', f"BR_{uuid.uuid4().hex[:8]}"),
            title=req_data.get('요구사항명', 'Untitled Requirement'),
            description=req_data.get('고객 요구사항 상세 내용', ''),
            requirement_type=req_type,
            priority=priority,
            citations=citations,
            stakeholders=req_data.get('이해관계자') or [],
            business_value=req_data.get('가치/효익(초안)'),
            acceptance_criteria=acceptance_criteria,
            tags=req_data.get('별칭/동의어') or [],
            dependencies=req_data.get('중복병합근거') or [],
            constraints=[req_data.get('제약사항')] if req_data.get('제약사항') else [],
            assumptions=[],
            notes=req_data.get('비고')
        )
    
    async def _fix_critical_errors(
        self, 
        requirement: BusinessRequirement, 
        errors: List[VerificationIssue],
        documents: Dict[str, str]
    ) -> Optional[BusinessRequirement]:
        """Fix critical errors in a requirement using LLM."""
        
        error_descriptions = [error.description for error in errors]
        
        prompt = f"""
        다음 비즈니스 요구사항에서 발견된 치명적 오류를 수정해주세요:
        
        요구사항: {requirement.title}
        설명: {requirement.description}
        
        발견된 오류들:
        {chr(10).join(f'- {desc}' for desc in error_descriptions)}
        
        원본 문서를 참조하여 요구사항을 수정하거나, 수정이 불가능하면 null을 반환하세요.
        수정된 요구사항을 JSON 형태로 반환하세요.
        """
        
        try:
            response = await self.llm_service.call_llm(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                temperature=0.1
            )
            
            # Try to parse as JSON and convert back to requirement
            # For now, return the original requirement
            return requirement
            
        except Exception:
            return None  # Could not fix
    
    async def _fix_justification_gaps(
        self, 
        requirement: BusinessRequirement,
        issues: List[VerificationIssue],
        documents: Dict[str, str]
    ) -> BusinessRequirement:
        """Fix justification gaps in a requirement."""
        
        # For now, return the original requirement
        # In full implementation, this would use LLM to improve citations and justifications
        return requirement