import type { RouteRecordRaw } from 'vue-router'

export const systemRoutes: RouteRecordRaw = {
  path: 'system',
  name: 'System',
  component: () => import('@/layouts/EmptyRouterView.vue'),
  meta: { 
    title: '系统管理', 
    icon: 'Setting', 
    roles: ['1'], // 仅超级管理员
    order: 11
  },
  children: [
    {
      path: 'basic-info',
      name: 'BasicInfoManagement',
      component: () => import('@/modules/system/pages/BasicInfoManagement.vue'),
      meta: { 
        title: '基础信息维护', 
        activeMenu: '/system/basic-info', 
        roles: ['1'],
        order: 1
      },
    },
    {
      path: 'users',
      name: 'SystemUser',
      component: () => import('@/modules/system/pages/UserManagement.vue'),
      meta: { 
        title: '用户管理', 
        activeMenu: '/system/users', 
        roles: ['1'],
        order: 2
      },
    },
    {
      path: 'logs',
      name: 'OperationLog',
      component: () => import('@/modules/system/pages/OperationLog.vue'),
      meta: { 
        title: '操作日志', 
        activeMenu: '/system/logs', 
        roles: ['1'],
        order: 3
      },
    },
    {
      path: 'backup',
      name: 'Backup',
      component: () => import('@/modules/system/pages/BackupManagement.vue'),
      meta: { 
        title: '数据备份', 
        activeMenu: '/system/backup', 
        roles: ['1'],
        order: 4
      },
    },
  ],
}
