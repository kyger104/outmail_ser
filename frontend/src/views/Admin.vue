<template>
  <div class="admin-container">
    <div class="admin-header">
      <h1>管理员面板</h1>
      <n-button type="primary" @click="$router.push('/inbox')">收件箱</n-button>
    </div>

    <div class="admin-content">
      <n-card title="批量导入邮箱" class="import-card">
        <n-form>
          <n-form-item label="邮箱列表（每行一个，格式：邮箱,令牌）">
            <n-input
              v-model:value="importText"
              type="textarea"
              placeholder="user1@outlook.com,app-password-1&#10;user2@hotmail.com,app-password-2"
              :rows="8"
            />
          </n-form-item>
          <n-space>
            <n-button type="primary" @click="handleImport" :loading="importing" attr-type="button">
              导入
            </n-button>
          </n-space>
        </n-form>

        <n-collapse-transition :show="importResult.show">
          <n-card :title="importResult.success > 0 ? '导入完成' : '导入失败'" :segmented="true" class="import-result">
            <n-result
              v-if="importResult.success > 0 && importResult.fail === 0"
              status="success"
              :title="`成功导入 ${importResult.success} 个邮箱`"
            />
            <n-result
              v-else-if="importResult.success > 0 && importResult.fail > 0"
              status="warning"
              :title="`成功 ${importResult.success} 个，失败 ${importResult.fail} 个`"
            >
              <template #default>
                <n-list v-if="importResult.errors.length">
                  <n-list-item v-for="(err, i) in importResult.errors" :key="i">
                    <n-text depth="3">{{ err }}</n-text>
                  </n-list-item>
                </n-list>
              </template>
            </n-result>
            <n-result
              v-else
              status="error"
              title="导入失败"
              :description="importResult.errors.join('; ')"
            />
          </n-card>
        </n-collapse-transition>
      </n-card>

      <n-card title="邮箱列表" class="list-card">
        <n-data-table
          :columns="columns"
          :data="mailboxes"
          :loading="loading"
          :bordered="true"
          :single-line="false"
        />
        <div class="pagination-bar">
          <n-space justify="center" align="center">
            <n-button size="small" @click="prevPage" :disabled="page <= 1">上一页</n-button>
            <n-text depth="3">第 {{ page }} 页</n-text>
            <n-button size="small" @click="nextPage" :disabled="mailboxes.length < pageSize">下一页</n-button>
          </n-space>
        </div>
      </n-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, h, onMounted } from 'vue'
import {
  NCard, NForm, NFormItem, NInput, NButton, NDataTable, NTag,
  NSpace, NText, NList, NListItem, NResult, NCollapseTransition,
  useMessage, useDialog
} from 'naive-ui'
import { format } from 'date-fns'
import api from '../utils/api'

interface Mailbox {
  id: number
  email: string
  status: string
  last_sync: string | null
  created_at: string
}

interface ImportResult {
  show: boolean
  success: number
  fail: number
  errors: string[]
}

const message = useMessage()
const dialog = useDialog()

const importText = ref('')
const importing = ref(false)
const mailboxes = ref<Mailbox[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20

const importResult = ref<ImportResult>({
  show: false,
  success: 0,
  fail: 0,
  errors: []
})

const statusMap: Record<string, { type: 'success' | 'warning' | 'error' | 'default', text: string }> = {
  active: { type: 'success', text: '活跃' },
  inactive: { type: 'warning', text: '未激活' },
  error: { type: 'error', text: '错误' }
}

const columns = [
  { title: 'ID', key: 'id', width: 70 },
  { title: '邮箱', key: 'email', ellipsis: { tooltip: true } },
  {
    title: '状态',
    key: 'status',
    width: 90,
    render: (row: Mailbox) => {
      const s = statusMap[row.status] || { type: 'default' as const, text: row.status }
      return h(NTag, { type: s.type, size: 'small' }, { default: () => s.text })
    }
  },
  {
    title: '最后同步',
    key: 'last_sync',
    render: (row: Mailbox) => row.last_sync ? format(new Date(row.last_sync), 'yyyy-MM-dd HH:mm:ss') : '-'
  },
  {
    title: '创建时间',
    key: 'created_at',
    render: (row: Mailbox) => format(new Date(row.created_at), 'yyyy-MM-dd HH:mm:ss')
  },
  {
    title: '操作',
    key: 'actions',
    width: 100,
    render: (row: Mailbox) => {
      return h(NButton, {
        size: 'small',
        type: 'error',
        onClick: () => handleDelete(row)
      }, { default: () => '删除' })
    }
  }
]

async function loadMailboxes() {
  loading.value = true
  try {
    const data = await api.get('/admin/mailboxes', {
      params: { page: page.value, limit: pageSize }
    }) as Mailbox[]
    mailboxes.value = data
  } catch {
    message.error('加载邮箱列表失败')
  } finally {
    loading.value = false
  }
}

function prevPage() {
  if (page.value > 1) {
    page.value--
    loadMailboxes()
  }
}

function nextPage() {
  page.value++
  loadMailboxes()
}

async function handleImport() {
  if (!importText.value.trim()) {
    message.warning('请输入邮箱信息')
    return
  }

  importing.value = true
  importResult.value.show = false

  try {
    const lines = importText.value.trim().split('\n')
    const mailboxesList = lines
      .map(line => {
        const [email, imap_token] = line.split(',').map(s => s.trim())
        return { email, imap_token }
      })
      .filter(m => m.email && m.imap_token)

    if (mailboxesList.length === 0) {
      message.warning('没有有效的邮箱数据')
      return
    }

    const result = await api.post('/admin/mailboxes/import', { mailboxes: mailboxesList }) as {
      imported: string[]
      errors: string[]
      total: number
    }

    importResult.value = {
      show: true,
      success: result.imported.length,
      fail: result.errors.length,
      errors: result.errors
    }

    if (result.imported.length > 0) {
      message.success(`成功导入 ${result.imported.length} 个邮箱`)
    }
    if (result.errors.length > 0) {
      message.warning(`失败 ${result.errors.length} 个`)
    }

    importText.value = ''
    await loadMailboxes()
  } catch (err: any) {
    message.error(err?.response?.data?.detail || '导入失败，请检查网络连接')
  } finally {
    importing.value = false
  }
}

function handleDelete(row: Mailbox) {
  dialog.warning({
    title: '确认删除',
    content: `确定要删除邮箱 ${row.email} 吗？此操作不可撤销。`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: async () => {
      try {
        await api.delete(`/admin/mailboxes/${row.id}`)
        message.success('删除成功')
        await loadMailboxes()
      } catch {
        message.error('删除失败')
      }
    }
  })
}

onMounted(loadMailboxes)
</script>

<style scoped>
.admin-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 100vh;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.admin-header h1 {
  margin: 0;
}

.admin-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.import-result {
  margin-top: 16px;
}

.pagination-bar {
  padding-top: 16px;
}
</style>
