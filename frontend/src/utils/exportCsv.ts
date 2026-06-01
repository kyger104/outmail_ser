type CsvValue = string | number | boolean | null | undefined
type CsvRow = Record<string, CsvValue>

function escapeCsvValue(value: CsvValue): string {
  const text = value == null ? '' : String(value)
  if (/[",\r\n]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`
  }
  return text
}

export function rowsToCsv(rows: CsvRow[], headers?: string[]): string {
  if (!rows.length) {
    return ''
  }

  const columns = headers ?? Object.keys(rows[0] ?? {})
  const lines = [
    columns.map(escapeCsvValue).join(','),
    ...rows.map((row) => columns.map((column) => escapeCsvValue(row[column])).join(','))
  ]

  return lines.join('\r\n')
}

export function downloadCsv(filename: string, rows: CsvRow[], headers?: string[]) {
  const csv = rowsToCsv(rows, headers)
  const blob = new Blob(['\uFEFF', csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  anchor.click()
  URL.revokeObjectURL(url)
}
