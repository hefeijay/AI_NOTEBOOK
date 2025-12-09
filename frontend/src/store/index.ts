import { createStore } from 'vuex'
import notesModule from './modules/notes'
import aiModule from './modules/ai'
import authModule from './modules/auth'
import { wsService } from '@/services/websocket'

const store = createStore({
  modules: {
    notes: notesModule,
    ai: aiModule,
    auth: authModule
  }
})

// WebSocket事件监听
wsService.on('note_update', (data) => {
  const note = data as { id: string; title: string; content: string; createdAt: string; updatedAt: string }
  store.commit('notes/UPDATE_NOTE', note)
})

wsService.on('note_create', (data) => {
  const note = data as { id: string; title: string; content: string; createdAt: string; updatedAt: string }
  store.commit('notes/ADD_NOTE', note)
})

wsService.on('note_delete', (data) => {
  const payload = data as { id: string }
  store.commit('notes/DELETE_NOTE', payload.id)
})

// 初始化WebSocket连接
wsService.connect()

export default store

