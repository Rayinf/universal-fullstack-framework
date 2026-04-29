<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>数据与系统备份</h2>
          <div class="page-description">规范管理数据库备份，确保数据安全可追溯。</div>
        </div>
      </div>
      <div class="header-stats">
        <div class="stat-item">
          <div class="stat-label">最近备份</div>
          <div class="stat-value">{{ latestRecord?.createdAt ?? '-' }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">成功次数</div>
          <div class="stat-value highlight">{{ stats.success }}</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">失败次数</div>
          <div class="stat-value highlight-warning">{{ stats.failed }}</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="searchQuery" class="search-form" inline @submit.prevent>
          <el-form-item label="备份文件名称">
            <el-input
              v-model="searchQuery.name"
              placeholder="请输入备份文件名称"
              clearable
              style="width: 240px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="备份类型">
            <el-select
              v-model="searchQuery.type"
              placeholder="全部类型"
              clearable
              style="width: 140px"
            >
              <el-option label="手动备份" :value="1" />
              <el-option label="自动备份" :value="2" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon><Search /></el-icon>查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon><RefreshLeft /></el-icon>重置
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="table-container">
        <div class="table-header">
          <div class="table-header__left">
            <span class="table-title">备份记录列表</span>
            <span class="table-subtitle">共 {{ pagination.total }} 条记录</span>
          </div>
          <div class="table-header__actions">
            <el-button type="primary" @click="handleBackup" :loading="backupLoading">
              <el-icon><Download /></el-icon>立即备份
            </el-button>
            <el-button type="success" @click="handleCreatePlan" plain>
              <el-icon><Timer /></el-icon>配置备份计划
            </el-button>
          </div>
        </div>

        <el-table
          :data="records"
          stripe
          highlight-current-row
          empty-text="暂无备份记录"
          class="unified-table"
        >
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
              <el-tag :type="row.type === '自动备份' ? 'success' : 'primary'" effect="light">
                {{ row.type }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="执行时间" width="180" />
          <el-table-column
            label="操作"
            width="160"
            align="center"
            fixed="right"
            class-name="col-actions"
          >
            <template #default="{ row }">
              <div class="table-actions">
                <el-button link type="primary" @click="handleDownload(row)">下载</el-button>
                <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

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
      class="custom-dialog"
      align-center
    >
      <el-form :model="planForm" label-width="100px">
        <el-form-item label="验证码">
          <el-input v-model="planForm.verificationCode" placeholder="请输入验证码" />
        </el-form-item>
        <el-form-item label="执行频率">
          <el-select v-model="planForm.frequency" placeholder="请选择执行频率" style="width: 100%">
            <el-option label="每天" :value="1" />
            <el-option label="每周" :value="2" />
            <el-option label="每月" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="planDialog = false">取消</el-button>
          <el-button type="primary" @click="handlePlanSubmit">保存</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Document, Timer, Search, RefreshLeft } from '@element-plus/icons-vue'
import type { BackupRecord, BackupPageRequest } from '@/types/system/backup'
import {
  pageBackupRecordsApi,
  downloadBackupApi,
  triggerBackupApi,
  deleteBackupRecordApi,
  getBackupPlansApi,
  createBackupPlanApi,
} from '@/api/system/backup'

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})

// 所有备份记录
const allRecords = ref<BackupRecord[]>([])

// 搜索查询参数
const searchQuery = reactive({
  name: '',
  type: undefined as number | undefined,
})

// 直接使用后端分页数据，不再进行前端过滤
const records = computed(() => allRecords.value)
const planDialog = ref(false)

const planForm = reactive({
  id: undefined as number | undefined,
  verificationCode: '',
  jobId: undefined as number | undefined,
  frequency: 1, // 默认每天（根据用户修改后的选项值）
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
    if (resp.code === 0) {
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
    const response = await downloadBackupApi(row.id)

    // response 是 Blob
    if (!response || !(response instanceof Blob)) {
      throw new Error('获取到的文件数据无效')
    }

    // 默认文件名
    const fileName = row.name || 'backup.sql'

    const url = window.URL.createObjectURL(response)
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
      customClass: 'custom-message-box',
    })

    // 要求用户输入验证码
    const verificationCode = await ElMessageBox.prompt('请输入删除验证码：', '验证码确认', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '验证码不能为空',
      inputType: 'password',
    })

    if (!verificationCode.value || !verificationCode.value.trim()) {
      ElMessage.error('验证码不能为空')
      return
    }

    const resp: any = await deleteBackupRecordApi(row.id, verificationCode.value.trim())
    if (resp.code === 0) {
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
    const resp = await getBackupPlansApi()
    const planData = Array.isArray(resp.data) ? resp.data[0] : resp.data

    if (resp.code === 0 && planData) {
      // 填充表单数据
      if (planData.id) {
        planForm.id = Number(planData.id)
      }
      // 简单的反向映射，实际应该解析cron表达式
      planForm.frequency = 1
      console.log('获取到定时任务配置:', planData)
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
      // id: planForm.id,
      name: '默认备份计划',
      enabled: true,
      // 根据frequency生成cronExpression
      cronExpression:
        planForm.frequency === 1
          ? '0 0 2 * * ?'
          : planForm.frequency === 2
            ? '0 0 2 ? * MON'
            : '0 0 2 1 * ?',
      retentionDays: 30, // 默认保留30天
      // verificationCode: planForm.verificationCode,
    }

    // 调试日志
    console.log('保存备份计划参数:', payload)

    const resp = await createBackupPlanApi(payload as any)
    if (resp.code === 0) {
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

  const lastBackupTime = new Date(lastBackup.createdAt!).getTime()
  const now = Date.now()
  const daysDiff = (now - lastBackupTime) / (1000 * 60 * 60 * 24)

  if (daysDiff > 7) {
    ElMessage.warning('距离上次备份已超过7天，建议尽快执行备份')
  }
}

// 加载后端备份列表
const loadBackups = async () => {
  try {
    const pageReq: BackupPageRequest = {
      current: pagination.currentPage,
      size: pagination.pageSize,
    }
    const dto = {
      sortColumn: 'create_time',
      sortType: 'desc' as const,
      name: searchQuery.name || undefined, // 传递备份文件名称搜索
      type: searchQuery.type, // 传递备份类型搜索
    }
    const resp = await pageBackupRecordsApi({ ...pageReq, ...dto })
    if (resp.code === 0 && resp.data) {
      const pageData = resp.data
      pagination.total = pageData.total
      // 映射到页面需要的 BackupRecord 结构
      allRecords.value = (pageData.records || []).map((r: any) => ({
        id: String(r.id),
        name: r.name || r.fileName,
        operator: r.createName || '-',
        type: r.type, // 保持原始类型值
        status: 1, // 默认为成功
        size: r.totalSizeFormat || '-',
        createdAt: r.createTime,
        description: r.name || '',
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
  // Use status as any to bypass stricter type check for now if enum is problematic
  const success = records.value.filter(
    (item: any) => item.status === 1 || item.status === 'success',
  ).length
  const failed = records.value.length - success
  return { success, failed }
})

const latestRecord = computed(() => records.value[0])
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  gap: 16px;
}

.table-container {
  flex: 1;
  padding: 0 24px 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.unified-table {
  width: 100%;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;

  &__left {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .table-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }

  .table-subtitle {
    font-size: 13px;
    color: var(--el-text-color-secondary);
  }

  &__actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.file-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--el-text-color-primary);
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
