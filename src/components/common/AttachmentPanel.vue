<template>
  <div class="attachment-panel">
    <div class="panel-header">
      <span class="panel-title">附件管理</span>
      <el-upload
        ref="uploadRef"
        :action="uploadAction"
        :headers="uploadHeaders"
        :data="{ bizType: props.bizType, bizId: props.bizId }"
        :show-file-list="false"
        :on-success="handleUploadSuccess"
        :on-error="handleUploadError"
        :before-upload="beforeUpload"
        :disabled="props.readonly"
        v-if="!props.readonly"
      >
        <el-button type="primary" size="small" :icon="Upload" :loading="uploading">
          上传附件
        </el-button>
      </el-upload>
    </div>

    <div class="file-list" v-loading="loading">
      <template v-if="fileList.length > 0">
        <div v-for="file in fileList" :key="file.id" class="file-item">
          <div class="file-info">
            <el-icon class="file-icon"><Document /></el-icon>
            <span class="file-name" :title="file.fileName">{{ file.fileName }}</span>
            <span class="file-size">{{ formatFileSize(file.fileSize) }}</span>
          </div>
          <div class="file-actions">
            <el-button type="primary" link size="small" @click="handleDownload(file)">
              下载
            </el-button>
            <el-button
              type="danger"
              link
              size="small"
              @click="handleDelete(file)"
              v-if="!props.readonly"
            >
              删除
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无附件" :image-size="40" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { Upload, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listAttachmentsApi,
  deleteAttachmentApi,
  getAttachmentDownloadUrl,
} from '@/api/system/attachment'
import type { AttachmentRecord } from '@/types/system/attachment'

interface Props {
  bizType: string
  bizId: string
  readonly?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  readonly: false,
})

const loading = ref<boolean>(false)
const uploading = ref<boolean>(false)
const fileList = ref<AttachmentRecord[]>([])

// 上传配置
const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
const uploadAction = `${baseUrl}/local/attachments/upload`
const uploadHeaders = ref<Record<string, string>>({})

// 动态获取 token
const refreshHeaders = () => {
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
  uploadHeaders.value = token ? { Authorization: `Bearer ${token}` } : {}
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const fetchFiles = async () => {
  if (!props.bizType || !props.bizId) {
    fileList.value = []
    return
  }
  loading.value = true
  try {
    const res = await listAttachmentsApi(props.bizType, props.bizId)
    if (res.code === 0 || res.code === 200) {
      fileList.value = res.data || []
    }
  } catch {
    fileList.value = []
  } finally {
    loading.value = false
  }
}

const beforeUpload = () => {
  refreshHeaders()
  uploading.value = true
  return true
}

const handleUploadSuccess = (response: any) => {
  uploading.value = false
  if (response.code === 0 || response.code === 200) {
    ElMessage.success('上传成功')
    fetchFiles()
  } else {
    ElMessage.error(response.msg || '上传失败')
  }
}

const handleUploadError = () => {
  uploading.value = false
  ElMessage.error('上传失败')
}

const handleDownload = (file: AttachmentRecord) => {
  const url = getAttachmentDownloadUrl(file.id)
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
  // 使用 fetch + blob 方式下载（带 token）
  fetch(url, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
    .then((res) => res.blob())
    .then((blob) => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(blob)
      a.download = file.fileName
      a.click()
      URL.revokeObjectURL(a.href)
    })
    .catch(() => {
      ElMessage.error('下载失败')
    })
}

const handleDelete = async (file: AttachmentRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除附件 "${file.fileName}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await deleteAttachmentApi(file.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      fetchFiles()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch {
    ElMessage.error('删除失败')
  }
}

watch(
  () => [props.bizType, props.bizId],
  () => {
    fetchFiles()
  },
)

onMounted(() => {
  refreshHeaders()
  fetchFiles()
})
</script>

<style scoped>
.attachment-panel {
  border: 1px solid #ebeef5;
  border-radius: 6px;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

.panel-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.file-list {
  min-height: 60px;
  max-height: 300px;
  overflow-y: auto;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  border-bottom: 1px solid #f2f6fc;
  transition: background-color 0.2s;
}

.file-item:hover {
  background-color: #f5f7fa;
}

.file-item:last-child {
  border-bottom: none;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.file-icon {
  color: #409eff;
  font-size: 18px;
  flex-shrink: 0;
}

.file-name {
  font-size: 13px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #909399;
  flex-shrink: 0;
}

.file-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  margin-left: 12px;
}
</style>
