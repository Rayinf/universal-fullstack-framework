<template>
  <BaseDialog
    v-model="visible"
    :title="title"
    :width="width"
    :loading="loading"
    :confirm-disabled="!isFormValid"
    @confirm="handleSubmit"
    @cancel="handleCancel"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="130px"
      label-position="right"
      class="form-dialog-content"
    >
      <slot :form-data="formData" />
    </el-form>
  </BaseDialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import BaseDialog from './BaseDialog.vue'

interface Props {
  modelValue: boolean
  title: string
  formData: Record<string, any>
  rules?: FormRules
  width?: string | number
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: '600px',
  loading: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  submit: [formData: Record<string, any>]
  cancel: []
}>()

const formRef = ref<FormInstance>()
const isFormValid = ref(true)

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    emit('submit', props.formData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handleCancel = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  emit('cancel')
}

// 监听表单数据变化，实时验证
watch(
  () => props.formData,
  async () => {
    if (formRef.value && props.rules) {
      try {
        await formRef.value.validate()
        isFormValid.value = true
      } catch {
        isFormValid.value = false
      }
    }
  },
  { deep: true }
)

// 暴露表单实例方法
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate()
})
</script>

<style scoped lang="scss">
.form-dialog-content {
  :deep(.el-form-item) {
    margin-bottom: 20px;
    
    .el-form-item__label {
      color: var(--el-text-color-primary);
      font-weight: 500;
      line-height: 32px;
      padding-right: 12px;
    }
    
    .el-form-item__content {
      position: relative;
      
      .el-input,
      .el-select,
      .el-textarea,
      .el-date-picker,
      .el-input-number {
        width: 100%;
      }
      
      .el-input__wrapper {
        border-radius: 6px;
        border: 1px solid var(--el-border-color-lighter);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        
        &:hover {
          border-color: var(--el-color-primary);
        }
        
        &.is-focus {
          border-color: var(--el-color-primary);
          box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
        }
        
        &.is-error {
          border-color: var(--el-color-danger);
          
          &.is-focus {
            box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.1);
          }
        }
      }
      
      .el-select .el-input__wrapper {
        cursor: pointer;
      }
      
      .el-input-number .el-input__wrapper {
        padding-right: 32px;
      }
      
      // 修复输入框后缀按钮样式
      .el-input__suffix {
        .el-button {
          padding: 0 8px;
          height: 24px;
          font-size: 12px;
          border: none;
          background: transparent;
          color: var(--el-color-primary);
          
          &:hover {
            background: rgba(24, 144, 255, 0.1);
          }
        }
      }
    }
    
    .el-form-item__error {
      color: var(--el-color-danger);
      font-size: 12px;
      line-height: 1.4;
      margin-top: 4px;
      position: absolute;
      left: 0;
      right: 0;
    }
  }
  
  // 行布局优化
  :deep(.el-row) {
    margin-left: -10px;
    margin-right: -10px;
    
    .el-col {
      padding-left: 10px;
      padding-right: 10px;
    }
  }
  
  :deep(.el-textarea__inner) {
    border-radius: 6px;
    border: 1px solid var(--el-border-color-lighter);
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    resize: vertical;
    min-height: 80px;
    
    &:hover {
      border-color: var(--el-color-primary);
    }
    
    &:focus {
      border-color: var(--el-color-primary);
      box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
      outline: none;
    }
    
    &.is-error {
      border-color: var(--el-color-danger);
      
      &:focus {
        box-shadow: 0 0 0 2px rgba(255, 77, 79, 0.1);
      }
    }
  }
  
  // 开关组件样式
  :deep(.el-switch) {
    .el-switch__core {
      border-radius: 11px;
      
      &.is-checked {
        background-color: var(--el-color-primary);
      }
    }
  }
  
  // 日期选择器样式
  :deep(.el-date-editor) {
    .el-input__wrapper {
      .el-input__inner {
        cursor: pointer;
      }
    }
  }
}
</style>
