import { Copy, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

interface ReportIdDisplayProps {
  reportId: string;
}

export function ReportIdDisplay({ reportId }: ReportIdDisplayProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(reportId);
    setCopied(true);
    toast.success('Rapor numarası kopyalandı');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="mt-3 p-3 bg-primary/10 border border-primary/20 rounded-lg">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-muted-foreground">Arıza Rapor Numarası</p>
          <p className="text-sm font-mono font-bold text-primary">{reportId}</p>
        </div>
        <Button variant="ghost" size="icon" onClick={handleCopy}>
          {copied ? <CheckCircle className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
