import { scaffoldedMenuRegistry } from '@/config/scaffoldMenuRegistry'

/**
 * 基础框架菜单配置
 * 当前启用系统管理 + 销售管理 + 生产执行，支持逐步扩展。
 */

export interface MenuItem {
  id: string
  title: string
  path?: string
  icon?: string
  children?: MenuItem[]
  functionCode?: string
  hidden?: boolean
  roles?: string[]
}

export const mesMenuConfig: MenuItem[] = [
  {
    id: 'home',
    title: '首页',
    path: '/',
    icon: 'HomeFilled',
    functionCode: 'FRAMEWORK-HOME',
  },
  {
    id: 'basic-crud',
    title: '本地基础CRUD',
    path: '/system/basic-crud',
    icon: 'List',
    functionCode: 'SRS-FUNC-00011-LOCAL-CRUD',
  },
  {
    id: 'project-demo',
    title: '项目管理示例',
    path: '/system/project-demo',
    icon: 'FolderOpened',
    functionCode: 'SRS-FUNC-00011-LOCAL-PROJECT',
  },
  {
    id: 'purchase-demo',
    title: '采购订单示例',
    path: '/system/purchase-demo',
    icon: 'ShoppingCart',
    functionCode: 'SRS-FUNC-00011-LOCAL-PURCHASE',
  },
  {
    id: 'inventory-demo',
    title: '库存管理示例',
    path: '/system/inventory-demo',
    icon: 'DataBoard',
    functionCode: 'SRS-FUNC-00011-LOCAL-INVENTORY',
  },
  ...scaffoldedMenuRegistry.root,
  {
    id: 'system',
    title: '系统管理',
    icon: 'Setting',
    functionCode: 'SRS-FUNC-00011',
    children: [
      {
        id: 'system-org',
        title: '组织架构管理',
        path: '/system/dept-management',
        icon: 'OfficeBuilding',
        functionCode: 'SRS-FUNC-00011-1',
      },
      {
        id: 'system-account',
        title: '账户管理',
        path: '/system/account-management',
        icon: 'User',
        functionCode: 'SRS-FUNC-00011-2-3-4',
      },
      {
        id: 'system-customer',
        title: '客户管理',
        path: '/system/customers',
        icon: 'Avatar',
        functionCode: 'SRS-FUNC-00011-14',
      },
      {
        id: 'system-role',
        title: '用户角色管理',
        path: '/system/role',
        icon: 'Key',
        functionCode: 'SRS-FUNC-00011-5',
      },
      {
        id: 'system-workstation',
        title: '工位与设备管理',
        path: '/system/workstation',
        icon: 'Cpu',
        functionCode: 'SRS-FUNC-00011-6',
        children: [
          {
            id: 'system-workstation-info',
            title: '工位信息管理',
            path: '/system/workstation/info',
            functionCode: 'SRS-FUNC-00011-6.1',
          },
          {
            id: 'system-equipment',
            title: '设备基础信息管理',
            path: '/system/workstation/equipment',
            functionCode: 'SRS-FUNC-00011-6.2',
          },
        ],
      },
      {
        id: 'system-param',
        title: '参数与字典',
        path: '/system/param',
        icon: 'Notebook',
        functionCode: 'SRS-FUNC-00011-7',
        children: [
          {
            id: 'system-param-manage',
            title: '参数管理',
            path: '/system/param/manage',
            functionCode: 'SRS-FUNC-00011-7.1',
          },
          {
            id: 'system-param-code',
            title: '编码规则配置',
            path: '/system/param/code',
            functionCode: 'SRS-FUNC-00011-7.2',
          },
        ],
      },
      {
        id: 'system-approval',
        title: '业务相关审批规则',
        path: '/system/approval',
        icon: 'Stamp',
        functionCode: 'SRS-FUNC-00011-8',
      },
      {
        id: 'system-operation-log',
        title: '系统日志管理',
        path: '/system/operation-log',
        icon: 'Monitor',
        functionCode: 'SRS-FUNC-00011-9',
      },
      {
        id: 'system-user-log',
        title: '用户日志管理',
        path: '/system/user-log',
        icon: 'Reading',
        functionCode: 'SRS-FUNC-00011-10',
      },
      {
        id: 'system-backup',
        title: '数据与系统备份',
        path: '/system/backup',
        icon: 'Coin',
        functionCode: 'SRS-FUNC-00011-13',
      },
      {
        id: 'system-config',
        title: '系统基础配置',
        path: '/system/system-config',
        icon: 'Operation',
        functionCode: 'SRS-FUNC-00011-11',
      },
      {
        id: 'system-notifications',
        title: '消息通知',
        path: '/system/notifications',
        icon: 'Bell',
        functionCode: 'SRS-FUNC-00011-NOTIFY',
      },
      ...scaffoldedMenuRegistry.system,
      {
        id: 'system-profile',
        title: '个人中心',
        path: '/system/profile',
        icon: 'UserFilled',
        hidden: true,
      },
    ],
  },
  {
    id: 'sales',
    title: '销售管理',
    icon: 'DataLine',
    children: [
      {
        id: 'sales-product-catalog',
        title: '产品目录管理',
        path: '/sales/product-catalog',
        icon: 'Goods',
        functionCode: 'SRS-FUNC-00011-LOCAL-PRODUCT',
      },
      {
        id: 'sales-quotation',
        title: '报价单管理',
        path: '/sales/quotation',
        icon: 'Money',
        functionCode: 'SRS-FUNC-00011-LOCAL-QUOTATION',
      },
      {
        id: 'sales-contracts',
        title: '合同管理',
        path: '/sales/contracts',
        icon: 'Collection',
        functionCode: 'SRS-FUNC-00011-LOCAL-CONTRACT',
      },
      {
        id: 'sales-payments',
        title: '回款跟踪',
        path: '/sales/payments',
        icon: 'Wallet',
        functionCode: 'SRS-FUNC-00011-LOCAL-PAYMENT',
      },
      {
        id: 'sales-commissions',
        title: '佣金计算',
        path: '/sales/commissions',
        icon: 'TrendCharts',
        functionCode: 'SRS-FUNC-00011-LOCAL-COMMISSION',
      },
      {
        id: 'sales-contract-dashboard',
        title: '合同业务看板',
        path: '/sales/contract-dashboard',
        icon: 'DataAnalysis',
        functionCode: 'SRS-FUNC-00011-LOCAL-CONTRACT-DASHBOARD',
      },
      ...scaffoldedMenuRegistry.sales,
    ],
  },
  {
    id: 'production',
    title: '生产执行',
    icon: 'Files',
    children: [
      {
        id: 'production-work-orders',
        title: '生产工单管理',
        path: '/production/work-orders',
        icon: 'Tickets',
        functionCode: 'SRS-FUNC-00011-LOCAL-WORK-ORDER',
      },
      {
        id: 'production-work-reports',
        title: '工序报工',
        path: '/production/work-reports',
        icon: 'Clock',
        functionCode: 'SRS-FUNC-00011-LOCAL-WORK-REPORT',
      },
      {
        id: 'production-work-inbounds',
        title: '完工入库',
        path: '/production/work-inbounds',
        icon: 'SoldOut',
        functionCode: 'SRS-FUNC-00011-LOCAL-WORK-INBOUND',
      },
      {
        id: 'production-work-order-dashboard',
        title: '生产工单看板',
        path: '/production/work-order-dashboard',
        icon: 'Odometer',
        functionCode: 'SRS-FUNC-00011-LOCAL-WORK-ORDER-DASHBOARD',
      },
      ...scaffoldedMenuRegistry.production,
    ],
  },
]

export function findMenuByPath(path: string): MenuItem | null {
  function search(items: MenuItem[]): MenuItem | null {
    for (const item of items) {
      if (item.path === path) return item
      if (item.children) {
        const found = search(item.children)
        if (found) return found
      }
    }
    return null
  }
  return search(mesMenuConfig)
}

export function findMenuByFunctionCode(code: string): MenuItem | null {
  function search(items: MenuItem[]): MenuItem | null {
    for (const item of items) {
      if (item.functionCode === code) return item
      if (item.children) {
        const found = search(item.children)
        if (found) return found
      }
    }
    return null
  }
  return search(mesMenuConfig)
}

export function getFlatMenuList(): MenuItem[] {
  const result: MenuItem[] = []
  function flatten(items: MenuItem[]) {
    for (const item of items) {
      result.push(item)
      if (item.children) flatten(item.children)
    }
  }
  flatten(mesMenuConfig)
  return result
}
