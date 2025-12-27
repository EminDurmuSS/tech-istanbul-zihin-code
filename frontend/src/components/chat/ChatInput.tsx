import { useState, FormEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { VoiceRecorder } from './VoiceRecorder';

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleVoiceTranscript = (text: string) => {
    setMessage(text);
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t bg-background">
      <div className="flex gap-2">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Mesajınızı yazın..."
          disabled={disabled}
          className="flex-1"
        />
        <VoiceRecorder onTranscript={handleVoiceTranscript} />
        <Button type="submit" disabled={disabled || !message.trim()} size="icon">
          <Send className="h-4 w-4" />
        </Button>
      </div>
    </form>
  );
}
