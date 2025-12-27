import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, AlertCircle, BarChart3, Settings } from 'lucide-react';
import { cn } from '@/lib/cn';
import { Button } from '@/components/ui/button';

const menuItems = [
  { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/admin/faults', label: 'Fault Tracking', icon: AlertCircle },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart3 },
  { path: '/admin/agents', label: 'Agent Config', icon: Settings },
];

export function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r bg-background h-[calc(100vh-4rem)]">
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link key={item.path} to={item.path}>
              <Button
                variant={isActive ? 'secondary' : 'ghost'}
                className={cn('w-full justify-start gap-3', isActive && 'bg-secondary')}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Button>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
