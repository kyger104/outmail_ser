<template>
  <main class="public-inbox">
    <section v-if="verified" class="mail-shell" aria-label="公开收件箱">
      <header class="mail-header">
        <div class="mailbox-meta">
          <div class="mailbox-label">Public Inbox</div>
          <h1>{{ mailboxInfo.email }}</h1>
          <div class="mailbox-subline">
            <span>{{ totalEmails }} 封邮件</span>
            <span>状态：{{ mailboxInfo.status || 'unknown' }}</span>
            <span>当前页 {{ emails.length }} 封</span>
          </div>
        </div>
        <div class="mail-actions">
          <n-input
            v-model:value="searchKeyword"
            clearable
            placeholder="搜索当前页主题、发件人、摘要"
            class="search-input"
          />
          <n-button :loading="loadingEmails" @click="refreshCurrentPage">刷新</n-button>
        </div>
      </header>

      <nav class="filter-bar" aria-label="邮件筛选">
        <button
          v-for="option in filterOptions"
          :key="option.value"
          type="button"
          class="filter-button"
          :class="{ active: activeFilter === option.value }"
          @click="activeFilter = option.value"
        >
          <span>{{ option.label }}</span>
          <strong>{{ filterCounts[option.value] }}</strong>
        </button>
      </nav>

      <div class="mail-layout">
        <aside class="message-list-pane" aria-label="邮件列表">
          <div class="pane-toolbar">
            <div>
              <strong>{{ filteredEmails.length }}</strong>
              <span> / 当前页 {{ emails.length }}</span>
            </div>
            <n-button size="tiny" text @click="clearFilters" :disabled="!hasActiveFilters">
              清除筛选
            </n-button>
          </div>

          <n-spin :show="loadingEmails">
            <div v-if="emailError" class="state-block error-state">
              <strong>邮件加载失败</strong>
              <span>{{ emailError }}</span>
              <n-button size="small" @click="loadEmails">重试</n-button>
            </div>

            <div v-else-if="!emails.length" class="state-block">
              <strong>暂无邮件</strong>
              <span>这个公开链接下还没有同步到邮件。</span>
            </div>

            <div v-else-if="!filteredEmails.length" class="state-block">
              <strong>没有匹配结果</strong>
              <span>当前页没有符合筛选或搜索条件的邮件。</span>
            </div>

            <ul v-else class="message-list">
              <li
                v-for="email in filteredEmails"
                :key="email.id"
                class="message-row"
                :class="{ selected: selectedEmailId === email.id, unread: !email.is_read }"
              >
                <button type="button" class="message-button" @click="selectEmail(email.id)">
                  <span class="row-topline">
                    <span class="sender">{{ email.sender || '(未知发件人)' }}</span>
                    <time>{{ formatRelativeDate(email.date) }}</time>
                  </span>
                  <span class="subject-line">{{ email.subject || '(无主题)' }}</span>
                  <span v-if="email.body_preview" class="preview-line">{{ email.body_preview }}</span>
                  <span class="row-badges">
                    <span v-if="!email.is_read" class="badge unread-badge">未读</span>
                    <span v-if="email.has_attachments" class="badge">附件</span>
                    <span v-if="summaryCode(email)" class="badge code-badge">
                      验证码 {{ summaryCode(email) }}
                    </span>
                  </span>
                </button>
                <n-button
                  v-if="summaryCode(email)"
                  size="tiny"
                  secondary
                  class="copy-code-button"
                  @click.stop="copyCode(summaryCode(email))"
                >
                  复制
                </n-button>
              </li>
            </ul>
          </n-spin>

          <footer class="pagination-bar">
            <n-button size="small" @click="prevPage" :disabled="page <= 1 || loadingEmails">
              上一页
            </n-button>
            <span>第 {{ page }} / {{ totalPages }} 页</span>
            <n-button size="small" @click="nextPage" :disabled="page >= totalPages || loadingEmails">
              下一页
            </n-button>
          </footer>
        </aside>

        <section class="message-detail-pane" aria-label="邮件详情">
          <div v-if="loadingDetail" class="detail-loading">
            <n-spin :show="true" />
            <span>正在加载邮件详情...</span>
          </div>

          <article v-else-if="selectedEmail" class="message-detail">
            <header class="detail-header">
              <div>
                <div class="detail-label">邮件详情</div>
                <h2>{{ selectedEmail.subject || '(无主题)' }}</h2>
              </div>
              <n-button
                v-if="detailCode"
                secondary
                type="primary"
                @click="copyCode(detailCode)"
              >
                复制验证码 {{ detailCode }}
              </n-button>
            </header>

            <dl class="detail-meta">
              <div>
                <dt>发件人</dt>
                <dd>{{ selectedEmail.sender || '-' }}</dd>
              </div>
              <div v-if="selectedEmail.recipient">
                <dt>收件人</dt>
                <dd>{{ selectedEmail.recipient }}</dd>
              </div>
              <div>
                <dt>时间</dt>
                <dd>{{ formatDateTime(selectedEmail.date) }}</dd>
              </div>
              <div>
                <dt>状态</dt>
                <dd>
                  {{ selectedEmail.is_read ? '已读' : '未读' }}
                  <span v-if="selectedEmail.has_attachments"> · 有附件</span>
                </dd>
              </div>
            </dl>

            <div v-if="detailCode" class="code-panel">
              <span>识别到验证码</span>
              <strong>{{ detailCode }}</strong>
              <n-button size="small" @click="copyCode(detailCode)">复制</n-button>
            </div>

            <div class="body-container" @click="handleBodyClick">
              <div v-if="sanitizedHtml" class="html-body" v-html="sanitizedHtml"></div>
              <pre v-else-if="selectedEmail.body_text" class="text-body">{{ selectedEmail.body_text }}</pre>
              <div v-else class="state-block">
                <strong>无邮件内容</strong>
                <span>这封邮件没有 HTML 或文本正文。</span>
              </div>
            </div>
          </article>

          <div v-else-if="detailError" class="state-block error-state detail-state">
            <strong>详情加载失败</strong>
            <span>{{ detailError }}</span>
            <n-button v-if="selectedEmailId" size="small" @click="selectEmail(selectedEmailId, true)">
              重试
            </n-button>
          </div>

          <div v-else class="state-block detail-state">
            <strong>选择一封邮件</strong>
            <span>在左侧列表中选择邮件后，这里会显示清洗后的正文和验证码。</span>
          </div>
        </section>
      </div>
    </section>

    <section v-else-if="checked" class="access-state">
      <n-result
        status="error"
        :title="accessErrorTitle"
        :description="accessErrorDescription"
      />
    </section>

    <section v-else class="access-state">
      <n-spin :show="true">
        <div class="verify-placeholder">正在验证公开访问链接...</div>
      </n-spin>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NInput, NResult, NSpin, useMessage } from 'naive-ui'
