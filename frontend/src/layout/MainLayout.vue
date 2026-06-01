<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Activity,
  BarChart3,
  Database,
  Download,
  Home,
  Inbox,
  KeyRound,
  LogOut,
  Mail,
  Menu,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  RefreshCw,
  Settings,
  Sun,
  Upload,
  X
} from '@lucide/vue'
import api from '../utils/api'
import { clearAdminCredentials } from '../utils/adminAuth'
import { useThemeControls } from '../composables/useThemeControls'
import type { AdminStats } from '../types'
import type { ThemeMode } from '../utils/themePreference'

const route = useRoute()
const router = useRouter()
const collapsed = ref(localStorage.getItem('imap_sidebar_collapsed') === 'true')
const mobileOpen = ref(false)
const health = ref<'checking' | 'ok' | 'error'>('checking')
const mailboxCount = ref(0)
const errorCount = ref(0)
const { themeMode, resolvedTheme, setThemeMode } = useThemeControls()

const navItems = [
  { name: 'Dashboard', label: '控制台', path: '/', icon: Home },
  { name: 'Admin', label: '邮箱管理', path: '/admin', icon: Database },
  { name: 'Import', label: '批量导入', path: '/import', icon: Upload },
  { name: 'ApiKeys', label: 'API Keys', path: '/api-keys', icon: KeyRound },
  { name: 'Stats', label: '统计数据', path: '/stats', icon: BarChart3 },
  { name: 'Settings', label: '系统设置', path: '/settings', icon: Settings }
]

const currentTitle = computed(() => navItems.find((item) => item.name === route.name)?.label ?? '工作区')
const statusLabel = computed(() => {
  if (health.value === 'ok') return '后端已连接'
  if (health.value === 'error') return '后端异常'
  return '检查连接'
})
const themeLabel = computed(() => {
  if (themeMode.value === 'auto') return resolvedTheme.value === 'dark' ? '跟随系统：深色' : '跟随系统：浅色'
  return themeMode.value === 'dark' ? '深色模式' : '浅色模式'
})

function setCollapsed(value: boolean) {
  collapsed.value = value
  localStorage.setItem('imap_sidebar_collapsed', String(value))
}

function openPath(path: string) {
  mobileOpen.value = false
  router.push(path)
}

function toggleThemeMode() {
  const nextMode: ThemeMode = resolvedTheme.value === 'dark' ? 'light' : 'dark'
  setThemeMode(nextMode)
}

function logout() {
  clearAdminCredentials()
  router.replace({ name: 'Login' })
}

async function refreshShell() {
  health.value = 'checking'
  try {
    await api.get('/health', { baseURL: '' })
    health.value = 'ok'
  } catch {
    health.value = 'error'
  }

  try {
    const stats = await api.get<AdminStats>('/admin/stats')
    mailboxCount.value = stats.total_mailboxes ?? 0
    errorCount.value = stats.error_mailboxes ?? 0
  } catch {
    mailboxCount.value = 0
    errorCount.value = 0
  }
}

onMounted(() => {
  void refreshShell()
})
</script>

<template>
  <div class="workspace-shell">
    <aside class="workspace-sidebar surface-panel" :class="{ 'workspace-sidebar--collapsed': collapsed }">
      <div class="sidebar-brand">
        <button class="brand-mark" type="button" title="回到控制台" @click="openPath('/')">
          <Mail :size="18" />
        </button>
        <div v-if="!collapsed" class="brand-copy">
          <strong>IMAP Hub</strong>
          <span>邮件托管工作区</span>
        </div>
        <button class="sidebar-toggle desktop-only" type="button" :title="collapsed ? '展开侧边栏' : '折叠侧边栏'" @click="setCollapsed(!collapsed)">
          <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="16" />
        </button>
      </div>

      <nav class="sidebar-body" aria-label="主导航">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="nav-item"
          :class="{ 'nav-item--active': route.name === item.name }"
          type="button"
          :title="item.label"
          @click="openPath(item.path)"
        >
          <span class="nav-item__main">
            <component :is="item.icon" :size="18" />
            <span v-if="!collapsed">{{ item.label }}</span>
          </span>
          <span v-if="!collapsed && item.name === 'Admin'" class="nav-item__count">{{ mailboxCount }}</span>
        </button>
      </nav>

      <div class="sidebar-footer" :class="{ 'sidebar-footer--compact': collapsed }">
        <div v-if="!collapsed" class="sidebar-footer__account">
          <strong>{{ mailboxCount }} 个邮箱</strong>
          <span>{{ errorCount }} 个异常需要处理</span>
        </div>
        <button class="ghost-button sidebar-footer__refresh" type="button" title="刷新状态" @click="refreshShell">
          <RefreshCw :size="16" />
        </button>
      </div>
    </aside>

    <div class="workspace-main">
      <header class="workspace-topbar surface-panel">
        <div class="topbar-start">
          <button class="topbar-icon mobile-only" type="button" title="打开导航" @click="mobileOpen = true">
            <Menu :size="18" />
          </button>
          <div class="topbar-copy">
            <div class="kicker">邮箱管理</div>
            <div class="topbar-title">{{ currentTitle }}</div>
          </div>
        </div>

        <div class="topbar-actions">
          <div class="glow-pill" :class="{ 'glow-pill--danger': health === 'error' }">
            <Activity :size="14" />
            <span>{{ statusLabel }}</span>
          </div>
          <button class="theme-toggle" type="button" :title="themeLabel" :aria-label="themeLabel" @click="toggleThemeMode">
            <component :is="resolvedTheme === 'dark' ? Sun : Moon" :size="17" />
            <span class="desktop-only">{{ resolvedTheme === 'dark' ? '浅色' : '深色' }}</span>
          </button>
          <button class="topbar-icon" type="button" title="退出登录" aria-label="退出登录" @click="logout">
            <LogOut :size="17" />
          </button>
          <button class="ghost-button desktop-only" type="button" @click="openPath('/admin')">
            <Inbox :size="16" />
            <span>邮箱列表</span>
          </button>
          <button class="action-button desktop-only" type="button" @click="openPath('/import')">
            <Download :size="16" />
            <span>导入邮箱</span>
          </button>
        </div>
      </header>

      <main class="workspace-content">
        <router-view />
      </main>
    </div>

    <Teleport to="body">
      <Transition name="drawer-fade">
        <div v-if="mobileOpen" class="mobile-drawer-wrap">
          <div class="mobile-drawer-mask" @click="mobileOpen = false"></div>
          <aside class="mobile-drawer surface-panel">
            <div class="mobile-drawer__header">
              <div>
                <strong>IMAP Hub</strong>
                <span>导航</span>
              </div>
              <button class="topbar-icon" type="button" title="关闭导航" @click="mobileOpen = false">
                <X :size="18" />
              </button>
            </div>
            <div class="mobile-drawer__body">
              <button
                v-for="item in navItems"
                :key="`mobile-${item.name}`"
                class="nav-item"
                :class="{ 'nav-item--active': route.name === item.name }"
                type="button"
                @click="openPath(item.path)"
              >
                <span class="nav-item__main">
                  <component :is="item.icon" :size="18" />
                  <span>{{ item.label }}</span>
                </span>
              </button>
            </div>
          </aside>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.workspace-shell {
  display: flex;
  min-height: 100vh;
  gap: 18px;
  padding: 18px;
}

