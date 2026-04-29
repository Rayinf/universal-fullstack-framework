/**
 * 请求队列管理器 - 控制API并发数量和优先级
 */

export interface QueuedRequest {
  id: string
  priority: 'high' | 'medium' | 'low'
  request: () => Promise<unknown>
  resolve: (value: unknown) => void
  reject: (reason: unknown) => void
  timestamp: number
  retryCount?: number
}

export interface RequestQueueOptions {
  maxConcurrent: number // 最大并发数
  maxRetries: number // 最大重试次数
  retryDelay: number // 重试延迟（毫秒）
  timeout: number // 请求超时时间（毫秒）
}

class RequestQueueManager {
  private queue: QueuedRequest[] = []
  private running: Map<string, QueuedRequest> = new Map()
  private options: RequestQueueOptions
  private requestIdCounter = 0

  constructor(options: Partial<RequestQueueOptions> = {}) {
    this.options = {
      maxConcurrent: 10, // 默认最大10个并发请求
      maxRetries: 3,
      retryDelay: 1000,
      timeout: 30000,
      ...options,
    }
  }

  /**
   * 添加请求到队列
   */
  async enqueue<T>(
    request: () => Promise<T>,
    priority: 'high' | 'medium' | 'low' = 'medium',
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const queuedRequest: QueuedRequest = {
        id: `req_${++this.requestIdCounter}_${Date.now()}`,
        priority,
        request,
        resolve: (value: unknown) => resolve(value as T),
        reject: (reason: unknown) => reject(reason),
        timestamp: Date.now(),
        retryCount: 0,
      }

      // 根据优先级插入队列
      this.insertByPriority(queuedRequest)
      this.processQueue()
    })
  }

  /**
   * 根据优先级插入队列
   */
  private insertByPriority(queuedRequest: QueuedRequest) {
    const priorityOrder = { high: 0, medium: 1, low: 2 }
    let insertIndex = this.queue.length

    for (let i = 0; i < this.queue.length; i++) {
      if (priorityOrder[queuedRequest.priority] < priorityOrder[this.queue[i].priority]) {
        insertIndex = i
        break
      }
    }

    this.queue.splice(insertIndex, 0, queuedRequest)
  }

  /**
   * 仅对网络错误、5xx、429进行重试，避免404等业务错误触发重试风暴
   */
  private shouldRetry(error: unknown): boolean {
    const status = (error as { response?: { status?: number } })?.response?.status
    if (!status) return true
    return status === 429 || status >= 500
  }

  /**
   * 处理队列
   */
  private async processQueue() {
    // 如果已达到最大并发数，等待
    if (this.running.size >= this.options.maxConcurrent) {
      return
    }

    // 如果队列为空，返回
    if (this.queue.length === 0) {
      return
    }

    const queuedRequest = this.queue.shift()!
    this.running.set(queuedRequest.id, queuedRequest)

    try {
      // 添加超时控制
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), this.options.timeout)
      })

      const result = await Promise.race([queuedRequest.request(), timeoutPromise])
      queuedRequest.resolve(result)
    } catch (error) {
      // 重试逻辑
      if (this.shouldRetry(error) && queuedRequest.retryCount! < this.options.maxRetries) {
        queuedRequest.retryCount!++
        console.warn(`请求 ${queuedRequest.id} 失败，第 ${queuedRequest.retryCount} 次重试`, error)

        // 延迟后重新加入队列
        setTimeout(() => {
          this.insertByPriority(queuedRequest)
          this.processQueue()
        }, this.options.retryDelay)
      } else {
        console.error(`请求 ${queuedRequest.id} 最终失败`, error)
        queuedRequest.reject(error)
      }
    } finally {
      this.running.delete(queuedRequest.id)
      // 继续处理队列中的其他请求
      this.processQueue()
    }
  }

  /**
   * 获取队列状态
   */
  getStatus() {
    return {
      queueLength: this.queue.length,
      runningCount: this.running.size,
      maxConcurrent: this.options.maxConcurrent,
      queueByPriority: {
        high: this.queue.filter((req) => req.priority === 'high').length,
        medium: this.queue.filter((req) => req.priority === 'medium').length,
        low: this.queue.filter((req) => req.priority === 'low').length,
      },
    }
  }

  /**
   * 清空队列
   */
  clear() {
    this.queue.forEach((req) => req.reject(new Error('Queue cleared')))
    this.queue = []
  }

  /**
   * 更新配置
   */
  updateOptions(newOptions: Partial<RequestQueueOptions>) {
    this.options = { ...this.options, ...newOptions }
  }
}

// 创建全局请求队列管理器实例
export const requestQueue = new RequestQueueManager({
  maxConcurrent: 10, // 最大10个并发请求
  maxRetries: 2,
  retryDelay: 1000,
  timeout: 30000,
})

// 导出便捷方法
export const queueRequest = <T>(
  request: () => Promise<T>,
  priority: 'high' | 'medium' | 'low' = 'medium',
): Promise<T> => {
  return requestQueue.enqueue(request, priority)
}

// 调试方法
export const getQueueStatus = () => requestQueue.getStatus()
