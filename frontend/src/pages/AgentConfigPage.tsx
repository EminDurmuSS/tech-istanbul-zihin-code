import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useAgent } from '@/hooks/useAgent';
import { CheckCircle } from 'lucide-react';

export function AgentConfigPage() {
  const { allAgents, currentAgent } = useAgent();

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Agent Configuration</h1>

      <div className="grid gap-4">
        {allAgents.map((agent) => {
          const isActive = currentAgent.id === agent.id;

          return (
            <Card key={agent.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{agent.icon}</span>
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {agent.name}
                        {isActive && <Badge variant="default">Active</Badge>}
                      </CardTitle>
                      <CardDescription>{agent.description}</CardDescription>
                    </div>
                  </div>
                  <CheckCircle className="h-5 w-5 text-green-500" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium mb-2">Capabilities</p>
                    <div className="flex flex-wrap gap-2">
                      {agent.capabilities.chat && <Badge variant="outline">Chat</Badge>}
                      {agent.capabilities.voiceInput && <Badge variant="outline">Voice Input</Badge>}
                      {agent.capabilities.quickReplies && <Badge variant="outline">Quick Replies</Badge>}
                      {agent.capabilities.faultReporting && <Badge variant="outline">Fault Reporting</Badge>}
                      {agent.capabilities.analytics && <Badge variant="outline">Analytics</Badge>}
                    </div>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">Base URL</p>
                    <code className="text-sm bg-muted px-2 py-1 rounded">{agent.baseUrl}</code>
                  </div>

                  <div>
                    <p className="text-sm font-medium mb-2">Supported Intents ({agent.intents.length})</p>
                    <div className="flex flex-wrap gap-1">
                      {agent.intents.map((intent) => (
                        <Badge key={intent} variant="secondary" className="text-xs">
                          {intent}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {agent.metadata && Object.keys(agent.metadata).length > 0 && (
                    <div>
                      <p className="text-sm font-medium mb-2">Metadata</p>
                      <div className="text-sm space-y-1">
                        {Object.entries(agent.metadata).map(([key, value]) => (
                          <div key={key} className="flex gap-2">
                            <span className="text-muted-foreground">{key}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