import DOMPurify from 'dompurify'
import type { EmailDetail, EmailSummary } from '../types'
import api from '../utils/api'
import { copyToClipboard } from '../utils/clipboard'
import { extractCode } from '../utils/extractCode'
import { formatDateTime, formatRelativeDate } from '../utils/formatDate'

type FilterValue = 'all' | 'unread' | 'read' | 'attachments' | 'code'

interface MailboxInfo {
  email: string
  mailbox_id: number
  status: string
}

interface EmailListResponse {
  items: EmailSummary[]
  total: number
  page: number
  page_size: number
}

const route = useRoute()
const message = useMessage()

const jwt = ref('')
const verified = ref(false)
const checked = ref(false)
const mailboxInfo = ref<MailboxInfo>({ email: '', mailbox_id: 0, status: '' })
const emails = ref<EmailSummary[]>([])
const selectedEmailId = ref<number | null>(null)
const selectedEmail = ref<EmailDetail | null>(null)
const page = ref(1)
const pageSize = 20
const totalEmails = ref(0)
const loadingEmails = ref(false)
const loadingDetail = ref(false)
const emailError = ref('')
const detailError = ref('')
const accessErrorTitle = ref('访问链接无效或已过期')
const accessErrorDescription = ref('请检查链接是否正确，或联系管理员获取新的访问链接。')
const activeFilter = ref<FilterValue>('all')
const searchKeyword = ref('')

