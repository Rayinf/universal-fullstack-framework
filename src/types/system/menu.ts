export interface MenuNode {
  id: string
  parentId: string
  weight?: number
  name: string
  path?: string | null
  keepAlive?: string
  sortOrder?: number
  icon?: string | null
  permission?: string | null
  label: string
  type: string // "0" = 菜单/页面, "1" = 页内Tab/按钮
  children?: MenuNode[]
}

export interface MenuQuery {
  lazy?: boolean
  parentId?: number
}
