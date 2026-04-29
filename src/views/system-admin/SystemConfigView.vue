<template>
  <div class="system-config-view page-view">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>系统基础配置</h2>
          <div class="page-description">配置系统基础信息，包括公司名称、系统名称和版本号</div>
        </div>
      </div>
    </div>

    <!-- 配置卡片 -->
    <div class="content-card">
      <div class="config-panel" v-loading="systemConfigStore.loading">
        <el-form ref="formRef" :model="formData" :rules="formRules" label-width="120px" class="config-form">
          <el-form-item label="公司名称" prop="companyName">
            <el-input v-model="formData.companyName" placeholder="请输入公司名称" maxlength="100" show-word-limit clearable />
            <div class="form-tip">公司名称将显示在系统首页</div>
          </el-form-item>

          <el-form-item label="系统名称" prop="systemName">
            <el-input v-model="formData.systemName" placeholder="请输入系统名称" maxlength="50" show-word-limit clearable />
            <div class="form-tip">系统名称将显示在顶部导航栏</div>
          </el-form-item>

          <el-form-item label="版本号" prop="version">
            <el-input v-model="formData.version" placeholder="请输入版本号，如 1.0.0" maxlength="20" show-word-limit
              clearable />
            <div class="form-tip">版本号将显示在系统首页底部</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSave" :loading="isSaving">
              <el-icon>
                <Check />
              </el-icon>
              保存配置
            </el-button>
            <el-button @click="handleReset">
              <el-icon>
                <RefreshLeft />
              </el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>

        <!-- 预览区域 -->
        <div class="preview-section">
          <h3>预览效果</h3>
          <div class="preview-card">
            <div class="preview-header">
              <div class="preview-logo">
                <img src="@/assets/单LOGO.png" alt="LOGO" class="logo-img" />
                <span class="system-name">{{ formData.systemName || 'GK-MES系统' }}</span>
              </div>
            </div>
            <div class="preview-body">
              <div class="company-info">
                <span class="company-label">公司：</span>
                <span class="company-name">{{ formData.companyName || '未设置' }}</span>
              </div>
              <div class="version-info">
                <span class="version-label">版本：</span>
                <span class="version-number">{{ formData.version || '1.0.0' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { Check, RefreshLeft } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { useSystemConfigStore } from '@/stores/system/systemConfig'

const systemConfigStore = useSystemConfigStore()

const formRef = ref<FormInstance>()
const isSaving = ref(false)

// 表单数据
const formData = reactive({
  companyName: '',
  systemName: '',
  version: '',
})

// 表单验证规则
const formRules: FormRules = {
  companyName: [{ max: 100, message: '公司名称不能超过100个字符', trigger: 'blur' }],
  systemName: [
    { required: true, message: '请输入系统名称', trigger: 'blur' },
    { max: 50, message: '系统名称不能超过50个字符', trigger: 'blur' },
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^[\d.]+$/, message: '版本号只能包含数字和点号', trigger: 'blur' },
    { max: 20, message: '版本号不能超过20个字符', trigger: 'blur' },
  ],
}

// 初始化表单数据
const initFormData = () => {
  formData.companyName = systemConfigStore.configData.companyName
  formData.systemName = systemConfigStore.configData.systemName
  formData.version = systemConfigStore.configData.version
}

// 监听 store 数据变化
watch(
  () => systemConfigStore.configData,
  () => {
    initFormData()
  },
  { deep: true },
)

// 保存配置
const handleSave = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      isSaving.value = true
      try {
        await systemConfigStore.updateAllConfigs({
          companyName: formData.companyName,
          systemName: formData.systemName,
          version: formData.version,
        })
      } finally {
        isSaving.value = false
      }
    }
  })
}

// 重置表单
const handleReset = () => {
  initFormData()
}

onMounted(async () => {
  // 确保数据已加载
  if (!systemConfigStore.hasLoaded) {
    await systemConfigStore.fetchSystemConfig()
  }
  initFormData()
})
</script>

<style scoped>
@import '@sys/styles/common.css';

/* 系统配置特定样式 */

.config-panel {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 32px;
  height: 100%;
  padding: 24px;
}

.config-form {
  max-width: 500px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.preview-section {
  border-left: 1px solid #ebeef5;
  padding-left: 32px;
}

.preview-section h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.preview-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #f8f9fa;
}

.preview-header {
  background: linear-gradient(135deg, #409eff, #57aeff);
  padding: 16px;
}

.preview-logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-img {
  width: 32px;
  height: 32px;
  object-fit: contain;
}

.system-name {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.preview-body {
  padding: 16px;
}

.company-info,
.version-info {
  margin-bottom: 8px;
  font-size: 14px;
}

.company-label,
.version-label {
  color: #909399;
  font-weight: 500;
}

.company-name,
.version-number {
  color: #303133;
  margin-left: 4px;
}

@media (max-width: 1024px) {
  .config-panel {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .preview-section {
    border-left: none;
    border-top: 1px solid #ebeef5;
    padding-left: 0;
    padding-top: 24px;
  }
}
</style>
