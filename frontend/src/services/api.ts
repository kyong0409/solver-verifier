import axios from 'axios';
import { RequirementSet, PipelineStatus, PipelineInfo } from '../types';

const API_BASE = process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 minutes for document processing
});

export class ApiService {
  // Process RFP documents with real-time progress
  static async processDocumentsRealtime(
    files: FileList,
    setName?: string,
    setDescription?: string
  ): Promise<{ session_id: string; message: string; websocket_url: string; files_uploaded: number }> {
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    if (setName) {
      formData.append('set_name', setName);
    }
    
    if (setDescription) {
      formData.append('set_description', setDescription);
    }

    const response = await api.post('/pipeline/process-realtime', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Process RFP documents (original method for compatibility)
  static async processDocuments(
    files: FileList,
    setName?: string,
    setDescription?: string
  ): Promise<RequirementSet> {
    const formData = new FormData();
    
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });
    
    if (setName) {
      formData.append('set_name', setName);
    }
    
    if (setDescription) {
      formData.append('set_description', setDescription);
    }

    const response = await api.post('/pipeline/process', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  }

  // Get pipeline status
  static async getPipelineStatus(setId: string): Promise<PipelineStatus> {
    const response = await api.get(`/pipeline/status/${setId}`);
    return response.data;
  }

  // Get pipeline information
  static async getPipelineInfo(): Promise<PipelineInfo> {
    const response = await api.get('/pipeline/stages');
    return response.data;
  }

  // Get current configuration
  static async getCurrentConfig(): Promise<any> {
    const response = await api.get('/pipeline/configure');
    return response.data;
  }

  // Configure analyzer prompt
  static async configureAnalyzerPrompt(prompt: string): Promise<any> {
    const formData = new FormData();
    formData.append('system_prompt', prompt);

    const response = await api.post('/pipeline/configure/analyzer', formData);
    return response.data;
  }

  // Configure verifier prompt
  static async configureVerifierPrompt(prompt: string): Promise<any> {
    const formData = new FormData();
    formData.append('system_prompt', prompt);

    const response = await api.post('/pipeline/configure/verifier', formData);
    return response.data;
  }

  // Load prompts from files
  static async loadPromptsFromFiles(): Promise<any> {
    const response = await api.post('/pipeline/prompts/load');
    return response.data;
  }

  // Save current prompts to files
  static async savePromptsToFiles(): Promise<any> {
    const response = await api.post('/pipeline/prompts/save');
    return response.data;
  }

  // Configure pipeline settings
  static async configurePipeline(config: {
    max_iterations?: number;
    acceptance_threshold?: number;
    enable_stage_4_review?: boolean;
  }): Promise<any> {
    const formData = new FormData();
    
    if (config.max_iterations !== undefined) {
      formData.append('max_iterations', config.max_iterations.toString());
    }
    if (config.acceptance_threshold !== undefined) {
      formData.append('acceptance_threshold', config.acceptance_threshold.toString());
    }
    if (config.enable_stage_4_review !== undefined) {
      formData.append('enable_stage_4_review', config.enable_stage_4_review.toString());
    }

    const response = await api.post('/pipeline/configure/pipeline', formData);
    return response.data;
  }
}