.workspace-sidebar {
  width: var(--sidebar-width);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-xl);
  overflow: hidden;
}

.workspace-sidebar--collapsed {
  width: var(--sidebar-collapsed);
}

.sidebar-brand,
.sidebar-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid var(--border-soft);
}

.sidebar-footer {
  border-top: 1px solid var(--border-soft);
  border-bottom: none;
  margin-top: auto;
}

.brand-mark,
.topbar-icon,
.sidebar-toggle,
.theme-toggle {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--border-strong);
  background: var(--bg-accent-soft);
  color: var(--accent);
  display: grid;
  place-items: center;
}

.brand-copy,
.sidebar-footer__account {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.brand-copy strong,
.sidebar-footer__account strong,
.mobile-drawer__header strong {
  color: var(--text-strong);
  font-size: 15px;
}

.brand-copy span,
.sidebar-footer__account span,
.mobile-drawer__header span {
  color: var(--text-muted);
  font-size: 12px;
}

.sidebar-toggle {
  margin-left: auto;
}

.sidebar-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item {
  width: 100%;
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 46px;
  padding: 0 14px;
  border-radius: 14px;
  transition: background 0.18s ease, border-color 0.18s ease, color 0.18s ease;
}

.nav-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-accent);
  color: var(--text-strong);
}

.nav-item--active {
  background: linear-gradient(135deg, rgba(70, 194, 255, 0.14), rgba(247, 185, 85, 0.1));
  border-color: rgba(70, 194, 255, 0.24);
  color: var(--text-strong);
}

.nav-item__main {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.nav-item__count {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 700;
}

.sidebar-footer--compact {
  justify-content: center;
}

.sidebar-footer__refresh {
  min-width: 44px;
  padding: 0;
}

.workspace-main {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.workspace-topbar {
  min-height: 92px;
  padding: 18px 22px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}

.topbar-start,
.topbar-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.topbar-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.topbar-copy {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.topbar-title {
  color: var(--text-strong);
  font-size: 20px;
  font-weight: 800;
}

.glow-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(57, 217, 138, 0.2);
  background: rgba(57, 217, 138, 0.08);
  color: var(--success);
  font-size: 12px;
  font-weight: 600;
}

.glow-pill--danger {
  border-color: rgba(255, 107, 122, 0.2);
  background: rgba(255, 107, 122, 0.08);
  color: var(--danger);
}

.theme-toggle {
  display: inline-flex;
  width: auto;
  min-width: 44px;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  font-weight: 700;
}

.mobile-only {
  display: none;
}

.mobile-drawer-wrap {
  position: fixed;
  inset: 0;
  z-index: 50;
}

.mobile-drawer-mask {
  position: absolute;
  inset: 0;
  background: rgba(3, 10, 18, 0.68);
  backdrop-filter: blur(8px);
}

.mobile-drawer {
  position: relative;
  z-index: 1;
  width: min(88vw, 360px);
  height: 100%;
  padding: 20px;
  border-radius: 0 28px 28px 0;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.mobile-drawer__header,
.mobile-drawer__body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-drawer__header {
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

@media (max-width: 1100px) {
  .workspace-shell {
    padding: 14px;
  }

  .workspace-sidebar {
    display: none;
  }

  .workspace-topbar {
    padding: 16px;
  }

  .mobile-only {
    display: inline-flex;
  }

  .desktop-only {
    display: none;
  }
}

@media (max-width: 720px) {
  .workspace-shell {
    padding: 10px;
    gap: 10px;
  }

  .workspace-topbar {
    min-height: 78px;
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
