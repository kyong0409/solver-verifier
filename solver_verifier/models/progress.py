"""Progress tracking models for pipeline execution."""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class ProgressStatus(str, Enum):
    """Status of a pipeline step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class PipelineStep(BaseModel):
    """Individual step in the pipeline."""
    step_id: str
    name: str
    description: str
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress_percent: int = 0
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class PipelineProgress(BaseModel):
    """Overall pipeline progress."""
    session_id: str
    total_steps: int
    current_step: int
    overall_progress: int  # 0-100
    status: ProgressStatus = ProgressStatus.PENDING
    started_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    steps: List[PipelineStep] = []
    current_iteration: int = 1
    max_iterations: int = 5
    
    def update_step(self, step_id: str, status: ProgressStatus, 
                   progress_percent: int = None, message: str = None, 
                   details: Dict[str, Any] = None, error: str = None):
        """Update a specific step's progress."""
        for step in self.steps:
            if step.step_id == step_id:
                step.status = status
                if progress_percent is not None:
                    step.progress_percent = progress_percent
                if message is not None:
                    step.message = message
                if details is not None:
                    step.details = details
                if error is not None:
                    step.error = error
                
                if status == ProgressStatus.IN_PROGRESS and step.started_at is None:
                    step.started_at = datetime.now()
                elif status in [ProgressStatus.COMPLETED, ProgressStatus.FAILED]:
                    step.completed_at = datetime.now()
                
                break
        
        # Update overall progress
        self._calculate_overall_progress()
        self.updated_at = datetime.now()
    
    def _calculate_overall_progress(self):
        """Calculate overall progress based on steps."""
        if not self.steps:
            self.overall_progress = 0
            return
        
        total_progress = sum(step.progress_percent for step in self.steps)
        self.overall_progress = min(100, total_progress // len(self.steps))
        
        # Update current step
        for i, step in enumerate(self.steps):
            if step.status == ProgressStatus.IN_PROGRESS:
                self.current_step = i + 1
                break
        elif all(step.status == ProgressStatus.COMPLETED for step in self.steps):
            self.current_step = len(self.steps)
            self.status = ProgressStatus.COMPLETED


class ProgressUpdate(BaseModel):
    """WebSocket progress update message."""
    type: str  # "progress_update", "step_update", "error", "complete"
    session_id: str
    timestamp: datetime
    data: Dict[str, Any]
    
    @classmethod
    def create_step_update(cls, session_id: str, step: PipelineStep):
        """Create a step update message."""
        return cls(
            type="step_update",
            session_id=session_id,
            timestamp=datetime.now(),
            data={
                "step_id": step.step_id,
                "name": step.name,
                "status": step.status,
                "progress_percent": step.progress_percent,
                "message": step.message,
                "details": step.details,
                "error": step.error
            }
        )
    
    @classmethod
    def create_progress_update(cls, session_id: str, progress: PipelineProgress):
        """Create a progress update message."""
        return cls(
            type="progress_update",
            session_id=session_id,
            timestamp=datetime.now(),
            data={
                "total_steps": progress.total_steps,
                "current_step": progress.current_step,
                "overall_progress": progress.overall_progress,
                "status": progress.status,
                "current_iteration": progress.current_iteration,
                "max_iterations": progress.max_iterations
            }
        )
    
    @classmethod
    def create_completion(cls, session_id: str, result: Dict[str, Any]):
        """Create a completion message."""
        return cls(
            type="complete",
            session_id=session_id,
            timestamp=datetime.now(),
            data=result
        )