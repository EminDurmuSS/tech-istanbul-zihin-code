import { useQuery } from '@tanstack/react-query';
import { metroAPI } from '@/api/endpoints/metro';
import { useAdminStore } from '@/store';

export function useFaultTracking() {
  const { faultFilters, setFaultFilters, clearFaultFilters } = useAdminStore();

  const {
    data: faults,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['faults', faultFilters],
    queryFn: async () => {
      const response = await metroAPI.getActiveFaults();
      return response.faults;
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  return {
    faults: faults || [],
    isLoading,
    error,
    filters: faultFilters,
    setFilters: setFaultFilters,
    clearFilters: clearFaultFilters,
    refresh: refetch,
  };
}
