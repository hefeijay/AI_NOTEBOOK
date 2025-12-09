<template>
  <div class="note-editor">
    <input
      v-model="localTitle"
      class="note-title-input"
      placeholder="输入标题..."
      @blur="handleTitleBlur"
      @input="handleTitleInput"
    />
    <textarea
      v-model="localContent"
      class="note-content-input"
      placeholder="开始记录你的想法..."
      @blur="handleContentBlur"
      @input="handleContentInput"
    ></textarea>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Note } from '@/types'

interface Props {
  note: Note
}

interface Emits {
  (e: 'update', data: { title?: string; content?: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const localTitle = ref(props.note.title)
const localContent = ref(props.note.content)

let titleDebounceTimer: number | null = null
let contentDebounceTimer: number | null = null

watch(
  () => props.note,
  (newNote) => {
    localTitle.value = newNote.title
    localContent.value = newNote.content
  },
  { deep: true }
)

const handleTitleInput = () => {
  if (titleDebounceTimer) {
    clearTimeout(titleDebounceTimer)
  }
  titleDebounceTimer = window.setTimeout(() => {
    emit('update', { title: localTitle.value })
  }, 500)
}

const handleTitleBlur = () => {
  if (titleDebounceTimer) {
    clearTimeout(titleDebounceTimer)
    titleDebounceTimer = null
  }
  emit('update', { title: localTitle.value })
}

const handleContentInput = () => {
  if (contentDebounceTimer) {
    clearTimeout(contentDebounceTimer)
  }
  contentDebounceTimer = window.setTimeout(() => {
    emit('update', { content: localContent.value })
  }, 500)
}

const handleContentBlur = () => {
  if (contentDebounceTimer) {
    clearTimeout(contentDebounceTimer)
    contentDebounceTimer = null
  }
  emit('update', { content: localContent.value })
}
</script>

<style scoped>
.note-editor {
  width: 100%;
}

.note-title-input {
  width: 100%;
  font-size: 24px;
  font-weight: 600;
  border: none;
  padding: 10px 0;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  transition: border-color 0.3s;
}

.note-title-input:focus {
  border-bottom-color: #007bff;
}

.note-content-input {
  width: 100%;
  min-height: 500px;
  font-size: 16px;
  line-height: 1.8;
  border: none;
  resize: vertical;
  font-family: inherit;
}

.note-content-input:focus {
  outline: none;
}

@media (max-width: 768px) {
  .note-title-input {
    font-size: 20px;
  }

  .note-content-input {
    min-height: 400px;
    font-size: 14px;
  }
}
</style>

