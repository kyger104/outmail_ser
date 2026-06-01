<template>
  <n-config-provider :theme="resolvedTheme === 'dark' ? darkTheme : null" :theme-overrides="themeOverrides" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-dialog-provider>
        <router-view />
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, provide, ref } from 'vue'
import { darkTheme, dateZhCN, NConfigProvider, NDialogProvider, NMessageProvider, zhCN } from 'naive-ui'
import { darkThemeOverrides, lightThemeOverrides } from './theme'
import { getStoredThemeMode, resolveThemeMode, storeThemeMode, type ResolvedThemeMode, type ThemeMode } from './utils/themePreference'

const themeMode = ref<ThemeMode>(getStoredThemeMode())
const prefersDark = ref(false)
let mediaQuery: MediaQueryList | undefined

const resolvedTheme = computed<ResolvedThemeMode>(() => resolveThemeMode(themeMode.value, prefersDark.value))
const themeOverrides = computed(() => resolvedTheme.value === 'dark' ? darkThemeOverrides : lightThemeOverrides)

provide('themeControls', { themeMode, resolvedTheme, setThemeMode })

function syncDocumentTheme() {
  document.documentElement.dataset.theme = resolvedTheme.value
  document.documentElement.style.colorScheme = resolvedTheme.value
}

function setThemeMode(mode: ThemeMode) {
  themeMode.value = mode
  storeThemeMode(mode)
  syncDocumentTheme()
}

function handlePreferenceChange(event: MediaQueryListEvent) {
  prefersDark.value = event.matches
  syncDocumentTheme()
}

onMounted(() => {
  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  prefersDark.value = mediaQuery.matches
  syncDocumentTheme()
  mediaQuery.addEventListener('change', handlePreferenceChange)
})

onBeforeUnmount(() => {
  mediaQuery?.removeEventListener('change', handlePreferenceChange)
})
</script>
