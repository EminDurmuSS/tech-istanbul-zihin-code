import { useAgent } from '@/hooks/useAgent';
import { Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ChatHeaderProps {
  onClearChat: () => void;
}

export function ChatHeader({ onClearChat }: ChatHeaderProps) {
  const { currentAgent } = useAgent();

  return (
    <div className="p-4 border-b bg-background flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-2xl">{currentAgent.icon}</span>
        <div>
          <h2 className="font-semibold">{currentAgent.name}</h2>
          <p className="text-xs text-muted-foreground">{currentAgent.description}</p>
        </div>
      </div>
      <Button variant="ghost" size="icon" onClick={onClearChat}>
        <Trash2 className="h-4 w-4" />
      </Button>
    </div>
  );
}
