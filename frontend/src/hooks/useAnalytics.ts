import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '@/api/endpoints/admin';

export function useAnalytics() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['analytics'],
    queryFn: adminAPI.getAnalytics,
    refetchInterval: 60000, // Refetch every minute
  });

  return {
    data,
    isLoading,
    error,
    refresh: refetch,
  };
}
