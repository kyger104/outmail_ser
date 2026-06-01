export type AdminCredentials = {
  username: string
  password: string
}

export const adminAuthStorageKey = 'imap_admin_auth'

function encodeCredentials(credentials: AdminCredentials): string {
  return btoa(unescape(encodeURIComponent(`${credentials.username}:${credentials.password}`)))
}

export function buildBasicAuthHeader(credentials: AdminCredentials): string {
  return `Basic ${encodeCredentials(credentials)}`
}

export function saveAdminCredentials(credentials: AdminCredentials, storage: Storage = sessionStorage) {
  storage.setItem(adminAuthStorageKey, JSON.stringify(credentials))
}

export function getAdminCredentials(storage: Storage = sessionStorage): AdminCredentials | null {
  try {
    const raw = storage.getItem(adminAuthStorageKey)
    if (!raw) return null
    const parsed = JSON.parse(raw) as Partial<AdminCredentials>
    if (!parsed.username || !parsed.password) return null
    return { username: parsed.username, password: parsed.password }
  } catch {
    return null
  }
}

export function clearAdminCredentials(storage: Storage = sessionStorage) {
  storage.removeItem(adminAuthStorageKey)
}

export function hasAdminCredentials(storage: Storage = sessionStorage): boolean {
  return Boolean(getAdminCredentials(storage))
}
