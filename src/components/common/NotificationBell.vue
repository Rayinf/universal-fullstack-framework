<template>
  <el-popover
    placement="bottom-end"
    :width="360"
    trigger="click"
    popper-class="notification-bell-popover"
    @show="onPopoverShow"
  >
    <template #reference>
      <el-badge :value="unreadCount" :hidden="unreadCount === 0" :max="99" class="bell-badge">
        <el-icon class="action-icon bell-icon" :size="20">
          <Bell />
        </el-icon>
      </el-badge>
    </template>

    <div class="popover-header">
      <span>消息通知</span>
      <el-button
        type="primary"
        link
        size="small"
        @click="handleMarkAllRead"
        :disabled="unreadCount === 0"
      >
        全部已读
      </el-button>
    </div>

    <div class="notification-list" v-loading="loading">
      <template v-if="notifications.length > 0">
        <div
          v-for="item in notifications"
          :key="item.id"
          class="notification-item"
          :class="{ 'is-unread': item.isRead === 0 }"
          @click="handleClickNotification(item)"
        >
          <div class="item-title">
            <el-tag :type="typeTagType(item.type)" size="small" effect="light" class="type-tag">
              {{ typeText(item.type) }}
            </el-tag>
            {{ item.title }}
          </div>
          <div class="item-content" v-if="item.content">{{ item.content }}</div>
          <div class="item-footer">
            <span>{{ item.createTime }}</span>
            <el-button type="danger" link size="small" @click.stop="handleDelete(item.id)">
              删除
            </el-button>
          </div>
        </div>
      </template>
      <el-empty v-else description="暂无通知" :image-size="60" />
    </div>

    <div class="popover-footer" v-if="notifications.length > 0">
      <el-button type="primary" link size="small" @click="handleViewAll"> 查看全部 </el-button>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell } from '@element-plus/icons-vue'
import {
  pageNotificationsApi,
  getUnreadCountApi,
  markNotificationReadApi,
  markAllNotificationsReadApi,
  deleteNotificationApi,
} from '@/api/system/notification'
import type { NotificationRecord } from '@/types/system/notification'

const router = useRouter()

const unreadCount = ref<number>(0)
const notifications = ref<NotificationRecord[]>([])
const loading = ref<boolean>(false)
let pollTimer: ReturnType<typeof setInterval> | null = null

const typeText = (type: number): string => {
  return ({ 1: '审批', 2: '预警', 3: '系统' } as Record<number, string>)[type] || '系统'
}

const typeTagType = (type: number): 'warning' | 'danger' | 'info' => {
  return (
    ({ 1: 'warning', 2: 'danger', 3: 'info' } as Record<number, 'warning' | 'danger' | 'info'>)[
      type
    ] || 'info'
  )
}

const fetchUnreadCount = async () => {
  try {
    const res = await getUnreadCountApi()
    if (res.code === 0 || res.code === 200) {
      unreadCount.value = res.data?.count ?? 0
    }
  } catch {
    // 静默失败
  }
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const res = await pageNotificationsApi({ current: 1, size: 10 })
    if ((res.code === 0 || res.code === 200) && res.data) {
      notifications.value = res.data.records || []
    }
  } catch {
    notifications.value = []
  } finally {
    loading.value = false
  }
}

const onPopoverShow = () => {
  fetchNotifications()
}

const handleClickNotification = async (item: NotificationRecord) => {
  if (item.isRead === 0) {
    try {
      await markNotificationReadApi(item.id)
      item.isRead = 1
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    } catch {
      // 静默失败
    }
  }
  // 如果有业务关联，可以跳转
  if (item.bizType && item.bizId) {
    const routeMap: Record<string, string> = {
      quotation: '/sales/quotation',
      contract: '/sales/contracts',
      work_order: '/production/work-orders',
    }
    const target = routeMap[item.bizType]
    if (target) {
      router.push(target)
    }
  }
}

const handleMarkAllRead = async () => {
  try {
    await markAllNotificationsReadApi()
    unreadCount.value = 0
    notifications.value.forEach((n) => (n.isRead = 1))
  } catch {
    // 静默失败
  }
}

const handleDelete = async (id: string) => {
  try {
    await deleteNotificationApi(id)
    const idx = notifications.value.findIndex((n) => n.id === id)
    if (idx !== -1) {
      if (notifications.value[idx].isRead === 0) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }
      notifications.value.splice(idx, 1)
    }
  } catch {
    // 静默失败
  }
}

const handleViewAll = () => {
  router.push('/system/notifications')
}

onMounted(() => {
  fetchUnreadCount()
  // 每 60 秒轮询一次未读数
  pollTimer = setInterval(fetchUnreadCount, 60000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})
</script>

<style scoped>
.bell-badge {
  display: flex;
  align-items: center;
}

.bell-icon {
  cursor: pointer;
  font-size: 20px;
  color: #5a5e66;
}

.bell-icon:hover {
  color: var(--el-color-primary);
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #ebeef5;
  font-weight: 600;
  font-size: 14px;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f2f6fc;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.is-unread {
  background-color: #ecf5ff;
}

.notification-item:last-child {
  border-bottom: none;
}

.item-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.type-tag {
  flex-shrink: 0;
}

.item-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
  color: #909399;
}

.popover-footer {
  padding: 8px 16px;
  border-top: 1px solid #ebeef5;
  text-align: center;
}
</style>
