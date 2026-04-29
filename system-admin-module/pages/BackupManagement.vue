<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>备份记录</h2>
          <div class="page-description">规范管理数据库备份，确保数据安全可追溯。</div>
        </div>
      </div>
      <div class="header-actions">
        <div class="summary" style="display: inline-flex; margin-right: 16px; gap: 16px;">
          <div class="summary-item" style="padding: 4px 12px; background: rgba(35, 116, 248, 0.06); border-radius: 4px; display: flex; flex-direction: column; line-height: 1.2;">
            <span class="label" style="font-size: 12px; color: var(--el-text-color-secondary);">最近备份: {{ latestRecord?.createdAt ?? '-' }}</span>
          </div>
          <div class="summary-item" style="padding: 4px 12px; background: rgba(35, 116, 248, 0.06); border-radius: 4px; display: flex; flex-direction: column; line-height: 1.2;">
            <span class="label" style="font-size: 12px; color: var(--el-text-color-secondary);">成功: {{ stats.success }} | 失败: {{ stats.failed }}</span>
          </div>
        </div>
        <el-button type="primary" @click="handleBackup" :loading="backupLoading" style="width: 100px;">
          <el-icon><Download /></el-icon>
          立即备份
        </el-button>
        <el-button type="success" @click="handleCreatePlan" style="width: 130px;">
          <el-icon><Timer /></el-icon>
          配置备份计划
        </el-button>
      </div>
    </div>

    <div class="search-actions-panel">
      <el-form :model="searchQuery" inline>
        <el-form-item label="备份文件名称：">
          <el-input
            v-model="searchQuery.name"
            placeholder="备份文件名称"
            clearable
            style="width: 300px;"
            @clear="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="备份类型：">
          <el-select
            v-model="searchQuery.type"
            placeholder="备份类型"
            clearable
            style="width: 120px;"
            @clear="handleSearch"
          >
            <el-option label="手动备份" :value="1" />
            <el-option label="自动备份" :value="2" />
          </el-select>
        </el-form-item>
      </el-form>
      <div class="action-area" style="display: flex; gap: 12px;">
        <el-button type="primary" @click="handleSearch" style="width: 100px;">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="handleReset" style="width: 100px;">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <div class="content-card">
      <div class="table-container">
        <el-table :data="records" stripe highlight-current-row empty-text="暂无备份记录" class="unified-table">
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="name" label="备份文件" min-width="220">
          <template #default="{ row }">
            <div class="file-cell">
              <el-icon><Document /></el-icon>
              <span>{{ row.name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="120">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ row.operator }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="类型" width="120">
          <template #default="{ row }">
            <el-tag type="primary" effect="light">{{ row.type }}</el-tag>
          </template>
        </el-table-column>
        <!-- <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" effect="dark">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column> -->
        <el-table-column prop="createdAt" label="执行时间" width="180" />
        <el-table-column label="操作" width="240" align="center" fixed="right" class-name="col-actions">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" size="small" @click="handleDownload(row)" style="width: 100px;">下载</el-button>
              <el-button type="warning" size="small" @click="handleDelete(row)" style="width: 100px;">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.currentPage"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>

    <el-dialog 
      v-model="planDialog" 
      title="配置备份计划" 
      width="500px"
      class="backup-plan-dialog custom-dialog"
      align-center
    >
      <el-form :model="planForm" label-width="100px">
        <el-form-item label="验证码">
          <el-input v-model="planForm.verificationCode" placeholder="请输入验证码" />
        </el-form-item>
        <el-form-item label="执行频率">
          <el-select v-model="planForm.frequency" placeholder="请选择执行频率">

            <el-option label="每天" :value="1" />
            <el-option label="每周" :value="2" />
            <el-option label="每月" :value="3" />
          </el-select>
        </el-form-item>
        <!-- <el-form-item label="执行时间">
          <el-time-picker 
            v-model="planForm.time" 
            placeholder="请选择执行时间"
            format="HH:mm"
            value-format="HH:mm"
            style="width: 100%"
          />
        </el-form-item> -->
      </el-form>
      <template #footer>
        <div class="dialog-footer">
        <el-button @click="planDialog = false">取消</el-button>
          <el-button type="primary" @click="handlePlanSubmit" style="margin-left: 12px;">保存</el-button>
        </div>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Document, Timer, Search, Refresh } from '@element-plus/icons-vue'
