import type { RouteRecordRaw } from 'vue-router'

// 导入页面组件
const DeptManagement = () => import('../pages/DeptManagement.vue')
const SystemConfigView = () => import('../pages/SystemConfigView.vue')

// 系统管理模块路由配置
export const systemAdminRoutes: RouteRecordRaw[] = [
  {
    path: '/dept-management',
    name: 'dept-management',
    component: DeptManagement,
    meta: { 
      requiresAuth: true,
      title: '部门管理',
      icon: 'OfficeBuilding',
      roles: ['admin'], // 仅超级管理员可访问
    },
  },
  {
    path: '/system-config',
    name: 'system-config',
    component: SystemConfigView,
    meta: { 
      requiresAuth: true,
      title: '系统配置',
      icon: 'Setting',
      roles: ['admin'], // 仅超级管理员可访问
    },
  },
]

// 系统管理菜单配置
export const systemAdminMenus = [
  {
    path: '/dept-management',
    name: 'dept-management',
    title: '部门管理',
    icon: 'OfficeBuilding',
    roles: ['admin'],
  },
  {
    path: '/system-config',
    name: 'system-config',
    title: '系统配置',
    icon: 'Setting',
    roles: ['admin'],
  },
]

export default systemAdminRoutes
