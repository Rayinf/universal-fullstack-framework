// 附件记录
export interface AttachmentRecord {
  id: string
  bizType: string
  bizId: string
  fileName: string
  fileSize: number
  filePath: string
  uploadBy: string
  uploadTime: string
}

// 上传结果
export interface AttachmentUploadResult {
  id: string
  fileName: string
  fileSize: number
  uploadTime: string
}
