<template>
  <div class="rich-editor">
    <QuillEditor
      v-model:content="localContent"
      contentType="html"
      :options="editorOptions"
      @blur="handleBlur"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { QuillEditor } from 'vue3-quill'
import type { Note } from '@/types'
import { uploadApi } from '@/services/upload'

interface Props {
  note: Note
}

interface Emits {
  (e: 'update', data: { title?: string; content?: string }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const localContent = ref(props.note.content)

watch(
  () => props.note.content,
  (val) => {
    localContent.value = val
  }
)

const editorOptions = computed(() => ({
  theme: 'snow',
  placeholder: '记录你的想法，支持富文本与图片...',
  modules: {
    toolbar: {
      container: [
        [{ header: [1, 2, 3, false] }],
        ['bold', 'italic', 'underline', 'strike', 'blockquote', 'code-block'],
        [{ color: [] }, { background: [] }],
        [{ align: [] }],
        [{ list: 'ordered' }, { list: 'bullet' }],
        ['link', 'image'],
        ['clean']
      ],
      handlers: {
        image: async function selectImage(this: any) {
          const input = document.createElement('input')
          input.setAttribute('type', 'file')
          input.setAttribute('accept', 'image/*')
          input.click()
          input.onchange = async () => {
            const file = input.files?.[0]
            if (!file) return
            try {
              const url = await uploadApi.uploadImage(file)
              const range = this.quill.getSelection(true)
              this.quill.insertEmbed(range.index, 'image', url)
            } catch (err) {
              console.error('图片上传失败', err)
            }
          }
        }
      }
    }
  }
}))

const handleBlur = () => {
  emit('update', { content: localContent.value })
}
</script>

<style scoped>
.rich-editor {
  min-height: 500px;
}

.ql-editor {
  min-height: 480px;
  line-height: 1.7;
}
</style>

