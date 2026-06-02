<template>
  <main class="page-shell settings-page">
    <header class="page-header">
      <div>
        <span class="kicker">Settings</span>
        <h1>设置</h1>
        <p class="muted-copy">仅管理本地 UI 偏好和缓存，不保存管理员密码、API Key 或邮箱令牌。</p>
      </div>
    </header>

    <section class="settings-grid">
      <article class="shell-card section-panel">
        <div class="panel-heading">
          <h2>本地 UI 偏好</h2>
          <p>这些配置只影响当前浏览器，不会上传到后端。</p>
        </div>

        <label class="setting-row">
          <span>
            <strong>紧凑列表</strong>
            <small>用于未来列表页降低行高和留白。</small>
          </span>
          <input v-model="preferences.compactList" type="checkbox" @change="savePreferences">
        </label>

        <label class="setting-row">
          <span>
            <strong>新标签打开收件箱链接</strong>
            <small>用于外部链接操作的本地行为偏好。</small>
          </span>
          <input v-model="preferences.openInboxInNewTab" type="checkbox" @change="savePreferences">
        </label>

        <label class="field-group">
          <span class="field-label">默认刷新间隔</span>
          <select v-model="preferences.refreshInterval" class="field-select" @change="savePreferences">
            <option :value="0">手动刷新</option>
            <option :value="30">30 秒</option>
            <option :value="60">1 分钟</option>
            <option :value="300">5 分钟</option>
          </select>
        </label>

        <p v-if="savedMessage" class="feedback feedback--success" role="status">{{ savedMessage }}</p>
      </article>

      <article class="shell-card section-panel">
        <div class="panel-heading">
          <h2>运行信息</h2>
          <p>用于排查部署环境，不包含敏感凭据。</p>
        </div>

        <dl class="info-list">
          <div>
            <dt>后端地址</dt>
            <dd>{{ backendBase }}</dd>
          </div>
          <div>
            <dt>当前版本</dt>
            <dd>{{ appVersion }}</dd>
          </div>
          <div>
            <dt>Base URL</dt>
            <dd>{{ baseUrl }}</dd>
          </div>
          <div>
            <dt>缓存项</dt>
            <dd>{{ cacheSummary }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section class="shell-card section-panel">
      <div class="panel-heading">
        <h2>本地缓存</h2>
        <p>清理 localStorage、sessionStorage 和可用的 Cache Storage。已打开页面内存中的临时认证会随刷新丢失。</p>
      </div>

      <div class="cache-actions">
        <button class="danger-button" type="button" @click="clearLocalCache">清理本地缓存</button>
        <button class="ghost-button" type="button" @click="refreshCacheState">重新计算</button>
      </div>

      <p v-if="cacheMessage" class="feedback feedback--success" role="status">{{ cacheMessage }}</p>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useDialog, useMessage } from 'naive-ui'

interface UiPreferences {
  compactList: boolean
  openInboxInNewTab: boolean
  refreshInterval: number
}

const preferenceKey = 'imap.ui.preferences'
const defaultPreferences: UiPreferences = {
  compactList: false,
  openInboxInNewTab: true,
  refreshInterval: 0
}

const dialog = useDialog()
const message = useMessage()
const preferences = reactive<UiPreferences>({ ...defaultPreferences })
const savedMessage = ref('')
const cacheMessage = ref('')
const localStorageCount = ref(0)
const sessionStorageCount = ref(0)
const cacheStorageCount = ref(0)

const backendBase = computed(() => `${window.location.origin}/api`)
const appVersion = computed(() => import.meta.env.VITE_APP_VERSION || 'dev')
const baseUrl = computed(() => import.meta.env.BASE_URL || '/')
const cacheSummary = computed(() => {
  return `localStorage ${localStorageCount.value} 项，sessionStorage ${sessionStorageCount.value} 项，Cache ${cacheStorageCount.value} 项`
})

