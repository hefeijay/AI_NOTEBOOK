<template>
  <div class="note-detail-view">
    <header class="header">
      <button class="btn-back" @click="goBack">← 返回</button>
      <div class="header-actions">
        <div class="user-info" v-if="user">
          <span class="username">{{ user.username }}</span>
          <button class="btn-logout" @click="handleLogout">退出</button>
        </div>
        <span v-if="savingStatus" class="save-status">{{ savingStatus }}</span>
        <button
          class="btn-save"
          :disabled="saving"
          @click="handleManualSave"
        >
          {{ saving ? '保存中...' : '保存' }}
        </button>
        <button
          class="btn-ai"
          :disabled="aiProcessing"
          @mousedown.prevent="handleAIProcess"
        >
          {{ buttonText }}
        </button>
        <button class="btn-danger" @click="handleDelete">删除</button>
      </div>
    </header>

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="currentNote" class="note-editor-container">
      <TipTapEditor
        ref="editorRef"
        :note="currentNote"
      />
    </div>

    <AIModal
      v-if="showAIModal"
      :content="aiResult"
      :original-text="selectedText"
      :processing="aiProcessing"
      @accept="handleAccept"
      @discard="handleDiscard"
    />
    
    <!-- 右下角浮动保存按钮 -->
    <button
      v-if="currentNote"
      class="btn-save-floating"
      :disabled="saving"
      @click="handleManualSave"
      :title="saving ? '保存中...' : '保存'"
    >
      {{ saving ? '保存中...' : '保存' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useStore } from 'vuex'
import TipTapEditor from '@/components/TipTapEditor.vue'
import AIModal from '@/components/AIModal.vue'
import { aiApi } from '@/services/api'

const router = useRouter()
const route = useRoute()
const store = useStore()

const showAIModal = ref(false)
const selectedText = ref('')
const selectedRange = ref<{ start: number; end: number } | null>(null) // 保存选中范围
const hasSelection = ref(false)
const buttonText = ref('AI处理整篇笔记')
const noteEditorRef = ref<InstanceType<typeof NoteEditor> | null>(null)
const editorRef = ref<InstanceType<typeof TipTapEditor> | null>(null)
const saving = ref(false)
const savingStatus = ref('')
let statusTimer: number | null = null

const currentNote = computed(() => store.getters['notes/currentNote'])
const loading = computed(() => store.getters['notes/loading'])
const error = computed(() => store.getters['notes/error'])
const aiProcessing = computed(() => store.getters['ai/processing'])
const aiResult = computed(() => store.getters['ai/result'])
const user = computed(() => store.getters['auth/user'])

onMounted(async () => {
  // 如果有 token，尝试加载用户信息
  const token = localStorage.getItem('token')
  if (token && !user.value) {
    try {
      await store.dispatch('auth/getCurrentUser')
    } catch (error) {
      console.error('加载用户信息失败:', error)
    }
  }
  
  const noteId = route.params.id as string
  try {
    await store.dispatch('notes/fetchNote', noteId)
  } catch (err) {
    console.error('加载笔记失败:', err)
  }
  
  // 监听文本选择变化（多种事件确保及时更新）
  document.addEventListener('selectionchange', checkSelection)
  document.addEventListener('mouseup', checkSelection)
  document.addEventListener('keyup', checkSelection)
  
  // 移除 Ctrl+S 快捷键，避免与浏览器保存冲突
  
  // 初始化按钮文本
  updateButtonText()
  
  // 监听处理状态变化
  watch(aiProcessing, () => {
    updateButtonText()
  })
})

onUnmounted(() => {
  // 移除事件监听
  document.removeEventListener('selectionchange', checkSelection)
  document.removeEventListener('mouseup', checkSelection)
  document.removeEventListener('keyup', checkSelection)
  
  // 清理定时器
  if (statusTimer) {
    clearTimeout(statusTimer)
  }
  
  store.dispatch('ai/reset')
})


const goBack = () => {
  router.push('/')
}

const handleLogout = () => {
  store.dispatch('auth/logout')
  router.push('/login')
}

const getSelectedText = (): string => {
  // 查找所有 textarea（因为 scoped CSS 会修改类名）
  const textareas = document.querySelectorAll('textarea')
  let textarea: HTMLTextAreaElement | null = null
  
  // 找到有内容且可能有选中的 textarea
  for (let i = 0; i < textareas.length; i++) {
    const ta = textareas[i] as HTMLTextAreaElement
    if (ta.value && ta.value.length > 0) {
      textarea = ta
      break
    }
  }
  
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    if (start !== end && start >= 0 && end > start) {
      const selected = textarea.value.substring(start, end)
      // 检查是否有实际内容（去除空白后）
      if (selected.trim()) {
        // 注意：这里不保存 selectedRange，因为可能会被其他调用覆盖
        // selectedRange 只在 handleAIProcess 中保存
        console.log('getSelectedText 检测到选中文本（不保存范围）:', {
          start,
          end,
          length: selected.length,
          preview: selected.substring(0, 50)
        })
        return selected.trim() // 返回时trim，但范围使用原始值
      }
    }
  }
  
  // 如果没有从 textarea 获取到，尝试 window.getSelection（用于其他元素）
  const selection = window.getSelection()
  if (selection && selection.toString().trim()) {
    return selection.toString().trim()
  }
  
  return ''
}

