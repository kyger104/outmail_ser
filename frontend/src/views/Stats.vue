<template>
  <main class="page-shell stats-page">
    <header class="page-header">
      <div>
        <span class="kicker">Stats</span>
        <h1>运行统计</h1>
        <p class="muted-copy">优先使用轻量统计接口，避免在小规格服务器上拉取全量邮箱和链接。</p>
      </div>
      <button class="ghost-button" type="button" :disabled="loading" @click="loadStats">
        {{ loading ? '加载中...' : '刷新统计' }}
      </button>
    </header>

    <p v-if="errorMessage" class="feedback feedback--error" role="alert">{{ errorMessage }}</p>

    <section class="stat-grid" aria-label="邮箱统计概览">
      <article class="metric-card">
        <span class="metric-label">总邮箱</span>
        <strong class="metric-value">{{ metrics.total }}</strong>
        <span class="metric-meta">来自 /admin/stats</span>
      </article>
      <article class="metric-card">
        <span class="metric-label">Active</span>
        <strong class="metric-value">{{ metrics.active }}</strong>
        <span class="metric-meta">Error {{ metrics.error }}</span>
      </article>
      <article class="metric-card">
        <span class="metric-label">已同步</span>
        <strong class="metric-value">{{ metrics.emails }}</strong>
        <span class="metric-meta">未读 {{ metrics.unread }} 封</span>
      </article>
      <article class="metric-card">
        <span class="metric-label">链接数</span>
        <strong class="metric-value">{{ metrics.links }}</strong>
        <span class="metric-meta">统计接口返回</span>
      </article>
    </section>

    <section class="content-grid">
      <article class="shell-card section-panel">
        <div class="panel-heading">
          <h2>状态分布</h2>
          <p>直接按邮箱 status 字段归类。</p>
        </div>

        <div v-if="loading" class="empty-panel">正在加载邮箱状态...</div>
        <div v-else-if="!statusRows.length" class="empty-panel">暂无邮箱数据</div>
        <div v-else class="status-list">
          <div v-for="row in statusRows" :key="row.status" class="status-row">
            <div>
              <strong>{{ row.status }}</strong>
              <span>{{ row.count }} 个</span>
            </div>
            <div class="bar-track" aria-hidden="true">
              <span class="bar-fill" :style="{ width: `${row.percent}%` }" />
            </div>
          </div>
        </div>
      </article>

      <article class="shell-card section-panel">
        <div class="panel-heading">
          <h2>最近邮箱</h2>
          <p>使用统计接口返回的 recent_mailboxes，优先展示最新 8 个。</p>
        </div>

        <div v-if="loading" class="empty-panel">正在加载最近邮箱...</div>
        <div v-else-if="!recentMailboxes.length" class="empty-panel">暂无最近邮箱</div>
        <div v-else class="mailbox-list">
          <article v-for="mailbox in recentMailboxes" :key="mailbox.id" class="mailbox-row">
            <div>
              <h3>{{ mailbox.email }}</h3>
              <p class="muted-copy">创建 {{ formatDateTime(mailbox.created_at) }}</p>
            </div>
            <div class="mailbox-meta">
              <span :class="['status-badge', statusClass(mailbox.status)]">{{ mailbox.status }}</span>
              <span>同步 {{ formatRelativeDate(mailbox.last_sync) }}</span>
            </div>
          </article>
        </div>
      </article>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '../utils/api'
import { formatDateTime, formatRelativeDate } from '../utils/formatDate'
import type { AdminStats } from '../types'

const stats = ref<AdminStats>({})
const loading = ref(false)
const errorMessage = ref('')

const metrics = computed(() => {
  return {
    total: stats.value.total_mailboxes ?? 0,
    active: stats.value.active_mailboxes ?? 0,
    error: stats.value.error_mailboxes ?? 0,
    emails: stats.value.total_emails ?? 0,
    unread: stats.value.unread_emails ?? 0,
    links: stats.value.total_links ?? 0
  }
})

