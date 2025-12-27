import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Message, ChatSession } from '@/api/types/models';
import { chatAPI } from '@/api/endpoints/chat';
import { STORAGE_KEYS } from '@/utils/constants';
import { v4 as uuidv4 } from 'uuid';

interface ChatStore {
  sessions: Map<string, ChatSession>;
  currentSessionId: string | null;
  messages: Message[];
  isTyping: boolean;

  // Actions
  sendMessage: (message: string, agentId: string) => Promise<void>;
  addMessage: (message: Message) => void;
  setTyping: (isTyping: boolean) => void;
  clearSession: () => void;
  loadSession: (sessionId: string) => void;
  createSession: (agentId: string) => string;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set, get) => ({
      sessions: new Map(),
      currentSessionId: null,
      messages: [],
      isTyping: false,

      sendMessage: async (message: string, agentId: string) => {
        const { currentSessionId, addMessage, setTyping } = get();

        // Create user message
        const userMessage: Message = {
          id: uuidv4(),
          role: 'user',
          content: message,
          timestamp: new Date().toISOString(),
        };

        addMessage(userMessage);
        setTyping(true);

        try {
          const response = await chatAPI.sendMessage({
            message,
            channel: 'web',
            session_id: currentSessionId || undefined,
          });

          // Create assistant message
          const assistantMessage: Message = {
            id: uuidv4(),
            role: 'assistant',
            content: response.response,
            timestamp: response.timestamp,
            metadata: {
              intent: response.intent,
              confidence: response.confidence,
              reportId: response.report_id,
              processingTime: response.processing_time_ms,
            },
            quickReplies: response.quick_replies,
          };

          addMessage(assistantMessage);
        } catch (error) {
          console.error('Failed to send message:', error);
        } finally {
          setTyping(false);
        }
      },

      addMessage: (message: Message) => {
        set((state) => {
          const newMessages = [...state.messages, message];

          // Update session
          if (state.currentSessionId) {
            const sessions = new Map(state.sessions);
            const session = sessions.get(state.currentSessionId);
            if (session) {
              session.messages = newMessages;
              session.updatedAt = new Date().toISOString();
              sessions.set(state.currentSessionId, session);
            }
            return { messages: newMessages, sessions };
          }

          return { messages: newMessages };
        });
      },

      setTyping: (isTyping: boolean) => {
        set({ isTyping });
      },

      clearSession: () => {
        set({ messages: [], currentSessionId: null });
      },

      loadSession: (sessionId: string) => {
        const { sessions } = get();
        const session = sessions.get(sessionId);
        if (session) {
          set({
            currentSessionId: sessionId,
            messages: session.messages,
          });
        }
      },

      createSession: (agentId: string) => {
        const sessionId = uuidv4();
        const session: ChatSession = {
          id: sessionId,
          agentId,
          messages: [],
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        };

        set((state) => {
          const sessions = new Map(state.sessions);
          sessions.set(sessionId, session);
          return {
            sessions,
            currentSessionId: sessionId,
            messages: [],
          };
        });

        return sessionId;
      },
    }),
    {
      name: STORAGE_KEYS.MESSAGES,
      partialize: (state) => ({
        sessions: Array.from(state.sessions.entries()),
        currentSessionId: state.currentSessionId,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && Array.isArray((state as any).sessions)) {
          state.sessions = new Map((state as any).sessions);
        }
      },
    }
  )
);
