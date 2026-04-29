import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getMenuTreeApi, getRoleMenuIdsApi } from '@/api/system/menu'
import { mesMenuConfig } from '@/config/menuConfig'
import { isFrameworkEnabledRoute } from '@/config/frameworkConfig'
import type { MenuItem } from '@/config/menuConfig'
import type { MenuNode } from '@/types/system/menu'
import { getStoredUserRoleIds } from '@/utils/auth'

export interface NavMenuItem {
  id: string
  title: string
  path?: string
  icon?: string
  children?: NavMenuItem[]
}

/**
 * 一级菜单图标映射（后端 icon 字段基本为 null，前端按名称补全）
 */
const MENU_ICON_MAP: Record<string, string> = {
  首页: 'HomeFilled',
  本地基础CRUD: 'List',
  项目管理示例: 'FolderOpened',
  采购订单示例: 'ShoppingCart',
  库存管理示例: 'DataBoard',
  销售管理: 'DataLine',
  生产执行: 'Files',
  任务管理: 'Document',
  计划排程管理: 'Calendar',
  工艺技术管理: 'Files',
  执行管理: 'Setting',
  生产执行管理: 'Setting',
  质量监督管理: 'CircleCheck',
  系统管理: 'Setting',
  信息发布与展示看板: 'DataAnalysis',
  生产协作: 'Connection',
  综合展示: 'Monitor',
}

/**
 * 一级菜单排序权重（数字越小越靠前）
 */
const MENU_ORDER_MAP: Record<string, number> = {
  首页: 0,
  本地基础CRUD: 1,
  项目管理示例: 2,
  采购订单示例: 3,
  库存管理示例: 4,
  销售管理: 5,
  生产执行: 6,
  系统管理: 7,
  任务管理: 1,
  计划排程管理: 2,
  工艺技术管理: 3,
  执行管理: 4,
  生产执行管理: 4,
  质量监督管理: 5,
  信息发布与展示看板: 6,
  生产协作: 7,
  综合展示: 8,
}

function resolveIcon(node: MenuNode): string | undefined {
  if (node.icon && node.icon !== 'monitor') return node.icon
  return MENU_ICON_MAP[node.label] || MENU_ICON_MAP[node.name] || undefined
}

function normalizePath(raw?: string | null): string | undefined {
  if (!raw) return undefined
  const trimmed = raw.trim()
  if (!trimmed) return undefined
  return trimmed.startsWith('/') ? trimmed : `/${trimmed}`
}

function isFrameworkPath(path?: string): boolean {
  const normalizedPath = normalizePath(path)
  if (!normalizedPath) return false
  return isFrameworkEnabledRoute(normalizedPath)
}

function getMenuOrder(title: string): number {
  return MENU_ORDER_MAP[title] ?? 50
}

function collectVisiblePaths(items: MenuItem[]): Set<string> {
  const result = new Set<string>()
  for (const item of items) {
    if (!item.hidden) {
      const normalizedPath = normalizePath(item.path)
      if (normalizedPath) {
        result.add(normalizedPath)
      }
    }
    if (item.children?.length) {
      const childPaths = collectVisiblePaths(item.children)
      childPaths.forEach((path) => result.add(path))
    }
  }
  return result
}

const ENABLED_MENU_PATHS = collectVisiblePaths(mesMenuConfig)

/**
 * 用允许的菜单 ID 集合过滤完整菜单树
 * 如果父节点 ID 在集合中，则保留该父节点；子节点也递归过滤
 * 保留有可见子节点的父节点（即使父节点 ID 不在集合中）
 */
function filterTreeByIds(nodes: MenuNode[], allowedIds: Set<string>): MenuNode[] {
  const result: MenuNode[] = []

  for (const node of nodes) {
    const nodeIdStr = String(node.id)
    const selfAllowed = allowedIds.has(nodeIdStr)

    const filteredChildren = node.children ? filterTreeByIds(node.children, allowedIds) : undefined
    const hasVisibleChildren = filteredChildren && filteredChildren.length > 0

    if (selfAllowed || hasVisibleChildren) {
      result.push({
        ...node,
        children: hasVisibleChildren ? filteredChildren : node.children ? [] : undefined,
      })
    }
  }

  return result
}

/**
 * 把后端 MenuNode 树转成前端导航所需的 NavMenuItem 树
 * - 只保留 type="0" 的菜单项（type="1" 是页内 Tab，不显示在导航）
 * - 路径归一化：补全缺少的前导 /
 */
function transformMenuTree(nodes: MenuNode[]): NavMenuItem[] {
  const result: NavMenuItem[] = []

  for (const node of nodes) {
    if (node.type !== '0') continue

    const children = node.children ? transformMenuTree(node.children) : undefined
    const hasVisibleChildren = children && children.length > 0

    const path = normalizePath(node.path)
    if (path === '/') continue

    result.push({
      id: node.id,
      title: node.label || node.name,
      path: path || undefined,
      icon: resolveIcon(node),
      children: hasVisibleChildren ? children : undefined,
    })
  }

  return result
}

function filterFrameworkNavMenus(menus: NavMenuItem[]): NavMenuItem[] {
  const result: NavMenuItem[] = []

  for (const menu of menus) {
    const filteredChildren = menu.children?.length
      ? filterFrameworkNavMenus(menu.children)
      : undefined
    const normalizedPath = normalizePath(menu.path)
    const keepCurrent =
      !!normalizedPath && isFrameworkPath(normalizedPath) && ENABLED_MENU_PATHS.has(normalizedPath)
    const keepByChildren = !!filteredChildren && filteredChildren.length > 0

    if (keepCurrent || keepByChildren) {
      result.push({
        ...menu,
        children: keepByChildren ? filteredChildren : undefined,
      })
    }
  }

  return result
}

