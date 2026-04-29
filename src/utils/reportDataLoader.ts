/**
 * 报告数据加载优化工具
 */

import { ref, type Ref } from 'vue'
import { SmartLoadManager, LoadStrategy } from './lazyLoader'
import { getCachedData, createCacheKey, versionManager } from './dataCache'
import request from './request'

export interface ReportDataConfig {
  key: string
  url: string
  priority: 'high' | 'medium' | 'low'
  strategy: LoadStrategy
  dependencies?: string[] // 依赖的其他数据
  cacheTTL?: number
  params?: any
}

export interface DashboardQueryParams {
  type: string
  startDate: string
  endDate: string
  salesId?: string
}

// 定义数据加载函数类型
type ReportDataLoaderFn = (params: DashboardQueryParams) => Promise<any>

/**
 * 报告数据加载管理器
 */
export class ReportDataLoader {
  private smartLoader = new SmartLoadManager()
  private loadingStates = new Map<string, Ref<boolean>>()
  private dataStates = new Map<string, Ref<any>>()
  private errorStates = new Map<string, Ref<Error | null>>()

  constructor() {
    this.initializeCommonConfigs()
  }

  /**
   * 初始化通用配置
   */
  private initializeCommonConfigs() {
    // 定义数据加载优先级和策略
    const configs: ReportDataConfig[] = [
      // 高优先级 - 关键数据
      {
        key: 'newCustomer',
        url: '/manage/api/dashboard/getCustomerList',
        priority: 'high',
        strategy: LoadStrategy.IMMEDIATE,
        cacheTTL: 2 * 60 * 1000, // 2分钟缓存
      },
      {
        key: 'workPlanMatch',
        url: '/manage/api/dashboard/getWorkPlanList',
        priority: 'high',
        strategy: LoadStrategy.IMMEDIATE,
        cacheTTL: 2 * 60 * 1000,
      },

      // 中优先级 - 重要数据
      {
        key: 'workingHours',
        url: '/manage/api/dashboard/getWorkingHoursList',
        priority: 'medium',
        strategy: LoadStrategy.ON_DEMAND,
        cacheTTL: 5 * 60 * 1000, // 5分钟缓存
      },
      {
        key: 'workingHoursPlan',
        url: '/manage/api/dashboard/getWorkingHoursPlanList',
        priority: 'medium',
        strategy: LoadStrategy.ON_DEMAND,
        cacheTTL: 5 * 60 * 1000,
      },
      {
        key: 'project',
        url: '/manage/api/dashboard/getProjectList',
        priority: 'medium',
        strategy: LoadStrategy.ON_DEMAND,
        cacheTTL: 3 * 60 * 1000,
      },

      // 低优先级 - 辅助数据
      {
        key: 'projectBusinessType',
        url: '/manage/api/dashboard/getProjectBusinessTypeList',
        priority: 'low',
        strategy: LoadStrategy.DELAYED,
        dependencies: ['project'],
        cacheTTL: 10 * 60 * 1000, // 10分钟缓存
      },
      {
        key: 'projectProductService',
        url: '/manage/api/dashboard/getProjectProductServiceList',
        priority: 'low',
        strategy: LoadStrategy.DELAYED,
        dependencies: ['project'],
        cacheTTL: 10 * 60 * 1000,
      },
      {
        key: 'opticsFollowUp',
        url: '/manage/api/dashboard/getOpticsFollowUpList',
        priority: 'low',
        strategy: LoadStrategy.BACKGROUND,
        cacheTTL: 15 * 60 * 1000,
      },
      {
        key: 'projectFollowUp',
        url: '/manage/api/dashboard/getProjectFollowUpList',
        priority: 'low',
        strategy: LoadStrategy.BACKGROUND,
        cacheTTL: 15 * 60 * 1000,
      },
      {
        key: 'projectPhaseAmount',
        url: '/manage/api/dashboard/getProjectPhaseAmountList',
        priority: 'low',
        strategy: LoadStrategy.BACKGROUND,
        cacheTTL: 15 * 60 * 1000,
      },
    ]

    // 注册所有配置
    configs.forEach((config) => {
      this.registerDataLoader(config)
    })
  }

  /**
   * 注册数据加载器
   */
  registerDataLoader(config: ReportDataConfig) {
    // 创建状态
    this.loadingStates.set(config.key, ref(false))
    this.dataStates.set(config.key, ref(null))
    this.errorStates.set(config.key, ref(null))

    // 创建加载函数
    const loader = async (): Promise<ReportDataLoaderFn> => this.createDataLoader(config)

    // 注册到智能加载管理器
    this.smartLoader.register<ReportDataLoaderFn>(config.key, loader, config.strategy, {
      priority: config.priority,
      cache: true,
      cacheKey: config.key,
    })
  }

  /**
   * 创建数据加载器
   */
  private createDataLoader(config: ReportDataConfig) {
    return async (params: DashboardQueryParams) => {
      const loadingState = this.loadingStates.get(config.key)!
      const dataState = this.dataStates.get(config.key)!
      const errorState = this.errorStates.get(config.key)!

      loadingState.value = true
      errorState.value = null

      try {
        // 创建缓存键
        const cacheKey = createCacheKey(
          config.key,
          params.type,
          params.startDate,
          params.endDate,
          params.salesId || 'all',
        )

        // 获取数据版本
        const version = versionManager.getVersion(config.key)

        // 使用缓存获取数据
        const data = await getCachedData(
          cacheKey,
          () => this.makeRequest(config.url, params),
          {
            ttl: config.cacheTTL,
            version,
          },
        )

        dataState.value = data
        return data
      } catch (error) {
        console.error(`加载 ${config.key} 数据失败:`, error)
        errorState.value = error as Error
        dataState.value = null
        throw error
      } finally {
        loadingState.value = false
      }
    }
  }

