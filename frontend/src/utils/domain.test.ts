import { describe, expect, it } from 'vitest'
import { extractCode } from './extractCode'
import { parseMailboxImport } from './importParser'
import { rowsToCsv } from './exportCsv'
import { formatRelativeDate } from './formatDate'
import { coerceThemeMode, getStoredThemeMode, themeStorageKey } from './themePreference'
import { buildBasicAuthHeader, getAdminCredentials, saveAdminCredentials } from './adminAuth'

function createMemoryStorage(): Storage {
  const values = new Map<string, string>()
  return {
    get length() {
      return values.size
    },
    clear: () => values.clear(),
    getItem: (key: string) => values.get(key) ?? null,
    key: (index: number) => Array.from(values.keys())[index] ?? null,
    removeItem: (key: string) => values.delete(key),
    setItem: (key: string, value: string) => {
      values.set(key, value)
    }
  }
}

describe('extractCode', () => {
  it('extracts verification codes from mixed mail content', () => {
    expect(extractCode('Your Microsoft security code is 482913')).toEqual('482913')
    expect(extractCode('验证码：839201，请在 5 分钟内使用')).toEqual('839201')
    expect(extractCode('No code in this message')).toEqual('')
  })
})

describe('parseMailboxImport', () => {
  it('parses multiple supported separators and reports invalid lines', () => {
    const result = parseMailboxImport('a@example.com:tok1\nbad line\nb@example.com----tok2\nc@example.com|tok3')

    expect(result.valid).toEqual([
      { line: 1, email: 'a@example.com', imap_token: 'tok1' },
      { line: 3, email: 'b@example.com', imap_token: 'tok2' },
      { line: 4, email: 'c@example.com', imap_token: 'tok3' }
    ])
    expect(result.invalid).toEqual([
      { line: 2, raw: 'bad line', reason: '无法识别邮箱和令牌分隔符' }
    ])
  })
})

describe('rowsToCsv', () => {
  it('escapes commas, quotes and newlines', () => {
    const csv = rowsToCsv([
      { email: 'a@example.com', note: 'hello, "world"', link: 'https://example.test/a\nb' }
    ])

    expect(csv).toBe('email,note,link\r\n' +
      'a@example.com,"hello, ""world""","https://example.test/a\nb"')
  })
})

describe('formatRelativeDate', () => {
  it('uses Chinese relative labels for today and yesterday', () => {
    const now = new Date('2026-05-31T12:00:00+08:00')

    expect(formatRelativeDate('2026-05-31T08:05:00+08:00', now)).toBe('08:05')
    expect(formatRelativeDate('2026-05-30T21:20:00+08:00', now)).toBe('昨天 21:20')
    expect(formatRelativeDate('2026-05-20T09:30:00+08:00', now)).toBe('2026/05/20')
  })
})

describe('themePreference', () => {
  it('normalizes persisted theme modes and ignores invalid values', () => {
    expect(coerceThemeMode('dark')).toBe('dark')
    expect(coerceThemeMode('light')).toBe('light')
    expect(coerceThemeMode('auto')).toBe('auto')
    expect(coerceThemeMode('blue')).toBe('auto')
  })

  it('reads the saved theme mode from storage', () => {
    const storage = createMemoryStorage()

    storage.setItem(themeStorageKey, 'dark')
    expect(getStoredThemeMode(storage)).toBe('dark')

    storage.setItem(themeStorageKey, 'unknown')
    expect(getStoredThemeMode(storage)).toBe('auto')
  })
})

describe('adminAuth', () => {
  it('persists admin credentials in the provided storage and builds a Basic header', () => {
    const storage = createMemoryStorage()

    saveAdminCredentials({ username: 'admin', password: 'secret' }, storage)

    expect(getAdminCredentials(storage)).toEqual({ username: 'admin', password: 'secret' })
    expect(buildBasicAuthHeader({ username: 'admin', password: 'secret' })).toBe('Basic YWRtaW46c2VjcmV0')
  })
})
