"""Business Requirement (BR) models and schemas."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RequirementType(str, Enum):
    """Type of business requirement."""
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    BUSINESS_RULE = "business_rule"
    CONSTRAINT = "constraint"
    ASSUMPTION = "assumption"
    DEPENDENCY = "dependency"


class Priority(str, Enum):
    """Requirement priority level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ErrorType(str, Enum):
    """Types of verification errors."""
    CRITICAL_ERROR = "critical_error"
    JUSTIFICATION_GAP = "justification_gap"


class SourceLocation(BaseModel):
    """Location information for requirement source."""
    document: str = Field(..., description="Source document name/path")
    section: Optional[str] = Field(None, description="Section or page reference")
    line_number: Optional[int] = Field(None, description="Line number if applicable")
    page_number: Optional[int] = Field(None, description="Page number if applicable")
    paragraph: Optional[str] = Field(None, description="Paragraph identifier")


class Citation(BaseModel):
    """Direct citation from source document."""
    text: str = Field(..., description="Exact quoted text from source")
    location: SourceLocation = Field(..., description="Location of the citation")
    context: Optional[str] = Field(None, description="Surrounding context")


class AcceptanceCriteria(BaseModel):
    """Acceptance criteria for a requirement."""
    criterion_id: str = Field(..., description="Unique identifier for the criterion")
    description: str = Field(..., description="Description of the acceptance criterion")
    testable: bool = Field(True, description="Whether this criterion is testable")


class BusinessRequirement(BaseModel):
    """Core business requirement model."""
    br_id: str = Field(..., description="Unique identifier for the business requirement")
    title: str = Field(..., description="Brief title of the requirement")
    description: str = Field(..., description="Detailed description of the requirement")
    
    # Classification
    requirement_type: RequirementType = Field(..., description="Type of requirement")
    priority: Priority = Field(..., description="Priority level")
    
    # Traceability
    citations: List[Citation] = Field(default_factory=list, description="Direct citations from source documents")
    
    # Stakeholders and Value
    stakeholders: List[str] = Field(default_factory=list, description="List of stakeholders")
    business_value: Optional[str] = Field(None, description="Business value or rationale")
    
    # Acceptance criteria
    acceptance_criteria: List[AcceptanceCriteria] = Field(default_factory=list, description="Acceptance criteria")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    
    # Dependencies and relationships
    dependencies: List[str] = Field(default_factory=list, description="IDs of dependent requirements")
    conflicts: List[str] = Field(default_factory=list, description="IDs of conflicting requirements")
    
    # Additional metadata
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    constraints: List[str] = Field(default_factory=list, description="Constraints or limitations")
    notes: Optional[str] = Field(None, description="Additional notes")


class HypothesisRequirement(BaseModel):
    """Requirement hypothesis with insufficient evidence."""
    hypothesis_id: str = Field(..., description="Unique identifier for the hypothesis")
    description: str = Field(..., description="Description of the hypothetical requirement")
    rationale: str = Field(..., description="Reasoning behind the hypothesis")
    confidence_level: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0-1)")
    evidence_needed: List[str] = Field(default_factory=list, description="What evidence is needed to confirm")
    created_at: datetime = Field(default_factory=datetime.now)


class VerificationIssue(BaseModel):
    """Issue found during verification."""
    issue_id: str = Field(..., description="Unique identifier for the issue")
    br_id: str = Field(..., description="ID of the business requirement with issue")
    error_type: ErrorType = Field(..., description="Type of error")
    severity: str = Field(..., description="Severity level")
    description: str = Field(..., description="Description of the issue")
    location: Optional[str] = Field(None, description="Location where issue was found")
    citation_issue: Optional[str] = Field(None, description="Issue with citation if applicable")
    suggested_fix: Optional[str] = Field(None, description="Suggested fix for the issue")
    created_at: datetime = Field(default_factory=datetime.now)


class CoverageMetrics(BaseModel):
    """Coverage and quality metrics for requirements."""
    total_requirements: int = Field(..., description="Total number of requirements")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    misinterpretation_rate: float = Field(..., ge=0.0, le=1.0, description="Rate of misinterpretation")
    traceability_score: float = Field(..., ge=0.0, le=1.0, description="Traceability completeness score")
    completion_rate: float = Field(..., ge=0.0, le=1.0, description="Pipeline completion rate")


class RequirementSet(BaseModel):
    """Complete set of requirements with metadata."""
    set_id: str = Field(..., description="Unique identifier for the requirement set")
    name: str = Field(..., description="Name of the requirement set")
    description: Optional[str] = Field(None, description="Description of the requirement set")
    
    # Requirements
    business_requirements: List[BusinessRequirement] = Field(default_factory=list)
    hypotheses: List[HypothesisRequirement] = Field(default_factory=list)
    
    # Verification results
    verification_issues: List[VerificationIssue] = Field(default_factory=list)
    coverage_metrics: Optional[CoverageMetrics] = Field(None)
    
    # Pipeline metadata
    pipeline_stage: int = Field(default=1, ge=1, le=6, description="Current pipeline stage")
    iteration_count: int = Field(default=0, description="Number of iterations performed")
    status: str = Field(default="in_progress", description="Processing status")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Source information
    source_documents: List[str] = Field(default_factory=list, description="List of source document names")