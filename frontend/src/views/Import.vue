<script setup lang="ts">
import { computed, ref } from 'vue'
import { AlertCircle, CheckCircle2, ClipboardPaste, Copy, FileDown, Play, Trash2, UploadCloud } from '@lucide/vue'
import api from '../utils/api'
import { copyToClipboard } from '../utils/clipboard'
import { downloadCsv } from '../utils/exportCsv'
import { parseMailboxImport, type InvalidMailboxImport } from '../utils/importParser'

type ImportedItem = string | {
  email?: string
  link?: string
  jwt_token?: string
  status?: string
}

type ImportErrorItem = string | {
  line?: number
  email?: string
  raw?: string
  reason?: string
  error?: string
}

interface ImportResponse {
  imported?: ImportedItem[]
  errors?: ImportErrorItem[]
  total?: number
}

interface NormalizedImported {
  email: string
  link: string
  status: string
}

interface NormalizedError {
  line: number | null
  email: string
  raw: string
  reason: string
}

interface ImportReport {
  imported: NormalizedImported[]
  errors: NormalizedError[]
  total: number
}

const inputText = ref('')
const generateLinks = ref(true)
const importing = ref(false)
const notice = ref<{ type: 'success' | 'warning' | 'danger'; text: string } | null>(null)
const report = ref<ImportReport | null>(null)

const parsed = computed(() => parseMailboxImport(inputText.value))
const totalRows = computed(() => parsed.value.valid.length + parsed.value.invalid.length)
const hasInput = computed(() => inputText.value.trim().length > 0)
const canImport = computed(() => parsed.value.valid.length > 0 && !importing.value)

const sampleText = [
  'user1@hotmail.com----password----client-id----imap-token-1',
  'user2@outlook.com----password----client-id----imap-token-2',
  'user3@live.com----password----client-id----imap-token-3'
].join('\n')

function showNotice(type: 'success' | 'warning' | 'danger', text: string) {
  notice.value = { type, text }
}

async function pasteFromClipboard() {
  try {
    inputText.value = await navigator.clipboard.readText()
    report.value = null
    showNotice('success', '已从剪贴板粘贴内容')
  } catch {
    showNotice('danger', '无法读取剪贴板，请手动粘贴')
  }
}

function clearInput() {
  inputText.value = ''
  report.value = null
  notice.value = null
}

function normalizeImported(item: ImportedItem): NormalizedImported {
  if (typeof item === 'string') {
    return { email: item, link: '', status: 'imported' }
  }

  const email = item.email ?? ''
  const link = item.link || (item.jwt_token ? `/inbox?jwt=${item.jwt_token}` : '')
  return {
    email,
    link,
    status: item.status ?? 'imported'
  }
}

function normalizeError(item: ImportErrorItem): NormalizedError {
  if (typeof item === 'string') {
    return { line: null, email: '', raw: item, reason: item }
  }

  return {
    line: item.line ?? null,
    email: item.email ?? '',
    raw: item.raw ?? '',
    reason: item.reason ?? item.error ?? '导入失败'
  }
}

function normalizeParseError(item: InvalidMailboxImport): NormalizedError {
  return {
    line: item.line,
    email: '',
    raw: item.raw,
    reason: item.reason
  }
}

function errorLine(error: NormalizedError) {
  const prefix = error.line ? `第 ${error.line} 行` : '服务端'
  const target = error.email || error.raw
  return target ? `${prefix}: ${target} - ${error.reason}` : `${prefix}: ${error.reason}`
}

