import { useEffect, useRef } from 'react';
import type { Message } from '@/api/types/models';
import { ChatMessage } from './ChatMessage';
import { TypingIndicator } from './TypingIndicator';

interface ChatMessagesProps {
  messages: Message[];
  isTyping: boolean;
  onQuickReply?: (reply: string) => void;
}

export function ChatMessages({ messages, isTyping, onQuickReply }: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto">
      {messages.length === 0 ? (
        <div className="h-full flex items-center justify-center text-center p-8">
          <div>
            <h3 className="text-lg font-semibold mb-2">Metro İstanbul Asistanı</h3>
            <p className="text-muted-foreground">
              Merhaba! Size nasıl yardımcı olabilirim?
              <br />
              Arıza bildirimi, sefer saatleri, istasyon bilgisi ve daha fazlası için soru sorabilirsiniz.
            </p>
          </div>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} onQuickReply={onQuickReply} />
          ))}
          {isTyping && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
