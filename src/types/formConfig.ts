/**
 * 高级动态表单配置系统类型定义
 */

// ==================== 字段级配置 (存储在 ProcessLibraryItemParam.jsonConfig) ====================
export type WidgetType =
  | 'input' // 文本输入
  | 'number' // 数字输入
  | 'textarea' // 多行文本
  | 'select' // 下莱选择
  | 'radio' // 单选框
  | 'checkbox' // 复选框组
  | 'date' // 日期选择
  | 'datetime' // 日期时间
  | 'upload' // 文件上传
  | 'text' // 静态文本(只读)
  | 'userSelect' // 人员选择器
  | 'deptSelect' // 部门选择器
  | 'subTable' // 子表单

export interface SubTableColumn {
  key: string
  label: string
  widgetType: Exclude<WidgetType, 'subTable'> // 列控件类型 (不能嵌套子表单)
  width?: string
  required?: boolean
  props?: FieldWidgetConfig['props']
  options?: FieldWidgetConfig['options']
}

export type SubTableRowData = Record<string, any>

export interface SubTableConfig extends FieldWidgetConfig {
  widgetType: 'subTable'
  columns: SubTableColumn[]
  minRows?: number
  maxRows?: number
  showIndex?: boolean
  allowAdd?: boolean
  allowDelete?: boolean
  defaultValue?: SubTableRowData[]
}

export interface FieldWidgetConfig {
  widgetType: WidgetType
  dataType?: 'string' | 'number' | 'date' | 'boolean' | 'array'
  props?: {
    placeholder?: string
    precision?: number
    min?: number
    max?: number
    maxlength?: number
    rows?: number
    clearable?: boolean
    format?: string
    multiple?: boolean
  }
  options?: Array<{
    label: string
    value: string | number
    color?: string
  }>
  validation?: {
    required?: boolean
    pattern?: string
    message?: string
  }
  defaultValue?: any
}

// ==================== 分组级布局配置 (存储在 ProcessLibraryItem.jsonConfig) ====================
export interface TableCell {
  id: string
  rowspan?: number
  colspan?: number
  content: {
    type: 'static' | 'field'
    value: string // 静态文本内容 或 fieldId
  }
  style?: {
    width?: string
    align?: 'left' | 'center' | 'right'
    verticalAlign?: 'top' | 'middle' | 'bottom'
    backgroundColor?: string
    fontWeight?: string
    fontSize?: string
    color?: string
    border?: string
  }
}

export interface FormLayoutConfig {
  layoutType: 'table'
  border: boolean
  rows: Array<{
    height?: string
    cells: TableCell[]
  }>
}
