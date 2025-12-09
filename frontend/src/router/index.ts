import { createRouter, createWebHistory } from 'vue-router'
import NotesView from '@/views/NotesView.vue'
import NoteDetailView from '@/views/NoteDetailView.vue'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import store from '@/store'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'notes',
      component: NotesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/note/:id',
      name: 'note-detail',
      component: NoteDetailView,
      props: true,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const requiresAuth = to.meta.requiresAuth !== false
  const token = localStorage.getItem('token')
  const isAuthenticated = store.getters['auth/isAuthenticated']

  // 如果路由需要认证
  if (requiresAuth) {
    // 如果有 token 但用户信息未加载，尝试加载用户信息
    if (token && !isAuthenticated) {
      try {
        await store.dispatch('auth/getCurrentUser')
        next()
      } catch (error) {
        // token 无效，跳转到登录页
        next('/login')
      }
    } else if (!token || !isAuthenticated) {
      // 没有 token 或未认证，跳转到登录页
      next('/login')
    } else {
      next()
    }
  } else {
    // 如果已经登录，访问登录/注册页时跳转到首页
    if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
      next('/')
    } else {
      next()
    }
  }
})

export default router

