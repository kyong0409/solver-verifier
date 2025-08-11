// Business Requirement Types
export interface BusinessRequirement {
  br_id: string;
  title: string;
  description: string;
  requirement_type: string;
  priority: string;
  citations: Citation[];
  stakeholders: string[];
  business_value?: string;
  acceptance_criteria: AcceptanceCriteria[];
  created_at: string;
  updated_at: string;
  tags: string[];
  dependencies: string[];
  conflicts: string[];
  assumptions: string[];
  constraints: string[];
  notes?: string;
}

export interface Citation {
  text: string;
  location: SourceLocation;
  context?: string;
}

export interface SourceLocation {
  document: string;
  section?: string;
  line_number?: number;
  page_number?: number;
  paragraph?: string;
}

export interface AcceptanceCriteria {
  criterion_id: string;
  description: string;
  testable: boolean;
}

export interface VerificationIssue {
  issue_id: string;
  br_id: string;
  error_type: string;
  severity: string;
  description: string;
  location?: string;
  citation_issue?: string;
  suggested_fix?: string;
  created_at: string;
}

export interface CoverageMetrics {
  total_requirements: number;
  recall: number;
  precision: number;
  misinterpretation_rate: number;
  traceability_score: number;
  completion_rate: number;
}

export interface RequirementSet {
  set_id: string;
  name: string;
  description?: string;
  business_requirements: BusinessRequirement[];
  hypotheses: any[];
  verification_issues: VerificationIssue[];
  coverage_metrics?: CoverageMetrics;
  pipeline_stage: number;
  iteration_count: number;
  status: string;
  created_at: string;
  updated_at: string;
  source_documents: string[];
}

// API Response Types
export interface ProcessResponse {
  message?: string;
  set_id?: string;
  status?: string;
}

export interface PipelineStatus {
  set_id: string;
  status: string;
  current_stage: number;
  iteration: number;
}

export interface PipelineStage {
  stage: number;
  name: string;
  description: string;
  performer: string;
}

export interface PipelineInfo {
  stages: PipelineStage[];
  verification_loop: string;
  supported_formats: string[];
}