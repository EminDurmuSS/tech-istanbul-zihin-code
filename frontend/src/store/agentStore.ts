import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AgentConfig } from '@/agents/types';
import { agentRegistry } from '@/agents/registry';
import { STORAGE_KEYS } from '@/utils/constants';

interface AgentStore {
  currentAgentId: string;
  agents: AgentConfig[];

  // Actions
  setCurrentAgent: (agentId: string) => void;
  registerAgent: (agent: AgentConfig) => void;
  unregisterAgent: (agentId: string) => void;
  getCurrentAgent: () => AgentConfig | undefined;
  refreshAgents: () => void;
}

export const useAgentStore = create<AgentStore>()(
  persist(
    (set, get) => ({
      currentAgentId: 'metro_agent',
      agents: agentRegistry.getAll(),

      setCurrentAgent: (agentId: string) => {
        if (agentRegistry.has(agentId)) {
          set({ currentAgentId: agentId });
        }
      },

      registerAgent: (agent: AgentConfig) => {
        agentRegistry.register(agent);
        set({ agents: agentRegistry.getAll() });
      },

      unregisterAgent: (agentId: string) => {
        agentRegistry.unregister(agentId);
        set({ agents: agentRegistry.getAll() });
      },

      getCurrentAgent: () => {
        const { currentAgentId } = get();
        return agentRegistry.get(currentAgentId);
      },

      refreshAgents: () => {
        set({ agents: agentRegistry.getAll() });
      },
    }),
    {
      name: STORAGE_KEYS.CURRENT_AGENT,
    }
  )
);
