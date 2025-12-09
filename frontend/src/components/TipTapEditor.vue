<template>
  <div class="tiptap-editor">
    <div class="toolbar">
      <button @click="toggleBold" :class="{ active: editor?.isActive('bold') }">B</button>
      <button @click="toggleItalic" :class="{ active: editor?.isActive('italic') }"><i>I</i></button>
      <button @click="toggleUnderline" :class="{ active: editor?.isActive('underline') }"><u>U</u></button>
      <button @click="setHeading(1)" :class="{ active: editor?.isActive('heading', { level: 1 }) }">H1</button>
      <button @click="setHeading(2)" :class="{ active: editor?.isActive('heading', { level: 2 }) }">H2</button>
      <button @click="toggleBullet" :class="{ active: editor?.isActive('bulletList') }">• List</button>
      <button @click="toggleOrdered" :class="{ active: editor?.isActive('orderedList') }">1. List</button>
      <button @click="align('left')" :class="{ active: editor?.isActive({ textAlign: 'left' }) }">左</button>
      <button @click="align('center')" :class="{ active: editor?.isActive({ textAlign: 'center' }) }">中</button>
      <button @click="align('right')" :class="{ active: editor?.isActive({ textAlign: 'right' }) }">右</button>
      <button @click="insertImage">图片</button>
      <button @click="clear">清除</button>
    </div>
    <EditorContent :editor="editor as any" class="editor" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { Editor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import TextAlign from '@tiptap/extension-text-align'
import Underline from '@tiptap/extension-underline'
import type { Note } from '@/types'
import { uploadApi } from '@/services/upload'
import { API_BASE_URL } from '@/utils/config'

interface Props {
  note: Note
}
interface Emits {
  (e: 'update', data: { content: string }): void
}

const props = defineProps<Props>()
const _emit = defineEmits<Emits>()

const editor = ref<Editor | undefined>(undefined)
let editorInitialized = false // 标记编辑器是否已初始化
let currentNoteId = '' // 记录当前笔记ID，只有ID变化时才更新内容
let lastContentHash = '' // 记录上次内容的哈希

// 转换内容中的相对路径图片URL为完整URL
const convertImageUrls = (html: string): string => {
  if (!html) return html
  // 使用正则表达式替换所有相对路径的图片URL
  return html.replace(
    /src="(\/static\/uploads\/[^"]+)"/g,
    (match, path) => {
      // 如果已经是完整URL，不处理
      if (path.startsWith('http')) {
        return match
      }
      return `src="${API_BASE_URL}${path}"`
    }
  )
}

onMounted(() => {
  // 转换内容中的图片URL
  const contentWithFullUrls = convertImageUrls(props.note.content)
  
  editor.value = new Editor({
    content: contentWithFullUrls,
    extensions: [
      StarterKit,
      Underline,
      Link.configure({
        openOnClick: true,
        autolink: true,
        HTMLAttributes: { rel: 'noopener noreferrer', target: '_blank' }
      }),
      Image.configure({
        allowBase64: true,
        inline: false,
        HTMLAttributes: {
          class: 'editor-image'
        }
      }),
      TextAlign.configure({
        types: ['heading', 'paragraph']
      })
    ],
    editorProps: {
      attributes: {
        class: 'prose'
      }
    },
    onUpdate: () => {
      // 不再自动保存
    }
  })
  editorInitialized = true
  lastContentHash = props.note.content
  currentNoteId = props.note.id
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})

// 暴露方法让父组件可以获取当前内容
const getContent = () => {
  return editor.value?.getHTML() || ''
}

// 暴露方法让父组件可以设置内容
const setContent = (content: string) => {
  if (editor.value) {
    editor.value.commands.setContent(content, false)
    lastContentHash = content
  }
}

// 暴露方法让父组件可以获取选中的内容和范围
const getSelection = () => {
  if (!editor.value) {
    return { text: '', html: '', from: 0, to: 0, hasSelection: false }
  }
  
  const { from, to } = editor.value.state.selection
  const hasSelection = from !== to
  
  if (hasSelection) {
    const text = editor.value.state.doc.textBetween(from, to, ' ')
    // 获取选中部分的 HTML
    const selectedContent = editor.value.state.doc.slice(from, to)
    const html = selectedContent.content.size > 0 
      ? editor.value.getHTML().slice(from, to) // 简化处理，实际应该从文档片段生成
      : text
    
    return {
      text: text.trim(),
      html: html,
      from,
      to,
      hasSelection: true
    }
  }
  
  return { text: '', html: '', from: 0, to: 0, hasSelection: false }
}

