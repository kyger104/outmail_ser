<template>
  <div class="inbox-container">
    <div class="toolbar">
      <n-space align="center" wrap>
        <n-select
          v-model:value="selectedMailboxId"
          :options="mailboxOptions"
          placeholder="选择邮箱"
          style="min-width: 320px"
          :loading="loadingMailboxes"
          clearable
          @update:value="onMailboxChange"
        />
        <n-button
          quaternary
          circle
          @click="copyCurrentMailbox"
          :disabled="!selectedMailboxId"
          title="复制邮箱地址"
        >
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
          </template>
        </n-button>
        <n-button @click="handleRefresh" :loading="refreshing" title="手动刷新">
          <template #icon>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ spinning: refreshing }">
              <polyline points="23 4 23 10 17 10"/>
              <polyline points="1 20 1 14 7 14"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
          </template>
          刷新
        </n-button>
        <n-tag type="success" v-if="currentMailboxLabel">
          {{ currentMailboxLabel }}
        </n-tag>
        <n-tag type="info" v-if="totalEmails > 0">
          共 {{ totalEmails }} 封
        </n-tag>
      </n-space>
    </div>

    <div class="main-content">
      <div class="email-list-panel">
        <div class="email-list-header">
          <span class="panel-title">邮件列表</span>
          <n-tag size="small" :bordered="false" type="info">
            {{ unreadCount }} 封未读
          </n-tag>
        </div>

        <n-list v-if="emails.length > 0" hoverable class="email-list">
          <n-list-item
            v-for="email in emails"
            :key="email.id"
            @click="selectEmail(email.id)"
            :class="{ active: selectedEmailId === email.id }"
          >
            <div class="email-item" :class="{ unread: !email.is_read }">
              <div class="email-sender">{{ email.sender || '(未知发件人)' }}</div>
              <div class="email-subject">{{ email.subject || '(无主题)' }}</div>
              <div class="email-meta">
                <span class="email-date">{{ formatDate(email.date || email.received_at) }}</span>
                <span v-if="email.has_attachments" class="attach-badge">📎</span>
              </div>
            </div>
          </n-list-item>
        </n-list>

        <n-empty v-else-if="!loadingEmails && selectedMailboxId" description="暂无邮件" class="empty-state" />
        <n-empty v-else-if="!selectedMailboxId" description="请先选择一个邮箱" class="empty-state" />

        <div class="pagination-bar" v-if="emails.length > 0">
          <n-space justify="center" align="center">
            <n-button size="small" @click="prevPage" :disabled="page <= 1">上一页</n-button>
            <n-text depth="3">第 {{ page }} 页</n-text>
            <n-button size="small" @click="nextPage" :disabled="emails.length < pageSize">下一页</n-button>
          </n-space>
        </div>
      </div>

      <div class="email-detail-panel">
        <template v-if="selectedEmail">
          <div class="detail-header">
            <h2 class="detail-subject">{{ selectedEmail.subject || '(无主题)' }}</h2>
            <n-space vertical size="small" class="detail-meta">
              <div class="meta-row">
                <span class="meta-label">发件人：</span>
                <span>{{ selectedEmail.sender_name ? `${selectedEmail.sender_name} <${selectedEmail.sender}>` : selectedEmail.sender }}</span>
              </div>
              <div class="meta-row" v-if="selectedEmail.recipient">
                <span class="meta-label">收件人：</span>
                <span>{{ selectedEmail.recipient }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">时间：</span>
                <span>{{ formatDateTime(selectedEmail.date || selectedEmail.received_at) }}</span>
              </div>
              <div class="meta-row" v-if="selectedEmail.has_attachments && selectedEmail.attachments?.length">
                <span class="meta-label">附件：</span>
                <n-space size="small">
                  <n-tag v-for="att in selectedEmail.attachments" :key="att.id" size="small">
                    {{ att.filename }}
                  </n-tag>
                </n-space>
              </div>
            </n-space>
          </div>

          <div class="detail-body">
            <div v-if="sanitizedHtml" class="html-body" v-html="sanitizedHtml"></div>
            <pre v-else-if="selectedEmail.body_text" class="text-body">{{ selectedEmail.body_text }}</pre>
            <n-empty v-else description="无邮件内容" />
          </div>
        </template>

        <template v-else>
          <div class="no-selection">
            <n-empty description="请从左侧选择一封邮件查看" />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {
  NButton, NSpace, NTag, NSelect, NList, NListItem,
  NEmpty, NText, useMessage
} from 'naive-ui'
import { format } from 'date-fns'
import DOMPurify from 'dompurify'
import api from '../utils/api'

interface Mailbox {
  id: number
  email: string
  status: string
  last_sync: string | null
}

interface EmailSummary {
  id: number
  subject: string
  sender: string
  date: string
  received_at: string
  is_read: boolean
  has_attachments: boolean
}

interface Attachment {
  id: number
  filename: string
  content_type: string
  size: number
}

interface EmailDetail {
  id: number
  subject: string
  sender: string
  sender_name?: string
  recipient: string
  date: string
  received_at: string
  body_text: string
  body_html: string
  is_read: boolean
  has_attachments: boolean
  attachments?: Attachment[]
}

interface MailboxOption {
  label: string
  value: number
}

const message = useMessage()

const selectedMailboxId = ref<number | null>(null)
const mailboxOptions = ref<MailboxOption[]>([])
const loadingMailboxes = ref(false)
const currentMailboxLabel = ref('')

const emails = ref<EmailSummary[]>([])
const selectedEmailId = ref<number | null>(null)
const selectedEmail = ref<EmailDetail | null>(null)
const loadingEmails = ref(false)
const refreshing = ref(false)
const page = ref(1)
const pageSize = 20
const totalEmails = ref(0)
const unreadCount = computed(() => emails.value.filter(e => !e.is_read).length)

const sanitizedHtml = computed(() => {
  if (!selectedEmail.value?.body_html) return ''
  return DOMPurify.sanitize(selectedEmail.value.body_html, {
    ALLOWED_TAGS: ['a', 'b', 'br', 'div', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'hr', 'i', 'img', 'li', 'ol', 'p', 'pre', 'span', 'strong', 'table',
      'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul', 'blockquote',
      'code', 'del', 'ins', 'mark', 'q', 's', 'small', 'sub', 'sup'],
    ALLOWED_ATTR: ['href', 'target', 'src', 'alt', 'width', 'height',
      'style', 'class', 'id', 'title', 'rel', 'border', 'cellpadding',
      'cellspacing', 'colspan', 'rowspan', 'align', 'valign']
  })
})

async function loadMailboxes() {
  loadingMailboxes.value = true
  try {
    const data = await api.get('/admin/mailboxes', {
      params: { page: 1, limit: 1000 }
    }) as Mailbox[]
    mailboxOptions.value = data
      .filter(m => m.status === 'active')
      .map(m => ({
        label: m.email,
        value: m.id
      }))
    if (mailboxOptions.value.length > 0 && !selectedMailboxId.value) {
      selectedMailboxId.value = mailboxOptions.value[0].value
      currentMailboxLabel.value = mailboxOptions.value[0].label
      loadEmails()
    }
  } catch {
    message.error('加载邮箱列表失败')
  } finally {
    loadingMailboxes.value = false
  }
}

function onMailboxChange(value: number | null) {
  if (!value) {
    selectedMailboxId.value = null
    currentMailboxLabel.value = ''
    emails.value = []
    selectedEmail.value = null
    selectedEmailId.value = null
    return
  }
  const opt = mailboxOptions.value.find(o => o.value === value)
  currentMailboxLabel.value = opt?.label || ''
  page.value = 1
  selectedEmail.value = null
  selectedEmailId.value = null
  loadEmails()
}

async function loadEmails() {
  if (!selectedMailboxId.value) return
  loadingEmails.value = true
  try {
    const data = await api.get('/emails/', {
      params: { mailbox_id: selectedMailboxId.value, page: page.value, limit: pageSize }
    }) as EmailSummary[]
    emails.value = data
  } catch {
    message.error('加载邮件列表失败')
  } finally {
    loadingEmails.value = false
  }
}

async function selectEmail(emailId: number) {
  if (selectedEmailId.value === emailId) return
  selectedEmailId.value = emailId
  selectedEmail.value = null

  try {
    const data = await api.get(`/emails/${emailId}`) as EmailDetail
    selectedEmail.value = data

    if (!data.is_read) {
      await api.put(`/emails/${emailId}/read`)
      const email = emails.value.find(e => e.id === emailId)
      if (email) email.is_read = true
    }
  } catch {
    message.error('加载邮件详情失败')
    selectedEmailId.value = null
  }
}

async function handleRefresh() {
  if (!selectedMailboxId.value) {
    message.warning('请先选择邮箱')
    return
  }
  refreshing.value = true
  try {
    await api.post('/emails/refresh', null, {
      params: { mailbox_id: selectedMailboxId.value }
    })
    message.success('刷新完成')
    await loadEmails()
  } catch {
    message.error('刷新失败')
  } finally {
    refreshing.value = false
  }
}

function copyCurrentMailbox() {
  const opt = mailboxOptions.value.find(o => o.value === selectedMailboxId.value)
  if (opt) {
    navigator.clipboard.writeText(opt.label)
    message.success('已复制: ' + opt.label)
  }
}

function formatDate(date: string) {
  if (!date) return '-'
  return format(new Date(date), 'MM/dd HH:mm')
}

function formatDateTime(date: string) {
  if (!date) return '-'
  return format(new Date(date), 'yyyy/MM/dd HH:mm:ss')
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    loadEmails()
  }
}

