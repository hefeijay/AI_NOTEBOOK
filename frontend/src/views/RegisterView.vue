<template>
  <div class="register-container">
    <div class="register-card">
      <div class="register-header">
        <h1>AI 笔记</h1>
        <p>创建新账户</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="至少3个字符"
            required
            minlength="3"
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="至少6个字符"
            required
            minlength="6"
            autocomplete="new-password"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            required
            autocomplete="new-password"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" class="btn-register" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>

        <div class="form-footer">
          <span>已有账户？</span>
          <router-link to="/login" class="link">立即登录</router-link>
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
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  error.value = ''

  if (!username.value || !password.value || !confirmPassword.value) {
    error.value = '请填写所有字段'
    return
  }

  if (username.value.length < 3) {
    error.value = '用户名至少需要3个字符'
    return
  }

  if (password.value.length < 6) {
    error.value = '密码至少需要6个字符'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }

  loading.value = true

  try {
    await store.dispatch('auth/register', {
      username: username.value,
      password: password.value
    })
    router.push('/')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '注册失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.register-card {
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

.register-card::before {
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

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.register-header h1 {
  font-size: 36px;
  font-weight: 800;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 50%, #78dbff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.register-header p {
  color: rgba(226, 232, 240, 0.7);
  font-size: 16px;
  font-weight: 400;
}

.register-form {
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
  background: rgba(30, 38, 64, 0.7);
  border: 1px solid rgba(120, 119, 198, 0.3);
  border-radius: 12px;
  font-size: 16px;
  color: #e2e8f0;
  transition: all 0.3s;
  outline: none;
}

.form-group input::placeholder {
  color: rgba(226, 232, 240, 0.5);
}

.form-group input:focus {
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(30, 38, 64, 0.9);
  box-shadow: 
    0 0 0 3px rgba(120, 119, 198, 0.15),
    0 0 20px rgba(120, 119, 198, 0.25);
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

.btn-register {
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

.btn-register::before {
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

.btn-register:hover:not(:disabled)::before {
  left: 100%;
}

.btn-register:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(120, 119, 198, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-register:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-footer {
  text-align: center;
  margin-top: 16px;
  color: #718096;
  font-size: 14px;
}

.form-footer .link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  margin-left: 4px;
}

.form-footer .link:hover {
  text-decoration: underline;
}
</style>

