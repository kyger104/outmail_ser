<template>
  <section class="shell-card api-keys-panel">
    <header class="panel-top">
      <div>
        <h2>API Key</h2>
        <p class="muted-copy">外部调用凭据，默认收起创建表单。</p>
      </div>
      <div class="panel-actions">
        <button class="ghost-button compact-button" type="button" :disabled="loading" @click="loadKeys">
          {{ loading ? '加载中' : '刷新' }}
        </button>
        <button class="action-button compact-button" type="button" @click="showCreate = !showCreate">
          {{ showCreate ? '收起' : '新建 Key' }}
        </button>
      </div>
    </header>

    <form v-if="showCreate" class="form-panel" @submit.prevent="createKey">
      <div class="form-grid">
        <div class="panel-heading">
          <h2>创建 Key</h2>
          <p>Rate limit 为 0 表示不限制。</p>
        </div>

        <label class="field-group">
          <span class="field-label">名称</span>
          <input
            v-model.trim="createForm.name"
            class="field-input"
            maxlength="80"
            placeholder="例如：外部查询服务"
            type="text"
          >
        </label>

        <label class="field-group">
          <span class="field-label">描述</span>
          <textarea
            v-model.trim="createForm.description"
            class="field-textarea compact-textarea"
            maxlength="240"
            placeholder="可选，记录用途或调用方"
          />
        </label>

        <label class="field-group">
          <span class="field-label">Rate limit</span>
          <input v-model.number="createForm.rate_limit" class="field-input" min="0" step="1" type="number">
        </label>
      </div>

      <button class="action-button compact-button form-submit" type="submit" :disabled="!canCreate || creating">
        {{ creating ? '创建中...' : '创建 API Key' }}
      </button>
    </form>

    <p v-if="errorMessage" class="feedback feedback--error" role="alert">{{ errorMessage }}</p>
    <p v-if="successMessage" class="feedback feedback--success" role="status">{{ successMessage }}</p>

    <section v-if="createdKey" class="created-panel">
      <div>
        <h2>{{ createdKey.name }}</h2>
        <p class="muted-copy">新 Key 已生成，请及时复制保存。</p>
      </div>
      <code>{{ createdKey.api_key }}</code>
      <button class="ghost-button" type="button" @click="copyKey(createdKey.api_key)">复制 Key</button>
    </section>

    <section class="list-panel">
      <div class="panel-heading list-heading">
        <div>
          <h2>Key 列表</h2>
          <p>共 {{ total }} 个，{{ activeCount }} 个启用。</p>
        </div>
      </div>

      <div v-if="loading" class="empty-panel">正在加载 API Keys...</div>
      <div v-else-if="!keys.length" class="empty-panel">
        <div>
          <h3>暂无 API Key</h3>
          <p>创建一个 Key 后，外部服务可用它调用查询接口。</p>
        </div>
      </div>

      <div v-else class="key-list">
        <article v-for="item in keys" :key="item.id" class="key-row">
          <div class="key-main">
            <div class="key-title">
              <h3>{{ item.name }}</h3>
              <span :class="['status-badge', item.is_active ? 'status-badge--success' : 'status-badge--danger']">
                {{ item.is_active ? 'Active' : 'Disabled' }}
              </span>
            </div>
            <p class="muted-copy">{{ item.description || '无描述' }}</p>
            <code class="masked-key">{{ maskKey(item.api_key) }}</code>
          </div>

          <dl class="key-meta">
            <div>
              <dt>Rate limit</dt>
              <dd>{{ item.rate_limit === 0 ? '无限制' : item.rate_limit }}</dd>
            </div>
            <div>
              <dt>Usage</dt>
              <dd>{{ item.usage_count }}</dd>
            </div>
            <div>
              <dt>Created</dt>
              <dd>{{ formatDateTime(item.created_at) }}</dd>
            </div>
            <div>
              <dt>Last used</dt>
              <dd>{{ formatDateTime(item.last_used) }}</dd>
            </div>
          </dl>

          <div class="row-actions">
            <button class="ghost-button" type="button" @click="copyKey(item.api_key)">复制</button>
            <button
              class="ghost-button"
              type="button"
              :disabled="busyId === item.id"
              @click="toggleKey(item)"
            >
              {{ item.is_active ? '禁用' : '启用' }}
            </button>
            <button
              class="danger-button"
              type="button"
              :disabled="busyId === item.id"
              @click="deleteKey(item)"
            >
              删除
            </button>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import api from '../utils/api'
