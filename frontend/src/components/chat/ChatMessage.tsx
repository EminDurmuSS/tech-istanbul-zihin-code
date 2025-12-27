import type { Message } from '@/api/types/models';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/cn';
import ReactMarkdown from 'react-markdown';
import { MessageMetadata } from './MessageMetadata';
import { ReportIdDisplay } from './ReportIdDisplay';
import { QuickReplies } from './QuickReplies';

interface ChatMessageProps {
  message: Message;
  onQuickReply?: (reply: string) => void;
}

export function ChatMessage({ message, onQuickReply }: ChatMessageProps) {
  const isBot = message.role === 'assistant';

  return (
    <div className={cn('flex gap-3 p-4 animate-fadeIn', isBot ? 'bg-muted/50' : '')}>
      <Avatar className="h-8 w-8">
        <AvatarFallback>
          {isBot ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div className="flex-1 space-y-2">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {message.metadata?.reportId && <ReportIdDisplay reportId={message.metadata.reportId} />}

        {isBot && message.metadata && (
          <MessageMetadata
            intent={message.metadata.intent}
            confidence={message.metadata.confidence}
            processingTime={message.metadata.processingTime}
          />
        )}

        {message.quickReplies && onQuickReply && (
          <QuickReplies replies={message.quickReplies} onSelect={onQuickReply} />
        )}
      </div>
    </div>
  );
}
