import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MessageSquare, AlertCircle, Clock, ThumbsUp } from 'lucide-react';
import { useAnalytics } from '@/hooks/useAnalytics';
import { Skeleton } from '@/components/ui/skeleton';

export function DashboardPage() {
  const { data, isLoading } = useAnalytics();

  if (isLoading) {
    return (
      <div className="p-6 space-y-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Conversations',
      value: data?.totalConversations || 0,
      icon: MessageSquare,
      trend: '+12%',
    },
    {
      title: 'Active Faults',
      value: data?.activeFaults || 0,
      icon: AlertCircle,
      trend: '-5%',
      variant: 'warning' as const,
    },
    {
      title: 'Avg Response Time',
      value: `${data?.avgResponseTime || 0}ms`,
      icon: Clock,
    },
    {
      title: 'Satisfaction Rate',
      value: `${data?.satisfactionRate || 0}%`,
      icon: ThumbsUp,
      trend: '+8%',
      variant: 'success' as const,
    },
  ];

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                {stat.trend && (
                  <p className="text-xs text-muted-foreground mt-1">{stat.trend} from last month</p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Intent Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data?.intentDistribution?.map((item: any) => (
                <div key={item.name} className="flex justify-between items-center">
                  <span className="text-sm">{item.name}</span>
                  <span className="text-sm font-semibold">{item.value}%</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response Time Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data?.responseTimeTrend?.map((item: any) => (
                <div key={item.time} className="flex justify-between items-center">
                  <span className="text-sm">{item.time}</span>
                  <span className="text-sm font-semibold">{item.value}ms</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
