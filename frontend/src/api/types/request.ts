export interface MessageRequest {
  message: string;
  channel?: string;
  user_id?: string;
  session_id?: string;
}

export interface WebhookPayload {
  event_type: string;
  report_id: string;
  status: string;
  details?: Record<string, any>;
}
