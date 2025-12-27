import { useState, useEffect, useRef } from 'react';

interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message: string;
}

export function useSpeechToText() {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  useEffect(() => {
    if (!isSupported) {
      setError('Tarayıcınız sesli giriş özelliğini desteklemiyor');
      return;
    }

    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = 'tr-TR';
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;

    recognitionRef.current.onresult = (event: SpeechRecognitionEvent) => {
      const transcript = event.results[0][0].transcript;
      setTranscript(transcript);
      setIsRecording(false);
    };

    recognitionRef.current.onerror = (event: SpeechRecognitionErrorEvent) => {
      setError(event.error);
      setIsRecording(false);
    };

    recognitionRef.current.onend = () => {
      setIsRecording(false);
    };

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [isSupported]);

  const startRecording = () => {
    if (!isSupported) {
      setError('Tarayıcınız sesli giriş özelliğini desteklemiyor');
      return;
    }

    setError(null);
    setTranscript('');
    setIsRecording(true);

    try {
      recognitionRef.current?.start();
    } catch (err) {
      setError('Ses kaydı başlatılamadı');
      setIsRecording(false);
    }
  };

  const stopRecording = () => {
    recognitionRef.current?.stop();
    setIsRecording(false);
  };

  return {
    isRecording,
    transcript,
    error,
    isSupported,
    startRecording,
    stopRecording,
  };
}
