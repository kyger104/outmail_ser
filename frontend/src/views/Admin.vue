<script setup lang="ts">
import { computed, h, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  AlertTriangle,
  CheckCircle2,
  Copy,
  Download,
  ExternalLink,
  Link2,
  RefreshCw,
  Search,
  RotateCw,
  Trash2
} from '@lucide/vue'
import { NButton, NDataTable, NTag, useDialog, useMessage } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'
import api from '../utils/api'
import { copyToClipboard } from '../utils/clipboard'
import { downloadCsv } from '../utils/exportCsv'
import { formatDateTime } from '../utils/formatDate'
import type { AdminStats, BatchDeleteResponse, Mailbox, MailboxLink, MailboxSyncResponse } from '../types'

const route = useRoute()
const message = useMessage()
const dialog = useDialog()

const loading = ref(false)
const linkLoading = ref(false)
const statsLoading = ref(false)
const mailboxes = ref<Mailbox[]>([])
const links = ref<MailboxLink[]>([])
const stats = ref<AdminStats>({})
const selectedRowKeys = ref<number[]>([])
const searchQuery = ref('')
const statusFilter = ref((route.query.status as string) || 'all')
const page = ref(1)
const pageSize = 50
const syncingIds = ref(new Set<number>())

const statusOptions = [
  { label: '全部状态', value: 'all' },
  { label: '活跃', value: 'active' },
  { label: '异常', value: 'error' },
  { label: '未激活', value: 'inactive' },
  { label: '未同步', value: 'unsynced' }
]

const linkMap = computed(() => new Map(links.value.map((item) => [item.id ?? item.mailbox_id, item.link])))
const selectedRows = computed(() => mailboxes.value.filter((row) => selectedRowKeys.value.includes(row.id)))
const filteredRows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  return mailboxes.value.filter((row) => {
    const matchesSearch = !query || [row.email, row.status, row.last_sync, row.created_at].join(' ').toLowerCase().includes(query)
    const matchesStatus =
      statusFilter.value === 'all' ||
      (statusFilter.value === 'unsynced' ? !row.last_sync : row.status === statusFilter.value)
    return matchesSearch && matchesStatus
  })
})

const metrics = computed(() => [
  { label: '总邮箱数', value: stats.value.total_mailboxes ?? mailboxes.value.length, meta: stats.value.total_mailboxes == null ? '当前已加载' : '全局统计' },
  { label: '活跃邮箱', value: stats.value.active_mailboxes ?? mailboxes.value.filter((item) => item.status === 'active').length, meta: '可正常取信' },
  { label: '异常邮箱', value: stats.value.error_mailboxes ?? mailboxes.value.filter((item) => item.status === 'error').length, meta: '需要检查令牌' },
  { label: '已选中', value: selectedRowKeys.value.length, meta: selectedRowKeys.value.length ? '可批量操作' : '暂未选择' }
])

function statusTag(row: Mailbox) {
  const type = row.status === 'active' ? 'success' : row.status === 'error' ? 'error' : 'warning'
  return h(NTag, { type, size: 'small', round: true }, { default: () => row.status })
}

const columns = computed<DataTableColumns<Mailbox>>(() => [
  { type: 'selection' },
  { title: 'ID', key: 'id', width: 72 },
  { title: '邮箱地址', key: 'email', minWidth: 240, ellipsis: { tooltip: true } },
  { title: '状态', key: 'status', width: 110, render: statusTag },
  {
    title: '最后同步',
    key: 'last_sync',
    minWidth: 170,
    render: (row) => formatDateTime(row.last_sync)
  },
  {
    title: '创建时间',
    key: 'created_at',
    minWidth: 170,
    render: (row) => formatDateTime(row.created_at)
  },
  {
    title: '操作',
    key: 'actions',
    width: 260,
    render: (row) => h('div', { class: 'table-actions' }, [
      h(NButton, { size: 'small', tertiary: true, title: '复制访问链接', onClick: () => copyLink(row) }, { icon: () => h(Link2, { size: 15 }) }),
      h(NButton, { size: 'small', tertiary: true, title: '打开收件箱', onClick: () => openInbox(row) }, { icon: () => h(ExternalLink, { size: 15 }) }),
      h(NButton, { size: 'small', tertiary: true, title: '手动同步', loading: syncingIds.value.has(row.id), disabled: syncingIds.value.has(row.id), onClick: () => syncMailbox(row) }, { icon: () => h(RotateCw, { size: 15 }) }),
      h(NButton, { size: 'small', tertiary: true, type: 'error', title: '删除邮箱', onClick: () => confirmDelete(row) }, { icon: () => h(Trash2, { size: 15 }) })
    ])
  }
])

