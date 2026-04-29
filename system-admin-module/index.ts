// 系统管理模块入口文件

// 导出页面组件
export { default as DeptManagement } from './pages/DeptManagement.vue'
export { default as SystemConfigView } from './pages/SystemConfigView.vue'

// 导出 Store
export { useDeptStore, useSystemConfigStore } from './stores'

// 导出 API
export * from './api/dept'
export * from './api/systemConfig'

// 导出类型定义
export * from './types/dept'
export * from './types/systemConfig'

// 导出路由配置
export { systemAdminRoutes, systemAdminMenus } from './router/systemAdmin'

// 导出权限配置
export { MENU_KEYS, ROLE_PERMISSIONS, hasMenuPermission, hasButtonPermission } from './permissions'

// 导出工具函数
export { default as request } from './utils/request'

// 导出样式文件（需要在主应用中手动引入）
// import './styles/common.css'