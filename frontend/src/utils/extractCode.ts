const codePatterns = [
  /(?:验证码|校验码|确认码|动态码|安全代码|security code|verification code|code)\D{0,24}(\d{4,8})/i,
  /\b(\d{6})\b/,
  /\b(\d{4,8})\b/
]

export function extractCode(content: string | null | undefined): string {
  if (!content) {
    return ''
  }

  for (const pattern of codePatterns) {
    const match = content.match(pattern)
    if (match?.[1]) {
      return match[1]
    }
  }

  return ''
}
