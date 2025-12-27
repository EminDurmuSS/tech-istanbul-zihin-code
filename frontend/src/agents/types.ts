import type { IntentType } from '@/api/types/models';

export interface AgentCapabilities {
  chat: boolean;
  voiceInput: boolean;
  quickReplies: boolean;
  faultReporting: boolean;
  analytics: boolean;
}

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  baseUrl: string;
  capabilities: AgentCapabilities;
  intents: IntentType[];
  metadata: Record<string, any>;
}

export interface AgentStatus {
  id: string;
  online: boolean;
  lastPing?: string;
}
