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
  loading: false,
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
  set: (value) => emit('update:modelValue', value),
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
  { deep: true },
)

// 暴露表单实例方法
defineExpose({
  validate: () => formRef.value?.validate(),
  resetFields: () => formRef.value?.resetFields(),
  clearValidate: () => formRef.value?.clearValidate(),
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
    }
  }
}
</style>