async function loadStats() {
  statsLoading.value = true
  try {
    stats.value = await api.get<AdminStats>('/admin/stats')
  } catch (error: any) {
    stats.value = {}
    message.error(error.response?.data?.detail || '加载统计失败')
  } finally {
    statsLoading.value = false
  }
}

async function loadMailboxes() {
  loading.value = true
  try {
    mailboxes.value = await api.get<Mailbox[]>('/admin/mailboxes', {
      params: { page: page.value, limit: 200 }
    })
    selectedRowKeys.value = []
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载邮箱列表失败')
  } finally {
    loading.value = false
  }
}

async function loadLinks() {
  linkLoading.value = true
  try {
    const response = await api.get<{ items: MailboxLink[] }>('/admin/mailboxes/links')
    links.value = response.items ?? []
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载访问链接失败')
  } finally {
    linkLoading.value = false
  }
}

async function refreshAll() {
  await Promise.all([loadStats(), loadMailboxes()])
}

async function ensureLink(row: Mailbox) {
  const cached = linkMap.value.get(row.id)
  if (cached) {
    return cached
  }
  const response = await api.get<MailboxLink>(`/admin/mailboxes/${row.id}/link`)
  links.value = [...links.value, { ...response, id: row.id }]
  return response.link
}

async function copyLink(row: Mailbox) {
  try {
    const link = await ensureLink(row)
    await copyToClipboard(link)
    message.success('访问链接已复制')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '复制链接失败')
  }
}

async function openInbox(row: Mailbox) {
  try {
    const link = await ensureLink(row)
    window.open(link, '_blank', 'noopener,noreferrer')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '打开收件箱失败')
  }
}

function buildExportRows(rows: Mailbox[]) {
  return rows.map((row) => ({
    email: row.email,
    status: row.status,
    last_sync: row.last_sync ?? '',
    created_at: row.created_at,
    access_link: linkMap.value.get(row.id) ?? ''
  }))
}

async function copySelectedLinks() {
  if (!selectedRows.value.length) {
    message.warning('请先选择邮箱')
    return
  }

  const lines = await Promise.all(selectedRows.value.map(async (row) => `${row.email},${await ensureLink(row)}`))
  await copyToClipboard(lines.join('\n'))
  message.success(`已复制 ${lines.length} 条链接`)
}

async function exportRows(rows: Mailbox[], filename: string) {
  if (!rows.length) {
    message.warning('没有可导出的数据')
    return
  }
  if (!links.value.length) {
    await loadLinks()
  }
  downloadCsv(filename, buildExportRows(rows), ['email', 'status', 'last_sync', 'created_at', 'access_link'])
  message.success(`已导出 ${rows.length} 条数据`)
}

async function syncMailbox(row: Mailbox) {
  syncingIds.value = new Set(syncingIds.value).add(row.id)
  try {
    const response = await api.post<MailboxSyncResponse>(`/admin/mailboxes/${row.id}/sync`)
    message.success(response.message || '同步任务已触发')
    await refreshAll()
  } catch (error: any) {
    message.error(error.response?.data?.detail || '同步失败')
  } finally {
    const next = new Set(syncingIds.value)
    next.delete(row.id)
    syncingIds.value = next
  }
}

function confirmDelete(row: Mailbox) {
  dialog.warning({
    title: '删除邮箱',
    content: `确认删除 ${row.email}？此操作会删除该邮箱下的邮件记录，且不可撤销。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.delete(`/admin/mailboxes/${row.id}`)
        message.success('邮箱已删除')
        await refreshAll()
      } catch (error: any) {
        message.error(error.response?.data?.detail || '删除失败')
      }
    }
  })
}

function confirmBatchDelete() {
  if (!selectedRows.value.length) {
    message.warning('请先选择邮箱')
    return
  }
  dialog.warning({
    title: '批量删除邮箱',
    content: `确认删除选中的 ${selectedRows.value.length} 个邮箱？此操作会删除对应邮件记录，且不可撤销。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        const ids = selectedRows.value.map((row) => row.id)
        const response = await api.post<BatchDeleteResponse>('/admin/mailboxes/batch-delete', { ids })
        const deleted = Array.isArray(response.deleted) ? response.deleted.length : response.deleted ?? ids.length
        const errors = response.errors?.length ?? 0
        if (errors) {
          message.warning(`已删除 ${deleted} 个邮箱，${errors} 个失败`)
        } else {
          message.success(`已删除 ${deleted} 个邮箱`)
        }
        await refreshAll()
      } catch (error: any) {
        message.error(error.response?.data?.detail || '批量删除失败')
      }
    }
  })
}

