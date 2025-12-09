/**
 * 流式文本处理器 - 优化长文本渲染性能
 * 使用 requestAnimationFrame 分批更新，避免卡顿
 */

export class StreamProcessor {
  private buffer: string = ''
  private pendingUpdate: number | null = null
  private callback: (content: string) => void

  constructor(callback: (content: string) => void) {
    this.callback = callback
  }

  /**
   * 添加新的文本片段
   */
  append(chunk: string): void {
    this.buffer += chunk

    // 如果已有待处理的更新，取消它
    if (this.pendingUpdate !== null) {
      cancelAnimationFrame(this.pendingUpdate)
    }

    // 使用 requestAnimationFrame 延迟更新
    this.pendingUpdate = requestAnimationFrame(() => {
      this.flush()
      this.pendingUpdate = null
    })
  }

  /**
   * 立即刷新缓冲区
   */
  flush(): void {
    if (this.buffer) {
      this.callback(this.buffer)
      this.buffer = ''
    }
  }

  /**
   * 获取当前内容
   */
  getContent(): string {
    return this.buffer
  }

  /**
   * 重置处理器
   */
  reset(): void {
    if (this.pendingUpdate !== null) {
      cancelAnimationFrame(this.pendingUpdate)
      this.pendingUpdate = null
    }
    this.buffer = ''
  }
}