import type { BackupRecord } from '@/types/system'
import { pageBackupsApi, downloadBackupRawApi, triggerBackupApi, deleteBackupApi, getScheduledTaskConfigApi, saveScheduledTaskApi, type BakRecord, type BakPageRequest } from '@/api/modules/backup'

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 所有备份记录
const allRecords = ref<BackupRecord[]>([])

// 搜索查询参数
const searchQuery = reactive({
  name: '',
  type: undefined as number | undefined
})

// 直接使用后端分页数据，不再进行前端过滤
const records = computed(() => allRecords.value)
const planDialog = ref(false)

const planForm = reactive({
  id: undefined as number | undefined,
  verificationCode: '',
  jobId: undefined as number | undefined,
  frequency: 1 // 默认每天（根据用户修改后的选项值）
})

// 备份功能
const backupLoading = ref(false)

// 分页事件处理
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadBackups() // 重新加载数据
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadBackups() // 重新加载数据
}

// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1 // 重置到第一页
  loadBackups() // 重新加载数据
}

// 重置搜索
const handleReset = () => {
  searchQuery.name = ''
  searchQuery.type = undefined
  pagination.currentPage = 1
  loadBackups() // 重新加载数据
}

const handleBackup = async () => {
  try {
    const code = window.prompt('请输入备份验证码：') || ''
    if (!code.trim()) return
    const resp = await triggerBackupApi(code.trim())
    if (resp.code === 200 || resp.code === 200) {
      ElMessage.success('备份任务已触发')
      await loadBackups()
    } else {
      ElMessage.error(resp.msg || '备份触发失败')
    }
  } catch (e) {
    console.error('备份触发失败:', e)
    ElMessage.error('备份触发失败')
  }
}

const handleDownload = async (row: BackupRecord) => {
  try {
    const { blob, disposition } = await downloadBackupRawApi(Number(row.id))
    
    // 验证blob对象
    if (!blob || !(blob instanceof Blob)) {
      throw new Error('获取到的文件数据无效')
    }
    
    // 从响应头提取文件名，如果没有则使用记录中的文件名
    let fileName = row.name || 'backup.sql'
    const match = disposition.match(/filename\*?=([^;]+)/i)
    if (match && match[1]) {
      const rawName = match[1].replace(/^UTF-8''/, '').replace(/["']/g, '').trim()
      try { fileName = decodeURIComponent(rawName) } catch { fileName = rawName }
    }
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('开始下载备份文件')
  } catch (e) {
    console.error('下载失败:', e)
    ElMessage.error('下载失败')
  }
}


const handleDelete = async (row: BackupRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除备份 ${row.name} 吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
      customClass: 'custom-message-box'
    })
    
    // 要求用户输入验证码
    const verificationCode = await ElMessageBox.prompt('请输入删除验证码：', '验证码确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '验证码不能为空',
      inputType: 'password'
    })
    
    if (!verificationCode.value || !verificationCode.value.trim()) {
      ElMessage.error('验证码不能为空')
      return
    }
    
    const resp: any = await deleteBackupApi(row.id, verificationCode.value.trim())
    if (resp.code === 200 || resp.code === 200) {
      ElMessage.success('删除成功')
      await loadBackups()
    } else {
      ElMessage.error(resp.msg || '删除失败')
    }
  } catch (e: any) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}


const handleCreatePlan = async () => {
  try {
    // 获取现有的定时任务配置
    const resp = await getScheduledTaskConfigApi()
    if ((resp.code === 200 || resp.code === 200) && resp.data) {
      // 填充表单数据
      planForm.id = resp.data.id
      planForm.jobId = resp.data.jobId
      planForm.frequency = resp.data.frequency || 1
      console.log('获取到定时任务配置:', resp.data)
    } else {
      // 没有配置或获取失败，使用默认值
      planForm.id = undefined
      planForm.jobId = undefined
      planForm.frequency = 1
    }
  } catch (error) {
    console.error('获取定时任务配置失败:', error)
    // 获取失败使用默认值
    planForm.id = undefined
    planForm.jobId = undefined
    planForm.frequency = 1
  }
  
  // 清空验证码
  planForm.verificationCode = ''
  planDialog.value = true
}

