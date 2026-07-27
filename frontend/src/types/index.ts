export interface SearchResult {
  source: string;
  status: string;
  profile_url?: string;
  title?: string;
  summary?: string;
  confidence: number;
  raw_data?: Record<string, any>;
  error_message?: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  results?: SearchResult[];
}
