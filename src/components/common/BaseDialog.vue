<template>
  <el-dialog
    v-model="visible"
    :title="title"
    :width="width"
    :top="top"
    :modal="modal"
    :close-on-click-modal="closeOnClickModal"
    :close-on-press-escape="closeOnPressEscape"
    :show-close="showClose"
    :before-close="handleBeforeClose"
    :destroy-on-close="destroyOnClose"
    class="base-dialog"
    align-center
  >
    <div class="dialog-content">
      <slot />
    </div>

    <template #footer v-if="showFooter">
      <div class="dialog-footer">
        <slot name="footer">
          <el-button @click="handleCancel" :disabled="loading">
            {{ cancelText }}
          </el-button>
          <el-button
            type="primary"
            @click="handleConfirm"
            :loading="loading"
            :disabled="confirmDisabled"
          >
            {{ confirmText }}
          </el-button>
        </slot>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title: string
  width?: string | number
  top?: string
  modal?: boolean
  closeOnClickModal?: boolean
  closeOnPressEscape?: boolean
  showClose?: boolean
  destroyOnClose?: boolean
  showFooter?: boolean
  confirmText?: string
  cancelText?: string
  loading?: boolean
  confirmDisabled?: boolean
  beforeClose?: (done: () => void) => void
}

const props = withDefaults(defineProps<Props>(), {
  width: '600px',
  top: '15vh',
  modal: true,
  closeOnClickModal: false,
  closeOnPressEscape: true,
  showClose: true,
  destroyOnClose: false,
  showFooter: true,
  confirmText: '确定',
  cancelText: '取消',
  loading: false,
  confirmDisabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: []
  cancel: []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const handleConfirm = () => {
  emit('confirm')
}

const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

const handleBeforeClose = (done: () => void) => {
  if (props.beforeClose) {
    props.beforeClose(done)
  } else {
    done()
  }
}
</script>

<style lang="scss" scoped>
.base-dialog {
  :deep(.el-dialog) {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
  }

  :deep(.el-dialog__header) {
    padding: 20px 24px 16px;
    border-bottom: 1px solid var(--el-border-color-lighter);
    background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;

    .el-dialog__title {
      font-size: 18px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      line-height: 1.5;
      margin: 0;
      flex: 1;
    }

    .el-dialog__headerbtn {
      position: relative;
      top: auto;
      right: auto;
      width: 32px;
      height: 32px;
      margin: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      transition: all 0.3s;

      &:hover {
        background: rgba(0, 0, 0, 0.05);
      }
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
    max-height: 60vh;
    overflow-y: auto;

    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 3px;
    }

    &::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.05);
    }
  }

  :deep(.el-dialog__footer) {
    padding: 16px 24px 20px;
    border-top: 1px solid var(--el-border-color-lighter);
    background: #fafafa;
  }
}

.dialog-content {
  min-height: 60px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;

  .el-button {
    flex: 0 0 auto;
    min-width: 80px;
    max-width: 120px;
    height: 36px;
    border-radius: 6px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 8px 16px;
  }

  .el-button + .el-button {
    margin-left: 0;
  }
}
</style>
