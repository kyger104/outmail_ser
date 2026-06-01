<script setup lang="ts">
import { computed, ref } from 'vue'
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
        <p class="muted-copy">粘贴邮箱和 IMAP token，系统会先解析格式，再提交有效数据到后台导入接口。</p>
      </div>
      <div class="hero-actions">
        <button class="ghost-button" type="button" @click="pasteFromClipboard">一键粘贴</button>
        <button class="danger-button" type="button" :disabled="!hasInput && !report" @click="clearInput">清空</button>
      </div>
    </section>

    <section class="import-layout">
      <aside class="side-stack">
        <div class="shell-card info-card">
          <h2>输入格式</h2>
          <p class="muted-copy">每行一个邮箱，支持多种分隔符。空行会被忽略，IMAP token 不会保存到浏览器本地存储。</p>
          <pre>{{ sampleText }}</pre>
          <div class="format-list">
            <span class="status-badge">邮箱----IMAP token</span>
            <span class="status-badge">邮箱|IMAP token</span>
            <span class="status-badge">邮箱:IMAP token</span>
          </div>
        </div>

        <div class="shell-card config-card">
          <h2>导入配置</h2>
          <label class="toggle-row">
            <input v-model="generateLinks" type="checkbox" />
            <span>
              <strong>导入后生成访问链接</strong>
              <small>如接口返回 link 或 jwt_token，报告会显示并导出链接。</small>
            </span>
          </label>

          <button class="action-button run-button" type="button" :disabled="!canImport" @click="submitImport">
            {{ importing ? '导入中...' : `执行导入 ${parsed.valid.length} 个邮箱` }}
          </button>
        </div>

        <div class="shell-card stats-card">
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
              <h2>原始数据</h2>
              <p class="muted-copy">导入前会自动检查邮箱格式、分隔符和 token 是否为空。</p>
            </div>
            <div class="inline-actions">
              <button class="ghost-button compact-button" type="button" @click="pasteFromClipboard">粘贴</button>
              <button class="danger-button compact-button" type="button" :disabled="!hasInput" @click="clearInput">清空</button>
            </div>
          </div>

          <textarea
            v-model="inputText"
            class="field-textarea import-textarea"
            spellcheck="false"
            placeholder="user1@hotmail.com----imap-token-1&#10;user2@outlook.com|imap-token-2&#10;user3@live.com:imap-token-3"
          />

          <div v-if="parsed.invalid.length" class="parse-errors">
            <strong>格式错误预览</strong>
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
              <h2>执行报告</h2>
              <p class="muted-copy">导入成功后可复制成功邮箱、复制失败报告或导出 CSV。</p>
            </div>
            <div v-if="report" class="inline-actions">
              <button class="ghost-button compact-button" type="button" @click="copyImportedEmails">复制成功邮箱</button>
              <button class="ghost-button compact-button" type="button" @click="copyFailedReport">复制失败报告</button>
              <button class="action-button compact-button" type="button" @click="exportReportCsv">导出 CSV</button>
            </div>
          </div>

          <div v-if="notice" class="notice" :class="`notice--${notice.type}`">
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
            填入数据并点击执行导入后，这里会展示 imported / errors / total。
          </div>
        </section>
      </div>
    </section>
  </main>
</template>

<style scoped>
.import-page {
  padding: 28px;
}

.import-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}

.import-hero h1 {
  margin: 14px 0 8px;
  color: var(--text-strong);
  font-size: 32px;
  line-height: 1.2;
  letter-spacing: 0;
}

.import-hero p,
.section-header p,
.info-card p {
  margin: 0;
}

.hero-actions,
.inline-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.import-layout {
  display: grid;
  grid-template-columns: 330px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}

.side-stack,
.main-stack {
  display: grid;
  gap: 18px;
}

.shell-card {
  padding: 20px;
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

.info-card pre {
  overflow-x: auto;
  margin: 16px 0;
  padding: 14px;
  border: 1px solid var(--border-strong);
  border-radius: 14px;
  background: rgba(8, 17, 26, 0.72);
  color: var(--accent);
  font-size: 12px;
  line-height: 1.7;
}

.format-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.config-card {
  display: grid;
  gap: 18px;
}

.toggle-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 14px;
  border: 1px solid var(--border-strong);
  border-radius: 16px;
  background: rgba(12, 23, 36, 0.64);
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

.run-button {
  width: 100%;
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
  gap: 10px;
}

.stats-card div {
  min-width: 0;
  padding: 12px;
  border-radius: 14px;
  background: rgba(12, 23, 36, 0.66);
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
  margin-top: 6px;
  color: var(--text-strong);
  font-size: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.compact-button {
  min-height: 36px;
  padding: 0 12px;
  border-radius: 12px;
  font-size: 13px;
}

.import-textarea {
  min-height: 340px;
  font-family: 'Cascadia Code', 'SF Mono', Consolas, monospace;
  line-height: 1.65;
}

.parse-errors {
  margin-top: 14px;
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(255, 107, 122, 0.22);
  background: rgba(255, 107, 122, 0.07);
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
  background: rgba(57, 217, 138, 0.1);
  border: 1px solid rgba(57, 217, 138, 0.2);
}

.notice--warning {
  color: var(--warning);
  background: rgba(247, 185, 85, 0.1);
  border: 1px solid rgba(247, 185, 85, 0.2);
}

.notice--danger {
  color: var(--danger);
  background: rgba(255, 107, 122, 0.1);
  border: 1px solid rgba(255, 107, 122, 0.2);
}

.report-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.compact-metric {
  min-height: 112px;
  padding: 18px;
}

.compact-metric .metric-value {
  display: block;
  margin-top: 10px;
  font-size: 34px;
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
  background: rgba(12, 23, 36, 0.52);
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
  background: rgba(57, 217, 138, 0.08);
  border: 1px solid rgba(57, 217, 138, 0.14);
}

.error-row {
  background: rgba(255, 107, 122, 0.08);
  border: 1px solid rgba(255, 107, 122, 0.14);
}

.report-empty {
  min-height: 260px;
}

@media (max-width: 1080px) {
  .import-layout,
  .result-columns {
    grid-template-columns: 1fr;
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

  .hero-actions,
  .inline-actions {
    width: 100%;
  }

  .hero-actions > *,
  .inline-actions > * {
    flex: 1;
  }

  .report-grid,
  .stats-card {
    grid-template-columns: 1fr;
  }
}
</style>
