import { Module } from 'vuex'
import { authApi } from '@/services/api'

interface User {
  id: string
  username: string
  createdAt: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const authModule: Module<AuthState, unknown> = {
  namespaced: true,

  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
    loading: false,
    error: null
  }),

  mutations: {
    SET_LOADING(state: AuthState, loading: boolean) {
      state.loading = loading
    },

    SET_ERROR(state: AuthState, error: string | null) {
      state.error = error
    },

    SET_TOKEN(state: AuthState, token: string | null) {
      state.token = token
      if (token) {
        localStorage.setItem('token', token)
      } else {
        localStorage.removeItem('token')
      }
    },

    SET_USER(state: AuthState, user: User | null) {
      state.user = user
      state.isAuthenticated = !!user
    },

    LOGOUT(state: AuthState) {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      localStorage.removeItem('token')
    }
  },

  actions: {
    async login({ commit }, { username, password }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const response = await authApi.login(username, password)
        commit('SET_TOKEN', response.access_token)
        
        // 获取用户信息
        const user = await authApi.getCurrentUser()
        commit('SET_USER', user)
        
        return user
      } catch (error: any) {
        // 从错误响应中提取详细错误信息
        let message = '登录失败'
        if (error?.response?.data?.detail) {
          message = error.response.data.detail
        } else if (error instanceof Error) {
          message = error.message
        }
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async register({ commit }, { username, password }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const user = await authApi.register(username, password)
        // 注册成功后自动登录
        const response = await authApi.login(username, password)
        commit('SET_TOKEN', response.access_token)
        commit('SET_USER', user)
        return user
      } catch (error) {
        const message = error instanceof Error ? error.message : '注册失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async getCurrentUser({ commit, state }) {
      if (!state.token) {
        return null
      }
      try {
        const user = await authApi.getCurrentUser()
        commit('SET_USER', user)
        return user
      } catch (error) {
        // token 可能已过期
        commit('LOGOUT')
        throw error
      }
    },

    logout({ commit }) {
      commit('LOGOUT')
    }
  },

  getters: {
    user: (state: AuthState) => state.user,
    token: (state: AuthState) => state.token,
    isAuthenticated: (state: AuthState) => state.isAuthenticated,
    loading: (state: AuthState) => state.loading,
    error: (state: AuthState) => state.error
  }
}

export default authModule

