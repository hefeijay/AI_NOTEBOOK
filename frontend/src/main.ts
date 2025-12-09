import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './style.css'

const app = createApp(App)

app.use(store)
app.use(router)

// 初始化：如果有 token，尝试加载用户信息
const token = localStorage.getItem('token')
if (token) {
  store.dispatch('auth/getCurrentUser').catch(() => {
    // token 无效，清除
    localStorage.removeItem('token')
  })
}

app.mount('#app')