import { copyToClipboard } from '../utils/clipboard'
import { formatDateTime } from '../utils/formatDate'
import type { ApiKeyItem } from '../types'

interface ApiKeyListResponse {
  items: ApiKeyItem[]
  total: number
}

interface CreateApiKeyPayload {
  name: string
  description?: string
  rate_limit: number
}

const createForm = reactive({
  name: '',
  description: '',
  rate_limit: 0
})

const keys = ref<ApiKeyItem[]>([])
const total = ref(0)
const loading = ref(false)
const creating = ref(false)
const busyId = ref<number | null>(null)
const message = useMessage()
const dialog = useDialog()
const errorMessage = ref('')
const successMessage = ref('')
const createdKey = ref<ApiKeyItem | null>(null)
const showCreate = ref(false)

const canCreate = computed(() => createForm.name.length > 0 && createForm.rate_limit >= 0)
const activeCount = computed(() => keys.value.filter((item) => item.is_active).length)

function readError(error: unknown): string {
  const candidate = error as {
    response?: { data?: { detail?: string; error?: { message?: string } } }
    message?: string
  }

  return candidate.response?.data?.detail || candidate.response?.data?.error?.message || candidate.message || '请求失败'
}

function clearFeedback() {
  errorMessage.value = ''
  successMessage.value = ''
}

async function loadKeys() {
  loading.value = true
  clearFeedback()

  try {
    const response = await api.get('/admin/api-keys') as ApiKeyListResponse
    keys.value = response.items
    total.value = response.total
    successMessage.value = 'API Key 列表已更新。'
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    loading.value = false
  }
}

async function createKey() {
  if (!canCreate.value) {
    return
  }

  creating.value = true
  clearFeedback()

  const payload: CreateApiKeyPayload = {
    name: createForm.name,
    rate_limit: Number(createForm.rate_limit) || 0
  }

  if (createForm.description) {
    payload.description = createForm.description
  }

  try {
    const response = await api.post('/admin/api-keys', payload) as ApiKeyItem
    createdKey.value = response
    createForm.name = ''
    createForm.description = ''
    createForm.rate_limit = 0
    showCreate.value = false
    successMessage.value = 'API Key 创建成功。'
    await loadKeys()
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    creating.value = false
  }
}

async function toggleKey(item: ApiKeyItem) {
  busyId.value = item.id
  clearFeedback()

  try {
    const response = await api.put(
      `/admin/api-keys/${item.id}`,
      { is_active: !item.is_active }
    ) as ApiKeyItem
    const index = keys.value.findIndex((key) => key.id === item.id)
    if (index >= 0) {
      keys.value[index] = response
    }
    successMessage.value = response.is_active ? 'API Key 已启用。' : 'API Key 已禁用。'
  } catch (error) {
    errorMessage.value = readError(error)
  } finally {
    busyId.value = null
  }
}

async function deleteKey(item: ApiKeyItem) {
  dialog.warning({
    title: '删除 API Key',
    content: `确认删除「${item.name}」？此操作不可恢复。`,
    positiveText: '确认删除',
    negativeText: '取消',
    onPositiveClick: async () => {
      busyId.value = item.id
      clearFeedback()
      try {
        await api.delete(`/admin/api-keys/${item.id}`)
        keys.value = keys.value.filter((key) => key.id !== item.id)
        total.value = Math.max(0, total.value - 1)
        if (createdKey.value?.id === item.id) {
          createdKey.value = null
        }
        message.success('API Key 已删除')
      } catch (error) {
        message.error(readError(error))
      } finally {
        busyId.value = null
      }
    }
  })
}

