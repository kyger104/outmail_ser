import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Inbox from './views/Inbox.vue'
import Admin from './views/Admin.vue'

// 创建路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: Inbox
    },
    {
      path: '/inbox',
      name: 'Inbox',
      component: Inbox
    },
    {
      path: '/admin',
      name: 'Admin',
      component: Admin
    }
  ]
})

// 创建应用
const app = createApp(App)
app.use(router)
app.mount('#app')