  /**
   * 发起API请求
   */
  private async makeRequest(url: string, params: DashboardQueryParams) {
    console.log(`API请求: ${url}`, params)
    
    const result = await request.get(url, params, {
      priority: 'medium',
      useQueue: true,
    })

    if (result.code === 200 && result.data) {
      return result.data
    } else {
      throw new Error(result.msg || 'API请求失败')
    }
  }

  /**
   * 加载报告数据（智能策略）
   */
  async loadReportData(
    reportType: 'daily' | 'weekly' | 'monthly' | 'yearly',
    params: DashboardQueryParams,
  ): Promise<void> {
    console.log(`开始加载${reportType}报告数据...`)

    // 设置数据版本（基于报告类型和时间）
    const version = `${reportType}_${params.startDate}_${params.endDate}`
    Object.keys(this.dataStates).forEach((key) => {
      versionManager.setVersion(key, version)
    })

    try {
      // 1. 立即加载关键数据
      await this.loadCriticalData(params)

      // 2. 延迟加载其他数据
      this.loadNonCriticalData(params)

      console.log(`${reportType}报告关键数据加载完成`)
    } catch (error) {
      console.error(`${reportType}报告数据加载失败:`, error)
      throw error
    }
  }

  /**
   * 加载关键数据
   */
  private async loadCriticalData(params: DashboardQueryParams): Promise<void> {
    const criticalKeys = ['newCustomer', 'workPlanMatch']
    
    const promises = criticalKeys.map(async (key) => {
      const loader = this.smartLoader.get<ReportDataLoaderFn>(key)
      if (loader) {
        const dataLoader = await loader.load()
        return dataLoader(params)
      }
    })

    await Promise.all(promises.filter(Boolean))
  }

  /**
   * 延迟加载非关键数据
   */
  private loadNonCriticalData(params: DashboardQueryParams): void {
    const nonCriticalKeys = [
      'workingHours',
      'workingHoursPlan',
      'project',
      'projectBusinessType',
      'projectProductService',
      'opticsFollowUp',
      'projectFollowUp',
      'projectPhaseAmount',
    ]

    // 分批加载，避免并发过多
    const batchSize = 3
    const batches: string[][] = []
    
    for (let i = 0; i < nonCriticalKeys.length; i += batchSize) {
      batches.push(nonCriticalKeys.slice(i, i + batchSize))
    }

    // 逐批加载，每批间隔1秒
    batches.forEach((batch, index) => {
      setTimeout(async () => {
        const promises = batch.map(async (key) => {
          try {
            const loader = this.smartLoader.get<ReportDataLoaderFn>(key)
            if (loader) {
              const dataLoader = await loader.load()
              return dataLoader(params)
            }
          } catch (error) {
            console.warn(`加载 ${key} 数据失败:`, error)
          }
        })

        await Promise.all(promises.filter(Boolean))
        console.log(`批次 ${index + 1} 数据加载完成:`, batch)
      }, (index + 1) * 1000)
    })
  }

  /**
   * 获取数据状态
   */
  getDataState(key: string) {
    return {
      loading: this.loadingStates.get(key),
      data: this.dataStates.get(key),
      error: this.errorStates.get(key),
    }
  }

  /**
   * 获取所有数据状态
   */
  getAllDataStates() {
    const states: Record<string, any> = {}
    
    this.dataStates.forEach((data, key) => {
      states[key] = {
        loading: this.loadingStates.get(key)?.value || false,
        data: data.value,
        error: this.errorStates.get(key)?.value,
        hasData: data.value !== null,
      }
    })

    return states
  }

  /**
   * 强制刷新数据
   */
  async refreshData(key: string, params: DashboardQueryParams): Promise<void> {
    // 增加版本号以失效缓存
    versionManager.incrementVersion(key)
    
    const loader = this.smartLoader.get<ReportDataLoaderFn>(key)
    if (loader) {
      const dataLoader = await loader.load(true) // 强制重新加载
      await dataLoader(params)
    }
  }

  /**
   * 清理所有数据
   */
  clearAllData(): void {
    this.dataStates.forEach((data) => {
      data.value = null
    })
    this.errorStates.forEach((error) => {
      error.value = null
    })
  }

  /**
   * 获取加载统计
   */
  getLoadingStats() {
    const stats = {
      total: this.dataStates.size,
      loading: 0,
      loaded: 0,
      error: 0,
      empty: 0,
    }

    this.dataStates.forEach((data, key) => {
      const loading = this.loadingStates.get(key)?.value || false
      const error = this.errorStates.get(key)?.value

      if (loading) {
        stats.loading++
      } else if (error) {
        stats.error++
      } else if (data.value) {
        stats.loaded++
      } else {
        stats.empty++
      }
    })

    return stats
  }
}

// 创建全局实例
export const reportDataLoader = new ReportDataLoader()

/**
 * 便捷函数：为报告Store创建懒加载数据
 */
export function createReportDataLoader(reportType: 'daily' | 'weekly' | 'monthly' | 'yearly') {
  return {
    async loadData(params: DashboardQueryParams) {
      return reportDataLoader.loadReportData(reportType, params)
    },

    getDataState(key: string) {
      return reportDataLoader.getDataState(key)
    },

    getAllStates() {
      return reportDataLoader.getAllDataStates()
    },

    async refreshData(key: string, params: DashboardQueryParams) {
      return reportDataLoader.refreshData(key, params)
    },

    clearData() {
      reportDataLoader.clearAllData()
    },

    getStats() {
      return reportDataLoader.getLoadingStats()
    },
  }
}
