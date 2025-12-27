import { create } from 'zustand';

interface FaultFilters {
  status?: string;
  priority?: string;
  line?: string;
  station?: string;
  dateFrom?: string;
  dateTo?: string;
}

interface AdminStore {
  faultFilters: FaultFilters;
  selectedFaultId: string | null;

  // Actions
  setFaultFilters: (filters: FaultFilters) => void;
  clearFaultFilters: () => void;
  setSelectedFault: (id: string | null) => void;
}

export const useAdminStore = create<AdminStore>((set) => ({
  faultFilters: {},
  selectedFaultId: null,

  setFaultFilters: (filters: FaultFilters) => {
    set({ faultFilters: filters });
  },

  clearFaultFilters: () => {
    set({ faultFilters: {} });
  },

  setSelectedFault: (id: string | null) => {
    set({ selectedFaultId: id });
  },
}));
