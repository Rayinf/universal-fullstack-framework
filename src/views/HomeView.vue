<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">{{ systemTitle }}</span>
          <span class="card-subtitle">当前已收敛为系统管理基础框架</span>
        </div>
      </template>
      <p class="welcome-desc">
        当前版本仅保留系统管理完整功能，后续业务开发请基于该框架按模块逐步接入。
      </p>
      <el-button type="primary" @click="navigateTo(FRAMEWORK_DEFAULT_ROUTE)">
        进入系统管理
      </el-button>
    </el-card>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>已启用模块</span>
          </template>
          <div v-for="module in enabledModules" :key="module.id" class="module-item">
            <div class="module-title">{{ module.title }}</div>
            <div class="module-desc">{{ module.description }}</div>
            <el-tag type="success" size="small">已启用</el-tag>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <span>预留扩展模块</span>
          </template>
          <div v-for="module in plannedModules" :key="module.id" class="module-item">
            <div class="module-title">{{ module.title }}</div>
            <div class="module-desc">{{ module.description }}</div>
            <el-tag type="info" size="small">未启用</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="quick-card">
      <template #header>
        <span>系统管理快捷入口</span>
      </template>
      <el-row :gutter="12">
        <el-col :xs="12" :sm="8" :md="6" v-for="item in quickLinks" :key="item.path">
          <div class="quick-link" @click="navigateTo(item.path)">
            <el-icon class="quick-icon"><component :is="item.icon" /></el-icon>
            <div class="quick-title">{{ item.title }}</div>
            <div class="quick-desc">{{ item.desc }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useRouter } from 'vue-router'
import { User, OfficeBuilding, List, Checked, Tickets, Management, Grid, Document } from '@element-plus/icons-vue'
import { useSystemConfigStore } from '@/stores/system/systemConfig'
import { FRAMEWORK_DEFAULT_ROUTE, getEnabledModules, getPlannedModules } from '@/config/frameworkConfig'

interface QuickLink {
  title: string
  desc: string
  path: string
  icon: Component
}

const router = useRouter()
const systemConfigStore = useSystemConfigStore()

const systemTitle = computed(() => {
  return `${systemConfigStore.configData.systemName || 'MES管理系统'}基础框架`
})

const enabledModules = computed(() => getEnabledModules())
const plannedModules = computed(() => getPlannedModules())

const quickLinks: QuickLink[] = [
  {
    title: '基础CRUD',
    desc: '本地后端增删改查',
    path: '/system/basic-crud',
    icon: Grid,
  },
  {
    title: '项目示例',
    desc: '项目管理完整页面',
    path: '/system/project-demo',
    icon: Document,
  },
  {
    title: '采购示例',
    desc: '采购单状态流转',
    path: '/system/purchase-demo',
    icon: List,
  },
  {
    title: '库存示例',
    desc: '库存与流水联动',
    path: '/system/inventory-demo',
    icon: Management,
  },
  {
    title: '账户管理',
    desc: '用户与账号维护',
    path: '/system/account-management',
    icon: User,
  },
  {
    title: '组织管理',
    desc: '部门架构维护',
    path: '/system/dept-management',
    icon: OfficeBuilding,
  },
  {
    title: '参数字典',
    desc: '参数与编码规则',
    path: '/system/param/manage',
    icon: List,
  },
  {
    title: '审批规则',
    desc: '业务审批流程配置',
    path: '/system/approval',
    icon: Checked,
  },
  {
    title: '系统日志',
    desc: '操作与用户日志',
    path: '/system/operation-log',
    icon: Tickets,
  },
  {
    title: '系统配置',
    desc: '系统基础配置',
    path: '/system/system-config',
    icon: Management,
  },
]

const navigateTo = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.home-container {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: var(--system-gradient-bg);
  min-height: 100%;
  box-sizing: border-box;
}

:deep(.el-card) {
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04) !important;
  background-color: var(--el-bg-color);
}

:deep(.el-card__header) {
  border-bottom: 1px solid var(--el-border-color-lighter);
  font-weight: 600;
  color: var(--el-text-color-primary);
  padding: 16px 20px;
}

.welcome-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  line-height: 1.2;
}

.card-subtitle {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.welcome-desc {
  margin: 0 0 16px;
  color: var(--el-text-color-regular);
  line-height: 1.6;
}

.content-row {
  margin: 0;
}

.module-item {
  padding: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  margin-bottom: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background-color: var(--el-fill-color-light);
}

.module-item:last-child {
  margin-bottom: 0;
}

.module-title {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.module-desc {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.5;
}

.quick-card {
  border-radius: 8px;
}

.quick-link {
  height: 120px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  margin-bottom: 12px;
  transition: all 0.2s ease;
  background-color: var(--el-bg-color);
}

.quick-link:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transform: translateY(-2px);
}

.quick-icon {
  font-size: 24px;
  color: var(--el-color-primary);
  margin-bottom: 4px;
}

.quick-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.quick-desc {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
