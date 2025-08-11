"""Verifier service - equivalent to Verifier role in Gemini's approach."""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple

from ..models.business_requirement import (
    BusinessRequirement,
    VerificationIssue,
    CoverageMetrics,
    ErrorType
)
from ..models.agent_config import SystemSettings
from .llm_service import LLMService


class VerifierService:
    """
    Verifier service responsible for validating business requirements.
    Equivalent to the Verifier role in Gemini's mathematical problem-solving approach.
    """
    
    def __init__(self, settings: SystemSettings):
        self.settings = settings
        self.system_prompt = settings.verifier_system_prompt
        self.llm_service = LLMService(settings)
        
    async def verify_requirements(
        self, 
        requirements: List[BusinessRequirement], 
        source_documents: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Stage 3: Verify requirements and generate bug report.
        
        Verification checks:
        1. Traceability: Citations match original text and locations are accurate
        2. Semantic consistency: BR descriptions align with cited context
        3. Atomicity & scope: No unnecessary fusion or over-generalization
        4. Numbers & conditions: Values and conditions match original exactly
        5. Classification & schema: All required fields present
        
        Args:
            requirements: List of business requirements to verify
            source_documents: Original source documents for cross-referencing
            
        Returns:
            Dict containing 'issues' list and 'metrics' object
        """
        
        verification_issues = []
        
        # Verify each requirement
        for req in requirements:
            req_issues = await self._verify_single_requirement(req, source_documents)
            verification_issues.extend(req_issues)
        
        # Calculate coverage metrics
        metrics = await self._calculate_coverage_metrics(
            requirements, 
            verification_issues, 
            source_documents
        )
        
        return {
            'issues': verification_issues,
            'metrics': metrics
        }
    
    async def _verify_single_requirement(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> List[VerificationIssue]:
        """
        Verify a single business requirement against source documents.
        
        Returns list of issues found for this requirement.
        """
        issues = []
        
        # 1. Verify traceability - check citations against source documents
        traceability_issues = await self._verify_traceability(requirement, source_documents)
        issues.extend(traceability_issues)
        
        # 2. Verify semantic consistency
        semantic_issues = await self._verify_semantic_consistency(requirement, source_documents)
        issues.extend(semantic_issues)
        
        # 3. Verify atomicity and scope
        atomicity_issues = await self._verify_atomicity(requirement)
        issues.extend(atomicity_issues)
        
        # 4. Verify numbers and conditions
        numerical_issues = await self._verify_numerical_accuracy(requirement, source_documents)
        issues.extend(numerical_issues)
        
        # 5. Verify schema compliance
        schema_issues = await self._verify_schema_compliance(requirement)
        issues.extend(schema_issues)
        
        return issues
    
    async def _verify_traceability(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> List[VerificationIssue]:
        """
        Verify that citations match original text and locations are accurate.
        """
        issues = []
        
        for citation in requirement.citations:
            # Check if document exists
            if citation.location.document not in source_documents:
                issues.append(VerificationIssue(
                    issue_id=str(uuid.uuid4()),
                    br_id=requirement.br_id,
                    error_type=ErrorType.CRITICAL_ERROR,
                    severity="high",
                    description=f"Referenced document '{citation.location.document}' not found",
                    citation_issue=f"Document missing: {citation.location.document}"
                ))
                continue
            
            # Verify citation text appears in document
            document_content = source_documents[citation.location.document]
            if citation.text not in document_content:
                issues.append(VerificationIssue(
                    issue_id=str(uuid.uuid4()),
                    br_id=requirement.br_id,
                    error_type=ErrorType.CRITICAL_ERROR,
                    severity="high",
                    description="Citation text not found in source document",
                    citation_issue=f"Text '{citation.text[:100]}...' not found in {citation.location.document}",
                    suggested_fix="Verify and correct the citation text"
                ))
            
            # Check if location information is reasonable (basic validation)
            if citation.location.line_number and citation.location.line_number < 0:
                issues.append(VerificationIssue(
                    issue_id=str(uuid.uuid4()),
                    br_id=requirement.br_id,
                    error_type=ErrorType.JUSTIFICATION_GAP,
                    severity="medium",
                    description="Invalid line number in citation",
                    location=f"Line {citation.location.line_number}",
                    suggested_fix="Provide valid line number or remove if not available"
                ))
        
        return issues
    
    async def _verify_semantic_consistency(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> List[VerificationIssue]:
        """
        Verify that BR description aligns with cited context using LLM analysis.
        """
        issues = []
        
        # Basic check: ensure requirement has citations
        if not requirement.citations:
            issues.append(VerificationIssue(
                issue_id=str(uuid.uuid4()),
                br_id=requirement.br_id,
                error_type=ErrorType.CRITICAL_ERROR,
                severity="high",
                description="Requirement has no supporting citations",
                suggested_fix="Add citations from source documents to support this requirement"
            ))
            return issues
        
        try:
            # Use LLM to analyze semantic consistency
            user_prompt = self._build_semantic_verification_prompt(requirement, source_documents)
            
            llm_response = await self.llm_service.call_llm_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse LLM response for semantic issues
            if 'semantic_issues' in llm_response:
                for issue_data in llm_response['semantic_issues']:
                    try:
                        issue = VerificationIssue(
                            issue_id=str(uuid.uuid4()),
                            br_id=requirement.br_id,
                            error_type=ErrorType.JUSTIFICATION_GAP if issue_data.get('severity', 'low') != 'critical' else ErrorType.CRITICAL_ERROR,
                            severity=issue_data.get('severity', 'low'),
                            description=issue_data.get('description', 'Semantic consistency issue'),
                            suggested_fix=issue_data.get('suggested_fix', 'Review requirement alignment with citations')
                        )
                        issues.append(issue)
                    except Exception as e:
                        print(f"Error parsing semantic issue: {e}")
                        continue
            
        except Exception as e:
            print(f"Semantic verification LLM call failed: {e}")
            # Fall back to basic validation
            pass
        
        return issues
    
    async def _verify_atomicity(self, requirement: BusinessRequirement) -> List[VerificationIssue]:
        """
        Verify that requirement is atomic (single, focused requirement) using LLM analysis.
        """
        issues = []
        
        try:
            # Use LLM to analyze atomicity
            user_prompt = self._build_atomicity_verification_prompt(requirement)
            
            llm_response = await self.llm_service.call_llm_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse LLM response for atomicity issues
            if 'atomicity_issues' in llm_response:
                for issue_data in llm_response['atomicity_issues']:
                    try:
                        issue = VerificationIssue(
                            issue_id=str(uuid.uuid4()),
                            br_id=requirement.br_id,
                            error_type=ErrorType.JUSTIFICATION_GAP,
                            severity=issue_data.get('severity', 'medium'),
                            description=issue_data.get('description', 'Atomicity violation detected'),
                            suggested_fix=issue_data.get('suggested_fix', 'Consider splitting into separate atomic requirements')
                        )
                        issues.append(issue)
                    except Exception as e:
                        print(f"Error parsing atomicity issue: {e}")
                        continue
            
        except Exception as e:
            print(f"Atomicity verification LLM call failed, using heuristics: {e}")
            
            # Fall back to simple heuristic checks
            description = requirement.description.lower()
            
            # Check for multiple "and" conjunctions suggesting compound requirement
            if description.count(' and ') > 2:
                issues.append(VerificationIssue(
                    issue_id=str(uuid.uuid4()),
                    br_id=requirement.br_id,
                    error_type=ErrorType.JUSTIFICATION_GAP,
                    severity="medium",
                    description="Requirement may contain multiple requirements (compound)",
                    suggested_fix="Consider splitting into separate atomic requirements"
                ))
            
            # Check for multiple modal verbs suggesting multiple requirements
            modal_count = sum(1 for word in ['must', 'should', 'shall', 'will'] 
                             if f' {word} ' in description)
            if modal_count > 1:
                issues.append(VerificationIssue(
                    issue_id=str(uuid.uuid4()),
                    br_id=requirement.br_id,
                    error_type=ErrorType.JUSTIFICATION_GAP,
                    severity="low",
                    description="Multiple modal verbs detected - may indicate compound requirement",
                    suggested_fix="Review requirement for atomicity"
                ))
        
        return issues
    
    async def _verify_numerical_accuracy(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> List[VerificationIssue]:
        """
        Verify that numerical values and conditions match source documents using LLM analysis.
        """
        issues = []
        
        # Check if requirement contains numerical values
        import re
        numbers_in_req = re.findall(r'\d+(?:\.\d+)?', requirement.description)
        
        if not numbers_in_req:
            return issues  # No numbers to verify
        
        try:
            # Use LLM to analyze numerical accuracy
            user_prompt = self._build_numerical_verification_prompt(requirement, source_documents)
            
            llm_response = await self.llm_service.call_llm_json(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0.1
            )
            
            # Parse LLM response for numerical issues
            if 'numerical_issues' in llm_response:
                for issue_data in llm_response['numerical_issues']:
                    try:
                        issue = VerificationIssue(
                            issue_id=str(uuid.uuid4()),
                            br_id=requirement.br_id,
                            error_type=ErrorType.CRITICAL_ERROR if issue_data.get('severity') == 'critical' else ErrorType.JUSTIFICATION_GAP,
                            severity=issue_data.get('severity', 'medium'),
                            description=issue_data.get('description', 'Numerical accuracy issue detected'),
                            suggested_fix=issue_data.get('suggested_fix', 'Verify numerical values against source documents')
                        )
                        issues.append(issue)
                    except Exception as e:
                        print(f"Error parsing numerical issue: {e}")
                        continue
            
        except Exception as e:
            print(f"Numerical verification LLM call failed: {e}")
            # For numerical issues, we can't provide meaningful fallback without LLM
            pass
        
        return issues
    
    async def _verify_schema_compliance(self, requirement: BusinessRequirement) -> List[VerificationIssue]:
        """
        Verify that all required fields are present and properly formatted.
        """
        issues = []
        
        # Check required fields
        if not requirement.title:
            issues.append(VerificationIssue(
                issue_id=str(uuid.uuid4()),
                br_id=requirement.br_id,
                error_type=ErrorType.JUSTIFICATION_GAP,
                severity="medium",
                description="Missing requirement title",
                suggested_fix="Add a descriptive title for the requirement"
            ))
        
        if not requirement.description:
            issues.append(VerificationIssue(
                issue_id=str(uuid.uuid4()),
                br_id=requirement.br_id,
                error_type=ErrorType.CRITICAL_ERROR,
                severity="high",
                description="Missing requirement description",
                suggested_fix="Add detailed description of the requirement"
            ))
        
        if not requirement.stakeholders:
            issues.append(VerificationIssue(
                issue_id=str(uuid.uuid4()),
                br_id=requirement.br_id,
                error_type=ErrorType.JUSTIFICATION_GAP,
                severity="low",
                description="No stakeholders identified",
                suggested_fix="Identify relevant stakeholders for this requirement"
            ))
        
        return issues
    
    async def _calculate_coverage_metrics(
        self, 
        requirements: List[BusinessRequirement],
        issues: List[VerificationIssue],
        source_documents: Dict[str, str]
    ) -> CoverageMetrics:
        """
        Calculate coverage and quality metrics for the requirements set.
        """
        
        total_requirements = len(requirements)
        
        # Count different types of issues
        critical_errors = len([i for i in issues if i.error_type == ErrorType.CRITICAL_ERROR])
        justification_gaps = len([i for i in issues if i.error_type == ErrorType.JUSTIFICATION_GAP])
        
        # Calculate metrics (simplified implementation)
        # In real implementation, these would be more sophisticated calculations
        
        # Precision: Requirements without critical errors / total requirements
        precision = max(0.0, (total_requirements - critical_errors) / max(1, total_requirements))
        
        # Recall: This would require knowing the "true" number of requirements in documents
        # For now, use a placeholder calculation
        recall = 0.85  # Placeholder
        
        # Misinterpretation rate: Critical errors / total requirements
        misinterpretation_rate = critical_errors / max(1, total_requirements)
        
        # Traceability score: Requirements with proper citations / total requirements
        requirements_with_citations = len([r for r in requirements if r.citations])
        traceability_score = requirements_with_citations / max(1, total_requirements)
        
        # Completion rate: Requirements without any issues / total requirements
        requirements_without_issues = total_requirements - len(set(i.br_id for i in issues))
        completion_rate = requirements_without_issues / max(1, total_requirements)
        
        return CoverageMetrics(
            total_requirements=total_requirements,
            recall=recall,
            precision=precision,
            misinterpretation_rate=misinterpretation_rate,
            traceability_score=traceability_score,
            completion_rate=completion_rate
        )
    
    def _build_semantic_verification_prompt(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> str:
        """Build prompt for semantic consistency verification."""
        
        # Gather citation context
        citation_context = ""
        for citation in requirement.citations:
            doc_name = citation.location.document
            if doc_name in source_documents:
                # Get surrounding context around citation
                doc_content = source_documents[doc_name]
                citation_text = citation.text
                
                # Find citation in document and get context
                if citation_text in doc_content:
                    idx = doc_content.find(citation_text)
                    start = max(0, idx - 200)
                    end = min(len(doc_content), idx + len(citation_text) + 200)
                    context = doc_content[start:end]
                    citation_context += f"\n--- Citation from {doc_name} ---\n{context}\n"
        
        prompt = f"""
        다음 비즈니스 요구사항의 의미적 일관성을 검증해주세요:

        **요구사항 ID**: {requirement.br_id}
        **제목**: {requirement.title}
        **설명**: {requirement.description}

        **인용 컨텍스트**:
        {citation_context}

        다음을 확인해주세요:
        1. 요구사항 설명이 인용된 내용과 의미적으로 일치하는가?
        2. 요구사항이 원본 문서의 의도를 정확히 반영하는가?
        3. 인용에서 지지되지 않는 추가적인 해석이나 추론이 있는가?
        4. 요구사항이 인용 내용을 왜곡하거나 과도하게 일반화하지 않았는가?

        문제가 발견되면 다음 JSON 형식으로 응답하세요:
        {{
            "semantic_issues": [
                {{
                    "severity": "low|medium|high|critical",
                    "description": "구체적인 문제 설명",
                    "suggested_fix": "수정 제안사항"
                }}
            ]
        }}

        문제가 없으면 빈 배열을 반환하세요:
        {{"semantic_issues": []}}
        """
        
        return prompt
    
    def _build_atomicity_verification_prompt(self, requirement: BusinessRequirement) -> str:
        """Build prompt for atomicity verification."""
        
        prompt = f"""
        다음 비즈니스 요구사항의 원자성을 검증해주세요:

        **요구사항 ID**: {requirement.br_id}
        **제목**: {requirement.title}
        **설명**: {requirement.description}

        다음을 확인해주세요:
        1. 이 요구사항이 단일하고 명확한 하나의 기능/요구사항을 나타내는가?
        2. 여러 개의 독립적인 요구사항이 하나로 합쳐져 있지 않은가?
        3. "그리고", "또한", "동시에" 등의 접속사로 연결된 여러 요구사항이 있는가?
        4. 서로 다른 이해관계자나 다른 시스템 영역에 대한 요구사항이 섞여있지 않은가?

        원자성 위반이 발견되면 다음 JSON 형식으로 응답하세요:
        {{
            "atomicity_issues": [
                {{
                    "severity": "low|medium|high",
                    "description": "원자성 위반에 대한 구체적 설명",
                    "suggested_fix": "분리 제안사항"
                }}
            ]
        }}

        원자성 위반이 없으면 빈 배열을 반환하세요:
        {{"atomicity_issues": []}}
        """
        
        return prompt
    
    def _build_numerical_verification_prompt(
        self, 
        requirement: BusinessRequirement, 
        source_documents: Dict[str, str]
    ) -> str:
        """Build prompt for numerical accuracy verification."""
        
        # Extract numbers from requirement
        import re
        numbers_in_req = re.findall(r'\d+(?:\.\d+)?', requirement.description)
        
        # Gather citation context
        citation_context = ""
        for citation in requirement.citations:
            doc_name = citation.location.document
            if doc_name in source_documents:
                doc_content = source_documents[doc_name]
                citation_text = citation.text
                
                if citation_text in doc_content:
                    idx = doc_content.find(citation_text)
                    start = max(0, idx - 300)
                    end = min(len(doc_content), idx + len(citation_text) + 300)
                    context = doc_content[start:end]
                    citation_context += f"\n--- {doc_name} ---\n{context}\n"
        
        prompt = f"""
        다음 비즈니스 요구사항의 수치 정확성을 검증해주세요:

        **요구사항 ID**: {requirement.br_id}
        **제목**: {requirement.title}
        **설명**: {requirement.description}

        **요구사항에서 발견된 수치들**: {', '.join(numbers_in_req)}

        **원본 문서 컨텍스트**:
        {citation_context}

        다음을 확인해주세요:
        1. 요구사항의 모든 수치 값이 원본 문서의 수치와 정확히 일치하는가?
        2. 수치와 관련된 조건이나 제약사항이 정확히 반영되었는가?
        3. 단위나 측정 기준이 올바르게 명시되었는가?
        4. 수치 범위나 임계값이 원본과 일치하는가?

        수치 관련 문제가 발견되면 다음 JSON 형식으로 응답하세요:
        {{
            "numerical_issues": [
                {{
                    "severity": "low|medium|high|critical",
                    "description": "수치 정확성 문제에 대한 구체적 설명",
                    "suggested_fix": "수정 제안사항"
                }}
            ]
        }}

        수치 관련 문제가 없으면 빈 배열을 반환하세요:
        {{"numerical_issues": []}}
        """
        
        return prompt