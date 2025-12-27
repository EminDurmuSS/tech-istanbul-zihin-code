export const INTENT_TYPES = {
  FAULT_REPORT: 'fault_report',
  FAULT_INQUIRY: 'fault_inquiry',
  SERVICE_STATUS: 'service_status',
  DIRECTION_HELP: 'direction_help',
  TIMETABLE: 'timetable',
  FARE_INFO: 'fare_info',
  STATION_INFO: 'station_info',
  ACCESSIBILITY: 'accessibility',
  ANNOUNCEMENTS: 'announcements',
  GENERAL_FAQ: 'general_faq',
} as const;

export const INTENT_LABELS: Record<string, string> = {
  fault_report: 'Arıza Bildirimi',
  fault_inquiry: 'Arıza Sorgulama',
  service_status: 'Hizmet Durumu',
  direction_help: 'Yol Tarifi',
  timetable: 'Sefer Saatleri',
  fare_info: 'Ücret Bilgisi',
  station_info: 'İstasyon Bilgisi',
  accessibility: 'Erişilebilirlik',
  announcements: 'Duyurular',
  general_faq: 'Genel Sorular',
};

export const STORAGE_KEYS = {
  THEME: 'metro-agent-theme',
  SESSION: 'metro-agent-session',
  MESSAGES: 'metro-agent-messages',
  CURRENT_AGENT: 'metro-agent-current-agent',
} as const;
