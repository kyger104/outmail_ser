import { ref, onMounted, onUnmounted } from 'vue'

export function useAutoRefresh(callback: () => void, interval = 30000) {
  const timer = ref<number | null>(null)
  const countdown = ref(interval / 1000)
  const isRefreshing = ref(false)

  const start = () => {
    if (timer.value) return

    // 立即执行一次
    executeCallback()

    // 设置定时器
    timer.value = window.setInterval(() => {
      executeCallback()
    }, interval)

    // 倒计时
    setInterval(() => {
      if (countdown.value > 0) {
        countdown.value--
      } else {
        countdown.value = interval / 1000
      }
    }, 1000)
  }

  const stop = () => {
    if (timer.value) {
      clearInterval(timer.value)
      timer.value = null
    }
  }

  const executeCallback = async () => {
    isRefreshing.value = true
    try {
      await callback()
    } finally {
      isRefreshing.value = false
      countdown.value = interval / 1000
    }
  }

  const manualRefresh = () => {
    executeCallback()
  }

  onMounted(start)
  onUnmounted(stop)

  return {
    countdown,
    isRefreshing,
    manualRefresh,
    start,
    stop
  }
}
