export type ThemeMode = 'light' | 'dark' | 'auto'
export type ResolvedThemeMode = 'light' | 'dark'

export const themeStorageKey = 'imap_theme_mode'

export function coerceThemeMode(value: unknown): ThemeMode {
  return value === 'light' || value === 'dark' || value === 'auto' ? value : 'auto'
}

export function getStoredThemeMode(storage: Storage = localStorage): ThemeMode {
  try {
    return coerceThemeMode(storage.getItem(themeStorageKey))
  } catch {
    return 'auto'
  }
}

export function storeThemeMode(mode: ThemeMode, storage: Storage = localStorage) {
  try {
    storage.setItem(themeStorageKey, mode)
  } catch {
    // Ignore unavailable storage so the UI can still switch for this session.
  }
}

export function resolveThemeMode(mode: ThemeMode, prefersDark: boolean): ResolvedThemeMode {
  if (mode === 'auto') {
    return prefersDark ? 'dark' : 'light'
  }
  return mode
}
