<template>
  <main class="page-shell settings-page">
    <header class="page-header">
      <div>
        <h1>设置</h1>
      </div>
    </header>

    <nav class="settings-tabs" aria-label="设置分类">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-button"
        :class="{ 'tab-button--active': activeTab === tab.id }"
        type="button"
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </nav>

    <ApiKeysPanel v-if="activeTab === 'apiKeys'" />

    <section v-else-if="activeTab === 'cache'" class="shell-card section-panel">
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

    <section v-else class="shell-card section-panel">
      <div class="panel-heading">
        <h2>运行信息</h2>
        <p>用于排查部署环境，不包含敏感凭据。</p>
      </div>

      <dl class="info-list info-list--compact">
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
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useDialog, useMessage } from 'naive-ui'
import ApiKeysPanel from './ApiKeys.vue'

const dialog = useDialog()
const message = useMessage()
const cacheMessage = ref('')
const localStorageCount = ref(0)
const sessionStorageCount = ref(0)
const cacheStorageCount = ref(0)
const activeTab = ref<'apiKeys' | 'cache' | 'runtime'>('apiKeys')
const tabs = [
  { id: 'apiKeys', label: 'API Key' },
  { id: 'cache', label: '本地缓存' },
  { id: 'runtime', label: '运行信息' }
] as const

const backendBase = computed(() => `${window.location.origin}/api`)
const appVersion = computed(() => import.meta.env.VITE_APP_VERSION || 'dev')
const baseUrl = computed(() => import.meta.env.BASE_URL || '/')
const cacheSummary = computed(() => {
  return `localStorage ${localStorageCount.value} 项，sessionStorage ${sessionStorageCount.value} 项，Cache ${cacheStorageCount.value} 项`
})

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
    content: '确认清理 localStorage、sessionStorage 和 Cache？清理后需要重新登录。',
    positiveText: '确认清理',
    negativeText: '取消',
    onPositiveClick: async () => {
      window.localStorage.clear()
      window.sessionStorage.clear()

      if ('caches' in window) {
        const keys = await window.caches.keys()
        await Promise.all(keys.map((key) => window.caches.delete(key)))
      }

      cacheMessage.value = '本地缓存已清理。'
      await refreshCacheState()
      message.success('本地缓存已清理')
    }
  })
}

onMounted(async () => {
  await refreshCacheState()
})
</script>

<style scoped>
.settings-page {
  display: grid;
  gap: 12px;
}

.page-header,
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
  font-size: 22px;
}

.page-header p,
.panel-heading p {
  margin: 8px 0 0;
}

.section-panel {
  display: grid;
  flex: 1;
  gap: 12px;
  min-width: 0;
  padding: 16px;
}

.settings-tabs {
  position: sticky;
  top: 76px;
  z-index: 10;
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 6px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: var(--bg-panel);
  box-shadow: var(--shadow-panel);
}

.tab-button {
  min-height: 34px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-main);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.tab-button:hover,
.tab-button--active {
  border-color: var(--border-accent);
  background: var(--bg-accent-soft);
  color: var(--text-strong);
}

.panel-heading {
  display: grid;
  gap: 4px;
}

.panel-heading p {
  color: var(--text-muted);
  font-size: 13px;
}

.info-list {
  display: grid;
  gap: 8px;
  margin: 0;
}

.info-list--compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.info-list div {
  display: grid;
  gap: 4px;
  padding: 10px;
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
  .settings-tabs {
    top: 68px;
  }

  .info-list--compact {
    grid-template-columns: 1fr;
  }
}
</style>
