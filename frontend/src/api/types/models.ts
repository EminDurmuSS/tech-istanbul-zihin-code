export enum IntentType {
  FAULT_REPORT = 'fault_report',
  FAULT_INQUIRY = 'fault_inquiry',
  SERVICE_STATUS = 'service_status',
  DIRECTION_HELP = 'direction_help',
  TIMETABLE = 'timetable',
  FARE_INFO = 'fare_info',
  STATION_INFO = 'station_info',
  ACCESSIBILITY = 'accessibility',
  ANNOUNCEMENTS = 'announcements',
  GENERAL_FAQ = 'general_faq',
}

export interface Intent {
  type: IntentType;
  confidence: number;
  entities: Record<string, any>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  metadata?: {
    intent?: string;
    confidence?: number;
    reportId?: string;
    processingTime?: number;
  };
  quickReplies?: string[];
}

export interface ChatSession {
  id: string;
  agentId: string;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}
