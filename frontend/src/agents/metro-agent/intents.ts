import { IntentType } from '@/api/types/models';

export const metroAgentIntents: IntentType[] = [
  IntentType.FAULT_REPORT,
  IntentType.FAULT_INQUIRY,
  IntentType.SERVICE_STATUS,
  IntentType.DIRECTION_HELP,
  IntentType.TIMETABLE,
  IntentType.FARE_INFO,
  IntentType.STATION_INFO,
  IntentType.ACCESSIBILITY,
  IntentType.ANNOUNCEMENTS,
  IntentType.GENERAL_FAQ,
];
