import type { AgentConfig } from './types';

export abstract class BaseAgent {
  constructor(public config: AgentConfig) {}

  abstract initialize(): Promise<void>;
  abstract checkHealth(): Promise<boolean>;
}