const filterOptions: Array<{ label: string; value: FilterValue }> = [
  { label: '全部', value: 'all' },
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' },
  { label: '有附件', value: 'attachments' },
  { label: '含验证码', value: 'code' }
]

const totalPages = computed(() => Math.max(1, Math.ceil(totalEmails.value / pageSize)))

const filterCounts = computed<Record<FilterValue, number>>(() => ({
  all: emails.value.length,
  unread: emails.value.filter(email => !email.is_read).length,
  read: emails.value.filter(email => email.is_read).length,
  attachments: emails.value.filter(email => email.has_attachments).length,
  code: emails.value.filter(email => Boolean(summaryCode(email))).length
}))

const normalizedSearch = computed(() => searchKeyword.value.trim().toLowerCase())

const filteredEmails = computed(() => {
  return emails.value.filter((email) => {
    const matchesFilter =
      activeFilter.value === 'all' ||
      (activeFilter.value === 'unread' && !email.is_read) ||
      (activeFilter.value === 'read' && email.is_read) ||
      (activeFilter.value === 'attachments' && email.has_attachments) ||
      (activeFilter.value === 'code' && Boolean(summaryCode(email)))

    if (!matchesFilter) {
      return false
    }

    if (!normalizedSearch.value) {
      return true
    }

    return [
      email.subject,
      email.sender,
      email.body_preview
    ].some(value => value?.toLowerCase().includes(normalizedSearch.value))
  })
})

const hasActiveFilters = computed(() => activeFilter.value !== 'all' || Boolean(searchKeyword.value))

const detailCode = computed(() => {
  if (!selectedEmail.value) {
    return ''
  }

  return extractCode([
    selectedEmail.value.subject,
    selectedEmail.value.body_text,
    selectedEmail.value.body_html
  ].filter(Boolean).join('\n'))
})

const sanitizedHtml = computed(() => {
  if (!selectedEmail.value?.body_html) {
    return ''
  }

  return DOMPurify.sanitize(selectedEmail.value.body_html, {
    ADD_ATTR: ['target', 'rel'],
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input', 'button'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover']
  })
})

watch(page, () => {
  selectedEmailId.value = null
  selectedEmail.value = null
  void loadEmails()
})

function summaryCode(email: EmailSummary): string {
  return extractCode([email.subject, email.body_preview].filter(Boolean).join('\n'))
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (typeof error === 'object' && error !== null && 'response' in error) {
    const response = (error as { response?: { data?: { detail?: string } } }).response
    return response?.data?.detail || fallback
  }

  return fallback
}

async function verifyJWT() {
  jwt.value = typeof route.query.jwt === 'string' ? route.query.jwt : ''

  if (!jwt.value) {
    accessErrorTitle.value = '缺少访问参数'
    accessErrorDescription.value = '当前链接没有 jwt 参数，请使用完整的公开收件箱链接。'
    checked.value = true
    return
  }

  try {
    mailboxInfo.value = await api.get('/inbox/verify', { params: { jwt: jwt.value } }) as MailboxInfo
    verified.value = true
    await loadEmails()
  } catch (error) {
    verified.value = false
    accessErrorTitle.value = '访问链接无效或已过期'
    accessErrorDescription.value = getErrorMessage(error, '请检查链接是否正确，或联系管理员获取新的访问链接。')
  } finally {
    checked.value = true
  }
}

async function loadEmails() {
  if (!jwt.value) {
    return
  }

  loadingEmails.value = true
  emailError.value = ''

  try {
    const data = await api.get('/inbox/emails', {
      params: { jwt: jwt.value, page: page.value, page_size: pageSize }
    }) as EmailListResponse

    emails.value = data.items || []
    totalEmails.value = data.total || 0

    if (selectedEmailId.value && !emails.value.some(email => email.id === selectedEmailId.value)) {
      selectedEmailId.value = null
      selectedEmail.value = null
    }
  } catch (error) {
    emailError.value = getErrorMessage(error, '无法加载邮件列表，请稍后重试。')
    message.error(emailError.value)
  } finally {
    loadingEmails.value = false
  }
}

