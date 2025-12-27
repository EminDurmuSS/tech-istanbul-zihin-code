import { apiClient } from '../client';
import type {
  ServiceStatusResponse,
  FaultListResponse,
  LinesResponse,
  StationsResponse,
} from '../types/response';

export const metroAPI = {
  getServiceStatus: async (): Promise<ServiceStatusResponse> => {
    return apiClient.get<ServiceStatusResponse>('/service-status');
  },

  getActiveFaults: async (): Promise<FaultListResponse> => {
    return apiClient.get<FaultListResponse>('/faults');
  },

  getLines: async (): Promise<LinesResponse> => {
    return apiClient.get<LinesResponse>('/lines');
  },

  getStations: async (): Promise<StationsResponse> => {
    return apiClient.get<StationsResponse>('/stations');
  },

  getAnnouncements: async (language: string = 'tr'): Promise<any> => {
    return apiClient.get('/announcements', { language });
  },

  getFAQ: async (): Promise<any> => {
    return apiClient.get('/faq');
  },

  getTicketPrices: async (language: string = 'tr'): Promise<any> => {
    return apiClient.get('/ticket-prices', { language });
  },
};
