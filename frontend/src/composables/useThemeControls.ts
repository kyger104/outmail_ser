import { computed, inject, type ComputedRef, type Ref } from 'vue'
import type { ResolvedThemeMode, ThemeMode } from '../utils/themePreference'

type ThemeControls = {
  themeMode: Ref<ThemeMode>
  resolvedTheme: ComputedRef<ResolvedThemeMode>
  setThemeMode: (mode: ThemeMode) => void
}

export function useThemeControls() {
  const controls = inject<ThemeControls>('themeControls')
  if (controls) return controls

  const themeMode = computed(() => 'auto' as ThemeMode)
  const resolvedTheme = computed(() => 'light' as ResolvedThemeMode)
  return {
    themeMode,
    resolvedTheme,
    setThemeMode: () => {}
  }
}
