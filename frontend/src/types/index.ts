export interface Note {
  id: string
  title: string
  content: string
  createdAt: string
  updatedAt: string
}

export interface CreateNoteDto {
  title: string
  content: string
}

export interface UpdateNoteDto {
  title?: string
  content?: string
}

export interface AIProcessRequest {
  text: string
  noteId?: string
}

export interface AIProcessResponse {
  content: string
}

export interface WebSocketMessage {
  type: 'note_update' | 'note_create' | 'note_delete' | 'collaboration'
  payload: unknown
}