export const useMenuStore = defineStore('menu', () => {
  const rawMenuTree = ref<MenuNode[]>([])
  const allowedMenuIds = ref<Set<string>>(new Set())
  const loading = ref(false)
  const loaded = ref(false)
  const permissionResolved = ref(false)

  const navMenus = computed<NavMenuItem[]>(() => {
    const homeItem: NavMenuItem = {
      id: 'home',
      title: '首页',
      path: '/',
      icon: 'HomeFilled',
    }

    if (rawMenuTree.value.length === 0) return [homeItem]

    // 权限尚未解析时短暂展示完整菜单，解析完成后收敛到授权菜单
    const canUseAllMenus = !permissionResolved.value
    const hasAllowedMenus = allowedMenuIds.value.size > 0

    let filteredTree: MenuNode[]
    if (canUseAllMenus) {
      filteredTree = rawMenuTree.value
    } else if (hasAllowedMenus) {
      filteredTree = filterTreeByIds(rawMenuTree.value, allowedMenuIds.value)
    } else {
      filteredTree = []
    }

    const menus = transformMenuTree(filteredTree)
    menus.sort((a, b) => getMenuOrder(a.title) - getMenuOrder(b.title))

    const frameworkMenus = filterFrameworkNavMenus(menus)
    const navItems = [
      homeItem,
      ...frameworkMenus.filter((menu) => normalizePath(menu.path) !== '/'),
    ]
    const dedupedNavItems: NavMenuItem[] = []
    const seen = new Set<string>()
    for (const item of navItems) {
      const key = `${item.id}::${normalizePath(item.path)}`
      if (seen.has(key)) continue
      seen.add(key)
      dedupedNavItems.push(item)
    }
    return dedupedNavItems
  })

  /**
   * 从 localStorage 获取当前用户的角色 ID 列表
   */
  function getUserRoleIds(): string[] {
    return getStoredUserRoleIds()
  }

  /**
   * 加载完整菜单树 + 按用户角色获取可访问菜单 ID → 过滤
   */
  const fetchMenuTree = async () => {
    if (loading.value) return
    loading.value = true
    permissionResolved.value = false

    try {
      // 1. 获取完整菜单树
      const treeRes = await getMenuTreeApi()
      if (!((treeRes.code === 0 || treeRes.code === 200) && Array.isArray(treeRes.data))) {
        rawMenuTree.value = []
        allowedMenuIds.value = new Set()
        permissionResolved.value = true
        loaded.value = true
        return
      }
      rawMenuTree.value = treeRes.data

      // 2. 获取用户角色对应的菜单 ID
      const roleIds = getUserRoleIds()
      const mergedIds = new Set<string>()
      if (roleIds.length > 0) {
        const idResults = await Promise.all(
          roleIds.map((rid) => getRoleMenuIdsApi(rid).catch(() => null)),
        )

        for (const res of idResults) {
          if (res && (res.code === 0 || res.code === 200) && Array.isArray(res.data)) {
            res.data.forEach((id: string) => mergedIds.add(String(id)))
          }
        }
      }

      allowedMenuIds.value = mergedIds
      permissionResolved.value = true
      loaded.value = true
    } catch (error) {
      console.error('获取菜单树失败:', error)
      rawMenuTree.value = []
      allowedMenuIds.value = new Set()
      permissionResolved.value = true
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  /**
   * 在菜单树中按 label 递归查找节点
   */
  function findNodeByLabel(nodes: MenuNode[], label: string): MenuNode | null {
    for (const node of nodes) {
      if (node.label === label || node.name === label) return node
      if (node.children) {
        const found = findNodeByLabel(node.children, label)
        if (found) return found
      }
    }
    return null
  }

  /**
   * 获取某父菜单下所有被允许的 type="1" 子节点 label 集合。
   * 各页面拿到此集合后用精确匹配判断 tab 是否可见。
   * @param parentLabel 父菜单的 label（如"任务管理"）
   */
  function getPermittedTabs(parentLabel: string): Set<string> {
    if (!permissionResolved.value || allowedMenuIds.value.size === 0) return new Set()

    const parent = findNodeByLabel(rawMenuTree.value, parentLabel)
    if (!parent?.children) return new Set()

    const result = new Set<string>()
    for (const child of parent.children) {
      if (child.type !== '1') continue
      if (allowedMenuIds.value.has(String(child.id))) {
        result.add(child.label || child.name)
      }
    }
    return result
  }

  /**
   * 直接按菜单 ID 检查是否在当前角色的允许列表中。
   */
  function isMenuIdAllowed(menuId: string): boolean {
    if (!permissionResolved.value) return true
    if (allowedMenuIds.value.size === 0) return false
    return allowedMenuIds.value.has(menuId)
  }

  const reset = () => {
    rawMenuTree.value = []
    allowedMenuIds.value = new Set()
    loaded.value = false
    permissionResolved.value = false
  }

  return {
    rawMenuTree,
    allowedMenuIds,
    navMenus,
    loading,
    loaded,
    permissionResolved,
    fetchMenuTree,
    getPermittedTabs,
    isMenuIdAllowed,
    reset,
  }
})