async function submitImport() {
  notice.value = null
  report.value = null

  if (!hasInput.value) {
    showNotice('warning', '请先粘贴或输入邮箱数据')
    return
  }

  if (!parsed.value.valid.length) {
    showNotice('danger', '没有可导入的有效数据行')
    return
  }

  importing.value = true
  try {
    const payload = {
      mailboxes: parsed.value.valid.map((item) => ({
        email: item.email,
        imap_token: item.imap_token
      }))
    }

    const response = await api.post('/admin/mailboxes/import', payload) as ImportResponse
    const imported = (response.imported ?? []).map(normalizeImported).filter((item) => item.email)
    const serverErrors = (response.errors ?? []).map(normalizeError)
    const parseErrors = parsed.value.invalid.map(normalizeParseError)

    report.value = {
      imported,
      errors: [...parseErrors, ...serverErrors],
      total: response.total ?? payload.mailboxes.length
    }

    if (serverErrors.length || parseErrors.length) {
      showNotice('warning', `导入完成，成功 ${imported.length} 个，失败 ${serverErrors.length + parseErrors.length} 个`)
    } else {
      showNotice('success', `导入完成，成功 ${imported.length} 个邮箱`)
    }
  } catch (error: any) {
    const detail = error?.response?.data?.detail || error?.response?.data?.message || '导入失败，请稍后重试'
    showNotice('danger', detail)
  } finally {
    importing.value = false
  }
}

async function copyImportedEmails() {
  if (!report.value?.imported.length) {
    showNotice('warning', '没有成功邮箱可复制')
    return
  }

  const text = report.value.imported.map((item) => item.email).join('\n')
  await copyToClipboard(text)
  showNotice('success', '已复制成功邮箱列表')
}

async function copyFailedReport() {
  if (!report.value?.errors.length) {
    showNotice('warning', '没有失败报告可复制')
    return
  }

  await copyToClipboard(report.value.errors.map(errorLine).join('\n'))
  showNotice('success', '已复制失败报告')
}

function exportReportCsv() {
  if (!report.value) {
    showNotice('warning', '暂无可导出的执行报告')
    return
  }

  const importedRows = report.value.imported.map((item) => ({
    type: 'success',
    email: item.email,
    status: item.status,
    link: generateLinks.value ? item.link : '',
    line: '',
    raw: '',
    reason: ''
  }))

  const errorRows = report.value.errors.map((item) => ({
    type: 'failed',
    email: item.email,
    status: '',
    link: '',
    line: item.line ?? '',
    raw: item.raw,
    reason: item.reason
  }))

  downloadCsv(
    `mailbox-import-report-${new Date().toISOString().slice(0, 10)}.csv`,
    [...importedRows, ...errorRows],
    ['type', 'email', 'status', 'link', 'line', 'raw', 'reason']
  )
  showNotice('success', '已导出 CSV 报告')
}
</script>

