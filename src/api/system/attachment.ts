import request from '@/utils/request'
import type { AttachmentRecord, AttachmentUploadResult } from '@/types/system/attachment'

export const listAttachmentsApi = (bizType: string, bizId: string) =>
  request.get<AttachmentRecord[]>('/local/attachments/list', { bizType, bizId })

export const deleteAttachmentApi = (id: string) =>
  request.delete<unknown>(`/local/attachments/${id}`)

/**
 * 上传附件 — 使用 FormData 方式上传文件
 */
export const uploadAttachmentApi = (file: File, bizType: string, bizId: string) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('bizType', bizType)
  formData.append('bizId', bizId)
  return request.post<AttachmentUploadResult>('/local/attachments/upload', formData)
}

/**
 * 获取附件下载地址
 */
export const getAttachmentDownloadUrl = (id: string): string => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  return `${baseUrl}/local/attachments/download/${id}`
}

export type { AttachmentRecord, AttachmentUploadResult }
