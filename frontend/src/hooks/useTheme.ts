import { useUserStore } from '@/store';

export function useTheme() {
  const { theme, setTheme, toggleTheme } = useUserStore();

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme === 'dark',
  };
}
