export interface MessageResponse {
  success: boolean;
  response: string;
  intent: string;
  confidence: number;
  entities: Record<string, any>;
  report_id?: string;
  quick_replies: string[];
  actions: string[];
  processing_time_ms?: number;
  timestamp: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ServiceStatusResponse {
  success: boolean;
  statuses: Array<{
    line: string;
    status: string;
    message?: string;
  }>;
  timestamp: string;
}

export interface FaultListResponse {
  success: boolean;
  faults: Array<{
    id: string;
    station: string;
    line: string;
    equipment: string;
    status: string;
    priority: string;
    created_at: string;
    report_id?: string;
  }>;
  count: number;
  timestamp: string;
}

export interface LinesResponse {
  success: boolean;
  lines: Array<{
    id: string;
    name: string;
    color: string;
  }>;
  count: number;
}

export interface StationsResponse {
  success: boolean;
  stations: Array<{
    id: string;
    name: string;
    line: string;
  }>;
  count: number;
}
