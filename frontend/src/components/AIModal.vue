<template>
  <div class="modal-overlay" @click.self="handleDiscard">
    <div class="modal-content">
      <div class="modal-header">
        <h2>AI处理结果</h2>
        <button class="btn-close" @click="handleDiscard">×</button>
      </div>

      <div class="modal-body">
        <div v-if="processing" class="processing-indicator">
          <div class="spinner"></div>
          <span>AI正在处理中...</span>
        </div>
        <div v-else class="ai-content">
          <!-- 显示原始文本（只在真正选中文本时显示） -->
          <div v-if="originalText && originalText.trim()" class="original-text-section">
            <div class="section-label">原始文本：</div>
            <div class="original-text-display">{{ originalText }}</div>
          </div>
          
          <!-- 显示AI处理结果 -->
          <div class="result-section">
            <div class="section-label">{{ originalText && originalText.trim() ? 'AI处理结果：' : 'AI处理结果（整篇笔记）：' }}</div>
            <div class="content-display">{{ content || '暂无内容' }}</div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button
          class="btn-accept"
          :disabled="processing || !content"
          @click="handleAccept"
        >
          接受
        </button>
        <button class="btn-discard" @click="handleDiscard">丢弃</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  content: string
  originalText?: string  // 原始选中的文本
  processing: boolean
}

interface Emits {
  (e: 'accept'): void
  (e: 'discard'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()

const handleAccept = () => {
  emit('accept')
}

const handleDiscard = () => {
  emit('discard')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h2 {
  font-size: 20px;
  color: #333;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-close:hover {
  background: #f0f0f0;
}

.modal-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  min-height: 200px;
  max-height: calc(90vh - 160px);
}

.processing-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.ai-content {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-label {
  font-size: 14px;
  font-weight: 600;
  color: #666;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.original-text-section {
  width: 100%;
}

.original-text-display {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  font-size: 15px;
  color: #555;
  padding: 16px;
  background: #f5f5f5;
  border-left: 4px solid #6c757d;
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.result-section {
  width: 100%;
}

.content-display {
  white-space: pre-wrap;
  word-wrap: break-word;
  line-height: 1.8;
  font-size: 16px;
  color: #333;
  padding: 16px;
  background: #e8f5e9;
  border-left: 4px solid #28a745;
  border-radius: 6px;
  max-height: 400px;
  overflow-y: auto;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e0e0e0;
}

.btn-accept,
.btn-discard {
  padding: 10px 24px;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-accept {
  background: #28a745;
  color: white;
}

.btn-accept:hover:not(:disabled) {
  background: #218838;
}

.btn-accept:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.btn-discard {
  background: #6c757d;
  color: white;
}

.btn-discard:hover {
  background: #5a6268;
}

@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }

  .modal-content {
    max-height: 95vh;
  }

  .modal-header {
    padding: 16px;
  }

  .modal-header h2 {
    font-size: 18px;
  }

  .modal-body {
    padding: 16px;
    max-height: calc(95vh - 140px);
  }

  .original-text-display,
  .content-display {
    font-size: 14px;
    max-height: 200px;
  }
  
  .ai-content {
    gap: 15px;
  }

  .modal-footer {
    padding: 16px;
    flex-direction: column;
  }

  .btn-accept,
  .btn-discard {
    width: 100%;
  }
}
</style>

