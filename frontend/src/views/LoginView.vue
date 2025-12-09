<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>AI 笔记</h1>
        <p>登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="请输入用户名"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="请输入密码"
            required
            autocomplete="current-password"
          />
        </div>

        <transition name="fade">
          <div v-if="error" class="error-message">{{ error }}</div>
        </transition>

        <button type="submit" class="btn-login" :disabled="loading">
          {{ loading ? '登录中...' : '登录' }}
        </button>

        <div class="form-footer">
          <span>还没有账户？</span>
          <router-link to="/register" class="link">立即注册</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'

const router = useRouter()
const store = useStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await store.dispatch('auth/login', {
      username: username.value,
      password: password.value
    })
    router.push('/')
  } catch (err: any) {
    // 从错误响应中提取错误信息
    console.log('登录错误:', err)
    console.log('错误响应:', err?.response)
    console.log('错误数据:', err?.response?.data)
    
    let errorMessage = '登录失败，请重试'
    
    if (err?.response?.data?.detail) {
      const detail = err.response.data.detail
      // 如果 detail 是数组，提取第一个错误信息
      if (Array.isArray(detail) && detail.length > 0) {
        const firstError = detail[0]
        if (typeof firstError === 'string') {
          errorMessage = firstError
        } else if (firstError?.msg) {
          errorMessage = firstError.msg
        } else if (firstError?.loc && firstError?.msg) {
          errorMessage = `${firstError.loc.join('.')}: ${firstError.msg}`
        }
      } else if (typeof detail === 'string') {
        errorMessage = detail
      }
    } else if (err?.response?.data?.message) {
      errorMessage = err.response.data.message
    } else if (err?.message) {
      errorMessage = err.message
    }
    
    error.value = errorMessage
    console.log('设置的错误信息:', error.value)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.login-card {
  background: rgba(30, 38, 64, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 24px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    0 0 0 1px rgba(120, 119, 198, 0.15);
  padding: 48px;
  width: 100%;
  max-width: 420px;
  position: relative;
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent,
    rgba(120, 119, 198, 0.5),
    transparent
  );
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 50%, #78dbff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.login-header p {
  color: rgba(226, 232, 240, 0.7);
  font-size: 16px;
  font-weight: 400;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(226, 232, 240, 0.8);
  margin-bottom: 4px;
}

.form-group input {
  padding: 14px 18px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(120, 119, 198, 0.2);
  border-radius: 12px;
  font-size: 16px;
  color: #e2e8f0;
  transition: all 0.3s;
  outline: none;
}

.form-group input::placeholder {
  color: rgba(226, 232, 240, 0.4);
}

.form-group input:focus {
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(15, 23, 42, 0.8);
  box-shadow: 
    0 0 0 3px rgba(120, 119, 198, 0.1),
    0 0 20px rgba(120, 119, 198, 0.2);
}

.error-message {
  padding: 14px;
  background: rgba(220, 38, 38, 0.2);
  border: 1px solid rgba(220, 38, 38, 0.4);
  color: #fca5a5;
  border-radius: 12px;
  font-size: 14px;
  text-align: center;
  backdrop-filter: blur(10px);
}

.btn-login {
  padding: 16px;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 8px;
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 15px rgba(120, 119, 198, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-login::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.btn-login:hover:not(:disabled)::before {
  left: 100%;
}

.btn-login:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(120, 119, 198, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 24px;
  color: rgba(226, 232, 240, 0.6);
  font-size: 14px;
}

.form-footer .link {
  color: #7877c6;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
  transition: all 0.3s;
  position: relative;
}

.form-footer .link::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(90deg, #7877c6, #ff77c6);
  transition: width 0.3s;
}

.form-footer .link:hover::after {
  width: 100%;
}

.form-footer .link:hover {
  color: #ff77c6;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