async function selectEmail(emailId: number, force = false) {
  if (!force && selectedEmailId.value === emailId && selectedEmail.value) {
    return
  }

  selectedEmailId.value = emailId
  selectedEmail.value = null
  loadingDetail.value = true
  detailError.value = ''

  try {
    const data = await api.get(`/inbox/emails/${emailId}`, {
      params: { jwt: jwt.value }
    }) as EmailDetail

    selectedEmail.value = data

    const emailInList = emails.value.find(email => email.id === emailId)
    if (emailInList) {
      emailInList.is_read = data.is_read
    }
  } catch (error) {
    detailError.value = getErrorMessage(error, '无法加载邮件详情，请稍后重试。')
    message.error(detailError.value)
  } finally {
    loadingDetail.value = false
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value -= 1
  }
}

function nextPage() {
  if (page.value < totalPages.value) {
    page.value += 1
  }
}

function refreshCurrentPage() {
  void loadEmails()
}

function clearFilters() {
  activeFilter.value = 'all'
  searchKeyword.value = ''
}

async function copyCode(code: string) {
  if (!code) {
    return
  }

  try {
    await copyToClipboard(code)
    message.success(`已复制验证码 ${code}`)
  } catch {
    message.error('复制失败，请手动选择验证码。')
  }
}

function handleBodyClick(event: MouseEvent) {
  const target = event.target
  if (!(target instanceof Element)) {
    return
  }

  const link = target.closest('a')
  if (!link) {
    return
  }

  link.setAttribute('target', '_blank')
  link.setAttribute('rel', 'noopener noreferrer')
}

onMounted(() => {
  void verifyJWT()
})
</script>

<style scoped>
.public-inbox {
  min-height: 100vh;
  background: #f4f6f8;
  color: #1f2937;
}

.mail-shell {
  width: min(1440px, 100%);
  min-height: 100vh;
  margin: 0 auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background: #ffffff;
  border: 1px solid #d9e0e7;
  border-radius: 6px;
}

.mailbox-meta {
  min-width: 0;
}

.mailbox-label,
.detail-label {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
  text-transform: uppercase;
}

.mailbox-meta h1,
.detail-header h2 {
  margin: 2px 0;
  color: #111827;
  font-size: 22px;
  line-height: 1.25;
  overflow-wrap: anywhere;
}

.mailbox-subline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  color: #64748b;
  font-size: 13px;
}

.mail-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  width: min(520px, 100%);
}

.search-input {
  flex: 1;
  min-width: 220px;
}

.filter-bar {
  display: flex;
  gap: 8px;
  padding: 10px;
  overflow-x: auto;
  background: #ffffff;
  border: 1px solid #d9e0e7;
  border-radius: 6px;
}

.filter-button {
  min-height: 36px;
  padding: 6px 12px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #334155;
  background: #f8fafc;
  border: 1px solid #d9e0e7;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
}

.filter-button:hover,
.filter-button.active {
  color: #0f172a;
  background: #eaf2ff;
  border-color: #8bb9f3;
}

.filter-button strong {
  font-variant-numeric: tabular-nums;
}

.mail-layout {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-columns: minmax(320px, 390px) minmax(0, 1fr);
  gap: 12px;
}

.message-list-pane,
.message-detail-pane {
  min-height: calc(100vh - 154px);
  background: #ffffff;
  border: 1px solid #d9e0e7;
  border-radius: 6px;
  overflow: hidden;
}

.message-list-pane {
  display: flex;
  flex-direction: column;
}

.pane-toolbar,
.pagination-bar {
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  color: #64748b;
  border-bottom: 1px solid #e5e7eb;
}

.pagination-bar {
  border-top: 1px solid #e5e7eb;
  border-bottom: 0;
}

.message-list {
  flex: 1;
  min-height: 0;
  margin: 0;
  padding: 0;
  list-style: none;
  overflow-y: auto;
}

