import { apiClient } from '../client';
import type { WebhookPayload } from '../types/request';

export const adminAPI = {
  updateFaultStatus: async (payload: WebhookPayload): Promise<any> => {
    return apiClient.post('/webhook/fault-update', payload);
  },

  // Mock analytics endpoints (to be implemented on backend)
  getAnalytics: async (): Promise<any> => {
    // Mock data for now
    return Promise.resolve({
      totalConversations: 1524,
      activeFaults: 12,
      avgResponseTime: 850,
      satisfactionRate: 94,
      intentDistribution: [
        { name: 'Arıza Bildirimi', value: 35 },
        { name: 'Hizmet Durumu', value: 25 },
        { name: 'Yol Tarifi', value: 15 },
        { name: 'Sefer Saatleri', value: 12 },
        { name: 'Diğer', value: 13 },
      ],
      responseTimeTrend: [
        { time: '09:00', value: 750 },
        { time: '12:00', value: 820 },
        { time: '15:00', value: 890 },
        { time: '18:00', value: 950 },
      ],
    });
  },
};
