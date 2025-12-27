import { useAgentStore } from '@/store';
import type { AgentConfig } from '@/agents/types';

export function useAgent() {
  const { currentAgentId, agents, setCurrentAgent, getCurrentAgent } = useAgentStore();

  const currentAgent = getCurrentAgent();

  const switchAgent = (agentId: string) => {
    setCurrentAgent(agentId);
  };

  return {
    currentAgent: currentAgent as AgentConfig,
    allAgents: agents,
    switchAgent,
    currentAgentId,
  };
}