<template>
  <main class="import-page page-shell">
    <section class="shell-card import-console">
      <header class="console-toolbar">
        <div class="console-title">
          <h1>导入邮箱</h1>
          <span>默认格式：账号----密码----id----令牌，系统只取账号和第 4 段令牌。</span>
        </div>

        <div class="console-stats" aria-label="解析统计">
          <span><strong>{{ totalRows }}</strong> 行</span>
          <span class="success"><strong>{{ parsed.valid.length }}</strong> 有效</span>
          <span :class="{ danger: parsed.invalid.length }"><strong>{{ parsed.invalid.length }}</strong> 错误</span>
        </div>

        <div class="console-actions">
          <label class="link-toggle">
            <input v-model="generateLinks" type="checkbox" />
            显示链接
          </label>
          <button class="ghost-button compact-button" type="button" @click="pasteFromClipboard">
            <ClipboardPaste :size="16" />
            粘贴
          </button>
          <button class="danger-button compact-button" type="button" :disabled="!hasInput" @click="clearInput">
            <Trash2 :size="16" />
            清空
          </button>
          <button class="action-button compact-button run-button" type="button" :disabled="!canImport" @click="submitImport">
            <Play :size="16" />
            {{ importing ? '导入中' : `导入 ${parsed.valid.length}` }}
          </button>
        </div>
      </header>

      <div
        v-if="notice"
        class="notice"
        :class="`notice--${notice.type}`"
        :role="notice.type === 'danger' ? 'alert' : 'status'"
        :aria-live="notice.type === 'danger' ? 'assertive' : 'polite'"
      >
        {{ notice.text }}
      </div>

      <div class="format-strip">
        <UploadCloud :size="16" />
        <code>{{ sampleText.split('\n')[0] }}</code>
        <span>兼容旧格式：邮箱----token / 邮箱|token / 邮箱:token</span>
      </div>

      <section class="import-grid">
        <div class="work-panel input-panel">
          <div class="panel-bar">
            <h2>原始数据</h2>
            <span>{{ parsed.valid.length }} 个待导入</span>
          </div>

          <label class="sr-only" for="mailbox-import-input">邮箱导入原始数据</label>
          <textarea
            id="mailbox-import-input"
            v-model="inputText"
            class="field-textarea import-textarea"
            aria-label="邮箱导入原始数据"
            spellcheck="false"
            placeholder="账号----密码----id----令牌，每行一条"
          />

          <div v-if="parsed.invalid.length" class="parse-errors">
            <strong><AlertCircle :size="15" />格式错误</strong>
            <ul>
              <li v-for="item in parsed.invalid.slice(0, 5)" :key="`${item.line}-${item.raw}`">
                第 {{ item.line }} 行：{{ item.reason }} <code>{{ item.raw }}</code>
              </li>
            </ul>
            <p v-if="parsed.invalid.length > 5" class="muted-copy">还有 {{ parsed.invalid.length - 5 }} 行错误未显示。</p>
          </div>
        </div>

        <aside class="work-panel report-panel">
          <div class="panel-bar">
            <h2><CheckCircle2 :size="17" />导入结果</h2>
            <div v-if="report" class="result-actions">
              <button class="ghost-button compact-button" type="button" @click="copyImportedEmails">
                <Copy :size="15" />成功
              </button>
              <button class="ghost-button compact-button" type="button" @click="copyFailedReport">
                <Copy :size="15" />失败
              </button>
              <button class="action-button compact-button" type="button" @click="exportReportCsv">
                <FileDown :size="15" />CSV
              </button>
            </div>
          </div>

          <div v-if="report" class="result-summary">
            <span><strong>{{ report.imported.length }}</strong> 成功</span>
            <span :class="{ danger: report.errors.length }"><strong>{{ report.errors.length }}</strong> 失败</span>
            <span><strong>{{ report.total }}</strong> 提交</span>
          </div>

          <div v-if="report" class="result-lists">
            <section>
              <h3>成功邮箱</h3>
              <div v-if="report.imported.length" class="result-list">
                <div v-for="(item, index) in report.imported" :key="`${item.email}-${index}`" class="result-row success-row">
                  <span>{{ item.email }}</span>
                  <a v-if="generateLinks && item.link" :href="item.link" target="_blank" rel="noreferrer">查看</a>
                  <span v-else>{{ item.status }}</span>
                </div>
              </div>
              <div v-else class="empty-panel compact-empty">暂无成功项</div>
            </section>

            <section>
              <h3>失败报告</h3>
              <div v-if="report.errors.length" class="result-list">
                <div v-for="item in report.errors" :key="errorLine(item)" class="result-row error-row">
                  <span>{{ errorLine(item) }}</span>
                </div>
              </div>
              <div v-else class="empty-panel compact-empty">暂无失败项</div>
            </section>
          </div>

          <div v-else class="empty-panel report-empty">
            导入后在这里显示成功邮箱、失败原因和访问链接。
          </div>
        </aside>
      </section>
    </section>
  </main>
</template>

<style scoped>
.import-page {
  padding: 10px 12px 16px;
}

.import-console {
  display: grid;
  gap: 10px;
  padding: 12px;
}

.console-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.console-title {
  min-width: 260px;
}

.console-title h1 {
  margin: 0;
  color: var(--text-strong);
  font-size: 22px;
  line-height: 1.2;
}

