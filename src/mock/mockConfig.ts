/**
 * Mock数据配置
 * 控制是否使用模拟数据
 */

// 全局Mock开关 - 设置为true时使用模拟数据,false时调用真实API
export const MOCK_ENABLED = false

// 模拟API延迟(毫秒) - 模拟网络请求延迟
export const MOCK_DELAY = 300

// 各模块Mock开关 - 可以单独控制每个模块
export const MOCK_MODULES = {
  auth: true, // 登录认证
  user: true, // 用户管理
  task: true, // 任务管理
  planning: true, // 计划排程
  process: true, // 工艺技术
  production: true, // 生产执行
  quality: true, // 质量监督
  dashboard: true, // 信息看板
  system: true, // 系统管理
}

// 模拟延迟函数
export const mockDelay = (ms: number = MOCK_DELAY): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

// 生成唯一ID
export const generateId = (): string => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 生成指定范围的随机整数
export const randomInt = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

// 从数组中随机选择一个元素
export const randomPick = <T>(arr: T[]): T => {
  return arr[Math.floor(Math.random() * arr.length)]
}

// 生成随机日期(指定天数范围内)
export const randomDate = (daysAgo: number = 30): string => {
  const date = new Date()
  date.setDate(date.getDate() - randomInt(0, daysAgo))
  return date.toISOString().split('T')[0]
}

// 格式化日期时间
export const formatDateTime = (date: Date = new Date()): string => {
  return date.toISOString().replace('T', ' ').substring(0, 19)
}
