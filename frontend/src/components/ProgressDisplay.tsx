import React from 'react';
import { CheckCircle, Clock, AlertCircle, Loader2, Circle } from 'lucide-react';

interface ProgressStep {
  step_id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'skipped';
  progress_percent: number;
  message?: string;
  details?: any;
  error?: string;
  started_at?: string;
  completed_at?: string;
}

interface ProgressData {
  total_steps: number;
  current_step: number;
  overall_progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  current_iteration: number;
  max_iterations: number;
  steps: ProgressStep[];
}

interface ProgressDisplayProps {
  progress: ProgressData | null;
  isConnected: boolean;
  error?: string;
}

const getStatusIcon = (status: string, progress: number) => {
  switch (status) {
    case 'completed':
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    case 'failed':
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    case 'in_progress':
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    case 'pending':
      return <Circle className="w-5 h-5 text-gray-400" />;
    default:
      return <Clock className="w-5 h-5 text-gray-400" />;
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-500';
    case 'failed':
      return 'bg-red-500';
    case 'in_progress':
      return 'bg-blue-500';
    case 'pending':
      return 'bg-gray-300';
    default:
      return 'bg-gray-300';
  }
};

const ProgressDisplay: React.FC<ProgressDisplayProps> = ({ progress, isConnected, error }) => {
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-3">
          <AlertCircle className="w-6 h-6 text-red-500" />
          <div>
            <h3 className="text-lg font-medium text-red-900">처리 중 오류가 발생했습니다</h3>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!progress) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-pulse w-4 h-4 bg-gray-400 rounded-full"></div>
          <span className="text-gray-600">처리를 시작하고 있습니다...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">파이프라인 진행 상황</h3>
          <div className="flex items-center space-x-4 mt-1 text-sm text-gray-600">
            <span>단계 {progress.current_step}/{progress.total_steps}</span>
            {progress.status === 'in_progress' && progress.current_iteration > 1 && (
              <span>반복 {progress.current_iteration}/{progress.max_iterations}</span>
            )}
            <span className={`px-2 py-1 rounded-full text-xs ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {isConnected ? '연결됨' : '연결 끊어짐'}
            </span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">{progress.overall_progress}%</div>
          <div className="text-sm text-gray-500">전체 진행률</div>
        </div>
      </div>

      {/* Overall Progress Bar */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-500 h-3 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress.overall_progress}%` }}
          ></div>
        </div>
      </div>

      {/* Step Details */}
      <div className="space-y-4">
        {progress.steps.map((step, index) => (
          <div key={step.step_id} className="flex items-start space-x-4">
            {/* Step Icon */}
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon(step.status, step.progress_percent)}
            </div>

            {/* Step Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-900">{step.name}</h4>
                <span className="text-sm text-gray-500">{step.progress_percent}%</span>
              </div>
              
              <p className="text-sm text-gray-600 mt-1">{step.description}</p>
              
              {/* Current Message */}
              {step.message && step.status === 'in_progress' && (
                <div className="mt-2 p-2 bg-blue-50 rounded text-sm text-blue-800">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>{step.message}</span>
                  </div>
                </div>
              )}

              {/* Completed Message */}
              {step.message && step.status === 'completed' && (
                <div className="mt-2 p-2 bg-green-50 rounded text-sm text-green-800">
                  {step.message}
                </div>
              )}

              {/* Error Message */}
              {step.error && (
                <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-800">
                  <div className="flex items-center space-x-2">
                    <AlertCircle className="w-4 h-4" />
                    <span>{step.error}</span>
                  </div>
                </div>
              )}

              {/* Step Progress Bar */}
              {step.status === 'in_progress' && step.progress_percent > 0 && (
                <div className="mt-3">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ease-out ${getStatusColor(step.status)}`}
                      style={{ width: `${step.progress_percent}%` }}
                    ></div>
                  </div>
                </div>
              )}

              {/* Additional Details */}
              {step.details && Object.keys(step.details).length > 0 && (
                <div className="mt-2 text-xs text-gray-500">
                  {Object.entries(step.details).map(([key, value]) => (
                    <span key={key} className="mr-4">
                      {key}: {String(value)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Final Status */}
      {progress.status === 'completed' && (
        <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <h4 className="font-medium text-green-900">처리가 완료되었습니다!</h4>
              <p className="text-sm text-green-700 mt-1">
                파이프라인의 모든 단계가 성공적으로 완료되었습니다.
              </p>
            </div>
          </div>
        </div>
      )}

      {progress.status === 'failed' && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-6 h-6 text-red-500" />
            <div>
              <h4 className="font-medium text-red-900">처리가 실패했습니다</h4>
              <p className="text-sm text-red-700 mt-1">
                파이프라인 처리 중 오류가 발생했습니다. 자세한 내용은 위의 단계별 오류 메시지를 확인해주세요.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressDisplay;