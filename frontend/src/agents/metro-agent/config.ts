import type { AgentConfig } from '../types';
import { metroAgentIntents } from './intents';
import { config } from '@/lib/config';

export const metroAgentConfig: AgentConfig = {
  id: 'metro_agent',
  name: 'Metro İstanbul Asistanı',
  description: 'Metro İstanbul çağrı merkezi AI asistanı',
  icon: '🚇',
  color: '#0066CC',
  baseUrl: config.apiBaseUrl,
  capabilities: {
    chat: true,
    voiceInput: true,
    quickReplies: true,
    faultReporting: true,
    analytics: true,
  },
  intents: metroAgentIntents,
  metadata: {
    supportPhone: '153',
    website: 'metro.istanbul',
    operator: 'İBB Metro İstanbul',
  },
};
