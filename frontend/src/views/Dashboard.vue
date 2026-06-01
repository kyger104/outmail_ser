<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { AlertTriangle, ArrowUpRight, Copy, Inbox, MailCheck, RefreshCw, Upload } from '@lucide/vue'
import { useMessage } from 'naive-ui'
import api from '../utils/api'
import { copyToClipboard } from '../utils/clipboard'
import { formatDateTime } from '../utils/formatDate'
import type { AdminStats, Mailbox, MailboxLink } from '../types'

const router = useRouter()
const message = useMessage()
const loading = ref(false)
const stats = ref<AdminStats>({})
const links = ref<MailboxLink[]>([])

const recentMailboxes = computed<Mailbox[]>(() => (stats.value.recent_mailboxes ?? []).slice(0, 5))
const latestSync = computed(() => {
  const row = [...recentMailboxes.value].filter((item) => item.last_sync).sort((a, b) => new Date(b.last_sync ?? 0).getTime() - new Date(a.last_sync ?? 0).getTime())[0]
  return row?.last_sync ? formatDateTime(row.last_sync) : '暂无同步'
})
const metrics = computed(() => [
  { label: '总邮箱数', value: stats.value.total_mailboxes ?? 0, meta: '已托管邮箱' },
  { label: '活跃邮箱', value: stats.value.active_mailboxes ?? 0, meta: '状态为 active' },
  { label: '异常邮箱', value: stats.value.error_mailboxes ?? 0, meta: (stats.value.error_mailboxes ?? 0) ? '需要检查令牌或 IMAP' : '当前无异常' },
  { label: '邮件总数', value: stats.value.total_emails ?? 0, meta: `未读 ${stats.value.unread_emails ?? 0} 封，${latestSync.value}` }
])

async function loadDashboard() {
  loading.value = true
  try {
    stats.value = await api.get<AdminStats>('/admin/stats')
    links.value = []
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载控制台失败')
  } finally {
    loading.value = false
  }
}

async function copyAllLinks() {
  if (!links.value.length) {
    try {
      const response = await api.get<{ items?: MailboxLink[] }>('/admin/mailboxes/links')
      links.value = response.items ?? []
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载访问链接失败')
      return
    }
  }
  if (!links.value.length) {
    message.warning('暂无可复制的访问链接')
    return
  }
  await copyToClipboard(links.value.map((item) => `${item.email},${item.link}`).join('\n'))
  message.success(`已复制 ${links.value.length} 条访问链接`)
}

onMounted(loadDashboard)
</script>

<template>
  <section class="dashboard-shell page-shell">
    <div class="dashboard-hero shell-card">
      <div class="dashboard-hero__copy">
        <div class="kicker">工作区概览</div>
        <h1>IMAP 邮件托管控制台</h1>
        <p>集中查看邮箱规模、同步状态和访问链接，快速进入导入、管理和 API Key 配置。</p>
      </div>
      <div class="dashboard-hero__actions">
        <button class="ghost-button" type="button" :disabled="loading" @click="loadDashboard">
          <RefreshCw :size="16" />
          <span>{{ loading ? '刷新中' : '刷新概览' }}</span>
        </button>
        <button class="ghost-button" type="button" @click="copyAllLinks">
          <Copy :size="16" />
          <span>复制全部链接</span>
        </button>
        <button class="action-button" type="button" @click="router.push('/import')">
          <Upload :size="16" />
          <span>导入邮箱</span>
        </button>
      </div>
    </div>

    <div class="stat-grid">
      <article v-for="metric in metrics" :key="metric.label" class="metric-card">
        <div class="metric-label">{{ metric.label }}</div>
        <div class="metric-value">{{ metric.value }}</div>
        <div class="metric-meta">{{ metric.meta }}</div>
      </article>
    </div>

    <div class="dashboard-grid">
      <section class="shell-card section-panel">
        <div class="section-panel__head">
          <div>
            <div class="kicker">近期导入</div>
            <h2>最近邮箱</h2>
          </div>
          <button class="ghost-button" type="button" @click="router.push('/admin')">
            <ArrowUpRight :size="16" />
            <span>查看全部</span>
          </button>
        </div>
        <div v-if="recentMailboxes.length" class="recent-list">
          <article v-for="row in recentMailboxes" :key="row.id" class="recent-row">
            <div>
              <strong>{{ row.email }}</strong>
              <span>{{ formatDateTime(row.created_at) }}</span>
            </div>
            <span class="status-badge" :class="row.status === 'error' ? 'status-badge--danger' : 'status-badge--success'">{{ row.status }}</span>
          </article>
        </div>
        <div v-else class="empty-panel">
          <div>
            <Inbox :size="32" />
            <p>还没有导入邮箱</p>
          </div>
        </div>
      </section>

      <section class="shell-card section-panel">
        <div class="section-panel__head">
          <div>
            <div class="kicker">快捷入口</div>
            <h2>常用操作</h2>
          </div>
        </div>
        <div class="action-stack">
          <button class="action-stack__item" type="button" @click="router.push('/import')">
            <Upload :size="18" />
            <span><strong>批量导入邮箱</strong><small>支持多分隔符解析和行级错误报告</small></span>
          </button>
          <button class="action-stack__item" type="button" @click="router.push('/admin')">
            <MailCheck :size="18" />
            <span><strong>邮箱列表管理</strong><small>搜索、筛选、复制链接和批量导出</small></span>
          </button>
          <button class="action-stack__item" type="button" @click="router.push('/admin?status=error')">
            <AlertTriangle :size="18" />
            <span><strong>查看异常邮箱</strong><small>定位同步失败和 IMAP 登录问题</small></span>
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.dashboard-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dashboard-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.dashboard-hero__copy {
  max-width: 760px;
}

.dashboard-hero__copy h1,
.section-panel h2 {
  margin: 12px 0 8px;
  color: var(--text-strong);
}

.dashboard-hero__copy h1 {
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.1;
}

.dashboard-hero__copy p {
  margin: 0;
  color: var(--text-main);
  line-height: 1.7;
}

.dashboard-hero__actions,
.section-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  flex-wrap: wrap;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 460px);
  gap: 18px;
}

.section-panel {
  padding: 22px;
}

.recent-list,
.action-stack {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-row,
.action-stack__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 16px 18px;
  border: 1px solid var(--border-soft);
  background: rgba(12, 23, 36, 0.78);
  border-radius: 18px;
  color: var(--text-main);
}

.recent-row strong,
.action-stack__item strong {
  display: block;
  color: var(--text-strong);
}

.recent-row span,
.action-stack__item small {
  color: var(--text-muted);
}

.action-stack__item {
  justify-content: flex-start;
  text-align: left;
}

@media (max-width: 1120px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .dashboard-hero {
    flex-direction: column;
  }
}
</style>