// 暴露方法让父组件可以替换选中内容
const replaceSelection = (content: string, from?: number, to?: number) => {
  if (!editor.value) return false
  
  // 如果提供了 from/to，先恢复选中范围
  if (from !== undefined && to !== undefined && from !== to) {
    try {
      const docSize = editor.value.state.doc.content.size
      const safeFrom = Math.min(from, docSize)
      const safeTo = Math.min(to, docSize)
      
      if (safeFrom >= 0 && safeTo > safeFrom) {
        // 先设置选中范围
        editor.value.chain()
          .focus()
          .setTextSelection({ from: safeFrom, to: safeTo })
          .deleteSelection()
          .insertContent(content)
          .run()
        return true
      }
    } catch (e) {
      console.error('恢复选中范围失败:', e)
    }
  }
  
  // 如果没有提供范围或恢复失败，使用当前选中
  const { from: currentFrom, to: currentTo } = editor.value.state.selection
  const hasSelection = currentFrom !== currentTo
  
  if (hasSelection) {
    // 删除选中内容并插入新内容
    editor.value.chain()
      .focus()
      .deleteSelection()
      .insertContent(content)
      .run()
    return true
  }
  
  return false
}

// 暴露方法让父组件可以检查是否有未保存的更改
const hasUnsavedChanges = () => {
  if (!editor.value) return false
  const currentContent = editor.value.getHTML()
  return currentContent !== lastContentHash
}

// 暴露方法让父组件可以标记内容已保存
const markAsSaved = () => {
  if (editor.value) {
    lastContentHash = editor.value.getHTML()
  }
}

defineExpose({
  getContent,
  setContent,
  getSelection,
  replaceSelection,
  hasUnsavedChanges,
  markAsSaved
})

// 只监听 note.id 的变化，当切换到不同笔记时才更新内容
watch(
  () => props.note.id,
  (newId) => {
    if (!editor.value || !editorInitialized) return
    
    // 如果切换到不同的笔记，更新内容
    if (newId !== currentNoteId) {
      currentNoteId = newId
      const view = editor.value.view
      const editorElement = view.dom as HTMLElement
      
      // 记录滚动位置
      const scrollContainerTop = editorElement.scrollTop
      const windowTop = window.scrollY
      
      // 转换内容中的图片URL并更新
      const contentWithFullUrls = convertImageUrls(props.note.content)
      editor.value.commands.setContent(contentWithFullUrls, false)
      lastContentHash = props.note.content
      
      // 恢复滚动位置
      requestAnimationFrame(() => {
        if (editorElement) {
          if (scrollContainerTop > 0) {
            editorElement.scrollTop = scrollContainerTop
          } else if (windowTop > 0) {
            window.scrollTo({ top: windowTop, behavior: 'instant' })
          }
        }
      })
    }
  }
)

// 完全移除对 content 的 watch，避免自动保存后同步导致滚动丢失
// 编辑器内容由用户编辑维护，不需要从 props 同步回来

const toggleBold = () => editor.value?.chain().focus().toggleBold().run()
const toggleItalic = () => editor.value?.chain().focus().toggleItalic().run()
const toggleUnderline = () => editor.value?.chain().focus().toggleUnderline().run()
const setHeading = (level: 1 | 2) => editor.value?.chain().focus().toggleHeading({ level }).run()
const toggleBullet = () => editor.value?.chain().focus().toggleBulletList().run()
const toggleOrdered = () => editor.value?.chain().focus().toggleOrderedList().run()
const align = (pos: 'left' | 'center' | 'right') =>
  editor.value?.chain().focus().setTextAlign(pos).run()
const clear = () => editor.value?.chain().focus().clearNodes().unsetAllMarks().run()


const insertImage = async () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = 'image/*'
  input.click()
  input.onchange = async () => {
    const file = input.files?.[0]
    if (!file) return
    try {
      const url = await uploadApi.uploadImage(file)
      // 如果返回的是相对路径，转换为完整URL
      const imageUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
      editor.value?.chain().focus().setImage({ src: imageUrl }).run()
    } catch (e) {
      console.error('图片上传失败', e)
      alert('图片上传失败，请重试')
    }
  }
}
</script>

