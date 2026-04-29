<template>
  <div class="placeholder-container">
    <el-card class="placeholder-card">
      <div class="placeholder-content">
        <el-icon class="placeholder-icon" :size="80">
          <component :is="getModuleIcon()" />
        </el-icon>
        <h2 class="placeholder-title">{{ pageTitle }}</h2>
        <p class="placeholder-desc">{{ pageDesc }}</p>
        <div class="placeholder-info">
          <el-tag type="info" size="large">功能编号: {{ functionCode }}</el-tag>
          <el-tag type="warning" size="large">开发中</el-tag>
        </div>
        <el-divider />
        <div class="placeholder-details">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="当前路径">{{ currentPath }}</el-descriptions-item>
            <el-descriptions-item label="所属模块">{{ moduleName }}</el-descriptions-item>
            <el-descriptions-item label="功能状态">
              <el-tag type="info">待开发</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <div class="placeholder-actions">
          <el-button type="primary" @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回上一页
          </el-button>
          <el-button @click="goHome">
            <el-icon><HomeFilled /></el-icon>
            返回首页
          </el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft, HomeFilled, Document, Calendar, Files,
  Setting, CircleCheck, DataAnalysis, Connection, Monitor, Tools, Warning
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const pageTitle = computed(() => {
  return (route.meta.title as string) || '功能开发中'
})

const functionCode = computed(() => {
  return (route.meta.functionCode as string) || 'N/A'
})

const currentPath = computed(() => route.path)

const moduleName = computed(() => {
  const path = route.path
  if (path.startsWith('/task')) return '任务管理'
  if (path.startsWith('/planning')) return '计划排程管理'
  if (path.startsWith('/process')) return '工艺技术管理'
  if (path.startsWith('/production')) return '生产执行管理'
  if (path.startsWith('/quality')) return '质量监督管理'
  if (path.startsWith('/dashboard')) return '信息发布与展示看板'
  if (path.startsWith('/collaboration')) return '生产协作'
  if (path.startsWith('/comprehensive')) return '综合展示'
  if (path.startsWith('/system')) return '系统管理'
  return '其他模块'
})

const pageDesc = computed(() => {
  const code = functionCode.value
  if (code === 'N/A') return '该页面正在开发中,敬请期待...'
  return `该功能模块(${code})正在开发中,敬请期待...`
})

const getModuleIcon = () => {
  const path = route.path
  if (path.startsWith('/task')) return Document
  if (path.startsWith('/planning')) return Calendar
  if (path.startsWith('/process')) return Files
  if (path.startsWith('/production')) return Setting
  if (path.startsWith('/quality')) return CircleCheck
  if (path.startsWith('/dashboard')) return DataAnalysis
  if (path.startsWith('/collaboration')) return Connection
  if (path.startsWith('/comprehensive')) return Monitor
  if (path.startsWith('/system')) return Tools
  return Warning
}

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<style scoped>
.placeholder-container {
  padding: 40px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: calc(100vh - 120px);
}

.placeholder-card {
  max-width: 600px;
  width: 100%;
}

.placeholder-content {
  text-align: center;
  padding: 20px;
}

.placeholder-icon {
  color: #409eff;
  margin-bottom: 20px;
}

.placeholder-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
}

.placeholder-desc {
  font-size: 14px;
  color: #909399;
  margin: 0 0 20px 0;
}

.placeholder-info {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 10px;
}

.placeholder-details {
  text-align: left;
  margin-bottom: 20px;
}

.placeholder-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

@media (max-width: 768px) {
  .placeholder-container {
    padding: 20px 10px;
  }

  .placeholder-title {
    font-size: 20px;
  }

  .placeholder-actions {
    flex-direction: column;
  }

  .placeholder-info {
    flex-direction: column;
    align-items: center;
  }
}
</style>
