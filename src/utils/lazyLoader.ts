/**
 * 懒加载装饰器和工具函数
 */

import { ref, computed, type Ref } from 'vue'
import { queueRequest } from './requestQueue'

export interface LazyLoadOptions {
  priority?: 'high' | 'medium' | 'low'
  delay?: number // 延迟时间（毫秒）
  dependencies?: Ref<any>[] // 依赖项，当依赖项变化时重新加载
  cache?: boolean // 是否缓存结果
  cacheKey?: string // 缓存键
}

// 全局缓存
const globalCache = new Map<string, { data: any; timestamp: number; ttl: number }>()

/**
 * 懒加载数据管理器
 */
export class LazyDataLoader<T> {
  private _data = ref<T | null>(null)
  private _loading = ref(false)
  private _error = ref<Error | null>(null)
  private _loaded = ref(false)
  private loadPromise: Promise<T> | null = null

  constructor(
    private loader: () => Promise<T>,
    private options: LazyLoadOptions = {},
  ) {}

  get data() {
    return this._data as Ref<T | null>
  }

  get loading() {
    return this._loading
  }

  get error() {
    return this._error
  }

  get loaded() {
    return this._loaded
  }

  /**
   * 触发数据加载
   */
  async load(force = false): Promise<T> {
    // 如果已经在加载中，返回现有的Promise
    if (this.loadPromise && !force) {
      return this.loadPromise
    }

    // 检查缓存
    if (this.options.cache && this.options.cacheKey && !force) {
      const cached = this.getCachedData()
      if (cached) {
        this._data.value = cached
        this._loaded.value = true
        return cached
      }
    }

    this._loading.value = true
    this._error.value = null

    this.loadPromise = this.executeLoad()

    try {
      const result = await this.loadPromise
      this._data.value = result
      this._loaded.value = true

      // 缓存结果
      if (this.options.cache && this.options.cacheKey) {
        this.setCachedData(result)
      }

      return result
    } catch (error) {
      this._error.value = error as Error
      throw error
    } finally {
      this._loading.value = false
      this.loadPromise = null
    }
  }

  /**
   * 执行加载逻辑
   */
  private async executeLoad(): Promise<T> {
    // 应用延迟
    if (this.options.delay && this.options.delay > 0) {
      await new Promise((resolve) => setTimeout(resolve, this.options.delay))
    }

    // 使用请求队列
    return queueRequest(this.loader, this.options.priority || 'medium')
  }

  /**
   * 获取缓存数据
   */
  private getCachedData(): T | null {
    if (!this.options.cacheKey) return null

    const cached = globalCache.get(this.options.cacheKey)
    if (!cached) return null

    // 检查TTL（默认5分钟）
    const ttl = cached.ttl || 5 * 60 * 1000
    if (Date.now() - cached.timestamp > ttl) {
      globalCache.delete(this.options.cacheKey)
      return null
    }

    return cached.data
  }

  /**
   * 设置缓存数据
   */
  private setCachedData(data: T) {
    if (!this.options.cacheKey) return

    globalCache.set(this.options.cacheKey, {
      data,
      timestamp: Date.now(),
      ttl: 5 * 60 * 1000, // 默认5分钟TTL
    })
  }

  /**
   * 清除数据
   */
  clear() {
    this._data.value = null
    this._loaded.value = false
    this._error.value = null
    if (this.options.cacheKey) {
      globalCache.delete(this.options.cacheKey)
    }
  }
}

/**
 * 创建懒加载数据
 */
export function createLazyData<T>(
  loader: () => Promise<T>,
  options: LazyLoadOptions = {},
): LazyDataLoader<T> {
  return new LazyDataLoader(loader, options)
}

/**
 * 批量懒加载管理器
 */
export class BatchLazyLoader {
  private loaders: Map<string, LazyDataLoader<any>> = new Map()
  private loadOrder: string[] = []

  /**
   * 添加加载器
   */
  add<T>(
    key: string,
    loader: () => Promise<T>,
    options: LazyLoadOptions & { order?: number } = {},
  ): LazyDataLoader<T> {
    const lazyLoader = new LazyDataLoader(loader, options)
    this.loaders.set(key, lazyLoader)

    // 处理加载顺序
    if (options.order !== undefined) {
      const insertIndex = this.loadOrder.findIndex((k) => {
        const existingLoader = this.loaders.get(k)
        const existingOrder = (existingLoader as any).options?.order || 0
        return options.order! < existingOrder
      })
      if (insertIndex === -1) {
        this.loadOrder.push(key)
      } else {
        this.loadOrder.splice(insertIndex, 0, key)
      }
    } else {
      this.loadOrder.push(key)
    }

    return lazyLoader
  }

  /**
   * 获取加载器
   */
  get<T>(key: string): LazyDataLoader<T> | undefined {
    return this.loaders.get(key)
  }

  /**
   * 按顺序加载所有数据
   */
  async loadAll(parallel = false): Promise<void> {
    if (parallel) {
      // 并行加载（受请求队列控制）
      await Promise.all(
        Array.from(this.loaders.values()).map((loader) => loader.load()),
      )
    } else {
      // 顺序加载
      for (const key of this.loadOrder) {
        const loader = this.loaders.get(key)
        if (loader) {
          await loader.load()
        }
      }
    }
  }

