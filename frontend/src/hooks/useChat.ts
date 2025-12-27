import { useEffect } from 'react';
import { useChatStore } from '@/store';
import { useAgentStore } from '@/store';

export function useChat() {
  const { messages, isTyping, sendMessage, clearSession, createSession } = useChatStore();
  const { currentAgentId } = useAgentStore();

  useEffect(() => {
    // Create session if none exists
    if (!useChatStore.getState().currentSessionId) {
      createSession(currentAgentId);
    }
  }, [currentAgentId, createSession]);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message, currentAgentId);
  };

  return {
    messages,
    isTyping,
    sendMessage: handleSendMessage,
    clearSession,
  };
}
