<script setup lang="ts">
import { computed, ref } from 'vue'
import { AlertCircle, CheckCircle2, ClipboardPaste, Copy, FileDown, Info, Play, Trash2, UploadCloud } from '@lucide/vue'
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
  'user1@hotmail.com----imap-token-1',
  'user2@outlook.com|imap-token-2',
  'user3@live.com:imap-token-3'
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
    <section class="import-hero">
      <div>
        <span class="kicker">Mailbox Import</span>
        <h1>批量导入邮箱</h1>
        <p class="muted-copy">粘贴邮箱和 IMAP token，检查无误后一次提交导入。</p>
      </div>
    </section>

    <section class="import-workspace">
      <aside class="shell-card guide-panel">
        <div class="guide-block">
          <h2><Info :size="18" />格式说明</h2>
          <p class="muted-copy">每行一个邮箱，支持以下三种分隔符，空行会自动忽略。</p>
          <pre>{{ sampleText }}</pre>
        </div>

        <div class="format-list">
          <span class="status-badge">邮箱----IMAP token</span>
          <span class="status-badge">邮箱|IMAP token</span>
          <span class="status-badge">邮箱:IMAP token</span>
        </div>

        <div class="guide-divider" />

        <div class="guide-block">
          <h2>导入选项</h2>
          <label class="toggle-row">
            <input v-model="generateLinks" type="checkbox" />
            <span>
              <strong>显示访问链接</strong>
              <small>接口返回 link 或 jwt_token 时，在报告中显示并可导出。</small>
            </span>
          </label>
        </div>

        <div class="stats-card">
          <div>
            <span>总行数</span>
            <strong>{{ totalRows }}</strong>
          </div>
          <div>
            <span>有效行</span>
            <strong>{{ parsed.valid.length }}</strong>
          </div>
          <div>
            <span>错误行</span>
            <strong>{{ parsed.invalid.length }}</strong>
          </div>
        </div>
      </aside>

      <div class="main-stack">
        <section class="shell-card input-card">
          <div class="section-header">
            <div>
              <h2><UploadCloud :size="20" />输入数据</h2>
              <p class="muted-copy">导入前自动检查邮箱格式、分隔符和 token 是否为空。</p>
            </div>
            <div class="inline-actions">
              <button class="ghost-button icon-button" type="button" aria-label="粘贴" title="粘贴" @click="pasteFromClipboard">
                <ClipboardPaste :size="18" />
              </button>
              <button class="danger-button icon-button" type="button" :disabled="!hasInput" aria-label="清空" title="清空" @click="clearInput">
                <Trash2 :size="18" />
              </button>
            </div>
          </div>

          <label class="sr-only" for="mailbox-import-input">邮箱导入原始数据</label>
          <textarea
            id="mailbox-import-input"
            v-model="inputText"
            class="field-textarea import-textarea"
            aria-label="邮箱导入原始数据"
            spellcheck="false"
            placeholder="粘贴邮箱和 IMAP token，每行一条"
          />

          <div class="input-footer">
            <div class="parse-summary">
              <span class="status-badge">{{ totalRows }} 行</span>
              <span class="status-badge status-badge--success">{{ parsed.valid.length }} 有效</span>
              <span class="status-badge" :class="{ 'status-badge--danger': parsed.invalid.length }">
                {{ parsed.invalid.length }} 错误
              </span>
            </div>
            <button class="action-button run-button" type="button" :disabled="!canImport" @click="submitImport">
              <Play :size="17" />
              {{ importing ? '导入中...' : `开始导入 ${parsed.valid.length} 个邮箱` }}
            </button>
          </div>

          <div v-if="parsed.invalid.length" class="parse-errors">
            <strong><AlertCircle :size="16" />格式错误预览</strong>
            <ul>
              <li v-for="item in parsed.invalid.slice(0, 6)" :key="`${item.line}-${item.raw}`">
                第 {{ item.line }} 行：{{ item.reason }} <code>{{ item.raw }}</code>
              </li>
            </ul>
            <p v-if="parsed.invalid.length > 6" class="muted-copy">还有 {{ parsed.invalid.length - 6 }} 行错误未显示。</p>
          </div>
        </section>

        <section class="shell-card report-card">
          <div class="section-header">
            <div>
              <h2><CheckCircle2 :size="20" />转换结果</h2>
              <p class="muted-copy">导入成功后可复制成功邮箱、复制失败报告或导出 CSV。</p>
            </div>
            <div v-if="report" class="inline-actions">
              <button class="ghost-button compact-button" type="button" @click="copyImportedEmails">
                <Copy :size="16" />
                成功邮箱
              </button>
              <button class="ghost-button compact-button" type="button" @click="copyFailedReport">
                <Copy :size="16" />
                失败报告
              </button>
              <button class="action-button compact-button" type="button" @click="exportReportCsv">
                <FileDown :size="16" />
                CSV
              </button>
            </div>
          </div>

          <div
            v-if="notice"
            class="notice"
            :class="`notice--${notice.type}`"
            :role="notice.type === 'danger' ? 'alert' : 'status'"
            :aria-live="notice.type === 'danger' ? 'assertive' : 'polite'"
          >
            {{ notice.text }}
          </div>

          <div v-if="report" class="report-grid">
            <div class="metric-card compact-metric">
              <span class="metric-label">Imported</span>
              <strong class="metric-value">{{ report.imported.length }}</strong>
            </div>
            <div class="metric-card compact-metric">
              <span class="metric-label">Errors</span>
              <strong class="metric-value">{{ report.errors.length }}</strong>
            </div>
            <div class="metric-card compact-metric">
              <span class="metric-label">Total</span>
              <strong class="metric-value">{{ report.total }}</strong>
            </div>
          </div>

          <div v-if="report" class="result-columns">
            <div class="result-panel">
              <h3>成功邮箱</h3>
              <div v-if="report.imported.length" class="result-list">
                <div v-for="item in report.imported" :key="item.email" class="result-row success-row">
                  <span>{{ item.email }}</span>
                  <a v-if="generateLinks && item.link" :href="item.link" target="_blank" rel="noreferrer">访问链接</a>
                  <span v-else class="muted-copy">{{ item.status }}</span>
                </div>
              </div>
              <div v-else class="empty-panel">暂无成功导入项</div>
            </div>

            <div class="result-panel">
              <h3>失败报告</h3>
              <div v-if="report.errors.length" class="result-list">
                <div v-for="item in report.errors" :key="errorLine(item)" class="result-row error-row">
                  <span>{{ errorLine(item) }}</span>
                </div>
              </div>
              <div v-else class="empty-panel">暂无失败项</div>
            </div>
          </div>

          <div v-else class="empty-panel report-empty">
            填入数据并点击开始导入后，这里会展示成功邮箱、失败报告和总数。
          </div>
        </section>
      </div>
    </section>
  </main>
