<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Eye, EyeOff, LockKeyhole, MailCheck, Moon, ServerCog, ShieldCheck, Sun } from '@lucide/vue'
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
const showPassword = ref(false)
const errorMessage = ref('')
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
  errorMessage.value = ''
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
    errorMessage.value = error.response?.data?.detail || '登录失败，请检查账号密码'
    message.error(errorMessage.value)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="login-shell">
    <section class="login-frame" aria-label="管理员登录">
      <div class="login-visual">
        <div class="login-visual__top">
          <div class="brand-chip">
            <span class="brand-mark"><MailCheck :size="18" /></span>
            <span>IMAP Hub</span>
          </div>
          <button class="theme-toggle login-theme" type="button" :title="resolvedTheme === 'dark' ? '切换浅色模式' : '切换深色模式'" @click="toggleThemeMode">
            <component :is="resolvedTheme === 'dark' ? Sun : Moon" :size="17" />
          </button>
        </div>

        <div class="login-visual__copy">
          <span class="kicker">Secure Console</span>
          <h1>轻量邮件管理工作台</h1>
          <p>统一管理邮箱导入、同步状态、访问链接和 API Key。控制台接口已启用管理员认证。</p>
        </div>

        <div class="insight-stack" aria-hidden="true">
          <div class="insight-card">
            <ServerCog :size="18" />
            <span>后台服务</span>
            <strong>Active</strong>
          </div>
          <div class="insight-card">
            <ShieldCheck :size="18" />
            <span>Admin API</span>
            <strong>Protected</strong>
          </div>
        </div>
      </div>

      <div class="login-panel">
        <div class="login-panel__head">
          <div class="brand-lock">
            <LockKeyhole :size="22" />
          </div>
          <div>
            <h2>管理员登录</h2>
            <p>使用服务器 `.env` 中的管理员凭据。</p>
          </div>
        </div>

        <form class="login-form" autocomplete="off" @submit.prevent="submitLogin">
          <label>
            <span class="field-label">账号</span>
            <input v-model.trim="form.username" class="field-input login-input" autocomplete="username" placeholder="admin" type="text">
          </label>
          <label>
            <span class="field-label">密码</span>
            <span class="password-field">
              <input
                v-model="form.password"
                class="field-input login-input"
                autocomplete="current-password"
                placeholder="输入管理员密码"
                :type="showPassword ? 'text' : 'password'"
              >
              <button type="button" :aria-label="showPassword ? '隐藏密码' : '显示密码'" @click="showPassword = !showPassword">
                <component :is="showPassword ? EyeOff : Eye" :size="17" />
              </button>
            </span>
          </label>

          <p v-if="errorMessage" class="login-error" role="alert">{{ errorMessage }}</p>

          <button class="action-button login-submit" type="submit" :disabled="!canSubmit">
            <ShieldCheck :size="17" />
            <span>{{ loading ? '正在验证' : '进入控制台' }}</span>
          </button>
        </form>

        <div class="login-footnote">
          <span>会话仅保存在当前浏览器 sessionStorage。</span>
          <span>退出或关闭会话后需要重新登录。</span>
        </div>
      </div>
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

.login-frame {
  width: min(100%, 1040px);
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(360px, 0.92fr);
  border: 1px solid var(--border-soft);
  border-radius: 24px;
  background: var(--bg-panel);
  box-shadow: var(--shadow-panel);
  overflow: hidden;
}

.login-visual {
  position: relative;
  min-height: 620px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 34px;
  color: #effaf7;
  background:
    linear-gradient(135deg, rgba(7, 78, 68, 0.9), rgba(12, 44, 42, 0.96)),
    radial-gradient(circle at 78% 18%, rgba(45, 212, 191, 0.26), transparent 30%);
}

.login-visual::after {
  content: '';
  position: absolute;
  inset: 20px;
  pointer-events: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
}

.login-visual__top,
.brand-chip,
.insight-card,
.login-panel__head,
.password-field {
  display: flex;
  align-items: center;
}

.login-visual__top {
  position: relative;
  z-index: 1;
  justify-content: space-between;
  gap: 16px;
}

.brand-chip {
  gap: 10px;
  font-weight: 800;
}

.brand-mark,
.brand-lock {
  display: grid;
  place-items: center;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.13);
}

.login-visual__copy {
  position: relative;
  z-index: 1;
  max-width: 520px;
}

.login-visual__copy h1 {
  margin: 18px 0 14px;
  color: #ffffff;
  font-size: clamp(38px, 5vw, 58px);
  line-height: 1.04;
}

.login-visual__copy p {
  margin: 0;
  color: rgba(239, 250, 247, 0.74);
  font-size: 16px;
  line-height: 1.8;
}

.insight-stack {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.insight-card {
  min-height: 88px;
  gap: 10px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.08);
}

.insight-card span {
  color: rgba(239, 250, 247, 0.72);
  font-size: 13px;
}

.insight-card strong {
  margin-left: auto;
  color: #ffffff;
  font-size: 13px;
}

.login-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 42px;
  background: var(--bg-panel);
}

.login-panel__head {
  gap: 14px;
}

.brand-lock {
  width: 48px;
  height: 48px;
  border: 1px solid var(--border-accent);
  border-radius: 14px;
  background: var(--bg-accent-soft);
  color: var(--accent);
}

.login-panel__head h2 {
  margin: 0;
  color: var(--text-strong);
  font-size: 24px;
}

.login-panel__head p {
  margin: 5px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.login-form {
  margin-top: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.login-form label {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.login-input {
  min-height: 52px;
  border-radius: 14px;
}

.password-field {
  position: relative;
}

.password-field input {
  padding-right: 52px;
}

.password-field button {
  position: absolute;
  right: 7px;
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 12px;
  background: transparent;
  color: var(--text-muted);
}

.password-field button:hover {
  background: var(--bg-hover);
  color: var(--text-strong);
}

.login-error {
  margin: -4px 0 0;
  padding: 11px 13px;
  border: 1px solid rgba(211, 63, 73, 0.2);
  border-radius: 12px;
  background: rgba(211, 63, 73, 0.08);
  color: var(--danger);
  font-size: 13px;
  font-weight: 700;
}

.login-submit {
  width: 100%;
  min-height: 52px;
  margin-top: 6px;
  border-radius: 14px;
}

.login-theme {
  min-width: 44px;
  border-color: rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.login-footnote {
  display: grid;
  gap: 6px;
  margin-top: 22px;
  color: var(--text-muted);
  font-size: 12px;
  line-height: 1.6;
}

@media (max-width: 920px) {
  .login-frame {
    grid-template-columns: 1fr;
  }

  .login-visual {
    min-height: 360px;
  }
}

@media (max-width: 620px) {
  .login-shell {
    padding: 12px;
  }

  .login-frame {
    border-radius: 18px;
  }

  .login-visual,
  .login-panel {
    padding: 24px;
  }

  .insight-stack {
    grid-template-columns: 1fr;
  }
}
</style>