const handlePlanSubmit = async () => {
  try {
    // 验证必要参数
    if (!planForm.verificationCode?.trim()) {
      ElMessage.error('请输入验证码')
      return
    }
    if (!planForm.frequency) {
      ElMessage.error('请选择执行频率')
      return
    }
    
    const payload = {
      id: planForm.id,
      verificationCode: planForm.verificationCode,
      jobId: planForm.jobId,
      frequency: planForm.frequency
    }
    
    // 调试日志
    console.log('保存备份计划参数:', payload)
    
    const resp = await saveScheduledTaskApi(payload)
    if (resp.code === 200 || resp.code === 200) {
      ElMessage.success('备份计划已保存')
      planDialog.value = false
      await loadBackups()
    } else {
      ElMessage.error(resp.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存备份计划失败:', error)
    ElMessage.error('创建备份计划失败')
  }
}

// 自动备份检查
const checkAutoBackup = () => {
  const lastBackup = latestRecord.value
  if (!lastBackup) {
    ElMessage.warning('系统尚未进行过备份，建议立即执行备份操作')
    return
  }
  
  const lastBackupTime = new Date(lastBackup.createdAt).getTime()
  const now = Date.now()
  const daysDiff = (now - lastBackupTime) / (1000 * 60 * 60 * 24)
  
  if (daysDiff > 7) {
    ElMessage.warning('距离上次备份已超过7天，建议尽快执行备份')
  }
}

// 加载后端备份列表
const loadBackups = async () => {
  try {
    const pageReq: BakPageRequest = { current: pagination.currentPage, size: pagination.pageSize }
    const dto = { 
      sortColumn: 'create_time', 
      sortType: 'desc' as const,
      name: searchQuery.name || undefined,  // 传递备份文件名称搜索
      type: searchQuery.type  // 传递备份类型搜索
    }
    const resp = await pageBackupsApi({ ...pageReq, ...dto })
    if ((resp.code === 200 || resp.code === 200) && resp.data) {
      const pageData = resp.data
      pagination.total = pageData.total
      // 映射到页面需要的 BackupRecord 结构
      allRecords.value = (pageData.records || []).map((r: BakRecord) => ({
        id: String(r.id),
        name: r.name || r.fileName, // 优先使用后端的name字段，回退到fileName
        operator: r.createName || '-',
        type: r.type === 1 ? '手动备份' : r.type === 2 ? '自动备份' : '未知类型', // 1是手动备份，2是自动备份
        status: 'success',
        size: r.totalSizeFormat || '-',
        createdAt: r.createTime,
        description: r.name || ''
      }))
    } else {
      ElMessage.error(resp.msg || '获取备份列表失败')
    }
  } catch (e) {
    console.error('获取备份列表失败:', e)
    ElMessage.error('获取备份列表失败')
  }
}

onMounted(async () => {
  await loadBackups()
  // 查询现有定时任务配置，填充表单
  // 注意：这个接口可能返回非标准响应格式，导致HTTP拦截器抛出异常
  // 这是正常情况，不需要向用户显示错误
  setTimeout(checkAutoBackup, 2000)
})

const stats = computed(() => {
  const success = records.value.filter((item) => item.status === 'success').length
  const failed = records.value.length - success
  return { success, failed }
})

const latestRecord = computed(() => records.value[0])
</script>

<style scoped lang="scss">
.backup-toolbar {
  align-items: flex-start;
}

.summary {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;

  .summary-item {
    min-width: 200px;
    padding: 12px 16px;
    border-radius: var(--app-radius-sm);
    background: rgba(35, 116, 248, 0.06);
    border: 1px solid rgba(35, 116, 248, 0.12);
    display: flex;
    flex-direction: column;
    gap: 6px;

    .label {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }

    strong {
      font-size: 18px;
    }

    small {
      color: var(--el-text-color-secondary);
    }
  }
}

.page-toolbar__actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h3 {
    margin: 0 0 4px;
  }

  p {
    margin: 0;
    color: var(--el-text-color-secondary);
  }
}

.search-area {
  padding: 16px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 16px;

  .el-form {
    margin: 0;
  }

  .el-form-item {
    margin-bottom: 0;
    margin-right: 16px;

    &:last-child {
      margin-right: 0;
    }
  }

  .el-button {
    margin-left: 8px;

    &:first-child {
      margin-left: 0;
    }
  }
}

.file-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-primary);
}

