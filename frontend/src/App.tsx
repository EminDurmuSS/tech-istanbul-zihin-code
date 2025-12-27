import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'sonner';
import { Navbar } from './components/layout/Navbar';
import { ChatPage } from './pages/ChatPage';
import { AdminPage } from './pages/AdminPage';
import { DashboardPage } from './pages/DashboardPage';
import { FaultTrackingPage } from './pages/FaultTrackingPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { AgentConfigPage } from './pages/AgentConfigPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <Navbar />
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/admin" element={<AdminPage />}>
              <Route index element={<DashboardPage />} />
              <Route path="faults" element={<FaultTrackingPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
              <Route path="agents" element={<AgentConfigPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <Toaster position="top-right" />
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
