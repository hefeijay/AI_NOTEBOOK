import { Module } from 'vuex'
import type { Note, CreateNoteDto, UpdateNoteDto } from '@/types'
import { notesApi } from '@/services/api'
import { wsService } from '@/services/websocket'

interface NotesState {
  notes: Note[]
  currentNote: Note | null
  loading: boolean
  error: string | null
}

const notesModule: Module<NotesState, unknown> = {
  namespaced: true,

  state: (): NotesState => ({
    notes: [],
    currentNote: null,
    loading: false,
    error: null
  }),

  mutations: {
    SET_LOADING(state: NotesState, loading: boolean) {
      state.loading = loading
    },

    SET_ERROR(state: NotesState, error: string | null) {
      state.error = error
    },

    SET_NOTES(state: NotesState, notes: Note[]) {
      state.notes = notes
    },

    ADD_NOTE(state: NotesState, note: Note) {
      state.notes.unshift(note)
    },

    UPDATE_NOTE(state: NotesState, note: Note) {
      const index = state.notes.findIndex((n) => n.id === note.id)
      if (index !== -1) {
        state.notes[index] = note
      }
      if (state.currentNote?.id === note.id) {
        state.currentNote = note
      }
    },

    DELETE_NOTE(state: NotesState, id: string) {
      state.notes = state.notes.filter((n) => n.id !== id)
      if (state.currentNote?.id === id) {
        state.currentNote = null
      }
    },

    SET_CURRENT_NOTE(state: NotesState, note: Note | null) {
      state.currentNote = note
    }
  },

  actions: {
    async fetchNotes({ commit }: { commit: any }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const notes = await notesApi.getAllNotes()
        commit('SET_NOTES', notes)
      } catch (error) {
        const message = error instanceof Error ? error.message : '获取笔记失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async fetchNote({ commit }: { commit: any }, id: string) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const note = await notesApi.getNote(id)
        commit('SET_CURRENT_NOTE', note)
        return note
      } catch (error) {
        const message = error instanceof Error ? error.message : '获取笔记失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async createNote({ commit }: { commit: any }, data: CreateNoteDto) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const note = await notesApi.createNote(data)
        commit('ADD_NOTE', note)
        return note
      } catch (error) {
        const message = error instanceof Error ? error.message : '创建笔记失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async updateNote({ commit }: { commit: any }, { id, data }: { id: string; data: UpdateNoteDto }) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        const note = await notesApi.updateNote(id, data)
        commit('UPDATE_NOTE', note)
        
        // 通过WebSocket同步更新
        if (wsService.isConnected()) {
          wsService.send({
            type: 'note_update',
            payload: note
          })
        }
        
        return note
      } catch (error) {
        const message = error instanceof Error ? error.message : '更新笔记失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    },

    async deleteNote({ commit }: { commit: any }, id: string) {
      commit('SET_LOADING', true)
      commit('SET_ERROR', null)
      try {
        await notesApi.deleteNote(id)
        commit('DELETE_NOTE', id)
        
        // 通过WebSocket同步删除
        if (wsService.isConnected()) {
          wsService.send({
            type: 'note_delete',
            payload: { id }
          })
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : '删除笔记失败'
        commit('SET_ERROR', message)
        throw error
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },

  getters: {
    notes: (state: NotesState) => state.notes,
    currentNote: (state: NotesState) => state.currentNote,
    loading: (state: NotesState) => state.loading,
    error: (state: NotesState) => state.error
  }
}

export default notesModule

