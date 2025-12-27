import { Link } from 'react-router-dom';
import { MessageSquare, LayoutDashboard } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';
import { Button } from '@/components/ui/button';
import { useAgent } from '@/hooks/useAgent';

export function Navbar() {
  const { currentAgent } = useAgent();

  return (
    <nav className="border-b bg-background">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link to="/" className="flex items-center gap-2 font-semibold text-lg">
            <span className="text-2xl">{currentAgent.icon}</span>
            <span>Metro İstanbul Agent</span>
          </Link>

          <div className="flex gap-2">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <MessageSquare className="h-4 w-4" />
                Chat
              </Button>
            </Link>
            <Link to="/admin">
              <Button variant="ghost" size="sm" className="gap-2">
                <LayoutDashboard className="h-4 w-4" />
                Admin
              </Button>
            </Link>
          </div>
        </div>

        <ThemeToggle />
      </div>
    </nav>
  );
}
