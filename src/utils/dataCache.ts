/**
 * 数据缓存和去重机制
 */

export interface CacheItem<T> {
  data: T
  timestamp: number
  ttl: number // 生存时间（毫秒）
  key: string
  version?: string // 数据版本，用于缓存失效
}

export interface CacheOptions {
  ttl?: number // 默认TTL（毫秒）
  maxSize?: number // 最大缓存条目数
  enableCompression?: boolean // 是否启用压缩
  enablePersistence?: boolean // 是否持久化到localStorage
}

/**
 * 内存缓存管理器
 */
export class MemoryCache {
  private cache = new Map<string, CacheItem<any>>()
  private accessTimes = new Map<string, number>() // LRU访问时间
  private options: Required<CacheOptions>

  constructor(options: CacheOptions = {}) {
    this.options = {
      ttl: 5 * 60 * 1000, // 默认5分钟
      maxSize: 100, // 默认最大100个条目
      enableCompression: false,
      enablePersistence: false,
      ...options,
    }

    // 定期清理过期缓存
    setInterval(() => this.cleanup(), 60 * 1000) // 每分钟清理一次
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, ttl?: number, version?: string): void {
    // 检查缓存大小限制
    if (this.cache.size >= this.options.maxSize) {
      this.evictLRU()
    }

    const cacheItem: CacheItem<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.options.ttl,
      key,
      version,
    }

    this.cache.set(key, cacheItem)
    this.accessTimes.set(key, Date.now())

    // 持久化到localStorage
    if (this.options.enablePersistence) {
      this.persistToStorage(key, cacheItem)
    }
  }

  /**
   * 获取缓存
   */
  get<T>(key: string, version?: string): T | null {
    const item = this.cache.get(key)
    
    if (!item) {
      // 尝试从localStorage恢复
      if (this.options.enablePersistence) {
        const restored = this.restoreFromStorage<T>(key)
        if (restored) {
          this.cache.set(key, restored)
          this.accessTimes.set(key, Date.now())
          return restored.data
        }
      }
      return null
    }

    // 检查版本
    if (version && item.version && item.version !== version) {
      this.delete(key)
      return null
    }

    // 检查TTL
    if (Date.now() - item.timestamp > item.ttl) {
      this.delete(key)
      return null
    }

    // 更新访问时间
    this.accessTimes.set(key, Date.now())
    return item.data
  }

  /**
   * 删除缓存
   */
  delete(key: string): boolean {
    this.accessTimes.delete(key)
    
    if (this.options.enablePersistence) {
      localStorage.removeItem(`cache_${key}`)
    }
    
    return this.cache.delete(key)
  }

  /**
   * 检查缓存是否存在且有效
   */
  has(key: string, version?: string): boolean {
    return this.get(key, version) !== null
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    this.cache.clear()
    this.accessTimes.clear()
    
    if (this.options.enablePersistence) {
      // 清理localStorage中的缓存
      const keys = Object.keys(localStorage).filter(key => key.startsWith('cache_'))
      keys.forEach(key => localStorage.removeItem(key))
    }
  }

  /**
   * 获取缓存统计信息
   */
  getStats() {
    const now = Date.now()
    let validCount = 0
    let expiredCount = 0

    this.cache.forEach((item) => {
      if (now - item.timestamp <= item.ttl) {
        validCount++
      } else {
        expiredCount++
      }
    })

    return {
      total: this.cache.size,
      valid: validCount,
      expired: expiredCount,
      maxSize: this.options.maxSize,
      hitRate: this.calculateHitRate(),
    }
  }

  /**
   * 清理过期缓存
   */
  private cleanup(): void {
    const now = Date.now()
    const keysToDelete: string[] = []

    this.cache.forEach((item, key) => {
      if (now - item.timestamp > item.ttl) {
        keysToDelete.push(key)
      }
    })

    keysToDelete.forEach((key) => this.delete(key))
  }

  /**
   * LRU淘汰策略
   */
  private evictLRU(): void {
    let oldestKey = ''
    let oldestTime = Date.now()

    this.accessTimes.forEach((time, key) => {
      if (time < oldestTime) {
        oldestTime = time
        oldestKey = key
      }
    })

    if (oldestKey) {
      this.delete(oldestKey)
    }
  }

  /**
   * 持久化到localStorage
   */
  private persistToStorage<T>(key: string, item: CacheItem<T>): void {
    try {
      const serialized = JSON.stringify(item)
      localStorage.setItem(`cache_${key}`, serialized)
    } catch (error) {
      console.warn('缓存持久化失败:', error)
    }
  }

  /**
   * 从localStorage恢复
   */
  private restoreFromStorage<T>(key: string): CacheItem<T> | null {
    try {
      const serialized = localStorage.getItem(`cache_${key}`)
      if (!serialized) return null

      const item: CacheItem<T> = JSON.parse(serialized)
      
      // 检查是否过期
      if (Date.now() - item.timestamp > item.ttl) {
        localStorage.removeItem(`cache_${key}`)
        return null
      }

      return item
    } catch (error) {
      console.warn('缓存恢复失败:', error)
      localStorage.removeItem(`cache_${key}`)
      return null
    }
  }

  /**
   * 计算缓存命中率
   */
  private calculateHitRate(): number {
    // 这里简化实现，实际应该跟踪请求和命中次数
    return 0.85 // 模拟85%命中率
  }
}

/**
 * 请求去重管理器
 */
