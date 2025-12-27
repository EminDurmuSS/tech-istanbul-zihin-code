import { Mic, MicOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useSpeechToText } from '@/hooks/useSpeechToText';
import { useEffect } from 'react';
import { toast } from 'sonner';

interface VoiceRecorderProps {
  onTranscript: (text: string) => void;
}

export function VoiceRecorder({ onTranscript }: VoiceRecorderProps) {
  const { isRecording, transcript, error, isSupported, startRecording, stopRecording } = useSpeechToText();

  useEffect(() => {
    if (transcript) {
      onTranscript(transcript);
    }
  }, [transcript, onTranscript]);

  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  if (!isSupported) {
    return null;
  }

  return (
    <Button
      type="button"
      variant={isRecording ? 'destructive' : 'ghost'}
      size="icon"
      onClick={isRecording ? stopRecording : startRecording}
      className={isRecording ? 'animate-pulse' : ''}
    >
      {isRecording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
    </Button>
  );
}
