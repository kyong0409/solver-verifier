import React, { useState } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  FileText, 
  Users, 
  Target,
  ChevronDown,
  ChevronRight,
  ExternalLink
} from 'lucide-react';
import { RequirementSet, BusinessRequirement, VerificationIssue } from '../types';

interface ResultsDisplayProps {
  results: RequirementSet | null;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ results }) => {
  const [expandedRequirements, setExpandedRequirements] = useState<Set<string>>(new Set());
  const [activeTab, setActiveTab] = useState<'requirements' | 'issues' | 'metrics'>('requirements');

  if (!results) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">결과가 없습니다.</p>
      </div>
    );
  }

  const toggleRequirement = (brId: string) => {
    const newExpanded = new Set(expandedRequirements);
    if (newExpanded.has(brId)) {
      newExpanded.delete(brId);
    } else {
      newExpanded.add(brId);
    }
    setExpandedRequirements(newExpanded);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'accepted':
        return <CheckCircle className="text-green-500" size={24} />;
      case 'rejected':
        return <XCircle className="text-red-500" size={24} />;
      case 'in_progress':
        return <AlertTriangle className="text-yellow-500" size={24} />;
      default:
        return <AlertTriangle className="text-gray-500" size={24} />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center space-x-3">
              {getStatusIcon(results.status)}
              <div>
                <h2 className="text-xl font-bold text-gray-900">{results.name}</h2>
                <p className="text-sm text-gray-500">
                  Stage {results.pipeline_stage}/6 • Iteration {results.iteration_count} • 
                  Status: <span className="capitalize font-medium">{results.status}</span>
                </p>
              </div>
            </div>
          </div>
          
          <div className="text-right">
            <p className="text-2xl font-bold text-gray-900">
              {results.business_requirements.length}
            </p>
            <p className="text-sm text-gray-500">Requirements</p>
          </div>
        </div>

        {results.description && (
          <p className="mt-4 text-gray-600">{results.description}</p>
        )}

        {/* Source Documents */}
        {results.source_documents.length > 0 && (
          <div className="mt-4">
            <p className="text-sm font-medium text-gray-700 mb-2">Source Documents:</p>
            <div className="flex flex-wrap gap-2">
              {results.source_documents.map((doc, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  <FileText size={12} className="mr-1" />
                  {doc}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8 px-6">
          {[
            { key: 'requirements', label: `Requirements (${results.business_requirements.length})` },
            { key: 'issues', label: `Issues (${results.verification_issues.length})` },
            { key: 'metrics', label: 'Metrics' }
          ].map(tab => (
            <button
              key={tab.key}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.key
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab(tab.key as any)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      <div className="p-6">
        {/* Requirements Tab */}
        {activeTab === 'requirements' && (
          <div className="space-y-4">
            {results.business_requirements.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No requirements extracted yet.</p>
            ) : (
              results.business_requirements.map((req) => (
                <RequirementCard
                  key={req.br_id}
                  requirement={req}
                  isExpanded={expandedRequirements.has(req.br_id)}
                  onToggle={() => toggleRequirement(req.br_id)}
                />
              ))
            )}
          </div>
        )}

        {/* Issues Tab */}
        {activeTab === 'issues' && (
          <div className="space-y-4">
            {results.verification_issues.length === 0 ? (
              <div className="text-center py-8">
                <CheckCircle className="mx-auto text-green-500 mb-4" size={48} />
                <p className="text-gray-500">No verification issues found.</p>
              </div>
            ) : (
              results.verification_issues.map((issue) => (
                <IssueCard key={issue.issue_id} issue={issue} />
              ))
            )}
          </div>
        )}

        {/* Metrics Tab */}
        {activeTab === 'metrics' && (
          <div>
            {results.coverage_metrics ? (
              <MetricsDisplay metrics={results.coverage_metrics} />
            ) : (
              <p className="text-gray-500 text-center py-8">Metrics not yet calculated.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Requirement Card Component
const RequirementCard: React.FC<{
  requirement: BusinessRequirement;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ requirement, isExpanded, onToggle }) => (
  <div className="border border-gray-200 rounded-lg">
    <div
      className="p-4 cursor-pointer hover:bg-gray-50"
      onClick={onToggle}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-3">
            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <h3 className="text-lg font-medium text-gray-900">{requirement.title}</h3>
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(requirement.priority)}`}>
              {requirement.priority}
            </span>
          </div>
          <p className="mt-2 text-gray-600 line-clamp-2">{requirement.description}</p>
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <span className="text-xs text-gray-500">{requirement.br_id}</span>
        </div>
      </div>
    </div>

    {isExpanded && (
      <div className="px-4 pb-4 border-t border-gray-100">
        <div className="mt-4 space-y-4">
          {/* Stakeholders */}
          {requirement.stakeholders.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Users size={16} className="text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Stakeholders</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {requirement.stakeholders.map((stakeholder, index) => (
                  <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                    {stakeholder}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Acceptance Criteria */}
          {requirement.acceptance_criteria.length > 0 && (
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <Target size={16} className="text-gray-500" />
                <span className="text-sm font-medium text-gray-700">Acceptance Criteria</span>
              </div>
              <ul className="space-y-1">
                {requirement.acceptance_criteria.map((criteria) => (
                  <li key={criteria.criterion_id} className="text-sm text-gray-600">
                    • {criteria.description}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Citations */}
          {requirement.citations.length > 0 && (
            <div>
              <span className="text-sm font-medium text-gray-700 mb-2 block">Citations</span>
              <div className="space-y-2">
                {requirement.citations.map((citation, index) => (
                  <div key={index} className="p-3 bg-gray-50 rounded text-sm">
                    <p className="text-gray-600 italic">"{citation.text}"</p>
                    <p className="text-gray-500 mt-1">
                      — {citation.location.document}
                      {citation.location.page_number && `, p.${citation.location.page_number}`}
                      {citation.location.section && `, §${citation.location.section}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )}
  </div>
);

// Issue Card Component
const IssueCard: React.FC<{ issue: VerificationIssue }> = ({ issue }) => (
  <div className="border border-gray-200 rounded-lg p-4">
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-2 mb-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
            {issue.severity}
          </span>
          <span className="text-xs text-gray-500">{issue.error_type.replace('_', ' ')}</span>
        </div>
        <p className="text-gray-900 font-medium">{issue.description}</p>
        {issue.suggested_fix && (
          <p className="text-gray-600 mt-2 text-sm">
            <strong>Suggested fix:</strong> {issue.suggested_fix}
          </p>
        )}
      </div>
      <div className="text-right">
        <p className="text-xs text-gray-500">BR: {issue.br_id}</p>
      </div>
    </div>
  </div>
);

// Metrics Display Component
const MetricsDisplay: React.FC<{ metrics: any }> = ({ metrics }) => (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div className="bg-blue-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-blue-700 mb-2">Recall (Coverage)</h4>
      <p className="text-2xl font-bold text-blue-900">{Math.round(metrics.recall * 100)}%</p>
    </div>
    <div className="bg-green-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-green-700 mb-2">Precision</h4>
      <p className="text-2xl font-bold text-green-900">{Math.round(metrics.precision * 100)}%</p>
    </div>
    <div className="bg-purple-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-purple-700 mb-2">Traceability</h4>
      <p className="text-2xl font-bold text-purple-900">{Math.round(metrics.traceability_score * 100)}%</p>
    </div>
    <div className="bg-yellow-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-yellow-700 mb-2">Completion Rate</h4>
      <p className="text-2xl font-bold text-yellow-900">{Math.round(metrics.completion_rate * 100)}%</p>
    </div>
    <div className="bg-red-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-red-700 mb-2">Misinterpretation</h4>
      <p className="text-2xl font-bold text-red-900">{Math.round(metrics.misinterpretation_rate * 100)}%</p>
    </div>
    <div className="bg-gray-50 p-4 rounded-lg">
      <h4 className="text-sm font-medium text-gray-700 mb-2">Total Requirements</h4>
      <p className="text-2xl font-bold text-gray-900">{metrics.total_requirements}</p>
    </div>
  </div>
);

const getPriorityColor = (priority: string) => {
  switch (priority.toLowerCase()) {
    case 'critical':
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-green-100 text-green-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getSeverityColor = (severity: string) => {
  switch (severity.toLowerCase()) {
    case 'high':
      return 'bg-red-100 text-red-800';
    case 'medium':
      return 'bg-yellow-100 text-yellow-800';
    case 'low':
      return 'bg-blue-100 text-blue-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

export default ResultsDisplay;