function nextPage() {
  page.value++
  loadEmails()
}

onMounted(loadMailboxes)
</script>

<style scoped>
.inbox-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  padding: 12px 16px;
  border-bottom: 1px solid #e0e0e0;
  background: #fff;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.email-list-panel {
  width: 380px;
  min-width: 300px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.email-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
}

.panel-title {
  font-weight: 600;
  font-size: 14px;
}

.email-list {
  flex: 1;
  overflow-y: auto;
}

.email-item {
  padding: 8px 0;
  cursor: pointer;
}

.email-item.unread .email-sender {
  font-weight: 700;
  color: #1a1a1a;
}

.email-item.unread .email-subject {
  font-weight: 600;
}

.email-sender {
  font-size: 13px;
  color: #333;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.email-subject {
  font-size: 12px;
  color: #666;
  margin-bottom: 2px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.email-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.email-date {
  font-size: 11px;
  color: #999;
}

.attach-badge {
  font-size: 12px;
}

.active {
  background: #e8f0fe;
}

.pagination-bar {
  padding: 12px;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.email-detail-panel {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  padding: 24px;
}

.detail-subject {
  margin: 0 0 16px 0;
  font-size: 20px;
}

.detail-meta {
  margin-bottom: 24px;
}

.meta-row {
  font-size: 13px;
  color: #555;
  line-height: 1.8;
}

.meta-label {
  color: #888;
  display: inline-block;
  min-width: 60px;
}

.detail-body {
  border-top: 1px solid #e0e0e0;
  padding-top: 24px;
}

.html-body {
  line-height: 1.6;
  overflow-x: auto;
}

.text-body {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  line-height: 1.6;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinning {
  animation: spin 1s linear infinite;
}
</style>
