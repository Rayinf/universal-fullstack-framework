import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useMenuStore } from '@/stores/menuStore'
import { useUserStore } from '@/stores/userStore'
import { useSystemConfigStore } from '@/stores/system/systemConfig'
import { hasStoredTokenTriplet } from '@/utils/auth'
import type { MenuNode } from '@/types/system/menu'
import { FRAMEWORK_DEFAULT_ROUTE, isFrameworkEnabledRoute } from '@/config/frameworkConfig'
import { scaffoldedRoutes } from '@/router/scaffoldedRoutes'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'

const PlaceholderView = () => import('@/views/PlaceholderView.vue')

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false, title: '登录' },
  },
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true, title: '首页' },
  },
  {
    path: '/profile',
    redirect: '/system/profile',
  },

  // ========== 系统管理模块 ==========
  {
    path: '/system/basic-crud',
    name: 'system-basic-crud',
    component: () => import('@/views/system-admin/BasicCrudManagement.vue'),
    meta: { requiresAuth: true, title: '本地基础CRUD', functionCode: 'SRS-FUNC-00011-LOCAL-CRUD' },
  },
  {
    path: '/system/project-demo',
    name: 'system-project-demo',
    component: () => import('@/views/system-admin/ProjectDemoManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '项目管理示例',
      functionCode: 'SRS-FUNC-00011-LOCAL-PROJECT',
    },
  },
  {
    path: '/system/purchase-demo',
    name: 'system-purchase-demo',
    component: () => import('@/views/system-admin/PurchaseDemoManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '采购订单示例',
      functionCode: 'SRS-FUNC-00011-LOCAL-PURCHASE',
    },
  },
  {
    path: '/system/inventory-demo',
    name: 'system-inventory-demo',
    component: () => import('@/views/system-admin/InventoryDemoManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '库存管理示例',
      functionCode: 'SRS-FUNC-00011-LOCAL-INVENTORY',
    },
  },
  {
    path: '/system/account-management',
    name: 'system-account-management',
    component: () => import('@/views/system-admin/AccountManagement.vue'),
    meta: { requiresAuth: true, title: '账户管理', functionCode: 'SRS-FUNC-00011-2-3-4' },
  },
  {
    path: '/system/customers',
    name: 'system-customers',
    component: () => import('@/views/system-admin/CustomerManagement.vue'),
    meta: { requiresAuth: true, title: '客户管理', functionCode: 'SRS-FUNC-00011-14' },
  },
  {
    path: '/system/dept-management',
    name: 'system-dept-management',
    component: () => import('@/views/system-admin/DeptManagement.vue'),
    meta: { requiresAuth: true, title: '组织架构管理', functionCode: 'SRS-FUNC-00011-1' },
  },
  {
    path: '/system/system-config',
    name: 'system-config-view',
    component: () => import('@/views/system-admin/SystemConfigView.vue'),
    meta: { requiresAuth: true, title: '系统配置', functionCode: 'SRS-FUNC-00011-11' },
  },
  {
    path: '/system/basic-info',
    redirect: '/system/param/manage',
  },
  {
    path: '/system/user-log',
    name: 'system-user-log',
    component: () => import('@/views/system-admin/UserLogManagement.vue'),
    meta: { requiresAuth: true, title: '用户日志管理', functionCode: 'SRS-FUNC-00011-10' },
  },
  {
    path: '/system/operation-log',
    name: 'system-operation-log',
    component: () => import('@/views/system-admin/OperationLog.vue'),
    meta: { requiresAuth: true, title: '系统日志管理', functionCode: 'SRS-FUNC-00011-9' },
  },
  {
    path: '/system/backup',
    name: 'system-backup',
    component: () => import('@/views/system-admin/BackupManagement.vue'),
    meta: { requiresAuth: true, title: '数据与系统备份', functionCode: 'SRS-FUNC-00011-13' },
  },
  {
    path: '/system/profile',
    name: 'system-profile',
    component: () => import('@/views/system-admin/ProfileCenter.vue'),
    meta: { requiresAuth: true, title: '个人中心' },
  },
  {
    path: '/system/role',
    name: 'system-role',
    component: () => import('@/views/system-admin/RoleManagement.vue'),
    meta: { requiresAuth: true, title: '用户角色管理', functionCode: 'SRS-FUNC-00011-5' },
  },
  {
    path: '/system/workstation/info',
    name: 'system-workstation-info',
    component: () => import('@/views/system-admin/WorkstationManagement.vue'),
    meta: { requiresAuth: true, title: '工位信息管理', functionCode: 'SRS-FUNC-00011-6.1' },
  },
  {
    path: '/system/workstation/equipment',
    name: 'system-equipment',
    component: () => import('@/views/system-admin/DeviceManagement.vue'),
    meta: { requiresAuth: true, title: '设备基础信息管理', functionCode: 'SRS-FUNC-00011-6.2' },
  },
  {
    path: '/system/param/manage',
    name: 'system-param-manage',
    component: () => import('@/views/system-admin/ParameterManagement.vue'),
    meta: { requiresAuth: true, title: '参数管理', functionCode: 'SRS-FUNC-00011-7.1' },
  },
  {
    path: '/system/param/code',
    name: 'system-param-code',
    component: () => import('@/views/system-admin/CodeRuleManagement.vue'),
    meta: { requiresAuth: true, title: '编码规则配置', functionCode: 'SRS-FUNC-00011-7.2' },
  },
  {
    path: '/system/approval',
    name: 'system-approval',
    component: () => import('@/views/system-admin/ApprovalFlowManagement.vue'),
    meta: { requiresAuth: true, title: '业务相关审批规则', functionCode: 'SRS-FUNC-00011-8' },
  },
  {
    path: '/sales/product-catalog',
    name: 'sales-product-catalog',
    component: () => import('@/views/system-admin/ProductCatalogManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '产品目录管理',
      functionCode: 'SRS-FUNC-00011-LOCAL-PRODUCT',
    },
  },
  {
    path: '/sales/quotation',
    name: 'sales-quotation',
    component: () => import('@/views/system-admin/QuotationManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '报价单管理',
      functionCode: 'SRS-FUNC-00011-LOCAL-QUOTATION',
    },
  },
  {
    path: '/sales/contracts',
    name: 'sales-contracts',
    component: () => import('@/views/system-admin/ContractManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '合同管理',
      functionCode: 'SRS-FUNC-00011-LOCAL-CONTRACT',
    },
  },
  {
    path: '/sales/payments',
    name: 'sales-payments',
    component: () => import('@/views/system-admin/PaymentManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '回款跟踪',
      functionCode: 'SRS-FUNC-00011-LOCAL-PAYMENT',
    },
  },
  {
    path: '/sales/commissions',
    name: 'sales-commissions',
    component: () => import('@/views/system-admin/CommissionManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '佣金计算',
      functionCode: 'SRS-FUNC-00011-LOCAL-COMMISSION',
    },
  },
  {
    path: '/sales/contract-dashboard',
    name: 'sales-contract-dashboard',
    component: () => import('@/views/system-admin/ContractDashboard.vue'),
    meta: {
      requiresAuth: true,
      title: '合同业务看板',
      functionCode: 'SRS-FUNC-00011-LOCAL-CONTRACT-DASHBOARD',
    },
  },
  {
    path: '/production/work-orders',
    name: 'production-work-orders',
    component: () => import('@/views/system-admin/WorkOrderManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '生产工单管理',
      functionCode: 'SRS-FUNC-00011-LOCAL-WORK-ORDER',
    },
  },
  {
    path: '/production/work-reports',
    name: 'production-work-reports',
    component: () => import('@/views/system-admin/WorkReportManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '工序报工',
      functionCode: 'SRS-FUNC-00011-LOCAL-WORK-REPORT',
    },
  },
  {
    path: '/production/work-inbounds',
    name: 'production-work-inbounds',
    component: () => import('@/views/system-admin/WorkInboundManagement.vue'),
    meta: {
      requiresAuth: true,
      title: '完工入库',
      functionCode: 'SRS-FUNC-00011-LOCAL-WORK-INBOUND',
    },
  },
  {
    path: '/production/work-order-dashboard',
    name: 'production-work-order-dashboard',
    component: () => import('@/views/system-admin/WorkOrderDashboard.vue'),
    meta: {
      requiresAuth: true,
      title: '生产工单看板',
      functionCode: 'SRS-FUNC-00011-LOCAL-WORK-ORDER-DASHBOARD',
    },
  },
  {
    path: '/system/notifications',
    name: 'system-notifications',
    component: () => import('@/views/system-admin/NotificationManagement.vue'),
    meta: { requiresAuth: true, title: '消息通知', functionCode: 'SRS-FUNC-00011-NOTIFY' },
  },
  {
    path: '/system/product-catalog',
    redirect: '/sales/product-catalog',
  },
  {
    path: '/system/quotation',
    redirect: '/sales/quotation',
  },
  {
    path: '/system/contracts',
    redirect: '/sales/contracts',
  },
  {
    path: '/system/payments',
    redirect: '/sales/payments',
  },
  {
    path: '/system/commissions',
    redirect: '/sales/commissions',
  },
  {
    path: '/system/contract-dashboard',
    redirect: '/sales/contract-dashboard',
  },
  {
    path: '/system/work-orders',
    redirect: '/production/work-orders',
  },
  {
    path: '/system/work-reports',
    redirect: '/production/work-reports',
  },
  {
    path: '/system/work-inbounds',
    redirect: '/production/work-inbounds',
  },
  {
    path: '/system/work-order-dashboard',
    redirect: '/production/work-order-dashboard',
  },
  {
    path: '/system/log',
    redirect: '/system/operation-log',
  },
  {
    path: '/system/config',
    redirect: '/system/system-config',
  },

  ...scaffoldedRoutes,

  // 兼容历史业务模块路径，统一收敛到系统管理入口
  {
    path: '/task/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/planning/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/process/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/process-tech/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/technology/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/production/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/quality/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/dashboard/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/collaboration/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },
  {
    path: '/comprehensive/:pathMatch(.*)*',
    redirect: FRAMEWORK_DEFAULT_ROUTE,
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: PlaceholderView,
    meta: { requiresAuth: false, title: '页面未找到' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

function normalizeRoutePath(raw?: string | null): string {
  if (!raw) return ''
  const trimmed = raw.trim()
  if (!trimmed) return ''
  return trimmed.startsWith('/') ? trimmed : `/${trimmed}`
}

function findMenuIdByRoute(
  nodes: MenuNode[],
  functionCode: string | undefined,
  routePath: string,
): string | null {
  const normalizedRoutePath = normalizeRoutePath(routePath)

  for (const node of nodes) {
    const codeMatched = !!functionCode && node.permission === functionCode
    const pathMatched = normalizeRoutePath(node.path) === normalizedRoutePath

    if (codeMatched || pathMatched) {
      return String(node.id)
    }
    if (node.children?.length) {
      const childMenuId = findMenuIdByRoute(node.children, functionCode, routePath)
      if (childMenuId) return childMenuId
    }
  }

  return null
}

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const menuStore = useMenuStore()
  const systemConfigStore = useSystemConfigStore()
  const requiresAuth = to.meta.requiresAuth as boolean

  if (to.meta.title) {
    const systemName = systemConfigStore.configData.systemName || 'MES管理系统'
    document.title = `${to.meta.title} - ${systemName}`
  }

  if (requiresAuth) {
    const hasValidToken = hasStoredTokenTriplet()

    if (!(userStore.currentUser?.id || hasValidToken)) {
      next({ name: 'Login' })
      return
    }

    if (!isFrameworkEnabledRoute(to.path)) {
      next({ path: FRAMEWORK_DEFAULT_ROUTE })
      return
    }

    const functionCode = (to.meta.functionCode as string | undefined)?.trim()
    if (!menuStore.loaded) {
      await menuStore.fetchMenuTree()
    }

    const matchedMenuId = findMenuIdByRoute(menuStore.rawMenuTree, functionCode, to.path)
    if (matchedMenuId && !menuStore.isMenuIdAllowed(matchedMenuId)) {
      // 本地框架模式下，若后端权限ID未返回（空集合），避免卡死在重定向循环
      if (menuStore.allowedMenuIds.size === 0) {
        next()
        return
      }
      // 兜底：避免跳转到同一路由导致无限重定向
      if (to.path === '/' || to.path === FRAMEWORK_DEFAULT_ROUTE) {
        next()
        return
      }
      next({ path: FRAMEWORK_DEFAULT_ROUTE })
      return
    }

    next()
  } else {
    next()
  }
})

export default router
