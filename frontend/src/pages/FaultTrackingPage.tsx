import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useFaultTracking } from '@/hooks/useFaultTracking';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { RefreshCw } from 'lucide-react';

export function FaultTrackingPage() {
  const { faults, isLoading, refresh } = useFaultTracking();

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Fault Tracking</h1>
        <Button onClick={() => refresh()} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Active Faults ({faults.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {faults.length === 0 ? (
              <p className="text-muted-foreground text-center py-8">No active faults</p>
            ) : (
              faults.map((fault: any) => (
                <div
                  key={fault.id}
                  className="flex justify-between items-center p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{fault.station}</span>
                      <Badge variant="outline">{fault.line}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{fault.equipment}</p>
                    {fault.report_id && (
                      <p className="text-xs font-mono text-muted-foreground">ID: {fault.report_id}</p>
                    )}
                  </div>
                  <div className="text-right space-y-1">
                    <Badge variant={fault.priority === 'HIGH' ? 'destructive' : 'secondary'}>
                      {fault.priority}
                    </Badge>
                    <p className="text-xs text-muted-foreground">{fault.status}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
