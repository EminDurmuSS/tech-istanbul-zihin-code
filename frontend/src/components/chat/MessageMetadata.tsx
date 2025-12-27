import { Badge } from '@/components/ui/badge';
import { INTENT_LABELS } from '@/utils/constants';

interface MessageMetadataProps {
  intent?: string;
  confidence?: number;
  processingTime?: number;
}

export function MessageMetadata({ intent, confidence, processingTime }: MessageMetadataProps) {
  if (!intent) return null;

  const confidenceColor = confidence && confidence > 0.8 ? 'default' : confidence && confidence > 0.5 ? 'secondary' : 'destructive';

  return (
    <div className="flex gap-2 items-center mt-2 text-xs text-muted-foreground">
      <Badge variant="outline">{INTENT_LABELS[intent] || intent}</Badge>
      {confidence !== undefined && (
        <Badge variant={confidenceColor}>
          {(confidence * 100).toFixed(0)}% güven
        </Badge>
      )}
      {processingTime !== undefined && (
        <span>{processingTime}ms</span>
      )}
    </div>
  );
}
