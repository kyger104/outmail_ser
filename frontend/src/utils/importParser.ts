export interface ParsedMailboxImport {
  line: number
  email: string
  imap_token: string
}

export interface InvalidMailboxImport {
  line: number
  raw: string
  reason: string
}

export interface MailboxImportParseResult {
  valid: ParsedMailboxImport[]
  invalid: InvalidMailboxImport[]
}

const separators = ['----', '|', ':']
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function splitMailboxLine(raw: string, separator: string) {
  const parts = raw.split(separator).map((part) => part.trim())

  if (separator === '----' && parts.length >= 4) {
    return {
      email: parts[0] ?? '',
      imapToken: parts.slice(3).join(separator).trim()
    }
  }

  const [emailPart, ...tokenParts] = parts
  return {
    email: emailPart ?? '',
    imapToken: tokenParts.join(separator).trim()
  }
}

export function parseMailboxImport(input: string): MailboxImportParseResult {
  const valid: ParsedMailboxImport[] = []
  const invalid: InvalidMailboxImport[] = []

  input.split(/\r?\n/).forEach((line, index) => {
    const raw = line.trim()
    const lineNumber = index + 1

    if (!raw) {
      return
    }

    const separator = separators.find((candidate) => raw.includes(candidate))
    if (!separator) {
      invalid.push({ line: lineNumber, raw, reason: '无法识别邮箱和令牌分隔符' })
      return
    }

    const { email, imapToken } = splitMailboxLine(raw, separator)

    if (!emailPattern.test(email)) {
      invalid.push({ line: lineNumber, raw, reason: '邮箱格式不正确' })
      return
    }

    if (!imapToken) {
      invalid.push({ line: lineNumber, raw, reason: '缺少 IMAP 令牌' })
      return
    }

    valid.push({ line: lineNumber, email, imap_token: imapToken })
  })

  return { valid, invalid }
}
