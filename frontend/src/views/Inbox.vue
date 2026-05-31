<template>
  <div class="inbox-container" v-if="verified">
    <n-card :title="`📧 ${mailboxInfo.email} 的邮箱`">
      <!-- Email list -->
      <n-list bordered>
        <n-list-item
          v-for="email in emails"
          :key="email.id"
          @click="selectEmail(email.id)"
          style="cursor: pointer"
          :class="{ active: selectedEmailId === email.id, unread: !email.is_read }"
        >
          <n-thing>
            <template #header>
              <span :style="{ fontWeight: email.is_read ? 'normal' : 'bold' }">
                {{ email.subject || '(无主题)' }}
              </span>
            </template>
            <template #description>
              {{ email.sender || '(未知)' }} | {{ formatDate(email.date) }}
            </template>
          </n-thing>
        </n-list-item>
      </n-list>

      <!-- Pagination -->
      <n-space justify="center" style="margin-top: 16px">
        <n-button size="small" @click="prevPage" :disabled="page <= 1">上一页</n-button>
        <n-text>第 {{ page }} / {{ totalPages }} 页</n-text>
        <n-button size="small" @click="nextPage" :disabled="page >= totalPages">下一页</n-button>
      </n-space>

      <!-- Email Detail -->
      <n-card v-if="selectedEmail" title="邮件详情" style="margin-top: 20px">
        <p><strong>主题：</strong>{{ selectedEmail.subject }}</p>
        <p><strong>发件人：</strong>{{ selectedEmail.sender }}</p>
        <p v-if="selectedEmail.recipient"><strong>收件人：</strong>{{ selectedEmail.recipient }}</p>
        <p><strong>时间：</strong>{{ formatDateTime(selectedEmail.date) }}</p>
        <n-divider />
        <div v-if="sanitizedHtml" class="html-body" v-html="sanitizedHtml"></div>
        <pre v-else-if="selectedEmail.body_text" class="text-body">{{ selectedEmail.body_text }}</pre>
        <n-empty v-else description="无邮件内容" />
      </n-card>
    </n-card>
  </div>

  <n-result v-else-if="!verified && checked" status="error" title="访问链接无效或已过期"
    description="请检查链接是否正确，或联系管理员获取新的访问链接" />

  <n-spin v-else :show="true" style="margin: 40px auto">
    <div style="height: 40px"></div>
  </n-spin>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import {
  NCard, NList, NListItem, NThing, NButton, NSpace,
  NText, NDivider, NEmpty, NResult, NSpin, useMessage
} from 'naive-ui'
import DOMPurify from 'dompurify'
import api from '../utils/api'

interface EmailSummary {
  id: number
  subject: string
  sender: string
  date: string | null
  is_read: boolean
  has_attachments: boolean
  body_preview: string
}

interface EmailDetail {
  id: number
  subject: string
  sender: string
  recipient: string
  date: string | null
  body_text: string
  body_html: string
  is_read: boolean
  has_attachments: boolean
}

const route = useRoute()
const message = useMessage()

const jwt = ref('')
const verified = ref(false)
const checked = ref(false)
const mailboxInfo = ref({ email: '', mailbox_id: 0, status: '' })
const emails = ref<EmailSummary[]>([])
const selectedEmailId = ref<number | null>(null)
const selectedEmail = ref<EmailDetail | null>(null)
const page = ref(1)
const pageSize = 20
const totalEmails = ref(0)
const totalPages = computed(() => Math.ceil(totalEmails.value / pageSize) || 1)

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

async function verifyJWT() {
  jwt.value = (route.query.jwt as string) || ''
  if (!jwt.value) {
    checked.value = true
    return
  }
  try {
    const data = await api.get('/inbox/verify', { params: { jwt: jwt.value } }) as any
    mailboxInfo.value = data
    verified.value = true
    loadEmails()
  } catch {
    verified.value = false
  } finally {
    checked.value = true
  }
}

async function loadEmails() {
  try {
    const data = await api.get('/inbox/emails', {
      params: { jwt: jwt.value, page: page.value, page_size: pageSize }
    }) as { items: EmailSummary[]; total: number }
    emails.value = data.items
    totalEmails.value = data.total
  } catch {
    message.error('加载邮件失败')
  }
}

async function selectEmail(emailId: number) {
  if (selectedEmailId.value === emailId) return
  selectedEmailId.value = emailId
  selectedEmail.value = null
  try {
    const data = await api.get(`/inbox/emails/${emailId}`, {
      params: { jwt: jwt.value }
    }) as EmailDetail
    selectedEmail.value = data
    if (!data.is_read) {
      const emailInList = emails.value.find(e => e.id === emailId)
      if (emailInList) emailInList.is_read = true
    }
  } catch {
    message.error('加载邮件详情失败')
  }
}

function prevPage() {
  if (page.value > 1) { page.value--; loadEmails() }
}

function nextPage() {
  if (page.value < totalPages.value) { page.value++; loadEmails() }
}

function formatDate(date: string | null) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

function formatDateTime(date: string | null) {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(verifyJWT)
</script>

<style scoped>
.inbox-container {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  min-height: 100vh;
}
.unread {
  background: #f6f9fc;
}
.active {
  background: #e8f0fe;
}
.html-body {
  line-height: 1.6;
  word-wrap: break-word;
  overflow-x: auto;
}
.text-body {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
}
</style>
