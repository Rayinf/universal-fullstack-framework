export interface FrameworkModule {
  id: string
  title: string
  routePrefix: string
  description: string
  enabled: boolean
  order: number
}

export const FRAMEWORK_DEFAULT_ROUTE = '/system/basic-crud'

const FRAMEWORK_EXACT_ENABLED_ROUTES = ['/']
const FRAMEWORK_PREFIX_ENABLED_ROUTES = ['/system', '/sales', '/production']

export const frameworkModules: FrameworkModule[] = [
  {
    id: 'system-management',
    title: '系统管理',
    routePrefix: '/system',
    description: '组织、用户、角色、参数、审批、日志与系统配置的完整管理能力。',
    enabled: true,
    order: 1,
  },
  {
    id: 'sales-management',
    title: '销售管理',
    routePrefix: '/sales',
    description: '产品目录、报价、合同、回款、佣金与销售看板。',
    enabled: true,
    order: 2,
  },
  {
    id: 'production-execution',
    title: '生产执行',
    routePrefix: '/production',
    description: '生产工单、工序报工、完工入库与生产看板。',
    enabled: true,
    order: 3,
  },
  {
    id: 'task-management',
    title: '任务管理',
    routePrefix: '/task',
    description: '后续按业务需要在基础框架上扩展接入。',
    enabled: false,
    order: 4,
  },
  {
    id: 'planning-management',
    title: '计划排程',
    routePrefix: '/planning',
    description: '后续按业务需要在基础框架上扩展接入。',
    enabled: false,
    order: 5,
  },
  {
    id: 'process-management',
    title: '工艺技术',
    routePrefix: '/process',
    description: '后续按业务需要在基础框架上扩展接入。',
    enabled: false,
    order: 6,
  },
  {
    id: 'quality-management',
    title: '质量监督',
    routePrefix: '/quality',
    description: '后续按业务需要在基础框架上扩展接入。',
    enabled: false,
    order: 7,
  },
]

function normalizePath(path: string): string {
  if (!path) return '/'
  return path.startsWith('/') ? path : `/${path}`
}

export function isFrameworkEnabledRoute(path: string): boolean {
  const normalizedPath = normalizePath(path)

  if (FRAMEWORK_EXACT_ENABLED_ROUTES.includes(normalizedPath)) {
    return true
  }

  return FRAMEWORK_PREFIX_ENABLED_ROUTES.some((prefix) => {
    const normalizedPrefix = normalizePath(prefix)
    return normalizedPath === normalizedPrefix || normalizedPath.startsWith(`${normalizedPrefix}/`)
  })
}

export function getEnabledModules(): FrameworkModule[] {
  return frameworkModules.filter((module) => module.enabled).sort((a, b) => a.order - b.order)
}

export function getPlannedModules(): FrameworkModule[] {
  return frameworkModules.filter((module) => !module.enabled).sort((a, b) => a.order - b.order)
}
