import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    redirect: '/edit'
  },
  {
    path: '/edit',
    name: 'edit',
    component: () => import('../views/EditView.vue'),
    meta: { title: '이미지 편집' }
  },
  {
    path: '/style',
    name: 'style',
    component: () => import('../views/StyleView.vue'),
    meta: { title: '스타일 변환' }
  },
  {
    path: '/batch',
    name: 'batch',
    component: () => import('../views/BatchView.vue'),
    meta: { title: '배치 처리' }
  },
  {
    path: '/history',
    name: 'history',
    component: () => import('../views/HistoryView.vue'),
    meta: { title: '히스토리' }
  },
  {
    path: '/gallery',
    name: 'gallery',
    component: () => import('../views/GalleryView.vue'),
    meta: { title: '갤러리' }
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { title: '설정' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'Qwen Image Edit'} - Qwen Image Edit`
  next()
})

export default router