async function copyKey(value: string) {
  clearFeedback()

  try {
    await copyToClipboard(value)
    successMessage.value = 'API Key 已复制。'
  } catch (error) {
    errorMessage.value = readError(error)
  }
}

function maskKey(value: string): string {
  if (value.length <= 14) {
    return value
  }

  return `${value.slice(0, 7)}...${value.slice(-6)}`
}

onMounted(loadKeys)
</script>

<style scoped>
.api-keys-panel {
  display: grid;
  gap: 10px;
  padding: 12px;
}

.panel-top,
.panel-actions,
.created-panel,
.list-heading,
.key-row,
.key-title,
.row-actions {
  display: flex;
  align-items: center;
}

.panel-top {
  justify-content: space-between;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-soft);
}

.panel-top h2,
.panel-heading h2,
.created-panel h2,
.key-title h3,
.empty-panel h3 {
  margin: 0;
  color: var(--text-strong);
  letter-spacing: 0;
}

.panel-top h2 {
  font-size: 17px;
}

.panel-top p,
.panel-heading p,
.created-panel p,
.key-main p,
.empty-panel p {
  margin: 4px 0 0;
}

.form-panel {
  display: grid;
  gap: 10px;
  padding: 10px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg-panel-muted);
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(130px, 0.5fr) minmax(180px, 0.8fr) minmax(240px, 1fr) minmax(120px, 0.4fr);
  gap: 10px;
  align-items: end;
}

.form-submit {
  justify-self: start;
}

.panel-heading {
  display: grid;
  gap: 4px;
}

.panel-heading p {
  color: var(--text-muted);
  font-size: 13px;
}

.field-group {
  display: grid;
  gap: 6px;
}

.compact-textarea {
  min-height: 42px;
  resize: vertical;
}

.compact-button,
.row-actions > button {
  min-height: 34px;
  padding: 0 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 800;
}

.feedback {
  margin: 0;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 700;
}

.feedback--error {
  border: 1px solid color-mix(in srgb, var(--danger) 28%, transparent);
  background: var(--bg-danger-soft);
  color: var(--danger);
}

.feedback--success {
  border: 1px solid color-mix(in srgb, var(--success) 30%, transparent);
  background: var(--bg-success-soft);
  color: var(--success);
}

.created-panel {
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border: 1px solid var(--border-accent);
  border-radius: var(--radius-md);
  background: var(--bg-accent-soft);
}

.created-panel code,
.masked-key {
  overflow-wrap: anywhere;
  color: var(--accent);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 13px;
}

.list-panel {
  overflow: hidden;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
}

.list-heading {
  justify-content: space-between;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-soft);
}

.key-list {
  display: grid;
}

.key-row {
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-soft);
}

.key-row:last-child {
  border-bottom: 0;
}

.key-main {
  display: grid;
  gap: 5px;
  min-width: 220px;
  flex: 1.1;
}

.key-title {
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 10px;
}

.key-title h3 {
  font-size: 14px;
}

.key-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(92px, 1fr));
  gap: 8px;
  min-width: 430px;
  margin: 0;
}

.key-meta div {
  display: grid;
  gap: 4px;
}

.key-meta dt {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.key-meta dd {
  margin: 0;
  color: var(--text-main);
  font-size: 13px;
}

.row-actions {
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 6px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
}

@media (max-width: 1100px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }

  .created-panel,
  .key-row {
    flex-direction: column;
    align-items: stretch;
  }

  .key-meta {
    min-width: 0;
  }
}

@media (max-width: 640px) {
  .panel-top {
    align-items: stretch;
    flex-direction: column;
  }

  .form-grid,
  .key-meta {
    grid-template-columns: 1fr;
  }

  .row-actions {
    justify-content: stretch;
  }

  .row-actions > button {
    flex: 1;
  }
}
</style>
