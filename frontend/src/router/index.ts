import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layout/MainLayout.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
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

export default router
