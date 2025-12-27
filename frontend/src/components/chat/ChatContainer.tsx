import { Card } from '@/components/ui/card';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';
import { useChat } from '@/hooks/useChat';

export function ChatContainer() {
  const { messages, isTyping, sendMessage, clearSession } = useChat();

  const handleSend = async (message: string) => {
    await sendMessage(message);
  };

  const handleQuickReply = async (reply: string) => {
    await sendMessage(reply);
  };

  return (
    <Card className="flex flex-col h-[calc(100vh-2rem)] max-w-4xl mx-auto">
      <ChatHeader onClearChat={clearSession} />
      <ChatMessages messages={messages} isTyping={isTyping} onQuickReply={handleQuickReply} />
      <ChatInput onSend={handleSend} disabled={isTyping} />
    </Card>
  );
}
