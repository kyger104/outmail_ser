export interface Mailbox {
  id: number
  email: string
  status: string
  last_sync: string | null
  created_at: string
}

export interface AdminStats {
  total_mailboxes?: number
  active_mailboxes?: number
  error_mailboxes?: number
  total_links?: number
  total_emails?: number
  unread_emails?: number
  recent_mailboxes?: Mailbox[]
  recent_errors?: Mailbox[]
}

export interface BatchDeleteResponse {
  deleted?: number | number[]
  errors?: unknown[]
}

export interface MailboxSyncResponse {
  message?: string
  status?: string
}

export interface MailboxLink {
  id?: number
  mailbox_id?: number
  email: string
  link: string
  status?: string
  jwt_token?: string
}

export interface EmailSummary {
  id: number
  subject: string
  sender: string
  date: string | null
  is_read: boolean
  has_attachments: boolean
  body_preview: string
}

export interface EmailDetail extends EmailSummary {
  recipient: string
  body_text: string
  body_html: string
}

export interface ApiKeyItem {
  id: number
  api_key: string
  name: string
  description: string | null
  rate_limit: number
  is_active: boolean
  created_at: string
  last_used: string | null
  usage_count: number
}