watch(() => route.query.status, (value) => {
  statusFilter.value = (value as string) || 'all'
})

onMounted(refreshAll)
</script>

<template>
  <section class="admin-shell page-shell">
    <div class="admin-hero shell-card">
      <div>
        <div class="kicker">邮箱管理</div>
        <h1>托管邮箱列表</h1>
        <p>轻量管理 IMAP 邮箱、访问链接和同步状态。统计优先读取轻量接口，访问链接在复制或导出时按需加载。</p>
      </div>
      <div class="admin-hero__actions">
        <button class="ghost-button" type="button" :disabled="loading || linkLoading || statsLoading" @click="refreshAll">
          <RefreshCw :size="16" />
          <span>{{ loading || linkLoading || statsLoading ? '刷新中' : '刷新' }}</span>
        </button>
        <button class="ghost-button" type="button" @click="exportRows(filteredRows, 'mailboxes-filtered.csv')">
          <Download :size="16" />
          <span>导出筛选</span>
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

    <section class="shell-card list-panel">
      <div class="list-toolbar">
        <label class="search-box">
          <Search :size="16" />
          <input v-model="searchQuery" placeholder="搜索邮箱、状态或时间" type="search" />
        </label>
        <select v-model="statusFilter" class="field-select status-select" aria-label="状态筛选">
          <option v-for="option in statusOptions" :key="option.value" :value="option.value">{{ option.label }}</option>
        </select>
        <button class="ghost-button" type="button" @click="copySelectedLinks">
          <Copy :size="16" />
          <span>复制选中链接</span>
        </button>
        <button class="ghost-button" type="button" @click="exportRows(selectedRows, 'mailboxes-selected.csv')">
          <Download :size="16" />
          <span>导出选中</span>
        </button>
        <button class="danger-button" type="button" @click="confirmBatchDelete">
          <Trash2 :size="16" />
          <span>批量删除</span>
        </button>
      </div>

      <div v-if="selectedRows.length" class="selection-bar">
        <CheckCircle2 :size="16" />
        <span>已选择 {{ selectedRows.length }} 个邮箱</span>
      </div>

      <div v-if="!loading && mailboxes.length && !filteredRows.length" class="empty-panel">
        <div>
          <AlertTriangle :size="32" />
          <p>当前筛选条件下没有邮箱</p>
        </div>
      </div>
      <n-data-table
        v-else
        v-model:checked-row-keys="selectedRowKeys"
        :columns="columns"
        :data="filteredRows"
        :loading="loading"
        :row-key="(row: Mailbox) => row.id"
        :pagination="{ pageSize }"
        striped
      />
    </section>
  </section>
</template>

<style scoped>
.admin-shell {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.admin-hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  padding: 28px;
}

.admin-hero h1 {
  margin: 12px 0 8px;
  color: var(--text-strong);
  font-size: clamp(28px, 4vw, 40px);
}

.admin-hero p {
  max-width: 760px;
  margin: 0;
  color: var(--text-main);
  line-height: 1.7;
}

.admin-hero__actions,
.list-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
}

.list-panel {
  padding: 22px;
}

.search-box {
  min-width: min(100%, 320px);
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 14px;
  border: 1px solid var(--border-strong);
  background: var(--bg-panel-strong);
}

.search-box input {
  flex: 1;
  min-width: 0;
  border: none;
  background: transparent;
  color: var(--text-strong);
}

.search-box input:focus {
  outline: none;
}

.status-select {
  width: 170px;
}

.selection-bar {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin: 16px 0;
  padding: 10px 14px;
  border-radius: 14px;
  background: var(--bg-accent-soft);
  color: var(--accent);
}

:deep(.table-actions) {
  display: flex;
  gap: 8px;
}

@media (max-width: 900px) {
  .admin-hero {
    flex-direction: column;
  }

  .list-toolbar > * {
    width: 100%;
  }
}
</style>