</template>

<style scoped>
.import-page {
  padding: 26px;
}

.import-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.import-hero h1 {
  margin: 12px 0 6px;
  color: var(--text-strong);
  font-size: 30px;
  line-height: 1.2;
  letter-spacing: 0;
}

.import-hero p,
.section-header p,
.guide-panel p {
  margin: 0;
}

.inline-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.import-workspace {
  display: grid;
  grid-template-columns: minmax(280px, 360px) minmax(0, 1fr);
  grid-template-areas: 'guide main';
  gap: 20px;
  align-items: start;
}

.main-stack {
  grid-area: main;
  display: grid;
  gap: 20px;
}

.guide-panel {
  grid-area: guide;
}

.shell-card {
  padding: 22px;
}

.shell-card h2,
.result-panel h3 {
  margin: 0;
  color: var(--text-strong);
  letter-spacing: 0;
}

.shell-card h2 {
  font-size: 17px;
}

.guide-panel {
  position: sticky;
  top: 16px;
  display: grid;
  gap: 18px;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.guide-block {
  display: grid;
  gap: 12px;
}

.guide-block h2,
.input-card h2,
.report-card h2,
.parse-errors strong {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.guide-panel pre {
  overflow-x: auto;
  margin: 0;
  padding: 12px;
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  background: var(--bg-panel-muted);
  color: var(--text-main);
  font-size: 12px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.guide-divider {
  height: 1px;
  background: var(--border-soft);
}

.format-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.toggle-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  background: var(--bg-panel-muted);
}

.toggle-row input {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--accent);
}

.toggle-row strong,
.toggle-row small {
  display: block;
}

.toggle-row strong {
  color: var(--text-strong);
  font-size: 14px;
}

.toggle-row small {
  margin-top: 4px;
  color: var(--text-muted);
  line-height: 1.5;
}

.run-button:disabled,
.compact-button:disabled,
.danger-button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
  transform: none;
}

