/**
 * 日期处理工具函数 - 避免时区偏移问题
 */

/**
 * 安全的日期转换函数，避免时区偏移
 * 将各种日期格式转换为 YYYY-MM-DD 格式
 */
export const safeDateToLocalString = (dateStr: string): string => {
  if (!dateStr) return ''

  try {
    // 如果是 YYYY-MM-DD 格式，直接返回
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr
    }

    // 如果是 YYYY-MM-DD HH:mm:ss 格式，提取日期部分
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$/.test(dateStr)) {
      return dateStr.split(' ')[0]
    }

    // 如果是 ISO 格式，提取日期部分
    if (dateStr.includes('T')) {
      return dateStr.split('T')[0]
    }

    // 对于其他格式，尝试解析但避免时区偏移
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return ''

    // 使用本地日期组件来避免时区偏移
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch (error) {
    console.warn('日期转换失败:', dateStr, error)
    return ''
  }
}

/**
 * 安全的日期时间转换函数，避免时区偏移
 * 将各种日期时间格式转换为 YYYY-MM-DD HH:mm 格式
 */
export const safeDateTimeToLocalString = (dateStr: string): string => {
  if (!dateStr) return ''

  try {
    // 如果是 YYYY-MM-DD HH:mm 格式，直接返回
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$/.test(dateStr)) {
      return dateStr
    }

    // 如果是 YYYY-MM-DD HH:mm:ss 格式，截取到分钟
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$/.test(dateStr)) {
      return dateStr.slice(0, 16)
    }

    // 如果是 ISO 格式，转换为本地时间格式
    if (dateStr.includes('T')) {
      const date = new Date(dateStr)
      if (isNaN(date.getTime())) return ''

      // 使用本地时间组件来避免时区偏移
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hours}:${minutes}`
    }

    // 对于其他格式，尝试解析
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return ''

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  } catch (error) {
    console.warn('日期时间转换失败:', dateStr, error)
    return ''
  }
}

/**
 * 格式化日期为后端接受的格式（YYYY-MM-DD HH:mm:ss）
 * 避免时区偏移问题
 */
export const formatDateTimeForAPI = (dateStr: string): string => {
  if (!dateStr) return ''
  
  try {
    // 如果已经是 YYYY-MM-DD 格式，添加时间部分
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return `${dateStr} 00:00:00`
    }
    
    // 如果是 YYYY-MM-DD HH:mm 格式，添加秒部分
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$/.test(dateStr)) {
      return `${dateStr}:00`
    }
    
    // 如果已经是完整的日期时间格式，直接返回
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$/.test(dateStr)) {
      return dateStr
    }
    
    // 对于其他格式，转换为本地日期时间
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return ''
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    const seconds = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
  } catch (error) {
    console.warn('日期时间格式化失败:', dateStr, error)
    return ''
  }
}

/**
 * 格式化日期为后端接受的格式（YYYY-MM-DD）
 * 避免时区偏移问题
 */
export const formatDateForAPI = (dateStr: string): string => {
  if (!dateStr) return ''
  
  try {
    // 如果已经是 YYYY-MM-DD 格式，直接返回
    if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) {
      return dateStr
    }
    
    // 如果是 YYYY-MM-DD HH:mm:ss 格式，提取日期部分
    if (/^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$/.test(dateStr)) {
      return dateStr.split(' ')[0]
    }
    
    // 如果是 ISO 格式，提取日期部分
    if (dateStr.includes('T')) {
      return dateStr.split('T')[0]
    }
    
    // 对于其他格式，转换为本地日期
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return ''
    
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  } catch (error) {
    console.warn('日期格式化失败:', dateStr, error)
    return ''
  }
}

/**
 * 获取当前日期（YYYY-MM-DD 格式）
 */
export const getCurrentDate = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

/**
 * 获取当前日期时间（YYYY-MM-DD HH:mm:ss 格式）
 */
export const getCurrentDateTime = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

/**
 * 获取当前月份（YYYY-MM 格式）
 */
export const getCurrentMonth = (): string => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  return `${year}-${month}`
}

/**
 * 日期比较函数
 */
export const compareDates = (date1: string, date2: string): number => {
  const d1 = new Date(safeDateToLocalString(date1))
  const d2 = new Date(safeDateToLocalString(date2))
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) {
    return 0
  }
  
  return d1.getTime() - d2.getTime()
}

/**
 * 检查日期是否有效
 */
export const isValidDate = (dateStr: string): boolean => {
  if (!dateStr) return false
  
  try {
    const date = new Date(dateStr)
    return !isNaN(date.getTime())
  } catch {
    return false
  }
}

/**
 * 日期范围验证
 */
export const isDateInRange = (
  dateStr: string, 
  startDate: string, 
  endDate: string
): boolean => {
  const date = safeDateToLocalString(dateStr)
  const start = safeDateToLocalString(startDate)
  const end = safeDateToLocalString(endDate)
  
  if (!date || !start || !end) return false
  
  return date >= start && date <= end
}