  /**
   * 加载关键数据（高优先级）
   */
  async loadCritical(): Promise<void> {
    const criticalLoaders = Array.from(this.loaders.entries()).filter(
      ([_, loader]) => (loader as any).options?.priority === 'high',
    )

    await Promise.all(criticalLoaders.map(([_, loader]) => loader.load()))
  }

  /**
   * 延迟加载非关键数据
   */
  async loadNonCritical(delay = 1000): Promise<void> {
    const nonCriticalLoaders = Array.from(this.loaders.entries()).filter(
      ([_, loader]) => (loader as any).options?.priority !== 'high',
    )

    // 延迟后加载
    setTimeout(async () => {
      for (const [_, loader] of nonCriticalLoaders) {
        await loader.load()
      }
    }, delay)
  }

  /**
   * 清除所有数据
   */
  clear() {
    this.loaders.forEach((loader) => loader.clear())
  }

  /**
   * 获取加载状态
   */
  getStatus() {
    const status = {
      total: this.loaders.size,
      loaded: 0,
      loading: 0,
      error: 0,
    }

    this.loaders.forEach((loader) => {
      if (loader.loaded.value) status.loaded++
      else if (loader.loading.value) status.loading++
      else if (loader.error.value) status.error++
    })

    return status
  }
}

/**
 * 数据加载策略枚举
 */
export enum LoadStrategy {
  IMMEDIATE = 'immediate', // 立即加载
  ON_DEMAND = 'on_demand', // 按需加载
  DELAYED = 'delayed', // 延迟加载
  BACKGROUND = 'background', // 后台加载
}

/**
 * 智能加载策略管理器
 */
export class SmartLoadManager {
  private strategies = new Map<string, LoadStrategy>()
  private batchLoader = new BatchLazyLoader()

  /**
   * 设置数据加载策略
   */
  setStrategy(dataKey: string, strategy: LoadStrategy) {
    this.strategies.set(dataKey, strategy)
  }

  /**
   * 注册数据加载器
   */
  register<T>(
    key: string,
    loader: () => Promise<T>,
    strategy: LoadStrategy = LoadStrategy.ON_DEMAND,
    options: LazyLoadOptions = {},
  ): LazyDataLoader<T> {
    this.setStrategy(key, strategy)

    // 根据策略设置选项
    const strategyOptions = this.getOptionsForStrategy(strategy)
    const finalOptions = { ...strategyOptions, ...options }

    return this.batchLoader.add(key, loader, finalOptions)
  }

  /**
   * 根据策略获取选项
   */
  private getOptionsForStrategy(strategy: LoadStrategy): LazyLoadOptions {
    switch (strategy) {
      case LoadStrategy.IMMEDIATE:
        return { priority: 'high', delay: 0 }
      case LoadStrategy.ON_DEMAND:
        return { priority: 'medium', delay: 0 }
      case LoadStrategy.DELAYED:
        return { priority: 'low', delay: 2000 }
      case LoadStrategy.BACKGROUND:
        return { priority: 'low', delay: 5000 }
      default:
        return { priority: 'medium', delay: 0 }
    }
  }

  /**
   * 智能加载数据
   */
  async smartLoad(): Promise<void> {
    // 1. 立即加载关键数据
    await this.loadByStrategy(LoadStrategy.IMMEDIATE)

    // 2. 延迟加载其他数据
    setTimeout(() => this.loadByStrategy(LoadStrategy.DELAYED), 1000)
    setTimeout(() => this.loadByStrategy(LoadStrategy.BACKGROUND), 3000)
  }

  /**
   * 按策略加载数据
   */
  private async loadByStrategy(strategy: LoadStrategy): Promise<void> {
    const keys = Array.from(this.strategies.entries())
      .filter(([_, s]) => s === strategy)
      .map(([key]) => key)

    const promises = keys.map((key) => {
      const loader = this.batchLoader.get(key)
      return loader?.load()
    }).filter(Boolean)

    await Promise.all(promises)
  }

  /**
   * 获取加载器
   */
  get<T>(key: string): LazyDataLoader<T> | undefined {
    return this.batchLoader.get(key)
  }

  /**
   * 获取状态
   */
  getStatus() {
    return {
      batchLoader: this.batchLoader.getStatus(),
      strategies: Object.fromEntries(this.strategies),
    }
  }
}

// 导出全局实例
export const smartLoadManager = new SmartLoadManager()

/**
 * 便捷函数：创建懒加载数据
 */
export function useLazyData<T>(
  loader: () => Promise<T>,
  options: LazyLoadOptions = {},
) {
  return createLazyData(loader, options)
}

/**
 * 便捷函数：注册智能加载数据
 */
export function useSmartLoad<T>(
  key: string,
  loader: () => Promise<T>,
  strategy: LoadStrategy = LoadStrategy.ON_DEMAND,
  options: LazyLoadOptions = {},
) {
  return smartLoadManager.register(key, loader, strategy, options)
}
