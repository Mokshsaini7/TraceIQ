import axios from 'axios';
import {
  BugSubmission,
  BugSubmissionCreate,
  BugAttachment,
  DiagnosisReport,
  AgentExecutionLog,
  Dataset,
  KnowledgeBaseStats,
  IngestionJob,
  SearchResponse,
  EvaluationMetrics,
  SystemArchitecture,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const LONG_TIMEOUT = 120000;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

// Important: API errors are intentionally allowed to reach the UI. TraceIQ must never
// pretend that a request succeeded by quietly returning local demo or mock data.
export const api = {
  getHealth: async () => {
    const res = await apiClient.get('/health');
    return res.data;
  },

  createSubmission: async (data: BugSubmissionCreate): Promise<BugSubmission> => {
    const res = await apiClient.post<BugSubmission>('/submissions', data, { timeout: LONG_TIMEOUT });
    return res.data;
  },

  listSubmissions: async (params?: {
    page?: number; page_size?: number; status?: string; severity?: string;
    priority?: string; language?: string; search?: string; sort_by?: string; sort_order?: string;
  }): Promise<{ total: number; page: number; page_size: number; items: BugSubmission[] }> => {
    const res = await apiClient.get('/submissions', { params });
    return res.data;
  },

  getSubmissionById: async (id: string): Promise<BugSubmission> => {
    const res = await apiClient.get<BugSubmission>(`/submissions/${id}`);
    return res.data;
  },

  uploadAttachment: async (submissionId: string, file: File): Promise<BugAttachment> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<BugAttachment>(`/submissions/${submissionId}/attachments`, formData, {
      timeout: LONG_TIMEOUT,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  getDiagnosisReport: async (submissionId: string): Promise<DiagnosisReport> => {
    const res = await apiClient.get<DiagnosisReport>(`/diagnosis/${submissionId}`);
    return res.data;
  },

  triggerDiagnosis: async (submissionId: string, forceReanalysis = false): Promise<DiagnosisReport> => {
    const res = await apiClient.post<DiagnosisReport>('/diagnosis/trigger', {
      submission_id: submissionId,
      force_reanalysis: forceReanalysis,
    }, { timeout: LONG_TIMEOUT });
    return res.data;
  },

  getExecutionLogs: async (submissionId: string): Promise<AgentExecutionLog[]> => {
    const res = await apiClient.get<AgentExecutionLog[]>(`/diagnosis/${submissionId}/logs`);
    return res.data;
  },

  getKnowledgeStats: async (): Promise<KnowledgeBaseStats> => {
    const res = await apiClient.get<KnowledgeBaseStats>('/knowledge-base/stats');
    return res.data;
  },

  listDatasets: async (page = 1, pageSize = 50): Promise<Dataset[]> => {
    const res = await apiClient.get<Dataset[]>('/knowledge-base/datasets', {
      params: { page, page_size: pageSize },
    });
    return res.data;
  },

  uploadDataset: async (formData: FormData): Promise<Dataset> => {
    const res = await apiClient.post<Dataset>('/knowledge-base/datasets', formData, {
      timeout: LONG_TIMEOUT,
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  importDefaultDatasets: async () => {
    const res = await apiClient.post('/knowledge-base/import-default', undefined, { timeout: LONG_TIMEOUT });
    return res.data;
  },

  listIngestionJobs: async (datasetId?: string): Promise<IngestionJob[]> => {
    const res = await apiClient.get<IngestionJob[]>('/knowledge-base/jobs', {
      params: { dataset_id: datasetId },
    });
    return res.data;
  },

  searchHistoricalDefects: async (payload: {
    query: string; method?: 'semantic' | 'bm25' | 'hybrid'; top_k?: number;
    source_filter?: string; language_filter?: string;
  }): Promise<SearchResponse> => {
    const res = await apiClient.post<SearchResponse>('/search/historical', payload);
    return res.data;
  },

  getRetrievalEvaluation: async (): Promise<EvaluationMetrics> => {
    const res = await apiClient.get<EvaluationMetrics>('/search/evaluate', { timeout: LONG_TIMEOUT });
    return res.data;
  },

  getArchitecture: async (): Promise<SystemArchitecture> => {
    const res = await apiClient.get<SystemArchitecture>('/system/architecture');
    return res.data;
  },
};
