import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  FileText, 
  Zap, 
  Shield, 
  BarChart3,
  Loader2,
  Info
} from 'lucide-react';
import FileUploader from '../components/FileUploader';
import ResultsDisplay from '../components/ResultsDisplay';
import ProgressDisplay from '../components/ProgressDisplay';
import { ApiService } from '../services/api';
import { RequirementSet, PipelineInfo } from '../types';
import useWebSocket from '../hooks/useWebSocket';

const HomePage: React.FC = () => {
  const [files, setFiles] = useState<FileList | null>(null);
  const [setName, setSetName] = useState('');
  const [setDescription, setSetDescription] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState<RequirementSet | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pipelineInfo, setPipelineInfo] = useState<PipelineInfo | null>(null);
  const [processingStage, setProcessingStage] = useState<string>('');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  // WebSocket hook for real-time progress
  const { progress, isConnected, error: wsError, finalResult, connect, disconnect } = useWebSocket();

  useEffect(() => {
    // Load pipeline info on mount
    loadPipelineInfo();
  }, []);

  const loadPipelineInfo = async () => {
    try {
      const info = await ApiService.getPipelineInfo();
      setPipelineInfo(info);
    } catch (err) {
      console.error('Failed to load pipeline info:', err);
    }
  };

  const handleProcess = async () => {
    if (!files || files.length === 0) {
      setError('Please select files to process');
      return;
    }

    setIsProcessing(true);
    setError(null);
    setResults(null);
    setProcessingStage('파일을 업로드하고 있습니다...');

    try {
      // Start real-time processing
      const response = await ApiService.processDocumentsRealtime(files, setName, setDescription);
      
      const sessionId = response.session_id;
      setCurrentSessionId(sessionId);
      setProcessingStage('실시간 진행 상황을 연결하고 있습니다...');
      
      // Connect to WebSocket for real-time updates
      connect(sessionId);
      setProcessingStage('');
      
    } catch (err: any) {
      console.error('Processing error:', err);
      setError(err.response?.data?.detail || err.message || 'Processing failed');
      setProcessingStage('');
      setIsProcessing(false);
    }
  };

  // Handle final result from WebSocket
  useEffect(() => {
    if (finalResult) {
      console.log('Final result received:', finalResult);
      setIsProcessing(false);
      // You can set the results here if the finalResult contains the full RequirementSet
      // For now, we'll just show completion
    }
  }, [finalResult]);

  // Handle WebSocket errors
  useEffect(() => {
    if (wsError) {
      setError(wsError);
      setIsProcessing(false);
    }
  }, [wsError]);

  const clearResults = () => {
    setResults(null);
    setError(null);
    setFiles(null);
    setSetName('');
    setSetDescription('');
    setCurrentSessionId(null);
    setIsProcessing(false);
    setProcessingStage('');
    disconnect(); // Disconnect WebSocket
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                RFP Requirements Analyzer
              </h1>
              <p className="mt-2 text-gray-600">
                6-Stage Analyzer-Verifier Pipeline for Business Requirements Extraction
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Zap size={16} className="text-blue-500" />
                <span>Analyzer</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <Shield size={16} className="text-green-500" />
                <span>Verifier</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!results && !isProcessing ? (
          // Processing Form
          <div className="space-y-8">
            {/* Pipeline Info */}
            {pipelineInfo && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <Info className="text-blue-500 mt-1" size={20} />
                  <div>
                    <h3 className="text-sm font-medium text-blue-900">Pipeline Overview</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      6-stage pipeline with {pipelineInfo.verification_loop}
                    </p>
                    <p className="text-sm text-blue-600 mt-2">
                      <strong>Supported formats:</strong> {pipelineInfo.supported_formats.join(', ')}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Project Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Project Information</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="setName" className="block text-sm font-medium text-gray-700 mb-1">
                    Project Name
                  </label>
                  <input
                    type="text"
                    id="setName"
                    value={setName}
                    onChange={(e) => setSetName(e.target.value)}
                    placeholder="e.g., Project Alpha RFP"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessing}
                  />
                </div>
                <div>
                  <label htmlFor="setDescription" className="block text-sm font-medium text-gray-700 mb-1">
                    Description (Optional)
                  </label>
                  <input
                    type="text"
                    id="setDescription"
                    value={setDescription}
                    onChange={(e) => setSetDescription(e.target.value)}
                    placeholder="Brief project description"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={isProcessing}
                  />
                </div>
              </div>
            </div>

            {/* File Upload */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Documents</h2>
              <FileUploader
                onFilesChange={setFiles}
                supportedFormats={pipelineInfo?.supported_formats || ['.pdf', '.md', '.txt']}
                disabled={isProcessing}
              />
            </div>

            {/* Process Button */}
            <div className="flex justify-center">
              <button
                onClick={handleProcess}
                disabled={!files || files.length === 0 || isProcessing}
                className={`px-8 py-3 rounded-lg font-medium text-white transition-colors ${
                  !files || files.length === 0 || isProcessing
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isProcessing ? (
                  <div className="flex items-center space-x-2">
                    <Loader2 className="animate-spin" size={20} />
                    <span>Processing...</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <BarChart3 size={20} />
                    <span>Analyze Requirements</span>
                  </div>
                )}
              </button>
            </div>

            {/* Processing Status */}
            {processingStage && (
              <div className="text-center">
                <p className="text-gray-600">{processingStage}</p>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex">
                  <div className="text-red-400">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800">Processing Error</h3>
                    <div className="mt-2 text-sm text-red-700">
                      <p>{error}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : isProcessing ? (
          // Real-time Progress Display
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">파이프라인 실행 중</h2>
              <button
                onClick={clearResults}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                취소
              </button>
            </div>
            
            {processingStage && (
              <div className="text-center py-4">
                <div className="flex items-center justify-center space-x-3">
                  <Loader2 className="animate-spin text-blue-500" size={24} />
                  <span className="text-gray-600">{processingStage}</span>
                </div>
              </div>
            )}
            
            <ProgressDisplay 
              progress={progress} 
              isConnected={isConnected} 
              error={wsError || undefined} 
            />
          </div>
        ) : (
          // Results Display
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Results</h2>
              <button
                onClick={clearResults}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                New Analysis
              </button>
            </div>
            
            <ResultsDisplay results={results} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-gray-500 text-sm">
            Powered by Analyzer-Verifier Pipeline • Inspired by Gemini 2.5 Pro's IMO 2025 approach
          </p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;