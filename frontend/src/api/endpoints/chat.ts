import { apiClient } from '../client';
import type { MessageRequest } from '../types/request';
import type { MessageResponse } from '../types/response';

export const chatAPI = {
  sendMessage: async (request: MessageRequest): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>('/message', request);
  },

  checkHealth: async (): Promise<any> => {
    return apiClient.get('/health');
  },
};