.stats-card {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.stats-card div {
  min-width: 0;
  padding: 10px;
  border-radius: 12px;
  background: var(--bg-panel-muted);
  border: 1px solid var(--border-soft);
}

.stats-card span,
.metric-label {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.stats-card strong {
  display: block;
  margin-top: 4px;
  color: var(--text-strong);
  font-size: 22px;
}

.section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.compact-button {
  min-height: 44px;
  padding: 0 12px;
  border-radius: 12px;
  font-size: 13px;
}

.icon-button {
  width: 44px;
  min-width: 44px;
  padding: 0;
}

.import-textarea {
  min-height: 360px;
  font-family: 'Cascadia Code', 'SF Mono', Consolas, monospace;
  line-height: 1.65;
}

.input-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-top: 14px;
}

.parse-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.run-button {
  min-width: 220px;
}

.parse-errors {
  margin-top: 14px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--danger) 28%, transparent);
  background: var(--bg-danger-soft);
}

.parse-errors strong {
  color: var(--danger);
}

.parse-errors ul {
  display: grid;
  gap: 8px;
  margin: 10px 0 0;
  padding: 0;
  list-style: none;
}

.parse-errors li {
  color: var(--text-main);
  font-size: 13px;
  line-height: 1.5;
}

.parse-errors code {
  color: var(--text-muted);
  overflow-wrap: anywhere;
}

.notice {
  margin-bottom: 16px;
  padding: 12px 14px;
  border-radius: 14px;
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

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.compact-metric {
  min-height: 96px;
  padding: 16px;
}

.compact-metric .metric-value {
  display: block;
  margin-top: 8px;
  font-size: 32px;
}

.result-columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.result-panel {
  min-width: 0;
  border: 1px solid var(--border-soft);
  border-radius: 16px;
  background: var(--bg-panel-muted);
}

.result-panel h3 {
  padding: 14px;
  border-bottom: 1px solid var(--border-soft);
  font-size: 15px;
}

.result-list {
  display: grid;
  gap: 8px;
  max-height: 320px;
  overflow: auto;
  padding: 12px;
}

.result-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.45;
}

.result-row span {
  min-width: 0;
  overflow-wrap: anywhere;
}

.result-row a {
  flex: 0 0 auto;
  color: var(--accent);
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

.report-empty {
  min-height: 180px;
}

@media (max-width: 1080px) {
  .import-workspace,
  .result-columns {
    grid-template-columns: 1fr;
  }

  .import-workspace {
    grid-template-areas:
      'main'
      'guide';
  }

  .guide-panel {
    position: static;
  }
}

@media (max-width: 720px) {
  .import-page {
    padding: 18px;
  }

  .import-hero,
  .section-header {
    align-items: stretch;
    flex-direction: column;
  }

  .inline-actions {
    width: 100%;
  }

  .inline-actions > *:not(.icon-button),
  .input-footer > * {
    flex: 1;
  }

  .input-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .report-grid,
  .stats-card {
    grid-template-columns: 1fr;
  }

  .run-button {
    width: 100%;
    min-width: 0;
  }

  .report-empty {
    min-height: 140px;
  }
}
</style>
