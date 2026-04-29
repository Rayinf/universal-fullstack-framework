<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>用户日志管理</h2>
          <div class="page-description">查看用户操作日志，支持日志查询和详情查看。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="query" class="filter-form" inline @submit.prevent>
          <el-form-item label="用户名">
            <el-input v-model="query.username" placeholder="用户名" clearable>
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="操作内容">
            <el-input
              v-model="query.content"
              placeholder="操作内容关键词"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="日志类型">
            <el-select
              v-model="query.logType"
              placeholder="全部类型"
              clearable
              style="width: 140px"
            >
              <el-option label="普通用户日志" :value="0" />
              <el-option label="管理员日志" :value="1" />
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
            <span class="table-title">用户日志列表</span>
            <span class="table-subtitle">共 {{ pagination.total }} 条记录</span>
          </div>
          <div class="table-header__actions">
            <el-button type="danger" @click="handleClear" plain>
              <el-icon><Delete /></el-icon>清空日志
            </el-button>
          </div>
        </div>

        <el-table
          :data="logs"
          stripe
          highlight-current-row
          v-loading="loading"
          class="unified-table"
        >
          <el-table-column prop="username" label="用户名" width="120">
            <template #default="{ row }">
              {{ row.realName || row.username || row.creator }}
            </template>
          </el-table-column>
          <el-table-column prop="content" label="操作内容" min-width="200" />
          <el-table-column prop="createTime" label="创建时间" width="180" />
          <el-table-column label="操作" fixed="right" width="90" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleView(row)">详情</el-button>
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
    <el-dialog v-model="detailVisible" title="日志详情" width="800px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="用户名">{{
          currentLog?.realName || currentLog?.username || currentLog?.creator
        }}</el-descriptions-item>
        <el-descriptions-item label="日志ID">{{ currentLog?.id }}</el-descriptions-item>
        <el-descriptions-item label="系统日志ID" :span="2">{{
          currentLog?.sysLogId
        }}</el-descriptions-item>
        <el-descriptions-item label="操作内容" :span="2">{{
          currentLog?.content
        }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{
          currentLog?.createTime
        }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, RefreshLeft, Delete } from '@element-plus/icons-vue'
import { pageOperationLogApi, clearSysLogUserApi } from '@/api/system/log'
import type { SysLogUserRecord, SysLogUserPageQuery } from '@/types/system/log'

const query = reactive<SysLogUserPageQuery>({
  username: '',
  content: '',
  logType: undefined,
  sortColumn: 'create_time',
  sortType: 'desc',
})

const logs = ref<SysLogUserRecord[]>([])
const loading = ref(false)
const detailVisible = ref(false)
const currentLog = ref<SysLogUserRecord | null>(null)

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageOperationLogApi({
      ...query,
      current: pagination.currentPage,
      size: pagination.pageSize,
    })
    if (res.code === 0 && res.data) {
      logs.value = res.data.records || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    console.error('加载日志数据失败:', error)
    ElMessage.error('加载日志数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  query.username = ''
  query.content = ''
  query.logType = undefined
  handleSearch()
}

const handleSizeChange = () => {
  loadData()
}

const handleCurrentChange = () => {
  loadData()
}

const handleView = (row: SysLogUserRecord) => {
  currentLog.value = row
  detailVisible.value = true
}

const handleClear = () => {
  ElMessageBox.confirm('此操作将清空所有日志记录，是否继续？', '警告', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      try {
        await clearSysLogUserApi({ logType: 1, clearType: 9 })
        ElMessage.success('清空成功')
        loadData()
      } catch (error) {
        console.error('清空失败:', error)
        ElMessage.error('清空失败')
      }
    })
    .catch(() => {
      // 用户取消操作
    })
}

onMounted(() => {
  loadData()
})
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

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
