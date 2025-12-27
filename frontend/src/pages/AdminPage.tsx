import { Outlet } from 'react-router-dom';
import { Sidebar } from '@/components/layout/Sidebar';

export function AdminPage() {
  return (
    <div className="flex">
      <Sidebar />
      <main className="flex-1 overflow-y-auto h-[calc(100vh-4rem)]">
        <Outlet />
      </main>
    </div>
  );
}
