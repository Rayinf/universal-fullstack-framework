// 月内周期数据结构
export interface WeekPeriod {
  startDate: Date
  endDate: Date
  label: string
  value: string
}

// 其他通用类型可以在这里添加
export interface DateRange {
  startDate: string
  endDate: string
}
