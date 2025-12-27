import type { AgentConfig } from './types';
import { metroAgentConfig } from './metro-agent/config';

class AgentRegistry {
  private agents: Map<string, AgentConfig> = new Map();

  constructor() {
    // Register default agents
    this.register(metroAgentConfig);
  }

  register(agent: AgentConfig): void {
    this.agents.set(agent.id, agent);
  }

  unregister(id: string): void {
    this.agents.delete(id);
  }

  get(id: string): AgentConfig | undefined {
    return this.agents.get(id);
  }

  getAll(): AgentConfig[] {
    return Array.from(this.agents.values());
  }

  has(id: string): boolean {
    return this.agents.has(id);
  }
}

export const agentRegistry = new AgentRegistry();
