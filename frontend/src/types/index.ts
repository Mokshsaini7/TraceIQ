// BugDiag TypeScript Type Definitions

export interface BugAttachment {
  id: string;
  submission_id: string;
  filename: string;
  original_filename: string;
  file_path: string;
  file_size: number;
  content_type: string;
  file_hash: string;
  created_at: string;
}

export interface BugAnalysisContext {
  schema_version: string;
  orchestration_status: 'completed' | 'partial' | 'failed';
  triage_status: string;
  log_analysis_status: string;
  triage_output?: TriageResult | null;
  log_analysis_output?: LogAnalysisResult | null;
  combined_context: Record<string, unknown>;
  errors: string[];
}

export interface BugSubmission {
  id: string;
  title: string;
  description: string;
  stack_trace?: string | null;
  error_logs?: string | null;
  programming_language?: string | null;
  framework?: string | null;
  environment_info?: string | null;
  severity: 'critical' | 'high' | 'medium' | 'low';
  priority: 'p1' | 'p2' | 'p3' | 'p4';
  reproduction_steps?: string | null;
  expected_behavior?: string | null;
  actual_behavior?: string | null;
  status: 'pending' | 'analyzing' | 'analyzed' | 'resolved' | 'closed' | 'failed';
  created_at: string;
  updated_at: string;
  attachments?: BugAttachment[];
  analysis_context?: BugAnalysisContext | null;
}

export interface BugSubmissionCreate {
  title: string;
  description: string;
  stack_trace?: string;
  error_logs?: string;
  programming_language?: string;
  framework?: string;
  environment_info?: string;
  severity: string;
  priority: string;
  reproduction_steps?: string;
  expected_behavior?: string;
  actual_behavior?: string;
}

export interface TriageReasoning {
  severity_reason: string;
  priority_reason: string;
  component_reason: string;
  evidence: string[];
}

export interface TriageResult {
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  priority: 'p1' | 'p2' | 'p3' | 'p4';
  affected_component: string;
  programming_language: string;
  framework?: string | null;
  confidence_score: number;
  reasoning: TriageReasoning;
  missing_information: string[];
  completeness_score: number;
}

export interface StackFrameInfo {
  file: string;
  line?: number | null;
  function?: string | null;
  code_context?: string | null;
  class_name?: string | null;
}

export interface LogAnalysisResult {
  has_stack_trace: boolean;
  detected_format?: string;
  frame_count?: number;
  analysis_summary?: string | null;
  exception_type?: string | null;
  error_message?: string | null;
  stack_frames: StackFrameInfo[];
  suspect_files: string[];
  technical_evidence: string[];
  failure_point?: { file?: string | null; class_name?: string | null; method?: string | null; line?: number | null } | null;
  code_path?: StackFrameInfo[];
  confidence_score?: number;
}

export interface HistoricalMatchReference {
  defect_id: string;
  source_repo: string;
  original_issue_id: string;
  title: string;
  similarity_score: number;
  resolution?: string | null;
  url?: string | null;
}

export interface RootCauseResult {
  identified_root_cause: string;
  explanation: string;
  confidence: number;
  supporting_evidence: string[];
  historical_matches: HistoricalMatchReference[];
}

export interface DuplicateMatch {
  defect_id: string;
  source_repo: string;
  original_issue_id: string;
  title: string;
  similarity_score: number;
  retrieval_method: string;
}

export interface DuplicateDetectionResult {
  is_duplicate: boolean;
  highest_similarity: number;
  potential_duplicates: DuplicateMatch[];
}

export interface FixRecommendation {
  title: string;
  description: string;
  diff_snippet?: string | null;
  is_verified_from_history: boolean;
  source_defect_id?: string | null;
}

export interface RemediationResult {
  verified_fixes: FixRecommendation[];
  suggested_fixes: FixRecommendation[];
  rationale: string;
  historical_references: HistoricalMatchReference[];
}

export interface DiagnosisReport {
  id: string;
  submission_id: string;
  triage_result?: TriageResult | null;
  log_analysis_result?: LogAnalysisResult | null;
  root_cause_result?: RootCauseResult | null;
  duplicate_detection_result?: DuplicateDetectionResult | null;
  remediation_result?: RemediationResult | null;
  overall_confidence: number;
  status: 'processing' | 'completed' | 'failed';
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentExecutionLog {
  id: string;
  submission_id: string;
  agent_name: string;
  status: string;
  input_payload?: any;
  output_payload?: any;
  execution_time_ms: number;
  error_message?: string | null;
  created_at: string;
}

export interface Dataset {
  id: string;
  name: string;
  source: string;
  description?: string | null;
  file_path: string;
  format: string;
  column_mapping?: Record<string, any> | null;
  total_records: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface IngestionJob {
  id: string;
  dataset_id: string;
  total_records: number;
  processed_records: number;
  failed_records: number;
  status: string;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBaseStats {
  total_datasets: number;
  total_defects: number;
  total_chunks: number;
  total_embeddings: number;
  by_source: Record<string, number>;
  by_language: Record<string, number>;
  vector_index_status: string;
  bm25_index_status: string;
}

export interface SearchResultItem {
  defect_id: string;
  original_issue_id: string;
  source_repo: string;
  title: string;
  description: string;
  stack_trace?: string | null;
  resolution?: string | null;
  status?: string | null;
  programming_language?: string | null;
  similarity_score: number;
  source_url?: string | null;
  retrieval_method: string;
  matched_chunk?: string | null;
}

export interface SearchResponse {
  query: string;
  method: string;
  total_results: number;
  execution_time_ms: number;
  results: SearchResultItem[];
}

export interface EvaluationMetrics {
  dataset_name: string;
  sample_queries_evaluated: number;
  precision_at_k: Record<string, number>;
  recall_at_k: Record<string, number>;
  mrr: number;
  comparison_by_method: Record<string, Record<string, number>>;
  timestamp: string;
}

export interface SystemArchitecture {
  platform_name: string;
  milestone: string;
  pipeline_workflow: string[];
  agents: Array<{
    name: string;
    role: string;
    responsibilities: string[];
  }>;
  tech_stack: Record<string, string>;
}
