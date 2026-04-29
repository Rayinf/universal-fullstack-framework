import request from '@/utils/request'
import type {
  NotificationPageData,
  NotificationPageParams,
  UnreadCountData,
} from '@/types/system/notification'

export const pageNotificationsApi = (params: NotificationPageParams) =>
  request.get<NotificationPageData>('/local/notifications/page', params)

export const getUnreadCountApi = () =>
  request.get<UnreadCountData>('/local/notifications/unread-count')

export const markNotificationReadApi = (id: string) =>
  request.put<unknown>(`/local/notifications/${id}/read`)

export const markAllNotificationsReadApi = () =>
  request.put<unknown>('/local/notifications/read-all')

export const deleteNotificationApi = (id: string) =>
  request.delete<unknown>(`/local/notifications/${id}`)

export type { NotificationPageData, UnreadCountData }