const updateButtonText = () => {
  if (aiProcessing.value) {
    buttonText.value = 'AI处理中...'
    return
  }
  const selection = getSelectedText()
  if (selection) {
    buttonText.value = 'AI处理选中文本 ✨'
  } else {
    buttonText.value = 'AI处理整篇笔记'
  }
}

const checkSelection = () => {
  // 注意：这里不保存 selectedRange，只用于更新按钮文本
  // selectedRange 只在 handleAIProcess 中保存，避免被频繁重置
  hasSelection.value = getSelectedText().length > 0
  updateButtonText()
}

const handleAIProcess = async (event?: MouseEvent) => {
  if (!currentNote.value) return
  
  // 使用 mousedown 事件，在失去焦点前立即获取选中文本
  // 阻止默认行为，避免失去焦点
  if (event) {
    event.preventDefault()
  }

  let selected = ''
  let range: { start: number; end: number } | null = null
  
  // 优先从 TipTap 编辑器获取选中内容
  if (editorRef.value) {
    const selection = editorRef.value.getSelection()
    if (selection.hasSelection && selection.text.trim()) {
      selected = selection.text.trim()
      selectedText.value = selected
      // 保存 TipTap 编辑器的选中范围（from/to 是 ProseMirror 的位置）
      selectedRange.value = { start: selection.from, end: selection.to }
      range = { start: selection.from, end: selection.to }
      console.log('✅ 从 TipTap 编辑器获取到选中文本，长度:', selected.length)
      console.log('选中范围 (from/to):', selection.from, '到', selection.to)
    }
  }
  
  // 如果没有从编辑器获取到，尝试从 window.getSelection 获取（备用方案）
  if (!selected) {
    const selection = window.getSelection()
    if (selection && selection.toString().trim()) {
      selected = selection.toString().trim()
      selectedText.value = selected
      selectedRange.value = null // window.getSelection 无法获取精确范围
      console.log('✅ 从 window.getSelection 获取到选中文本，长度:', selected.length)
    }
  }
  
  // 确定要处理的文本 - 如果有选中，强制使用选中的文本
  const text = selected ? selected : currentNote.value.content
  
  console.log('最终决定:')
  console.log('  - selected存在:', !!selected)
  console.log('  - selected长度:', selected.length)
  console.log('  - 将使用的text长度:', text.length)
  console.log('  - 整篇笔记长度:', currentNote.value.content.length)

  if (!text.trim()) {
    alert('请先输入内容或选中要处理的文本')
    return
  }

  console.log('=== AI处理调试信息 ===')
  console.log('selected变量:', selected)
  console.log('range变量:', range)
  console.log('text变量长度:', text.length)
  console.log('text变量内容（前100字符）:', text.substring(0, 100))
  console.log('currentNote.value.content长度:', currentNote.value.content.length)
  
  if (selected && range) {
    console.log('✅ 检测到选中文本')
    console.log('选中文本:', selected)
    console.log('选中范围:', range)
    console.log('选中文本长度:', selected.length)
    console.log('将处理选中文本（前50字符）:', text.substring(0, 50) + '...')
    console.log('保存 selectedRange.value =', range)
    console.log('保存后 selectedRange.value =', selectedRange.value)
    
    // 确保 selectedRange 和 selectedText 已保存
    // 这里不再重置，因为已经在上面保存了
  } else {
    // 只有在真正没有选中时才重置
    if (!selected) {
      selectedText.value = ''
      selectedRange.value = null
      console.log('❌ 未选中文本，处理整篇笔记')
      console.log('将处理整篇笔记（前50字符）:', text.substring(0, 50) + '...')
    }
  }
  
  // 在处理前再次确认 selectedRange 已保存
  if (selected && range) {
    console.log('处理前再次确认 selectedRange:', selectedRange.value)
    console.log('处理前再次确认 selectedText:', selectedText.value)
  }
  
  showAIModal.value = true
  store.dispatch('ai/reset')
  store.dispatch('ai/setProcessing', true)

  try {
    // 直接使用 appendResult，不使用 StreamProcessor（避免内容丢失）
    // StreamProcessor 会在 flush 时清空 buffer，导致内容丢失
    // 重要：这里使用 text（选中的文本或整篇），而不是 currentNote.value.content
    console.log('发送给API的文本长度:', text.length)
    console.log('发送给API的文本（前100字符）:', text.substring(0, 100))
    for await (const chunk of aiApi.processText(text, currentNote.value.id)) {
      // 直接追加每个 chunk 到结果中
      store.dispatch('ai/appendResult', chunk)
    }
    
    // 处理完成后再次确认 selectedRange
    if (selected && range) {
      console.log('处理完成后再次确认 selectedRange:', selectedRange.value)
      console.log('处理完成后再次确认 selectedText:', selectedText.value)
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : 'AI处理失败'
    store.dispatch('ai/setError', message)
    console.error('AI处理错误:', err)
  } finally {
    store.dispatch('ai/setProcessing', false)
  }
}

const showSaveStatus = (message: string, duration = 2000) => {
  savingStatus.value = message
  if (statusTimer) {
    clearTimeout(statusTimer)
  }
  statusTimer = window.setTimeout(() => {
    savingStatus.value = ''
    statusTimer = null
  }, duration)
}

const performSave = async (data: { title?: string; content?: string }) => {
  if (!currentNote.value) return
  
  saving.value = true
  try {
    await store.dispatch('notes/updateNote', {
      id: currentNote.value.id,
      data
    })
    showSaveStatus('已保存', 1500)
    // 标记编辑器内容已保存
    if (editorRef.value) {
      editorRef.value.markAsSaved()
    }
  } catch (err) {
    console.error('更新笔记失败:', err)
    showSaveStatus('保存失败', 2000)
  } finally {
    saving.value = false
  }
}

const handleManualSave = async () => {
  if (!currentNote.value || saving.value) return
  
  // 从编辑器获取当前内容
  const content = editorRef.value?.getContent() || currentNote.value.content
  
  // 保存内容
  await performSave({
    content
  })
}

const handleAccept = async () => {
  if (!currentNote.value || !aiResult.value) return

  // 检查是否有选中的文本和范围
  const hasValidText = selectedText.value && selectedText.value.trim().length > 0
  const hasValidRange = selectedRange.value !== null && selectedRange.value !== undefined
  
  let replaced = false
  
  // 优先使用编辑器的 replaceSelection 方法（最准确）
  if (hasValidRange && hasValidText && editorRef.value) {
    // 使用保存的范围替换（即使当前没有选中，也能恢复选中并替换）
    const { start, end } = selectedRange.value
    replaced = editorRef.value.replaceSelection(aiResult.value, start, end)
    if (replaced) {
      console.log('✅ 使用编辑器 replaceSelection 替换成功')
    } else {
      console.log('⚠️ 编辑器 replaceSelection 失败，尝试备用方案')
    }
  }
  
  // 如果编辑器替换失败，使用备用方案
  if (!replaced) {
    const currentContent = editorRef.value?.getContent() || currentNote.value.content
    
    if (hasValidText && hasValidRange) {
      // 尝试在 HTML 内容中查找并替换（简化处理）
      const searchText = selectedText.value.trim()
      // 移除 HTML 标签后查找文本位置
      const textOnly = currentContent.replace(/<[^>]*>/g, '')
      const textIndex = textOnly.indexOf(searchText)
      
      if (textIndex !== -1) {
        // 在 HTML 中找到文本，尝试替换（简单替换第一个匹配）
        const newContent = currentContent.replace(searchText, aiResult.value)
        if (editorRef.value) {
          editorRef.value.setContent(newContent)
        }
        await performSave({ content: newContent })
        replaced = true
        console.log('✅ 使用文本查找替换成功')
      }
    }
    
    // 如果还是没替换成功，替换全部内容
    if (!replaced) {
      console.log('⚠️ 无法精确替换，使用全部替换')
      if (editorRef.value) {
        editorRef.value.setContent(aiResult.value)
      }
      await performSave({ content: aiResult.value })
    }
  } else {
    // 如果编辑器替换成功，保存内容
    const newContent = editorRef.value?.getContent() || currentNote.value.content
    await performSave({ content: newContent })
  }

  showAIModal.value = false
  selectedRange.value = null
  selectedText.value = ''
  store.dispatch('ai/reset')
}

const handleDiscard = () => {
  showAIModal.value = false
  store.dispatch('ai/reset')
}

const handleDelete = async () => {
  if (!currentNote.value) return

  if (!confirm('确定要删除这篇笔记吗？')) {
    return
  }

  try {
    await store.dispatch('notes/deleteNote', currentNote.value.id)
    router.push('/')
  } catch (err) {
    console.error('删除笔记失败:', err)
  }
}
</script>

<style scoped>
.note-detail-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding: 24px 32px;
  background: rgba(30, 38, 64, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(120, 119, 198, 0.4);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.25),
    inset 0 1px 0 rgba(255, 255, 255, 0.15);
  animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn-back {
  background: rgba(120, 119, 198, 0.2);
  color: #7877c6;
  font-size: 16px;
  font-weight: 500;
  padding: 10px 18px;
  border-radius: 12px;
  border: 1px solid rgba(120, 119, 198, 0.3);
  transition: all 0.3s;
}

.btn-back:hover {
  background: rgba(120, 119, 198, 0.3);
  border-color: rgba(120, 119, 198, 0.5);
  transform: translateX(-2px);
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-right: 8px;
}

.username {
  color: rgba(226, 232, 240, 0.8);
  font-size: 14px;
  font-weight: 500;
  padding: 8px 16px;
  background: rgba(120, 119, 198, 0.2);
  border-radius: 12px;
  border: 1px solid rgba(120, 119, 198, 0.3);
}

.btn-logout {
  background: rgba(220, 38, 38, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(220, 38, 38, 0.3);
  padding: 8px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-logout:hover {
  background: rgba(220, 38, 38, 0.3);
  border-color: rgba(220, 38, 38, 0.5);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.btn-ai {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 
    0 4px 15px rgba(16, 185, 129, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
}

.btn-ai:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(16, 185, 129, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-ai:disabled {
  background: rgba(108, 117, 125, 0.5);
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-danger {
  background: rgba(220, 38, 38, 0.8);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  border: 1px solid rgba(220, 38, 38, 0.5);
  box-shadow: 0 4px 15px rgba(220, 38, 38, 0.3);
  transition: all 0.3s;
}

.btn-danger:hover {
  background: rgba(220, 38, 38, 1);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(220, 38, 38, 0.4);
}

.btn-save {
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  color: white;
  padding: 12px 24px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 
    0 4px 15px rgba(120, 119, 198, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}

.btn-save::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.btn-save:hover:not(:disabled)::before {
  left: 100%;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 
    0 8px 25px rgba(120, 119, 198, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-save:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.save-status {
  display: flex;
  align-items: center;
  padding: 10px 15px;
  color: #28a745;
  font-size: 14px;
  font-weight: 500;
}


.loading,
.error {
  text-align: center;
  padding: 60px 20px;
}

.error {
  color: #dc3545;
}

.note-editor-container {
  background: transparent;
  padding: 0;
  margin-top: 0;
  animation: fadeIn 0.5s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.btn-save-floating {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #7877c6 0%, #ff77c6 100%);
  color: white;
  padding: 16px 32px;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  box-shadow: 
    0 8px 24px rgba(120, 119, 198, 0.5),
    0 0 0 1px rgba(120, 119, 198, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
  overflow: hidden;
  min-width: 100px;
  text-align: center;
}

.btn-save-floating::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  transition: left 0.5s;
}

.btn-save-floating:hover:not(:disabled)::before {
  left: 100%;
}

.btn-save-floating:hover:not(:disabled) {
  box-shadow: 
    0 12px 32px rgba(120, 119, 198, 0.6),
    0 0 0 1px rgba(120, 119, 198, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  transform: translateY(-3px) scale(1.02);
}

.btn-save-floating:active:not(:disabled) {
  transform: translateY(-1px) scale(0.98);
}

.btn-save-floating:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-save-floating:active:not(:disabled) {
  transform: translateY(0);
}

.btn-save-floating:disabled {
  background: #6c757d;
  cursor: not-allowed;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .note-detail-view {
    padding: 15px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .btn-ai,
  .btn-danger {
    flex: 1;
  }

  .btn-save-floating {
    bottom: 20px;
    right: 20px;
    padding: 14px 24px;
    font-size: 15px;
    min-width: 90px;
  }
}
</style>