const statusRows = computed(() => {
  const total = metrics.value.total
  const rows = [
    { status: 'active', count: metrics.value.active },
    { status: 'error', count: metrics.value.error },
    { status: 'other', count: Math.max(total - metrics.value.active - metrics.value.error, 0) }
  ].filter((row) => row.count > 0)

  return rows.map((row) => ({
    ...row,
    percent: total === 0 ? 0 : Math.round((row.count / total) * 100)
  }))
})

const recentMailboxes = computed(() => {
  return [...(stats.value.recent_mailboxes ?? [])]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 8)
})

function normalizeStatus(status: string): string {
  return status.trim().toLowerCase()
}

function isErrorStatus(status: string): boolean {
  const normalized = normalizeStatus(status)
  return normalized === 'error' || normalized === 'failed' || normalized.includes('error')
}

function statusClass(status: string): string {
  const normalized = normalizeStatus(status)

  if (normalized === 'active') {
    return 'status-badge--success'
  }

  if (isErrorStatus(status)) {
    return 'status-badge--danger'
  }

  return 'status-badge--warning'
}

function readError(error: unknown): string {
  const candidate = error as {
    response?: { data?: { detail?: string; error?: { message?: string } } }
    message?: string
  }

  return candidate.response?.data?.detail || candidate.response?.data?.error?.message || candidate.message || '统计加载失败'
}

async function loadStats() {
  loading.value = true
  errorMessage.value = ''

  try {
    stats.value = await api.get<AdminStats>('/admin/stats')
  } catch (error) {
    stats.value = {}
    errorMessage.value = readError(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadStats()
})
</script>

<style scoped>
.stats-page {
  display: grid;
  gap: 20px;
}

.page-header,
.content-grid,
.mailbox-row,
.mailbox-meta {
  display: flex;
  align-items: center;
}

.page-header {
  justify-content: space-between;
  gap: 16px;
}

.page-header h1,
.panel-heading h2,
.mailbox-row h3 {
  margin: 0;
  color: var(--text-strong);
  letter-spacing: 0;
}

.page-header h1 {
  margin-top: 12px;
  font-size: clamp(28px, 4vw, 40px);
}

.page-header p,
.panel-heading p,
.mailbox-row p {
  margin: 8px 0 0;
}

.feedback {
  margin: 0;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  font-weight: 700;
}

.feedback--error {
  border: 1px solid color-mix(in srgb, var(--danger) 28%, transparent);
  background: var(--bg-danger-soft);
  color: var(--danger);
}

.content-grid {
  align-items: stretch;
  gap: 16px;
}

.section-panel {
  flex: 1;
  min-width: 0;
  padding: 20px;
}

.panel-heading {
  display: grid;
  gap: 4px;
  margin-bottom: 16px;
}

.panel-heading p {
  color: var(--text-muted);
  font-size: 13px;
}

.status-list,
.mailbox-list {
  display: grid;
  gap: 10px;
}

.status-row {
  display: grid;
  gap: 8px;
  padding: 12px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-panel-muted);
}

.status-row > div:first-child {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.status-row strong {
  color: var(--text-strong);
}

.status-row span {
  color: var(--text-muted);
  font-size: 13px;
}

.bar-track {
  overflow: hidden;
  height: 8px;
  border-radius: 999px;
  background: var(--bg-panel-muted);
}

.bar-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--accent);
}

.mailbox-row {
  justify-content: space-between;
  gap: 16px;
  padding: 12px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-panel-muted);
}

.mailbox-row h3 {
  overflow-wrap: anywhere;
  font-size: 15px;
}

.mailbox-meta {
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--text-muted);
  font-size: 13px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
}

@media (max-width: 980px) {
  .content-grid,
  .mailbox-row {
    flex-direction: column;
    align-items: stretch;
  }

  .mailbox-meta {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .page-header {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
