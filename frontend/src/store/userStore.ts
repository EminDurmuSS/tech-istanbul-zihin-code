import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { STORAGE_KEYS } from '@/utils/constants';

interface UserStore {
  theme: 'light' | 'dark';
  language: 'tr' | 'en';
  userId: string | null;

  // Actions
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  setLanguage: (language: 'tr' | 'en') => void;
  setUserId: (userId: string) => void;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      theme: 'light',
      language: 'tr',
      userId: null,

      setTheme: (theme: 'light' | 'dark') => {
        set({ theme });
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },

      toggleTheme: () => {
        const { theme, setTheme } = get();
        setTheme(theme === 'light' ? 'dark' : 'light');
      },

      setLanguage: (language: 'tr' | 'en') => {
        set({ language });
      },

      setUserId: (userId: string) => {
        set({ userId });
      },
    }),
    {
      name: STORAGE_KEYS.THEME,
      onRehydrateStorage: () => (state) => {
        if (state) {
          document.documentElement.classList.toggle('dark', state.theme === 'dark');
        }
      },
    }
  )
);
