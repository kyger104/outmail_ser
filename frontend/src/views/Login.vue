<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { LockKeyhole, Moon, ShieldCheck, Sun } from '@lucide/vue'
import { useMessage } from 'naive-ui'
import api from '../utils/api'
import { buildBasicAuthHeader, saveAdminCredentials } from '../utils/adminAuth'
import { useThemeControls } from '../composables/useThemeControls'
import type { ThemeMode } from '../utils/themePreference'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const { resolvedTheme, setThemeMode } = useThemeControls()
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const canSubmit = computed(() => form.username.trim().length > 0 && form.password.length > 0 && !loading.value)

function toggleThemeMode() {
  const nextMode: ThemeMode = resolvedTheme.value === 'dark' ? 'light' : 'dark'
  setThemeMode(nextMode)
}

async function submitLogin() {
  if (!canSubmit.value) return
  loading.value = true
  const credentials = {
    username: form.username.trim(),
    password: form.password
  }
  try {
    await api.get('/admin/stats', {
      headers: {
        Authorization: buildBasicAuthHeader(credentials)
      }
    })
    saveAdminCredentials(credentials)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.replace(redirect)
  } catch (error: any) {
    message.error(error.response?.data?.detail || '登录失败，请检查账号密码')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-shell">
    <section class="login-panel">
      <div class="login-panel__head">
        <div class="brand-lock">
          <LockKeyhole :size="22" />
        </div>
        <button class="theme-toggle login-theme" type="button" :title="resolvedTheme === 'dark' ? '切换浅色模式' : '切换深色模式'" @click="toggleThemeMode">
          <component :is="resolvedTheme === 'dark' ? Sun : Moon" :size="17" />
        </button>
      </div>

      <div class="login-copy">
        <span class="kicker">控制台保护</span>
        <h1>管理员登录</h1>
        <p>输入服务器环境变量中的管理员账号密码后，才能查看邮箱列表、导入记录和统计数据。</p>
      </div>

      <form class="login-form" autocomplete="off" @submit.prevent="submitLogin">
        <label>
          <span class="field-label">账号</span>
          <input v-model.trim="form.username" class="field-input" autocomplete="username" placeholder="admin" type="text">
        </label>
        <label>
          <span class="field-label">密码</span>
          <input v-model="form.password" class="field-input" autocomplete="current-password" placeholder="请输入密码" type="password">
        </label>
        <button class="action-button login-submit" type="submit" :disabled="!canSubmit">
          <ShieldCheck :size="17" />
          <span>{{ loading ? '验证中' : '进入控制台' }}</span>
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.login-shell {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

.login-panel {
  width: min(100%, 440px);
  padding: 28px;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: var(--bg-panel);
  box-shadow: var(--shadow-panel);
}

.login-panel__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.brand-lock {
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border-accent);
  border-radius: 14px;
  background: var(--bg-accent-soft);
  color: var(--accent);
}

.login-copy {
  margin: 24px 0;
}

.login-copy h1 {
  margin: 14px 0 8px;
  color: var(--text-strong);
  font-size: 30px;
  line-height: 1.16;
}

.login-copy p {
  margin: 0;
  color: var(--text-muted);
  line-height: 1.7;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.login-submit {
  width: 100%;
  margin-top: 6px;
}

.login-theme {
  min-width: 44px;
}
</style>
