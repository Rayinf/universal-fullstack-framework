<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-row">
        <div class="title-accent"></div>
        <h2>消息通知</h2>
      </div>
      <span class="page-description">查看和管理系统通知消息</span>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <div class="search-area">
          <el-form :inline="true" @submit.prevent="handleSearch">
            <el-form-item>
              <el-select
                v-model="query.isRead"
                placeholder="阅读状态"
                clearable
                class="search-input"
                @change="handleSearch"
              >
                <el-option label="未读" value="0" />
                <el-option label="已读" value="1" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="action-area">
          <el-button type="primary" @click="handleMarkAllRead" :disabled="unreadCount === 0">
            全部标为已读
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table
          :data="tableData"
          stripe
          highlight-current-row
          v-loading="loading"
          style="width: 100%"
        >
          <el-table-column label="状态" width="70" align="center">
            <template #default="{ row }">
              <el-tag :type="row.isRead === 0 ? 'danger' : 'info'" size="small" effect="light">
                {{ row.isRead === 0 ? '未读' : '已读' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="类型" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="typeTagType(row.type)" size="small" effect="plain">
                {{ typeText(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
          <el-table-column prop="createTime" label="时间" width="180" />
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleMarkRead(row)" v-if="row.isRead === 0">
                标为已读
              </el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  pageNotificationsApi,
  getUnreadCountApi,
  markNotificationReadApi,
  markAllNotificationsReadApi,
  deleteNotificationApi,
} from '@/api/system/notification'
import type { NotificationRecord } from '@/types/system/notification'

interface NotificationQuery {
  isRead: string
}

const loading = ref<boolean>(false)
const tableData = ref<NotificationRecord[]>([])
const unreadCount = ref<number>(0)
const query = reactive<NotificationQuery>({ isRead: '' })
const pagination = reactive({ current: 1, size: 20, total: 0 })

const typeText = (type: number): string =>
  (({ 1: '审批', 2: '预警', 3: '系统' }) as Record<number, string>)[type] || '系统'

const typeTagType = (type: number): 'warning' | 'danger' | 'info' =>
  (({ 1: 'warning', 2: 'danger', 3: 'info' }) as Record<number, 'warning' | 'danger' | 'info'>)[
    type
  ] || 'info'

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageNotificationsApi({
      current: pagination.current,
      size: pagination.size,
      isRead: query.isRead || undefined,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
      ElMessage.error(res.msg || '获取通知失败')
    }
  } catch (error) {
    console.error('获取通知失败:', error)
    tableData.value = []
    pagination.total = 0
    ElMessage.error('发生网络错误')
  } finally {
    loading.value = false
  }
}

const fetchUnreadCount = async () => {
  try {
    const res = await getUnreadCountApi()
    if (res.code === 0 || res.code === 200) {
      unreadCount.value = res.data?.count ?? 0
    }
  } catch {
    // 静默
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  query.isRead = ''
  pagination.current = 1
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.current = 1
  loadData()
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
  loadData()
}

const handleMarkRead = async (row: NotificationRecord) => {
  try {
    const res = await markNotificationReadApi(row.id)
    if (res.code === 0 || res.code === 200) {
      row.isRead = 1
      unreadCount.value = Math.max(0, unreadCount.value - 1)
      ElMessage.success('已标为已读')
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

const handleMarkAllRead = async () => {
  try {
    const res = await markAllNotificationsReadApi()
    if (res.code === 0 || res.code === 200) {
      unreadCount.value = 0
      tableData.value.forEach((n) => (n.isRead = 1))
      ElMessage.success('已全部标为已读')
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row: NotificationRecord) => {
  try {
    await ElMessageBox.confirm('确定删除该通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    const res = await deleteNotificationApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
      fetchUnreadCount()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadData()
  fetchUnreadCount()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
