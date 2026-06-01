const pad = (value: number) => String(value).padStart(2, '0')

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return '-'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatRelativeDate(value: string | null | undefined, now = new Date()): string {
  if (!value) {
    return '-'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  const dateKey = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
  const nowKey = `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`
  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const yesterdayKey = `${yesterday.getFullYear()}-${yesterday.getMonth()}-${yesterday.getDate()}`
  const time = `${pad(date.getHours())}:${pad(date.getMinutes())}`

  if (dateKey === nowKey) {
    return time
  }

  if (dateKey === yesterdayKey) {
    return `昨天 ${time}`
  }

  return `${date.getFullYear()}/${pad(date.getMonth() + 1)}/${pad(date.getDate())}`
}