.message-row {
  position: relative;
  border-bottom: 1px solid #edf0f3;
  background: #ffffff;
}

.message-row.unread {
  background: #f7fbff;
}

.message-row.selected {
  background: #eaf2ff;
  box-shadow: inset 3px 0 0 #2f80ed;
}

.message-button {
  width: 100%;
  min-height: 104px;
  padding: 12px 74px 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 5px;
  text-align: left;
  color: inherit;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.message-button:hover {
  background: rgba(47, 128, 237, 0.06);
}

.row-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
}

.sender {
  min-width: 0;
  color: #111827;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row-topline time {
  flex: 0 0 auto;
  color: #64748b;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
}

.subject-line {
  color: #1f2937;
  font-size: 15px;
  font-weight: 650;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-row:not(.unread) .subject-line {
  font-weight: 500;
}

.preview-line {
  display: -webkit-box;
  color: #64748b;
  font-size: 13px;
  line-height: 1.45;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.row-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 22px;
}

.badge {
  display: inline-flex;
  align-items: center;
  min-height: 20px;
  padding: 2px 7px;
  color: #475569;
  background: #eef2f7;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
}

.unread-badge {
  color: #075985;
  background: #e0f2fe;
}

.code-badge {
  color: #166534;
  background: #dcfce7;
}

.copy-code-button {
  position: absolute;
  right: 12px;
  bottom: 12px;
}

.message-detail-pane {
  overflow-y: auto;
}

.detail-loading,
.detail-state {
  min-height: 420px;
}

.detail-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #64748b;
}

.message-detail {
  min-height: 100%;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
  border-bottom: 1px solid #e5e7eb;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 18px;
  margin: 0;
  padding: 16px 20px;
  background: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.detail-meta div {
  min-width: 0;
}

.detail-meta dt {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.detail-meta dd {
  margin: 2px 0 0;
  color: #1f2937;
  overflow-wrap: anywhere;
}

.code-panel {
  margin: 16px 20px 0;
  padding: 12px 14px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #14532d;
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  border-radius: 6px;
}

.code-panel strong {
  font-size: 20px;
  letter-spacing: 0;
  font-variant-numeric: tabular-nums;
}

.body-container {
  padding: 20px;
}

.html-body,
.text-body {
  max-width: 980px;
  color: #1f2937;
  font-size: 14px;
  line-height: 1.65;
  overflow-wrap: anywhere;
}

.html-body {
  overflow-x: auto;
}

.html-body :deep(img) {
  max-width: 100%;
  height: auto;
}

.html-body :deep(a) {
  color: #1d4ed8;
  text-decoration: underline;
}

.html-body :deep(table) {
  max-width: 100%;
  border-collapse: collapse;
}

.html-body :deep(td),
.html-body :deep(th) {
  border: 1px solid #e5e7eb;
  padding: 6px;
}

.text-body {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
}

.state-block {
  min-height: 240px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #64748b;
  text-align: center;
}

.state-block strong {
  color: #1f2937;
  font-size: 16px;
}

.error-state strong {
  color: #b42318;
}

.access-state {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.verify-placeholder {
  width: 240px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
}

@media (max-width: 900px) {
  .mail-shell {
    padding: 10px;
  }

  .mail-header,
  .detail-header {
    flex-direction: column;
    align-items: stretch;
  }

  .mail-actions {
    width: 100%;
  }

  .search-input {
    min-width: 0;
  }

  .mail-layout {
    grid-template-columns: 1fr;
  }

  .message-list-pane,
  .message-detail-pane {
    min-height: auto;
  }

  .message-list {
    max-height: 46vh;
  }

  .detail-meta {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .mail-actions,
  .code-panel {
    flex-direction: column;
    align-items: stretch;
  }

  .mailbox-meta h1,
  .detail-header h2 {
    font-size: 19px;
  }

  .message-button {
    padding-right: 14px;
    padding-bottom: 48px;
  }

  .copy-code-button {
    left: 14px;
    right: auto;
  }
}
</style>
