import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'
import { hasAdminCredentials } from '../utils/adminAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAdmin: true },
      children: [
        { path: '', name: 'Dashboard', component: () => import('../views/Dashboard.vue') },
        { path: 'admin', name: 'Admin', component: () => import('../views/Admin.vue') },
        { path: 'import', name: 'Import', component: () => import('../views/Import.vue') },
        { path: 'api-keys', name: 'ApiKeys', component: () => import('../views/ApiKeys.vue') },
        { path: 'stats', name: 'Stats', component: () => import('../views/Stats.vue') },
        { path: 'settings', name: 'Settings', component: () => import('../views/Settings.vue') }
      ]
    },
    {
      path: '/inbox',
      name: 'Inbox',
      component: () => import('../views/Inbox.vue')
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAdmin && !hasAdminCredentials()) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'Login' && hasAdminCredentials()) {
    return { path: '/' }
  }
  return true
})

export default router