@media (max-width: 768px) {
  .summary {
    flex-direction: column;
  }

  .toolbar-actions {
    width: 100%;
  }
}

.backup-plan-dialog,
.restore-confirm-dialog {
  .el-dialog__body {
    padding: 24px;
  }
  
  .el-dialog__footer {
    padding: 16px 24px 24px;
    border-top: 1px solid var(--el-border-color-lighter);
  }
}

.backup-plan-dialog {
  .el-form {
    .el-form-item {
      margin-bottom: 20px;
      
      .el-form-item__label {
        color: var(--el-text-color-regular);
        font-weight: 500;
      }
      
      .el-input,
      .el-select,
      .el-time-picker {
        width: 100%;
      }
    }
  }
}

// 自定义弹窗样式优化
.custom-dialog {
  .el-dialog__footer {
    padding: 16px 24px 20px;
    border-top: 1px solid var(--el-border-color-lighter);
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;

    .el-button {
      flex: 0 0 auto;
      min-width: 80px;
      max-width: 120px;
      white-space: nowrap;
      padding: 8px 16px;
      font-size: 14px;
      
      // 响应式调整
      @media (max-width: 768px) {
        min-width: 72px;
        max-width: 100px;
        padding: 6px 12px;
        font-size: 13px;
      }
      
      @media (max-width: 480px) {
        min-width: 64px;
        max-width: 88px;
        padding: 6px 10px;
        font-size: 12px;
      }
    }

    .el-button + .el-button {
      margin-left: 0;
    }
  }
  
  // 移动端弹窗优化
  @media (max-width: 768px) {
    width: 90% !important;
    max-width: 450px !important;
    
    .el-dialog__body {
      padding: 16px 20px;
    }
    
    .el-form {
      .el-form-item {
        margin-bottom: 16px;
        
        .el-form-item__label {
          font-size: 13px;
        }
      }
    }
  }
  
  @media (max-width: 480px) {
    width: 95% !important;
    max-width: 360px !important;
    
    .el-dialog__header {
      padding: 16px 20px 12px;
      
      .el-dialog__title {
        font-size: 15px;
      }
    }
    
    .el-dialog__body {
      padding: 12px 20px;
    }
    
    .el-dialog__footer {
      padding: 12px 20px 16px;
      gap: 8px;
    }
    
    .el-form {
      .el-form-item {
        margin-bottom: 12px;
        
        .el-form-item__label {
          font-size: 12px;
          width: 80px !important;
        }
      }
    }
  }
}

.restore-confirm {
  .restore-warning {
    margin: 20px 0;
    
    h4 {
      margin: 0 0 12px;
      color: var(--el-text-color-primary);
      font-size: 14px;
      font-weight: 600;
    }
    
    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        margin-bottom: 8px;
        color: var(--el-text-color-regular);
        font-size: 13px;
        line-height: 1.5;
      }
    }
  }
  
  .el-descriptions {
    margin: 20px 0;
    
    :deep(.el-descriptions__body) {
      .el-descriptions__table {
        .el-descriptions__cell {
          padding: 12px 16px;
          
          &.is-bordered-label {
            background-color: #fafafa;
            font-weight: 500;
            color: var(--el-text-color-regular);
          }
          
          &:not(.is-bordered-label) {
            color: var(--el-text-color-primary);
          }
        }
      }
    }
  }
  
  .el-checkbox {
    margin-top: 20px;
    
    .el-checkbox__label {
      color: var(--el-text-color-primary);
      font-weight: 500;
    }
  }
}

</style>
