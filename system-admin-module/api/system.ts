import { request } from '@/api/http'
import type { BackupRecord, OperationLog, SystemUser } from '@/types/system'

export const fetchUsersApi = (params?: Record<string, unknown>) =>
  request<SystemUser[]>({
    url: '/system/users',
    method: 'get',
    params,
  })

export const createUserApi = (data: Partial<SystemUser>) =>
  request<void>({
    url: '/system/users',
    method: 'post',
    data,
  })

export const fetchLogsApi = (params?: Record<string, unknown>) =>
  request<OperationLog[]>({
    url: '/system/logs',
    method: 'get',
    params,
  })

export const fetchBackupApi = () =>
  request<BackupRecord[]>({
    url: '/system/backup-records',
    method: 'get',
  })

export const triggerBackupApi = () =>
  request<void>({
    url: '/system/backup-records',
    method: 'post',
  })