<style scoped>
.tiptap-editor {
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 20px;
  background: rgba(30, 38, 64, 0.85);
  overflow: hidden;
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 20px;
  border-bottom: 1px solid rgba(120, 119, 198, 0.3);
  background: rgba(30, 38, 64, 0.7);
  border-radius: 20px 20px 0 0;
  position: relative;
}

.toolbar::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, 
    transparent,
    rgba(120, 119, 198, 0.5),
    transparent
  );
}

.toolbar button {
  padding: 10px 16px;
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 12px;
  background: rgba(120, 119, 198, 0.2);
  color: rgba(226, 232, 240, 0.95);
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.toolbar button::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent,
    rgba(255, 255, 255, 0.1),
    transparent
  );
  transition: left 0.5s;
}

.toolbar button:hover::before {
  left: 100%;
}

.toolbar button:hover {
  background: rgba(120, 119, 198, 0.3);
  border-color: rgba(120, 119, 198, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(120, 119, 198, 0.4);
}

.toolbar button.active {
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  border-color: transparent;
  color: white;
  box-shadow: 
    0 4px 15px rgba(120, 119, 198, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.toolbar button.active:hover {
  box-shadow: 
    0 6px 20px rgba(120, 119, 198, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.editor {
  padding: 0;
}

.editor :global(.ProseMirror) {
  min-height: 520px;
  padding: 32px;
  line-height: 1.8;
  outline: none;
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(226, 232, 240, 0.95);
  background: rgba(30, 38, 64, 0.6);
  border-radius: 0 0 16px 16px;
}

.editor :global(.ProseMirror p) {
  margin: 0 0 16px;
  color: rgba(226, 232, 240, 0.95);
}

.editor :global(.ProseMirror h1) {
  font-size: 2.25em;
  font-weight: 700;
  margin: 24px 0 16px;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.5px;
}

.editor :global(.ProseMirror h2) {
  font-size: 1.75em;
  font-weight: 600;
  margin: 20px 0 12px;
  color: rgba(226, 232, 240, 0.95);
  letter-spacing: -0.3px;
}

.editor :global(.ProseMirror strong) {
  color: rgba(226, 232, 240, 1);
  font-weight: 600;
}

.editor :global(.ProseMirror em) {
  color: rgba(226, 232, 240, 0.9);
  font-style: italic;
}

.editor :global(.ProseMirror u) {
  color: rgba(226, 232, 240, 0.9);
  text-decoration: underline;
  text-decoration-color: rgba(120, 119, 198, 0.6);
}

.editor :global(.ProseMirror ul),
.editor :global(.ProseMirror ol) {
  padding-left: 24px;
  margin: 12px 0;
  color: rgba(226, 232, 240, 0.95);
}

.editor :global(.ProseMirror li) {
  margin: 8px 0;
  color: rgba(226, 232, 240, 0.95);
}

.editor :global(.ProseMirror blockquote) {
  border-left: 4px solid rgba(120, 119, 198, 0.6);
  padding: 16px 20px;
  margin: 16px 0;
  background: rgba(120, 119, 198, 0.1);
  border-radius: 8px;
  color: rgba(226, 232, 240, 0.8);
  font-style: italic;
}

.editor :global(.ProseMirror code) {
  background: rgba(120, 119, 198, 0.2);
  color: #ff77c6;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.editor :global(.ProseMirror pre) {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(120, 119, 198, 0.3);
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  overflow-x: auto;
}

.editor :global(.ProseMirror pre code) {
  background: transparent;
  color: rgba(226, 232, 240, 0.9);
  padding: 0;
}

.editor :global(.ProseMirror a) {
  color: #7877c6;
  text-decoration: underline;
  text-decoration-color: rgba(120, 119, 198, 0.5);
  transition: all 0.3s;
}

.editor :global(.ProseMirror a:hover) {
  color: #ff77c6;
  text-decoration-color: rgba(255, 119, 198, 0.6);
}

.editor :global(.ProseMirror img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 24px auto;
  border-radius: 12px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(120, 119, 198, 0.2);
}

.editor :global(.ProseMirror-focused) {
  outline: none;
}

.editor :global(.ProseMirror)::placeholder {
  color: rgba(226, 232, 240, 0.3);
}

.prose {
  min-height: 500px;
  line-height: 1.8;
  outline: none;
  color: rgba(226, 232, 240, 0.95);
}
</style>

