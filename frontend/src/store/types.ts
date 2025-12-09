// Vuex 类型定义
import { Commit } from 'vuex'

export interface ActionContext {
  commit: Commit
  state: any
  getters: any
  dispatch: any
  rootState: any
  rootGetters: any
}

