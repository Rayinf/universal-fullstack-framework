<template>
  <div class="page-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>操作日志列表</h2>
          <div class="page-description">共 {{ pagination.total }} 条记录，帮助追溯关键操作行为。</div>
        </div>
      </div>
      <div class="header-actions" style="display: flex; justify-content: flex-end; gap: 12px;">
        <el-button 
          type="danger" 
          @click="handleBatchDelete" 
          :disabled="!selectedLogs.length"
          size="small"
          style="width: 100px;"
        >
          <el-icon><Delete /></el-icon>
          批量删除
        </el-button>
        <el-button type="danger" @click="handleClearLogs" :disabled="!hasData" style="width: 100px;">
          <el-icon><Delete /></el-icon>
          清空日志
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-actions-panel">
      <el-form :model="query" class="search-form" @submit.prevent>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="日志类型">
              <el-select v-model="query.type" placeholder="全部类型" clearable>
                <el-option label="普通用户日志" :value="0" />
                <el-option label="管理员日志" :value="1" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="操作人">
              <el-input v-model="query.operator" placeholder="请输入操作人" clearable>
                <template #prefix>
                  <el-icon><User /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="操作内容">
              <el-input v-model="query.content" placeholder="请输入操作内容关键词" clearable>
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
          </el-col>
          <!-- <el-col :span="6">
            <el-form-item label="租户代码">
              <el-input v-model="query.tenantCode" placeholder="请输入租户代码" clearable />
            </el-form-item>
          </el-col> -->
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="时间范围">
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
                @change="handleDateRangeChange"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <div class="action-area search-actions">
              <el-button type="primary" @click="handleSearch" style="width: 100px;">
                <el-icon><Search /></el-icon>
                查询
              </el-button>
              <el-button @click="handleReset" style="width: 100px;">
                <el-icon><Refresh /></el-icon>
                重置
              </el-button>
            </div>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <div class="content-card">
      <div class="table-container">
        <el-table 
        :data="logs" 
        v-loading="loading" 
        stripe 
        highlight-current-row 
        empty-text="暂无日志数据" 
        class="unified-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <!-- <el-table-column prop="id" label="ID" width="80" /> -->
        <el-table-column prop="type" label="日志类型" width="160" align="center">
          <template #default="{ row }">
            <el-tag :type="getLogTypeTagType(row.type)" size="small">
              {{ getLogTypeText(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="160">
          <template #default="{ row }">
            <el-tag type="info" effect="plain">{{ row.operator }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="module" label="模块" width="160" />
        <el-table-column prop="action" label="操作内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="createTime" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" align="center" class-name="col-actions">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" size="small" @click="handleDetail(row)">
                <el-icon><View /></el-icon>
                详情
              </el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
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

    <!-- 日志详情弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="日志详情"
      width="800px"
      :close-on-click-modal="false"
      align-center
    >
      <div v-if="current" class="log-detail">
        <el-descriptions :column="2" border>
          <!-- <el-descriptions-item label="日志ID">{{ current.id }}</el-descriptions-item> -->
          <el-descriptions-item label="日志类型">
            <el-tag :type="getLogTypeTagType(current.type)" size="small">
              {{ getLogTypeText(current.type) }}
            </el-tag>
          </el-descriptions-item>
          <!-- <el-descriptions-item label="操作人">{{ current.operator }}</el-descriptions-item> -->
          <el-descriptions-item label="模块">{{ current.module }}</el-descriptions-item>
          <!-- <el-descriptions-item label="系统日志ID">{{ current.sysLogId }}</el-descriptions-item> -->
          <el-descriptions-item label="创建时间">{{ current.createTime }}</el-descriptions-item>
          <el-descriptions-item label="操作内容" :span="2">
            <div class="log-content">{{ current.action }}</div>
          </el-descriptions-item>
          <el-descriptions-item label="请求参数" :span="2">
            <pre class="log-content">{{ current.request }}</pre>
          </el-descriptions-item>
          <el-descriptions-item label="响应结果" :span="2">
            <pre class="log-content">{{ current.response }}</pre>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 清空日志弹窗 -->
    <el-dialog
      v-model="clearDialogVisible"
      title="清空日志"
      width="500px"
      :close-on-click-modal="false"
      align-center
    >
      <el-form :model="clearForm" label-width="100px">
        <el-form-item label="日志类型">
          <el-select v-model="clearForm.logType" placeholder="请选择日志类型">
            <el-option label="普通用户日志" :value="0" />
            <el-option label="管理员日志" :value="1" />
          </el-select>
        </el-form-item>
        <el-form-item label="清空类型">
          <el-select v-model="clearForm.clearType" placeholder="请选择清空类型">
            <el-option label="最近一周" :value="1" />
            <el-option label="最近一个月" :value="2" />
            <el-option label="最近3个月" :value="3" />
            <el-option label="最近半年" :value="4" />
            <el-option label="最近一年" :value="5" />
            <el-option label="最近三年" :value="6" />
            <el-option label="全部" :value="9" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="clearDialogVisible = false">取消</el-button>
          <el-button type="danger" @click="handleConfirmClear" :loading="clearLoading" style="margin-left: 12px;">
            确认清空
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Delete,
  User,
  Search,
  Refresh,
  View
} from '@element-plus/icons-vue'
import { 
  pageOperationLogApi, 
  getOperationLogDetailApi 
} from '@/api/modules/operation-log'
import {
  deleteSysLogUserApi,
  clearSysLogUserApi
} from '@/api/modules/sys-log-user'
import type { 
  OperationLogRecord, 
  OperationLogPageQuery,
  SysLogUserVO,
  SysLogUserPageRequest,
  SysLogUserQueryDto
} from '@/types/operation-log'

// UI查询参数 (包含扩展字段)
const query = reactive<OperationLogPageQuery>({
  sortColumn: 'create_time',
  sortType: 'desc',
  type: undefined, // 允许查询所有类型
  content: '',
  username: '',
  startTime: '',
  endTime: '',
  tenantCode: '',
  // UI扩展字段
  operator: '',
  module: ''
})

// 时间范围
const dateRange = ref<[string, string] | null>(null)

// 数据状态
const logs = ref<OperationLogRecord[]>([])
const loading = ref(false)
const clearLoading = ref(false)
const dialogVisible = ref(false)
const clearDialogVisible = ref(false)
const current = ref<OperationLogRecord | null>(null)

// 选中的日志
const selectedLogs = ref<OperationLogRecord[]>([])

// 清空表单
const clearForm = reactive({
  logType: 1, // 默认管理员日志
  clearType: 1
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 计算属性
const hasData = computed(() => logs.value.length > 0)

// 模块选项 (从已有数据中提取或预定义)
const moduleOptions = ref<string[]>([
  '用户管理',
  '订单管理', 
  '客户管理',
  '文档管理',
  '系统管理',
  '数据备份'
])

// 加载操作日志数据
const loadData = async () => {
  loading.value = true
  try {
    // 构建分页参数 (page)
    const pageRequest: SysLogUserPageRequest = {
      current: pagination.currentPage,
      size: pagination.pageSize,
      optimizeJoinOfCountSql: true
    }
    
    // 构建查询条件参数 (dto) - 转换UI参数到API参数
    const queryDto: SysLogUserQueryDto = {
      sortColumn: query.sortColumn || 'create_time',
      sortType: query.sortType || 'desc',
      type: query.type, // 使用用户选择的日志类型
      content: buildContentFilter(query.content || '', query.module || ''),
      realName: query.operator || '', // 操作人查询使用realName字段
      startTime: query.startTime,
      endTime: query.endTime,
      tenantCode: query.tenantCode || ''
    }
    
    const response = await pageOperationLogApi(pageRequest, queryDto)
    if (response.code === 200 && response.data) {
      // 转换SysLogUserVO数据格式以适配操作日志UI
      logs.value = response.data.records.map((record: SysLogUserVO): OperationLogRecord => ({
        // 原始API字段
        id: record.id,
        content: record.content,
        type: record.type,
        sysLogId: record.sysLogId,
        creator: record.creator,
        createBy: record.createBy,
        createTime: record.createTime,
        realName: record.realName,
        // UI扩展字段
        operator: record.realName || record.creator,
        module: extractModuleFromContent(record.content),
        action: record.content,
        ip: '203.0.113.10', // 模拟IP地址
        request: `{"action": "${record.content}", "operator": "${record.realName || record.creator}"}`,
        response: `{"code": 0, "msg": "操作成功", "timestamp": "${record.createTime}"}`
      }))
      pagination.total = response.data.total
      
      // 更新模块选项
      const modules = Array.from(new Set(logs.value.map(log => log.module).filter(Boolean))) as string[]
      if (modules.length > 0) {
        moduleOptions.value = [...new Set([...moduleOptions.value, ...modules])]
      }
    } else {
      ElMessage.error(response.msg || '查询失败')
    }
  } catch (error) {
    console.error('查询操作日志失败:', error)
    ElMessage.error('查询操作日志失败，请重试')
  } finally {
    loading.value = false
  }
}

// 构建内容筛选条件
const buildContentFilter = (content: string, module: string): string => {
  const filters: string[] = []
  
  // 添加直接内容筛选
  if (content && content.trim()) {
    filters.push(content.trim())
  }
  
  // 根据模块添加关键词筛选
  if (module) {
    const moduleKeywords = getModuleKeywords(module)
    if (moduleKeywords.length > 0) {
      // 如果已有内容筛选，则组合；否则直接使用模块关键词
      if (filters.length > 0) {
        // 使用AND逻辑：内容包含指定文本且属于指定模块
        filters.push(...moduleKeywords)
      } else {
        // 只有模块筛选，使用OR逻辑：包含任一模块关键词
        return moduleKeywords[0] || '' // 使用主要关键词
      }
    }
  }
  
  return filters.join(' ')
}

// 获取模块对应的关键词
const getModuleKeywords = (module: string): string[] => {
  const moduleKeywordMap: Record<string, string[]> = {
    '用户管理': ['用户', '登录', '账号'],
    '订单管理': ['订单', '项目', '工单'],
    '客户管理': ['客户', '顾客'],
    '文档管理': ['文档', '资料', '文件'],
    '系统管理': ['系统', '配置', '参数'],
    '数据备份': ['备份', '数据库', '恢复']
  }
  return moduleKeywordMap[module] || []
}

// 从日志内容中提取模块信息
const extractModuleFromContent = (content: string): string => {
  if (content.includes('用户') || content.includes('登录') || content.includes('账号')) return '用户管理'
  if (content.includes('订单') || content.includes('项目') || content.includes('工单')) return '订单管理'
  if (content.includes('客户') || content.includes('顾客')) return '客户管理'
  if (content.includes('文档') || content.includes('资料') || content.includes('文件')) return '文档管理'
  if (content.includes('系统') || content.includes('配置') || content.includes('参数')) return '系统管理'
  if (content.includes('备份') || content.includes('数据库') || content.includes('恢复')) return '数据备份'
  return '其他'
}


// 搜索处理
const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

// 重置处理
const handleReset = () => {
  // 重置UI查询参数
  Object.assign(query, {
    sortColumn: 'create_time',
    sortType: 'desc',
    type: undefined,
    content: '',
    username: '',
    startTime: '',
    endTime: '',
    tenantCode: '',
    operator: '',
    module: ''
  })
  dateRange.value = null
  pagination.currentPage = 1
  loadData()
}

// 时间范围变化处理
const handleDateRangeChange = (dates: [string, string] | null) => {
  if (dates) {
    query.startTime = dates[0]
    query.endTime = dates[1]
  } else {
    query.startTime = ''
    query.endTime = ''
  }
}

// 选择变化处理
const handleSelectionChange = (selection: OperationLogRecord[]) => {
  selectedLogs.value = selection
}

const handleDetail = async (row: OperationLogRecord) => {
  try {
    const response = await getOperationLogDetailApi(row.id)
    if (response.code === 200 && response.data) {
      const record = response.data
      current.value = {
        // 原始API字段
        id: record.id,
        content: record.content,
        type: record.type,
        sysLogId: record.sysLogId,
        creator: record.creator,
        createBy: record.createBy,
        createTime: record.createTime,
        realName: record.realName,
        // UI扩展字段
        operator: record.realName || record.creator,
        module: extractModuleFromContent(record.content),
        action: record.content,
        ip: '203.0.113.10',
        request: JSON.stringify({
          action: record.content,
          operator: record.realName || record.creator,
          timestamp: record.createTime,
          logType: record.type
        }, null, 2),
        response: JSON.stringify({
          code: 200,
          msg: "操作成功",
          data: {
            logId: record.id,
            sysLogId: record.sysLogId,
            timestamp: record.createTime
          }
        }, null, 2)
      }
      dialogVisible.value = true
    } else {
      ElMessage.error(response.msg || '获取日志详情失败')
    }
  } catch (error) {
    console.error('获取日志详情失败:', error)
    ElMessage.error('获取日志详情失败，请重试')
  }
}

// 删除单条日志
const handleDelete = async (row: OperationLogRecord) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除ID为 ${row.id} 的日志吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'custom-message-box'
      }
    )
    
    const response = await deleteSysLogUserApi([row.id])
    if (response.code === 200) {
      ElMessage.success('日志删除成功')
      loadData()
    } else {
      ElMessage.error(response.msg || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除日志失败:', error)
      ElMessage.error('删除日志失败，请重试')
    }
  }
}

// 批量删除
const handleBatchDelete = async () => {
  if (selectedLogs.value.length === 0) {
    ElMessage.warning('请选择要删除的日志')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedLogs.value.length} 条日志吗？此操作不可撤销。`,
      '批量删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        customClass: 'custom-message-box'
      }
    )
    
    const ids = selectedLogs.value.map(log => log.id)
    const response = await deleteSysLogUserApi(ids)
    if (response.code === 200) {
      ElMessage.success(`成功删除 ${selectedLogs.value.length} 条日志`)
      selectedLogs.value = []
      loadData()
    } else {
      ElMessage.error(response.msg || '批量删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除日志失败:', error)
      ElMessage.error('批量删除日志失败，请重试')
    }
  }
}

// 清空日志
const handleClearLogs = () => {
  clearDialogVisible.value = true
}

// 确认清空
const handleConfirmClear = async () => {
  clearLoading.value = true
  try {
    const response = await clearSysLogUserApi(clearForm.logType, clearForm.clearType)
    if (response.code === 200) {
      ElMessage.success('日志清空成功')
      clearDialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(response.msg || '清空失败')
    }
  } catch (error) {
    console.error('清空日志失败:', error)
    ElMessage.error('清空日志失败，请重试')
  } finally {
    clearLoading.value = false
  }
}


// 工具函数
const getLogTypeText = (type: number) => {
  const typeMap: Record<number, string> = {
    0: '普通用户日志',
    1: '管理员日志'
  }
  return typeMap[type] || '未知类型'
}

type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'
const getLogTypeTagType = (type: number): TagType => {
  const typeMap: Record<number, TagType> = {
    0: 'success',  // 普通用户日志
    1: 'primary'   // 管理员日志
  }
  return typeMap[type] ?? 'info'
}

// 分页事件处理
const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadData()
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})

</script>

<style scoped lang="scss">
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 24px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  
  &__icon {
    font-size: 28px;
    color: var(--el-color-primary);
  }
}

.page-actions {
  display: flex;
  gap: 12px;
}

.search-card {
  margin-bottom: 24px;
  
  .search-form {
    .search-actions {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      align-items: center;
      height: 32px;
    }
  }
}

.table-card {
  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0 0 4px;
      font-size: 18px;
      font-weight: 600;
    }
    
    p {
      margin: 0;
      color: var(--el-text-color-secondary);
      font-size: 13px;
    }
    
    &__actions {
      display: flex;
      gap: 8px;
    }
  }
}

.log-detail {
  .log-content {
    max-height: 200px;
    overflow-y: auto;
    padding: 12px;
    background: var(--el-fill-color-lighter);
    border-radius: 6px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-break: break-all;
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .page-actions {
    justify-content: center;
  }
  
  .search-form {
    .el-row {
      .el-col {
        margin-bottom: 16px;
      }
    }
    
    .search-actions {
      justify-content: center;
    }
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    
    &__actions {
      justify-content: center;
    }
  }
}
</style>

<style lang="scss">
/* 全局样式：修复MessageBox按钮宽度 */
.custom-message-box {
  .el-message-box__btns {
    .el-button {
      min-width: 70px !important;
      max-width: 100px !important;
      padding: 8px 16px !important;
    }
  }
}

</style>
