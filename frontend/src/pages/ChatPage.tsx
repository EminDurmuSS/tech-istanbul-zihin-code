import { ChatContainer } from '@/components/chat/ChatContainer';
import { AgentSwitcher } from '@/components/layout/AgentSwitcher';

export function ChatPage() {
  return (
    <div className="container mx-auto p-4">
      <AgentSwitcher />
      <div className="mt-4">
        <ChatContainer />
      </div>
    </div>
  );
}
