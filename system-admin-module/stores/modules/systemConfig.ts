import { defineStore } from 'pinia'
import { ref } from 'vue'
import request from '../../utils/request'
import { ElMessage } from 'element-plus'

// 系统配置数据接口
export interface SystemConfigData {
  companyName: string
  systemName: string
  version: string
}

// 更新配置的请求接口
export interface UpdateConfigRequest {
  id: number
  code: string
  value: string
}

// 配置项的代码常量
export const CONFIG_CODES = {
  COMPANY_NAME: 'companyName',
  SYSTEM_NAME: 'systemName',
  VERSION: 'version',
}

export const useSystemConfigStore = defineStore('systemConfig', () => {
  // 系统配置数据
  const configData = ref<SystemConfigData>({
    companyName: '',
    systemName: 'GK-MES系统',
    version: '1.0.0',
  })

  // 加载状态
  const loading = ref(false)

  // 是否已加载
  const hasLoaded = ref(false)

  /**
   * 获取系统默认配置信息
   */
  const fetchSystemConfig = async () => {
    loading.value = true
    try {
      const response = await request.get<SystemConfigData>(
        '/manage/api/systemConfig/getSystemDefaultData',
      )
      if (response.code === 200 && response.data) {
        configData.value = {
          companyName: response.data.companyName || '',
          systemName: response.data.systemName || 'GK-MES系统',
          version: response.data.version || '1.0.0',
        }
        hasLoaded.value = true

        // 缓存到 localStorage
        localStorage.setItem('systemConfig', JSON.stringify(configData.value))
      } else {
        console.error('获取系统配置失败:', response.msg)
      }
    } catch (error) {
      console.error('获取系统配置时发生错误:', error)
      // 尝试从 localStorage 恢复
      restoreFromLocalStorage()
    } finally {
      loading.value = false
    }
  }

  /**
   * 更新系统配置
   */
  const updateSystemConfig = async (code: string, value: string): Promise<boolean> => {
    loading.value = true
    try {
      const payload: UpdateConfigRequest = {
        id: 0, // 后端会根据 code 查找
        code,
        value,
      }

      const response = await request.put('/manage/api/systemConfig/update', payload)
      if (response.code === 200) {
        // 更新本地状态
        switch (code) {
          case CONFIG_CODES.COMPANY_NAME:
            configData.value.companyName = value
            break
          case CONFIG_CODES.SYSTEM_NAME:
            configData.value.systemName = value
            break
          case CONFIG_CODES.VERSION:
            configData.value.version = value
            break
        }

        // 更新 localStorage
        localStorage.setItem('systemConfig', JSON.stringify(configData.value))

        ElMessage.success('配置更新成功')
        return true
      } else {
        ElMessage.error(`配置更新失败: ${response.msg || '未知错误'}`)
        return false
      }
    } catch (error) {
      console.error('更新系统配置时发生错误:', error)
      ElMessage.error('更新系统配置时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 批量更新系统配置
   */
  const updateAllConfigs = async (configs: SystemConfigData): Promise<boolean> => {
    loading.value = true
    try {
      const updates = [
        { code: CONFIG_CODES.COMPANY_NAME, value: configs.companyName },
        { code: CONFIG_CODES.SYSTEM_NAME, value: configs.systemName },
        { code: CONFIG_CODES.VERSION, value: configs.version },
      ]

      const results = await Promise.all(
        updates.map((update) =>
          request.put('/manage/api/systemConfig/update', {
            id: 0,
            code: update.code,
            value: update.value,
          }),
        ),
      )

      const allSuccess = results.every((res) => res.code === 200)
      if (allSuccess) {
        configData.value = { ...configs }
        localStorage.setItem('systemConfig', JSON.stringify(configData.value))
        ElMessage.success('系统配置保存成功')
        return true
      } else {
        ElMessage.error('部分配置更新失败')
        // 重新获取最新配置
        await fetchSystemConfig()
        return false
      }
    } catch (error) {
      console.error('批量更新系统配置时发生错误:', error)
      ElMessage.error('更新系统配置时发生网络错误')
      return false
    } finally {
      loading.value = false
    }
  }

  /**
   * 从 localStorage 恢复配置
   */
  const restoreFromLocalStorage = () => {
    const stored = localStorage.getItem('systemConfig')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        configData.value = {
          companyName: parsed.companyName || '',
          systemName: parsed.systemName || 'GK-MES系统',
          version: parsed.version || '1.0.0',
        }
        hasLoaded.value = true
      } catch (e) {
        console.error('解析 localStorage 中的系统配置失败:', e)
      }
    }
  }

  /**
   * 初始化 - 先从 localStorage 恢复，然后从服务器获取最新
   */
  const initialize = async () => {
    // 先从 localStorage 恢复，保证快速显示
    restoreFromLocalStorage()
    // 然后从服务器获取最新配置
    await fetchSystemConfig()
  }

  return {
    configData,
    loading,
    hasLoaded,
    fetchSystemConfig,
    updateSystemConfig,
    updateAllConfigs,
    initialize,
    restoreFromLocalStorage,
  }
})