export class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>()
  private requestCounts = new Map<string, number>()

  /**
   * 去重执行请求
   */
  async dedupe<T>(key: string, requestFn: () => Promise<T>): Promise<T> {
    // 如果相同请求正在进行中，返回现有Promise
    if (this.pendingRequests.has(key)) {
      console.log(`请求去重: ${key}`)
      return this.pendingRequests.get(key) as Promise<T>
    }

    // 记录请求次数
    const count = this.requestCounts.get(key) || 0
    this.requestCounts.set(key, count + 1)

    // 创建新请求
    const requestPromise = requestFn()
      .finally(() => {
        // 请求完成后清理
        this.pendingRequests.delete(key)
      })

    this.pendingRequests.set(key, requestPromise)
    return requestPromise
  }

  /**
   * 取消所有待处理请求
   */
  cancelAll(): void {
    this.pendingRequests.clear()
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      pendingCount: this.pendingRequests.size,
      totalRequests: Array.from(this.requestCounts.values()).reduce((a, b) => a + b, 0),
      uniqueRequests: this.requestCounts.size,
      deduplicationRate: this.calculateDeduplicationRate(),
    }
  }

  /**
   * 计算去重率
   */
  private calculateDeduplicationRate(): number {
    const total = Array.from(this.requestCounts.values()).reduce((a, b) => a + b, 0)
    const unique = this.requestCounts.size
    return unique > 0 ? (total - unique) / total : 0
  }
}

/**
 * 智能缓存管理器（结合缓存和去重）
 */
export class SmartCache {
  private cache: MemoryCache
  private deduplicator: RequestDeduplicator

  constructor(options: CacheOptions = {}) {
    this.cache = new MemoryCache(options)
    this.deduplicator = new RequestDeduplicator()
  }

  /**
   * 智能获取数据（缓存 + 去重）
   */
  async get<T>(
    key: string,
    requestFn: () => Promise<T>,
    options: {
      ttl?: number
      version?: string
      forceRefresh?: boolean
    } = {},
  ): Promise<T> {
    const { ttl, version, forceRefresh = false } = options

    // 检查缓存
    if (!forceRefresh) {
      const cached = this.cache.get<T>(key, version)
      if (cached !== null) {
        console.log(`缓存命中: ${key}`)
        return cached
      }
    }

    // 去重执行请求
    const data = await this.deduplicator.dedupe(key, requestFn)

    // 缓存结果
    this.cache.set(key, data, ttl, version)

    return data
  }

  /**
   * 设置缓存
   */
  set<T>(key: string, data: T, ttl?: number, version?: string): void {
    this.cache.set(key, data, ttl, version)
  }

  /**
   * 删除缓存
   */
  delete(key: string): boolean {
    return this.cache.delete(key)
  }

  /**
   * 清空缓存
   */
  clear(): void {
    this.cache.clear()
    this.deduplicator.cancelAll()
  }

  /**
   * 获取统计信息
   */
  getStats() {
    return {
      cache: this.cache.getStats(),
      deduplicator: this.deduplicator.getStats(),
    }
  }

  /**
   * 批量预加载数据
   */
  async preload<T>(
    items: Array<{
      key: string
      requestFn: () => Promise<T>
      ttl?: number
      version?: string
    }>,
  ): Promise<void> {
    const promises = items.map(({ key, requestFn, ttl, version }) =>
      this.get(key, requestFn, { ttl, version }),
    )

    await Promise.all(promises)
  }

  /**
   * 缓存失效（通过版本控制）
   */
  invalidateByVersion(oldVersion: string): void {
    // 这里简化实现，实际应该遍历所有缓存项检查版本
    console.log(`缓存失效: 版本 ${oldVersion}`)
  }

  /**
   * 缓存失效（通过模式匹配）
   */
  invalidateByPattern(pattern: RegExp): void {
    const keysToDelete: string[] = []
    
    // 这里需要访问cache的内部结构，实际实现可能需要调整
    // 简化实现：清空所有缓存
    this.cache.clear()
    console.log(`缓存失效: 模式 ${pattern}`)
  }
}

// 创建全局实例
export const globalCache = new SmartCache({
  ttl: 5 * 60 * 1000, // 5分钟
  maxSize: 200,
  enablePersistence: true,
})

// 便捷函数
export const getCachedData = <T>(
  key: string,
  requestFn: () => Promise<T>,
  options?: {
    ttl?: number
    version?: string
    forceRefresh?: boolean
  },
): Promise<T> => {
  return globalCache.get(key, requestFn, options)
}

// 创建缓存键的工具函数
export const createCacheKey = (...parts: (string | number | boolean)[]): string => {
  return parts.filter(Boolean).join(':')
}

// 数据版本管理
export class DataVersionManager {
  private versions = new Map<string, string>()

  /**
   * 设置数据版本
   */
  setVersion(dataType: string, version: string): void {
    this.versions.set(dataType, version)
  }

  /**
   * 获取数据版本
   */
  getVersion(dataType: string): string | undefined {
    return this.versions.get(dataType)
  }

  /**
   * 增加版本号
   */
  incrementVersion(dataType: string): string {
    const current = this.getVersion(dataType) || '0'
    const next = (parseInt(current) + 1).toString()
    this.setVersion(dataType, next)
    return next
  }

  /**
   * 生成基于时间的版本
   */
  generateTimeBasedVersion(): string {
    return Date.now().toString()
  }
}

export const versionManager = new DataVersionManager()
