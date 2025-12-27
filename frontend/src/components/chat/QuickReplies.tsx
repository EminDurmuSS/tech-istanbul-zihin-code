import { Button } from '@/components/ui/button';

interface QuickRepliesProps {
  replies: string[];
  onSelect: (reply: string) => void;
}

export function QuickReplies({ replies, onSelect }: QuickRepliesProps) {
  if (!replies || replies.length === 0) return null;

  return (
    <div className="flex gap-2 flex-wrap mt-2">
      {replies.map((reply, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          onClick={() => onSelect(reply)}
          className="animate-fadeIn"
        >
          {reply}
        </Button>
      ))}
    </div>
  );
}
