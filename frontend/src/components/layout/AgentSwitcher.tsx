import { useAgent } from '@/hooks/useAgent';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

export function AgentSwitcher() {
  const { currentAgent, allAgents, switchAgent } = useAgent();

  if (allAgents.length <= 1) return null;

  return (
    <div className="flex gap-2 p-4 border-b">
      <span className="text-sm text-muted-foreground mr-2">Agents:</span>
      {allAgents.map((agent) => (
        <Button
          key={agent.id}
          variant={currentAgent.id === agent.id ? 'default' : 'outline'}
          size="sm"
          onClick={() => switchAgent(agent.id)}
          className="gap-2"
        >
          <span>{agent.icon}</span>
          <span>{agent.name}</span>
          {currentAgent.id === agent.id && <Badge variant="secondary">Active</Badge>}
        </Button>
      ))}
    </div>
  );
}
