// Vuex 类型声明修复
declare module 'vuex' {
  import type { Store } from 'vuex/types'
  export function createStore<S>(options: any): Store<S>
  export function useStore<S = any>(): Store<S>
  export interface Module<S, R> {
    namespaced?: boolean
    state?: S | (() => S)
    getters?: any
    actions?: any
    mutations?: any
    modules?: any
  }
  export interface Commit {
    (type: string, payload?: any, options?: any): void
    <P extends any>(payloadWithType: P, options?: any): void
  }
}

