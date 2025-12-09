import axios from 'axios'
import type { Note, CreateNoteDto, UpdateNoteDto } from '@/types'
import { API_BASE_URL } from '@/utils/config'

const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加 token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理 401 错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // 如果是登录/注册页面的 401 错误，不要跳转，让页面自己处理错误
    const isAuthPage = window.location.pathname === '/login' || window.location.pathname === '/register'
    
    if (error.response?.status === 401 && !isAuthPage) {
      // token 过期或无效，清除 token 并跳转到登录页
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    // 其他错误直接抛出，让调用方处理
    return Promise.reject(error)
  }
)

export const notesApi = {
  // 获取所有笔记
  getAllNotes: async (): Promise<Note[]> => {
    const response = await api.get<Note[]>('/notes')
    return response.data
  },

  // 获取单个笔记
  getNote: async (id: string): Promise<Note> => {
    const response = await api.get<Note>(`/notes/${id}`)
    return response.data
  },

  // 创建笔记
  createNote: async (data: CreateNoteDto): Promise<Note> => {
    const response = await api.post<Note>('/notes', data)
    return response.data
  },

  // 更新笔记
  updateNote: async (id: string, data: UpdateNoteDto): Promise<Note> => {
    const response = await api.put<Note>(`/notes/${id}`, data)
    return response.data
  },

  // 删除笔记
  deleteNote: async (id: string): Promise<void> => {
    await api.delete(`/notes/${id}`)
  }
}

export const authApi = {
  // 用户注册
  register: async (username: string, password: string) => {
    const response = await api.post('/auth/register', { username, password })
    return response.data
  },

  // 用户登录
  login: async (username: string, password: string) => {
    // OAuth2PasswordRequestForm 需要 application/x-www-form-urlencoded 格式
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)
    
    const response = await api.post('/auth/login', params, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })
    return response.data
  },

  // 获取当前用户信息
  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  }
}

export const aiApi = {
  // 处理文本（流式）
  processText: async function* (
    text: string,
    noteId?: string
  ): AsyncGenerator<string, void, unknown> {
    const token = localStorage.getItem('token')
    const headers: HeadersInit = {
      'Content-Type': 'application/json'
    }
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE_URL}/api/ai/process`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ text, note_id: noteId })
    })

    if (!response.body) {
      throw new Error('Response body is null')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              return
            }
            try {
              const parsed = JSON.parse(data)
              if (parsed.content) {
                yield parsed.content
              } else if (parsed.error) {
                // 处理错误信息
                throw new Error(parsed.error)
              }
            } catch (parseError) {
              // 如果是错误信息，抛出异常
              if (parseError instanceof Error) {
                throw parseError
              }
              // 其他解析错误忽略
              console.warn('解析SSE数据失败:', data)
            }
          }
        }
      }
    } finally {
      reader.releaseLock()
    }
  }
}

