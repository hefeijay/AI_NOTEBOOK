<template>
  <div class="notes-view">
    <header class="header">
      <div class="header-left">
        <h1>AI笔记应用</h1>
      </div>
      <div class="header-right">
        <div class="user-info" v-if="user">
          <span class="username">{{ user.username }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </div>
        <button class="btn-primary" @click="handleCreateNote">新建笔记</button>
      </div>
    </header>

    <div class="notes-container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="notes.length === 0" class="empty">
        <p>还没有笔记，点击"新建笔记"开始吧！</p>
      </div>
      <div v-else class="notes-list">
        <div
          v-for="note in notes"
          :key="note.id"
          class="note-card"
          @click="goToNote(note.id)"
        >
          <h3 class="note-title">{{ note.title || '无标题' }}</h3>
          <p class="note-preview">{{ getPreview(note.content) }}</p>
          <span class="note-date">{{ formatDate(note.updatedAt) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import type { Note } from '@/types'

const router = useRouter()
const store = useStore()

const notes = computed(() => store.getters['notes/notes'])
const loading = computed(() => store.getters['notes/loading'])
const error = computed(() => store.getters['notes/error'])
const user = computed(() => store.getters['auth/user'])

onMounted(async () => {
  // 如果有 token，尝试加载用户信息
  const token = localStorage.getItem('token')
  if (token && !user.value) {
    try {
      await store.dispatch('auth/getCurrentUser')
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  }
  store.dispatch('notes/fetchNotes')
})

const handleLogout = () => {
  store.dispatch('auth/logout')
  router.push('/login')
}

const handleCreateNote = async () => {
  try {
    const note = await store.dispatch('notes/createNote', {
      title: '新笔记',
      content: ''
    })
    router.push(`/note/${note.id}`)
  } catch (err) {
    console.error('创建笔记失败:', err)
  }
}

const goToNote = (id: string) => {
  router.push(`/note/${id}`)
}

const getPreview = (content: string): string => {
  if (!content) return '暂无内容'
  return content.length > 100 ? content.substring(0, 100) + '...' : content
}

const formatDate = (dateString: string): string => {
  // 如果时间字符串没有时区信息，假设它是UTC时间
  let dateStr = dateString
  if (!dateStr.endsWith('Z') && !dateStr.includes('+') && !dateStr.includes('-', 10)) {
    // 没有时区标记，添加Z表示UTC
    dateStr = dateStr + 'Z'
  }
  
  const date = new Date(dateStr)
  
  // 使用北京时间（UTC+8）显示
  return date.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.notes-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
  padding: 24px 32px;
  background: rgba(30, 38, 64, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header h1 {
  font-size: 32px;
  font-weight: 800;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 50%, #78dbff 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  letter-spacing: -0.5px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.username {
  color: rgba(226, 232, 240, 0.8);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(120, 119, 198, 0.2);
  border-radius: 12px;
  border: 1px solid rgba(120, 119, 198, 0.3);
}

.btn-logout {
  background: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(220, 38, 38, 0.3);
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: rgba(220, 38, 38, 0.3);
  border-color: rgba(220, 38, 38, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-primary {
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 
    0 4px 15px rgba(120, 119, 198, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
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

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(120, 119, 198, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.notes-container {
  min-height: 400px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 80px 20px;
  color: rgba(226, 232, 240, 0.6);
  font-size: 18px;
}

.error {
  color: #fca5a5;
}

.notes-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.note-card {
  background: rgba(30, 38, 64, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 20px;
  padding: 28px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.note-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, 
    transparent,
    rgba(120, 119, 198, 0.5),
    transparent
  );
  opacity: 0;
  transition: opacity 0.3s;
}

.note-card:hover {
  transform: translateY(-8px);
  border-color: rgba(120, 119, 198, 0.6);
  box-shadow: 
    0 16px 48px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(120, 119, 198, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.note-card:hover::before {
  opacity: 1;
}

.note-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  letter-spacing: -0.3px;
}

.note-preview {
  color: rgba(226, 232, 240, 0.6);
  font-size: 14px;
  line-height: 1.7;
  margin-bottom: 16px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-date {
  font-size: 12px;
  color: rgba(226, 232, 240, 0.4);
  font-weight: 500;
}

@media (max-width: 768px) {
  .notes-view {
    padding: 15px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header h1 {
    font-size: 24px;
  }

  .notes-list {
    grid-template-columns: 1fr;
  }
}
</style>

