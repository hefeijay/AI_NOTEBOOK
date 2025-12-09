import { Module } from 'vuex'

interface AIState {
  processing: boolean
  result: string
  error: string | null
}

const aiModule: Module<AIState, unknown> = {
  namespaced: true,

  state: (): AIState => ({
    processing: false,
    result: '',
    error: null
  }),

  mutations: {
    SET_PROCESSING(state: AIState, processing: boolean) {
      state.processing = processing
    },

    SET_RESULT(state: AIState, result: string) {
      state.result = result
    },

    APPEND_RESULT(state: AIState, chunk: string) {
      state.result += chunk
    },

    SET_ERROR(state: AIState, error: string | null) {
      state.error = error
    },

    RESET(state: AIState) {
      state.processing = false
      state.result = ''
      state.error = null
    }
  },

  actions: {
    setProcessing({ commit }: { commit: any }, processing: boolean) {
      commit('SET_PROCESSING', processing)
    },

    setResult({ commit }: { commit: any }, result: string) {
      commit('SET_RESULT', result)
    },

    appendResult({ commit }: { commit: any }, chunk: string) {
      commit('APPEND_RESULT', chunk)
    },

    setError({ commit }: { commit: any }, error: string | null) {
      commit('SET_ERROR', error)
    },

    reset({ commit }: { commit: any }) {
      commit('RESET')
    }
  },

  getters: {
    processing: (state: AIState) => state.processing,
    result: (state: AIState) => state.result,
    error: (state: AIState) => state.error
  }
}

export default aiModule