function loadPreferences() {
  try {
    const raw = window.localStorage.getItem(preferenceKey)
    if (!raw) {
      return
    }

    const parsed = JSON.parse(raw) as Partial<UiPreferences>
    preferences.compactList = Boolean(parsed.compactList)
    preferences.openInboxInNewTab = parsed.openInboxInNewTab !== false
    preferences.refreshInterval = Number(parsed.refreshInterval) || 0
  } catch {
    window.localStorage.removeItem(preferenceKey)
  }
}

function savePreferences() {
  savedMessage.value = ''
  cacheMessage.value = ''

  const payload: UiPreferences = {
    compactList: preferences.compactList,
    openInboxInNewTab: preferences.openInboxInNewTab,
    refreshInterval: preferences.refreshInterval
  }

  window.localStorage.setItem(preferenceKey, JSON.stringify(payload))
  savedMessage.value = '本地 UI 偏好已保存。'
  refreshCacheState()
}

async function refreshCacheState() {
  localStorageCount.value = window.localStorage.length
  sessionStorageCount.value = window.sessionStorage.length

  if ('caches' in window) {
    const keys = await window.caches.keys()
    cacheStorageCount.value = keys.length
    return
  }

  cacheStorageCount.value = 0
}

async function clearLocalCache() {
  dialog.warning({
    title: '清理本地缓存',
    content: '确认清理本地缓存？本地 UI 偏好也会重置。',
    positiveText: '确认清理',
    negativeText: '取消',
    onPositiveClick: async () => {
      window.localStorage.clear()
      window.sessionStorage.clear()

      if ('caches' in window) {
        const keys = await window.caches.keys()
        await Promise.all(keys.map((key) => window.caches.delete(key)))
      }

      Object.assign(preferences, defaultPreferences)
      savedMessage.value = ''
      cacheMessage.value = '本地缓存已清理。'
      await refreshCacheState()
      message.success('本地缓存已清理')
    }
  })
}

onMounted(async () => {
  loadPreferences()
  await refreshCacheState()
})
</script>

<style scoped>
.settings-page {
  display: grid;
  gap: 20px;
}

.page-header,
.settings-grid,
.setting-row,
.cache-actions {
  display: flex;
  align-items: center;
}

.page-header {
  justify-content: space-between;
  gap: 16px;
}

.page-header h1,
.panel-heading h2 {
  margin: 0;
  color: var(--text-strong);
  letter-spacing: 0;
}

.page-header h1 {
  margin-top: 12px;
  font-size: clamp(28px, 4vw, 40px);
}

.page-header p,
.panel-heading p {
  margin: 8px 0 0;
}

.settings-grid {
  align-items: stretch;
  gap: 16px;
}

.section-panel {
  display: grid;
  flex: 1;
  gap: 16px;
  min-width: 0;
  padding: 20px;
}

.panel-heading {
  display: grid;
  gap: 4px;
}

.panel-heading p {
  color: var(--text-muted);
  font-size: 13px;
}

.setting-row {
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-soft);
}

.setting-row:last-of-type {
  border-bottom: 0;
}

.setting-row strong {
  display: block;
  color: var(--text-strong);
}

.setting-row small {
  display: block;
  margin-top: 4px;
  color: var(--text-muted);
  font-size: 13px;
}

.setting-row input[type='checkbox'] {
  width: 22px;
  height: 22px;
  accent-color: var(--accent);
}

.field-group {
  display: grid;
  gap: 8px;
}

.info-list {
  display: grid;
  gap: 12px;
  margin: 0;
}

.info-list div {
  display: grid;
  gap: 6px;
  padding: 12px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: var(--bg-panel-muted);
}

.info-list dt {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.info-list dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--text-strong);
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 13px;
}

.cache-actions {
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 10px;
}

.feedback {
  margin: 0;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  font-weight: 700;
}

.feedback--success {
  border: 1px solid color-mix(in srgb, var(--success) 28%, transparent);
  background: var(--bg-success-soft);
  color: var(--success);
}

@media (max-width: 860px) {
  .settings-grid,
  .setting-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
