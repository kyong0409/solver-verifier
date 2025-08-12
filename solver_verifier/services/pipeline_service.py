"""Core pipeline service implementing the 6-stage RFP requirement extraction pipeline."""

import uuid
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

from ..models.business_requirement import (
    BusinessRequirement, 
    RequirementSet, 
    HypothesisRequirement,
    VerificationIssue, 
    CoverageMetrics,
    Citation,
    SourceLocation
)
from ..models.agent_config import SystemSettings, AgentPromptConfig
from ..models.progress import PipelineProgress, PipelineStep, ProgressStatus, ProgressUpdate
from .analyzer_service import AnalyzerService
from .verifier_service import VerifierService
from .document_parser import DocumentParserService
from .websocket_manager import websocket_manager


class PipelineService:
    """
    6-stage RFP requirement extraction pipeline service.
    
    Stages:
    1. Initial BR Draft Generation
    2. Self-improvement Pass  
    3. Verifier Verification & Bug Report
    4. Bug Report Review (Optional)
    5. Bug Report-based Improvement
    6. Accept/Reject Decision
    """
    
    def __init__(self, settings: SystemSettings):
        self.settings = settings
        self.analyzer = AnalyzerService(settings)
        self.verifier = VerifierService(settings)
        self.document_parser = DocumentParserService()
        
    async def process_rfp_documents_with_progress(
        self, 
        document_paths: List[str],
        session_id: str,
        set_name: str = None,
        set_description: str = None
    ) -> RequirementSet:
        """
        Process RFP documents with real-time progress updates via WebSocket.
        
        Args:
            document_paths: List of paths to RFP documents
            session_id: Unique session ID for WebSocket updates
            set_name: Name for the requirement set
            set_description: Description for the requirement set
            
        Returns:
            Complete RequirementSet with all requirements and metrics
        """
        # Initialize progress tracker
        progress = PipelineProgress(
            session_id=session_id,
            total_steps=8,  # Document parsing + 6 pipeline stages + final processing
            current_step=1,
            overall_progress=0,
            max_iterations=self.settings.pipeline_config.max_iterations,
            steps=[
                PipelineStep(step_id="doc_parsing", name="문서 파싱", description="RFP 문서들을 파싱하고 텍스트를 추출합니다"),
                PipelineStep(step_id="stage1", name="1단계: 초기 BR 생성", description="Analyzer가 초기 비즈니스 요구사항을 추출합니다"),
                PipelineStep(step_id="stage2", name="2단계: 자체 개선", description="Analyzer가 추출된 요구사항을 개선합니다"),
                PipelineStep(step_id="verification_loop", name="3-5단계: 검증 루프", description="Verifier가 검증하고 Analyzer가 수정합니다"),
                PipelineStep(step_id="stage6", name="6단계: 최종 판정", description="최종 수용/거부 결정을 내립니다"),
                PipelineStep(step_id="completion", name="완료", description="결과를 정리하고 완료합니다")
            ]
        )
        progress.status = ProgressStatus.IN_PROGRESS
        progress.started_at = datetime.now()

        # Send initial progress
        await websocket_manager.send_update(
            session_id, 
            ProgressUpdate.create_progress_update(session_id, progress)
        )

        try:
            # Initialize requirement set
            requirement_set = RequirementSet(
                set_id=str(uuid.uuid4()),
                name=set_name or f"RFP_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=set_description,
                source_documents=[Path(p).name for p in document_paths],
                pipeline_stage=1
            )

            # Step 1: Document Parsing
            progress.update_step("doc_parsing", ProgressStatus.IN_PROGRESS, 0, "문서를 파싱하고 있습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[0]))

            documents_content = await self.document_parser.parse_documents(document_paths)
            
            progress.update_step("doc_parsing", ProgressStatus.COMPLETED, 100, f"{len(documents_content)}개 문서 파싱 완료")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[0]))
            await websocket_manager.send_update(session_id, ProgressUpdate.create_progress_update(session_id, progress))

            # Stage 1: Initial BR Draft Generation
            progress.update_step("stage1", ProgressStatus.IN_PROGRESS, 0, "초기 비즈니스 요구사항을 추출하고 있습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[1]))
            
            requirement_set = await self._stage_1_initial_draft_with_progress(requirement_set, documents_content, progress, session_id)
            
            progress.update_step("stage1", ProgressStatus.COMPLETED, 100, f"{len(requirement_set.business_requirements)}개 초기 요구사항 추출 완료")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[1]))

            # Stage 2: Self-improvement Pass
            progress.update_step("stage2", ProgressStatus.IN_PROGRESS, 0, "요구사항을 개선하고 있습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[2]))
            
            requirement_set = await self._stage_2_self_improvement_with_progress(requirement_set, documents_content, progress, session_id)
            
            progress.update_step("stage2", ProgressStatus.COMPLETED, 100, f"{len(requirement_set.business_requirements)}개 요구사항으로 개선 완료")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[2]))

            # Stages 3-5: Verification loop
            progress.update_step("verification_loop", ProgressStatus.IN_PROGRESS, 0, "검증 루프를 시작합니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[3]))
            
            requirement_set = await self._verification_loop_with_progress(requirement_set, documents_content, progress, session_id)
            
            progress.update_step("verification_loop", ProgressStatus.COMPLETED, 100, f"{progress.current_iteration}회 반복 후 검증 완료")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[3]))

            # Stage 6: Final Accept/Reject Decision
            progress.update_step("stage6", ProgressStatus.IN_PROGRESS, 0, "최종 판정을 진행합니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[4]))
            
            requirement_set = await self._stage_6_final_decision(requirement_set)
            
            progress.update_step("stage6", ProgressStatus.COMPLETED, 100, f"최종 판정: {requirement_set.status}")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[4]))

            # Final completion
            progress.update_step("completion", ProgressStatus.IN_PROGRESS, 50, "결과를 정리하고 있습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[5]))

            # Save results to file
            await self._save_results_to_file(requirement_set, session_id)
            
            progress.update_step("completion", ProgressStatus.IN_PROGRESS, 75, "결과를 파일로 저장했습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[5]))

            # Final progress update
            progress.status = ProgressStatus.COMPLETED
            progress.overall_progress = 100
            progress.update_step("completion", ProgressStatus.COMPLETED, 100, "파이프라인 처리가 완료되었습니다!")
            
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[5]))
            await websocket_manager.send_update(session_id, ProgressUpdate.create_progress_update(session_id, progress))

            # Send completion message with results
            await websocket_manager.send_update(
                session_id,
                ProgressUpdate.create_completion(session_id, {
                    "success": True,
                    "requirements_count": len(requirement_set.business_requirements),
                    "hypotheses_count": len(requirement_set.hypotheses),
                    "status": requirement_set.status,
                    "iterations": progress.current_iteration
                })
            )

            return requirement_set

        except Exception as e:
            # Send error update
            progress.status = ProgressStatus.FAILED
            await websocket_manager.send_update(
                session_id,
                ProgressUpdate(
                    type="error",
                    session_id=session_id,
                    timestamp=datetime.now(),
                    data={"error": str(e)}
                )
            )
            requirement_set.status = "error"
            requirement_set.updated_at = datetime.now()
            raise e

    async def process_rfp_documents(
        self, 
        document_paths: List[str],
        set_name: str = None,
        set_description: str = None
    ) -> RequirementSet:
        """
        Process RFP documents through the complete 6-stage pipeline.
        
        Args:
            document_paths: List of paths to RFP documents
            set_name: Name for the requirement set
            set_description: Description for the requirement set
            
        Returns:
            Complete RequirementSet with all requirements and metrics
        """
        # Initialize requirement set
        requirement_set = RequirementSet(
            set_id=str(uuid.uuid4()),
            name=set_name or f"RFP_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=set_description,
            source_documents=[Path(p).name for p in document_paths],
            pipeline_stage=1
        )
        
        # Parse and prepare documents
        documents_content = await self.document_parser.parse_documents(document_paths)
        
        try:
            # Stage 1: Initial BR Draft Generation
            requirement_set = await self._stage_1_initial_draft(requirement_set, documents_content)
            
            # Stage 2: Self-improvement Pass
            requirement_set = await self._stage_2_self_improvement(requirement_set, documents_content)
            
            # Stages 3-5: Verification loop
            requirement_set = await self._verification_loop(requirement_set, documents_content)
            
            # Stage 6: Final Accept/Reject Decision
            requirement_set = await self._stage_6_final_decision(requirement_set)
            
        except Exception as e:
            requirement_set.status = "error"
            requirement_set.updated_at = datetime.now()
            # Log error details
            raise e
            
        return requirement_set
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return ['.pdf', '.md', '.txt', '.docx', '.pptx', '.xlsx']
    
    async def _stage_1_initial_draft(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str]
    ) -> RequirementSet:
        """
        Stage 1: Initial BR Draft Generation
        
        - Extract BR candidates with direct citations and location info
        - Apply clarity, completeness, consistency, verifiability principles
        - Separate confirmed requirements from hypotheses
        """
        requirement_set.pipeline_stage = 1
        requirement_set.updated_at = datetime.now()
        
        # Use Analyzer to generate initial draft
        draft_result = await self.analyzer.generate_initial_draft(documents)
        
        requirement_set.business_requirements = draft_result.get('requirements', [])
        requirement_set.hypotheses = draft_result.get('hypotheses', [])
        
        return requirement_set
    
    async def _stage_2_self_improvement(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str]
    ) -> RequirementSet:
        """
        Stage 2: Self-improvement Pass
        
        - Search for missing, ambiguous, or duplicate requirements
        - Deep rescan by document sections
        - Decompose multi-requirement statements
        - Review incomplete traceability
        """
        requirement_set.pipeline_stage = 2
        requirement_set.updated_at = datetime.now()
        
        # Use Analyzer to improve the draft
        improved_result = await self.analyzer.self_improvement_pass(
            requirement_set.business_requirements,
            requirement_set.hypotheses,
            documents
        )
        
        requirement_set.business_requirements = improved_result.get('requirements', [])
        requirement_set.hypotheses = improved_result.get('hypotheses', [])
        
        return requirement_set
    
    async def _verification_loop(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str]
    ) -> RequirementSet:
        """
        Stages 3-5: Verification Loop
        
        - Stage 3: Verifier verification and bug report generation
        - Stage 4: Optional bug report review
        - Stage 5: Bug report-based improvements
        - Repeat until acceptance criteria met or max iterations reached
        """
        consecutive_passes = 0
        max_iterations = self.settings.pipeline_config.max_iterations
        acceptance_threshold = self.settings.pipeline_config.acceptance_threshold
        
        for iteration in range(max_iterations):
            requirement_set.iteration_count = iteration + 1
            
            # Stage 3: Verification & Bug Report
            requirement_set.pipeline_stage = 3
            verification_result = await self.verifier.verify_requirements(
                requirement_set.business_requirements,
                documents
            )
            
            requirement_set.verification_issues = verification_result.get('issues', [])
            requirement_set.coverage_metrics = verification_result.get('metrics')
            
            # Check if verification passed (no critical errors)
            critical_errors = [
                issue for issue in requirement_set.verification_issues 
                if issue.error_type == "critical_error"
            ]
            
            if not critical_errors:
                consecutive_passes += 1
                if consecutive_passes >= acceptance_threshold:
                    break
            else:
                consecutive_passes = 0
                
            # Stage 4: Optional Review (if enabled)
            if self.settings.pipeline_config.enable_stage_4_review:
                requirement_set.pipeline_stage = 4
                # This would call external review service or wait for human input
                # For now, we'll skip this optional stage
                pass
            
            # Stage 5: Bug Report-based Improvements
            requirement_set.pipeline_stage = 5
            if requirement_set.verification_issues:
                improved_result = await self.analyzer.fix_verification_issues(
                    requirement_set.business_requirements,
                    requirement_set.verification_issues,
                    documents
                )
                requirement_set.business_requirements = improved_result.get('requirements', [])
                requirement_set.updated_at = datetime.now()
        
        return requirement_set
    
    async def _stage_6_final_decision(self, requirement_set: RequirementSet) -> RequirementSet:
        """
        Stage 6: Accept/Reject Decision
        
        - Accept if consecutive passes meet threshold
        - Reject if max iterations reached with persistent critical errors
        """
        requirement_set.pipeline_stage = 6
        requirement_set.updated_at = datetime.now()
        
        # Check for remaining critical errors
        critical_errors = [
            issue for issue in requirement_set.verification_issues 
            if issue.error_type == "critical_error"
        ]
        
        if not critical_errors:
            requirement_set.status = "accepted"
        else:
            requirement_set.status = "rejected"
            
        return requirement_set
    
    async def get_pipeline_status(self, set_id: str) -> Dict[str, Any]:
        """Get current pipeline processing status."""
        # This would typically query a database or cache
        # For now, return a placeholder
        return {
            "set_id": set_id,
            "status": "in_progress",
            "current_stage": 1,
            "iteration": 0
        }
    
    async def _stage_1_initial_draft_with_progress(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str],
        progress: PipelineProgress,
        session_id: str
    ) -> RequirementSet:
        """Stage 1 with progress updates."""
        requirement_set.pipeline_stage = 1
        requirement_set.updated_at = datetime.now()
        
        # Update progress: Starting LLM call
        progress.update_step("stage1", ProgressStatus.IN_PROGRESS, 25, "LLM을 호출하여 초기 요구사항을 추출하고 있습니다...")
        await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[1]))
        
        # Use Analyzer to generate initial draft
        draft_result = await self.analyzer.generate_initial_draft(documents)
        
        # Update progress: Processing results
        progress.update_step("stage1", ProgressStatus.IN_PROGRESS, 75, "추출된 요구사항을 처리하고 있습니다...")
        await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[1]))
        
        requirement_set.business_requirements = draft_result.get('requirements', [])
        requirement_set.hypotheses = draft_result.get('hypotheses', [])
        
        return requirement_set
    
    async def _stage_2_self_improvement_with_progress(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str],
        progress: PipelineProgress,
        session_id: str
    ) -> RequirementSet:
        """Stage 2 with progress updates."""
        requirement_set.pipeline_stage = 2
        requirement_set.updated_at = datetime.now()
        
        # Update progress: Starting improvement
        progress.update_step("stage2", ProgressStatus.IN_PROGRESS, 25, "자체 개선 과정을 시작합니다...")
        await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[2]))
        
        # Use Analyzer to improve the draft
        improved_result = await self.analyzer.self_improvement_pass(
            requirement_set.business_requirements,
            requirement_set.hypotheses,
            documents
        )
        
        # Update progress: Processing improvements
        progress.update_step("stage2", ProgressStatus.IN_PROGRESS, 75, "개선된 요구사항을 적용하고 있습니다...")
        await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[2]))
        
        requirement_set.business_requirements = improved_result.get('requirements', [])
        requirement_set.hypotheses = improved_result.get('hypotheses', [])
        
        return requirement_set
    
    async def _verification_loop_with_progress(
        self, 
        requirement_set: RequirementSet, 
        documents: Dict[str, str],
        progress: PipelineProgress,
        session_id: str
    ) -> RequirementSet:
        """Verification loop with progress updates."""
        consecutive_passes = 0
        max_iterations = self.settings.pipeline_config.max_iterations
        acceptance_threshold = self.settings.pipeline_config.acceptance_threshold
        
        for iteration in range(max_iterations):
            progress.current_iteration = iteration + 1
            requirement_set.iteration_count = iteration + 1
            
            # Update progress for current iteration
            iteration_progress = int((iteration / max_iterations) * 80)  # 80% max for iterations
            progress.update_step("verification_loop", ProgressStatus.IN_PROGRESS, iteration_progress, 
                               f"검증 루프 {iteration + 1}/{max_iterations}회차를 진행하고 있습니다...")
            await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[3]))
            await websocket_manager.send_update(session_id, ProgressUpdate.create_progress_update(session_id, progress))
            
            # Stage 3: Verification & Bug Report
            requirement_set.pipeline_stage = 3
            verification_result = await self.verifier.verify_requirements(
                requirement_set.business_requirements,
                documents
            )
            
            requirement_set.verification_issues = verification_result.get('issues', [])
            requirement_set.coverage_metrics = verification_result.get('metrics')
            
            # Check if verification passed (no critical errors)
            critical_errors = [
                issue for issue in requirement_set.verification_issues 
                if issue.error_type == "critical_error"
            ]
            
            if not critical_errors:
                consecutive_passes += 1
                progress.update_step("verification_loop", ProgressStatus.IN_PROGRESS, iteration_progress + 10, 
                                   f"검증 통과! ({consecutive_passes}/{acceptance_threshold})")
                await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[3]))
                
                if consecutive_passes >= acceptance_threshold:
                    break
            else:
                consecutive_passes = 0
                progress.update_step("verification_loop", ProgressStatus.IN_PROGRESS, iteration_progress + 5, 
                                   f"{len(critical_errors)}개 오류 발견, 수정 진행 중...")
                await websocket_manager.send_update(session_id, ProgressUpdate.create_step_update(session_id, progress.steps[3]))
                
            # Stage 4: Optional Review (if enabled)
            if self.settings.pipeline_config.enable_stage_4_review:
                requirement_set.pipeline_stage = 4
                # This would call external review service or wait for human input
                # For now, we'll skip this optional stage
                pass
            
            # Stage 5: Bug Report-based Improvements
            requirement_set.pipeline_stage = 5
            if requirement_set.verification_issues:
                improved_result = await self.analyzer.fix_verification_issues(
                    requirement_set.business_requirements,
                    requirement_set.verification_issues,
                    documents
                )
                requirement_set.business_requirements = improved_result.get('requirements', [])
                requirement_set.updated_at = datetime.now()
        
        return requirement_set

    
    async def _save_results_to_file(self, requirement_set: RequirementSet, session_id: str):
        """Save pipeline results to JSON file based on acceptance status."""
        import json
        from pathlib import Path
        
        # Determine output directory based on status
        if requirement_set.status == "accepted":
            output_dir = Path(self.settings.output_directory)
        else:
            # For rejected or error status, use rejected_output directory
            output_dir = Path("./rejected_output")
        
        # Create directory if it doesn't exist
        output_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp and status
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{requirement_set.name}_{timestamp}_{requirement_set.status}_{session_id[:8]}.json"
        filepath = output_dir / filename
        
        # Prepare data for JSON serialization
        result_data = {
            "metadata": {
                "session_id": session_id,
                "set_id": requirement_set.set_id,
                "name": requirement_set.name,
                "description": requirement_set.description,
                "status": requirement_set.status,
                "pipeline_stage": requirement_set.pipeline_stage,
                "source_documents": requirement_set.source_documents,
                "created_at": requirement_set.created_at.isoformat() if requirement_set.created_at else None,
                "updated_at": requirement_set.updated_at.isoformat() if requirement_set.updated_at else None,
                "total_requirements": len(requirement_set.business_requirements),
                "total_hypotheses": len(requirement_set.hypotheses),
                "total_verification_issues": len(requirement_set.verification_issues)
            },
            "business_requirements": [
                {
                    "requirement_id": req.br_id,
                    "title": req.title,
                    "description": req.description,
                    "category": req.requirement_type,
                    "priority": req.priority,
                    "stakeholders": req.stakeholders,
                    "acceptance_criteria": req.acceptance_criteria,
                    "citations": [
                        {
                            "text": citation.text,
                            "source_document": citation.location.document,
                            "page_number": citation.location.page_number,
                            "section": citation.location.section,
                            "line_number": citation.location.line_number,
                            "paragraph": citation.location.paragraph,
                            "context": citation.context
                        } for citation in req.citations
                    ],
                    "tags": req.tags,
                    "created_at": req.created_at.isoformat() if req.created_at else None
                } for req in requirement_set.business_requirements
            ],
            "hypotheses": [
                {
                    "hypothesis_id": hyp.hypothesis_id,
                    "description": hyp.description,
                    "confidence_score": hyp.confidence_level,
                    "supporting_evidence": hyp.evidence_needed,
                    "created_at": hyp.created_at.isoformat() if hyp.created_at else None
                } for hyp in requirement_set.hypotheses
            ],
            "verification_issues": [
                {
                    "issue_id": issue.issue_id,
                    "error_type": issue.error_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "affected_requirement_id": issue.br_id,
                    "suggested_fix": issue.suggested_fix,
                    "created_at": issue.created_at.isoformat() if issue.created_at else None
                } for issue in requirement_set.verification_issues
            ],
            "coverage_metrics": {
                "recall": requirement_set.coverage_metrics.recall if requirement_set.coverage_metrics else None,
                "precision": requirement_set.coverage_metrics.precision if requirement_set.coverage_metrics else None,
                "misinterpretation_rate": requirement_set.coverage_metrics.misinterpretation_rate if requirement_set.coverage_metrics else None,
                "traceability_score": requirement_set.coverage_metrics.traceability_score if requirement_set.coverage_metrics else None,
                "completion_rate": requirement_set.coverage_metrics.completion_rate if requirement_set.coverage_metrics else None,
                "total_requirements": requirement_set.coverage_metrics.total_requirements if requirement_set.coverage_metrics else None
            }
        }
        
        # Write to JSON file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Results saved to: {filepath}")
            print(f"   Status: {requirement_set.status}")
            print(f"   Requirements: {len(requirement_set.business_requirements)}")
            print(f"   Issues: {len(requirement_set.verification_issues)}")
            
        except Exception as e:
            print(f"❌ Error saving results: {str(e)}")
            raise e