.console-title span {
  display: block;
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.console-stats,
.console-actions,
.result-actions,
.result-summary,
.format-strip,
.panel-bar,
.parse-errors strong {
  display: flex;
  align-items: center;
  gap: 8px;
}

.console-stats span,
.result-summary span {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  min-height: 32px;
  padding: 0 10px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-panel-muted);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.console-stats strong,
.result-summary strong {
  color: var(--text-strong);
  font-size: 18px;
  font-variant-numeric: tabular-nums;
}

.compact-button {
  min-height: 34px;
  padding: 0 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 800;
}

.run-button {
  min-width: 108px;
}

.link-toggle {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-height: 34px;
  color: var(--text-main);
  font-size: 12px;
  font-weight: 800;
}

.link-toggle input {
  width: 15px;
  height: 15px;
  accent-color: var(--accent);
}

.format-strip {
  min-width: 0;
  padding: 7px 10px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-panel-muted);
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.format-strip code {
  max-width: 520px;
  overflow: hidden;
  color: var(--text-main);
  font-family: 'Cascadia Code', 'SF Mono', Consolas, monospace;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.import-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(380px, 0.85fr);
  gap: 10px;
  align-items: stretch;
}

.work-panel {
  min-width: 0;
  padding: 10px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg-panel-muted);
}

.panel-bar {
  justify-content: space-between;
  min-height: 34px;
  margin-bottom: 8px;
}

.panel-bar h2,
.result-lists h3 {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 0;
  color: var(--text-strong);
  font-size: 14px;
  letter-spacing: 0;
}

.panel-bar span {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.import-textarea {
  min-height: min(52vh, 560px);
  font-family: 'Cascadia Code', 'SF Mono', Consolas, monospace;
  font-size: 12px;
  line-height: 1.55;
}

.parse-errors {
  margin-top: 8px;
  padding: 9px;
  border-radius: var(--radius-sm);
  border: 1px solid color-mix(in srgb, var(--danger) 28%, transparent);
  background: var(--bg-danger-soft);
}

.parse-errors strong {
  margin-bottom: 6px;
  color: var(--danger);
  font-size: 12px;
}

.parse-errors ul {
  display: grid;
  gap: 5px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.parse-errors li {
  color: var(--text-main);
  font-size: 12px;
  line-height: 1.35;
}

.parse-errors code {
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.notice {
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 700;
}

.notice--success {
  color: var(--success);
  background: var(--bg-success-soft);
  border: 1px solid color-mix(in srgb, var(--success) 28%, transparent);
}

.notice--warning {
  color: var(--warning);
  background: var(--bg-warning-soft);
  border: 1px solid color-mix(in srgb, var(--warning) 30%, transparent);
}

.notice--danger {
  color: var(--danger);
  background: var(--bg-danger-soft);
  border: 1px solid color-mix(in srgb, var(--danger) 28%, transparent);
}

.report-panel {
  display: grid;
  align-content: start;
  gap: 8px;
}

.result-lists {
  display: grid;
  gap: 8px;
}

.result-list {
  display: grid;
  gap: 5px;
  max-height: 235px;
  overflow: auto;
}

.result-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  padding: 7px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  line-height: 1.35;
}

.result-row span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.result-row a {
  flex: 0 0 auto;
  color: var(--accent);
  font-size: 12px;
  font-weight: 700;
}

.success-row {
  background: var(--bg-success-soft);
  border: 1px solid color-mix(in srgb, var(--success) 24%, transparent);
}

.error-row {
  background: var(--bg-danger-soft);
  border: 1px solid color-mix(in srgb, var(--danger) 24%, transparent);
}

.compact-empty,
.report-empty {
  min-height: 92px;
  border-radius: var(--radius-sm);
}

.success {
  color: var(--success) !important;
}

.danger {
  color: var(--danger) !important;
}

.run-button:disabled,
.compact-button:disabled,
.danger-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
}

@media (max-width: 1180px) {
  .console-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .console-actions {
    flex-wrap: wrap;
  }

  .import-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .import-page {
    padding: 8px;
  }

  .console-stats {
    flex-wrap: wrap;
  }

  .format-strip {
    align-items: flex-start;
    flex-direction: column;
  }

  .format-strip code {
    max-width: 100%;
  }

  .console-actions > button,
  .run-button {
    flex: 1;
    min-width: 0;
  }
}
</style>
