<script setup lang="ts">
import { ref, watch, onMounted, computed, nextTick } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { SubTableConfig, SubTableRowData } from '@/types/formConfig'

interface Props {
  config: SubTableConfig
  modelValue: SubTableRowData[] | undefined
  disabled?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const tableData = ref<SubTableRowData[]>([])
const isInternalUpdate = ref(false) // 标志位：是否是内部更新
const isProgrammaticChange = ref(false) // 标志位：是否是程序化修改（添加/删除行）

// 验证并修复列配置
const validColumns = computed(() => {
  if (!props.config?.columns) return []

  return props.config.columns.map((col, index) => ({
    ...col,
    key: col.key || `col_${index}`, // 确保有 key
    label: col.label || `列${index + 1}`, // 确保有 label
    widgetType: col.widgetType || 'input', // 确保有 widgetType
    props: col.props || {},
    options: col.options || [],
  }))
})

// Initialize data
const initData = () => {
  if (Array.isArray(props.modelValue)) {
    tableData.value = [...props.modelValue]
  } else {
    tableData.value = []
  }
}

// 只在 modelValue 引用变化时更新，避免深度监听导致的循环
watch(
  () => props.modelValue,
  (newVal) => {
    // 先检查数据是否真的变化了
    const dataChanged = JSON.stringify(newVal) !== JSON.stringify(tableData.value)

    if (dataChanged) {
      // 数据变化了，需要更新
      // 即使是内部更新触发的，如果父组件修改了数据，也要接受
      if (isInternalUpdate.value) {
        isInternalUpdate.value = false
      }
      initData()
    } else {
      // 数据没变化，如果是内部更新，只需重置标志
      if (isInternalUpdate.value) {
        isInternalUpdate.value = false
      }
    }
  },
  { deep: true },
)

onMounted(() => {
  initData()
})

// 手动触发更新，而不是通过 watch
const emitUpdate = () => {
  isInternalUpdate.value = true
  emit('update:modelValue', [...tableData.value])
  // 注意：不在这里重置标志，让 watch 在接收到回传时重置
}

const addRow = () => {
  isProgrammaticChange.value = true // 标记为程序化修改
  const newRow: SubTableRowData = {}
  validColumns.value.forEach((col) => {
    // Set default values based on type
    if (col.widgetType === 'checkbox') {
      newRow[col.key] = []
    } else if (col.widgetType === 'number') {
      newRow[col.key] = undefined
    } else if (col.widgetType === 'radio') {
      // Radio 类型使用 undefined 或第一个选项的值
      newRow[col.key] = col.options?.[0]?.value ?? undefined
    } else {
      newRow[col.key] = ''
    }
  })
  tableData.value.push(newRow)
  emitUpdate()
  // 下一个 tick 后重置标志
  setTimeout(() => {
    isProgrammaticChange.value = false
  }, 0)
}

const deleteRow = (index: number) => {
  isProgrammaticChange.value = true // 标记为程序化修改
  tableData.value.splice(index, 1)
  emitUpdate()
  // 下一个 tick 后重置标志
  setTimeout(() => {
    isProgrammaticChange.value = false
  }, 0)
}

// 监听表格数据变化（用于单元格编辑）
let updateTimer: ReturnType<typeof setTimeout> | null = null
watch(
  tableData,
  () => {
    // 如果是程序化修改（添加/删除行），跳过
    if (isProgrammaticChange.value) {
      return
    }

    // 防抖处理
    if (updateTimer) {
      clearTimeout(updateTimer)
    }
    updateTimer = setTimeout(() => {
      emitUpdate()
      updateTimer = null
    }, 300)
  },
  { deep: true },
)

const getColumnComponent = (widgetType: string) => {
  const map: Record<string, any> = {
    input: 'el-input',
    number: 'el-input-number',
    textarea: 'el-input',
    select: 'el-select',
    radio: 'el-radio-group',
    checkbox: 'el-checkbox-group',
    date: 'el-date-picker',
  }
  return map[widgetType] || 'el-input'
}
</script>

<template>
  <div class="sub-table-renderer">
    <el-table :data="tableData" border stripe style="width: 100%" class="sub-table">
      <!-- Index Column -->
      <el-table-column
        v-if="config.showIndex !== false"
        type="index"
        label="序号"
        width="60"
        align="center"
      />

      <!-- Dynamic Columns -->
      <el-table-column
        v-for="col in validColumns"
        :key="col.key"
        :label="col.label"
        :min-width="col.width || 120"
      >
        <template #header>
          <span>
            <span v-if="col.required" class="required-mark">*</span>
            {{ col.label }}
          </span>
        </template>
        <template #default="{ row }">
          <component
            :is="getColumnComponent(col.widgetType)"
            v-model="row[col.key]"
            :disabled="disabled"
            :placeholder="col.props?.placeholder"
            size="small"
            style="width: 100%"
            :controls-position="col.widgetType === 'number' ? 'right' : undefined"
            :precision="col.props?.precision"
          >
            <!-- Select/Radio/Checkbox Options -->
            <template
              v-if="col.options && ['select', 'radio', 'checkbox'].includes(col.widgetType)"
            >
              <template v-if="col.widgetType === 'select'">
                <el-option
                  v-for="opt in col.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </template>
              <template v-else-if="col.widgetType === 'radio'">
                <el-radio
                  v-for="opt in col.options"
                  :key="opt.value"
                  :value="opt.value"
                  :label="opt.value"
                >
                  {{ opt.label }}
                </el-radio>
              </template>
              <template v-else-if="col.widgetType === 'checkbox'">
                <el-checkbox v-for="opt in col.options" :key="opt.value" :label="opt.value">
                  {{ opt.label }}
                </el-checkbox>
              </template>
            </template>
          </component>
        </template>
      </el-table-column>

      <!-- Operation Column -->
      <el-table-column
        v-if="config.allowDelete !== false && !disabled"
        label="操作"
        width="70"
        align="center"
        fixed="right"
      >
        <template #default="{ $index }">
          <el-button type="danger" :icon="Delete" size="small" circle @click="deleteRow($index)" />
        </template>
      </el-table-column>
    </el-table>

    <!-- Empty State / Add Button -->
    <div class="table-footer" v-if="config.allowAdd !== false && !disabled">
      <el-button
        type="primary"
        plain
        :icon="Plus"
        size="small"
        style="width: 100%; margin-top: 5px; border-style: dashed"
        @click="addRow"
      >
        添加明细行
      </el-button>
    </div>
  </div>
</template>

<style scoped lang="scss">
.sub-table-renderer {
  width: 100%;
  margin: 0;
  padding: 0;
}

.required-mark {
  color: #f56c6c;
  margin-right: 4px;
}

// 覆盖el-table样式，使其与主表格保持一致
:deep(.sub-table) {
  // 确保表格占满宽度，无任何边距
  width: 100% !important;
  margin: 0 !important;

  // 统一边框颜色为#333，与主表格一致
  &.el-table--border {
    border-color: #333;

    &::after,
    &::before {
      background-color: #333;
    }
  }

  // 完全移除表格外层边框，避免与父单元格边框重叠
  border: none !important;

  // 表头样式
  .el-table__header-wrapper {
    th {
      background-color: #f5f7fa;
      color: #303133;
      font-weight: 500;
      border-color: #333;
      padding: 8px 0;

      // 第一个表头单元格移除左边框
      &:first-child {
        border-left: none;
      }

      // 最后一个表头单元格移除右边框
      &:last-child {
        border-right: none;
      }

      // 所有表头单元格移除顶部边框
      border-top: none;
    }
  }

  // 单元格样式
  td,
  th {
    border-color: #333 !important;
    padding: 8px;
  }

  // 移除第一列的左边框
  td:first-child,
  th:first-child {
    border-left: none !important;
  }

  // 移除最后一列的右边框
  td:last-child,
  th:last-child {
    border-right: none !important;
  }

  // 第一行数据单元格移除顶部边框（紧贴表头）
  tbody tr:first-child td {
    border-top: none !important;
  }

  // 单元格内部padding
  .cell {
    padding: 0 8px;
    line-height: 28px;
  }

  // 斑马纹样式
  .el-table__row--striped {
    background-color: #fafafa;
  }
}

// 为可编辑的输入框添加浅色背景，与主表单保持一致
:deep(.el-input:not(.is-disabled) .el-input__wrapper),
:deep(.el-textarea:not(.is-disabled) .el-textarea__inner),
:deep(.el-select:not(.is-disabled) .el-input__wrapper) {
  background-color: #f2f8fe;
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s;
}

:deep(.el-input:not(.is-disabled) .el-input__wrapper.is-focus),
:deep(.el-textarea:not(.is-disabled) .el-textarea__inner:focus),
:deep(.el-select:not(.is-disabled) .el-input__wrapper.is-focus) {
  background-color: #fff;
  box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-input-number:not(.is-disabled) .el-input__wrapper) {
  background-color: #f2f8fe;
}

/* --- 只读模式显示优化 (针对 disabled 状态) --- */
:deep(.el-input.is-disabled .el-input__wrapper),
:deep(.el-textarea.is-disabled .el-textarea__inner),
:deep(.el-select.is-disabled .el-input__wrapper),
:deep(.el-input-number.is-disabled .el-input__wrapper),
:deep(.el-date-editor.is-disabled.el-input__wrapper) {
  background-color: #fff !important;
  box-shadow: 0 0 0 1px #dcdfe6 inset !important;
  cursor: default !important;
  .el-input__suffix {
    display: none;
  }
}

:deep(.el-input.is-disabled .el-input__inner),
:deep(.el-textarea.is-disabled .el-textarea__inner),
:deep(.el-select.is-disabled .el-input__inner),
:deep(.el-input-number.is-disabled .el-input__inner),
:deep(.el-checkbox.is-disabled .el-checkbox__label),
:deep(.el-radio.is-disabled .el-radio__label),
:deep(.el-date-editor.is-disabled .el-input__inner) {
  color: #303133 !important;
  -webkit-text-fill-color: #303133 !important;
  cursor: default !important;
}

:deep(.el-checkbox.is-disabled.is-checked .el-checkbox__inner) {
  background-color: #409eff !important;
  border-color: #409eff !important;
  &::after {
    border-color: #fff !important;
  }
}

:deep(.el-radio.is-disabled.is-checked .el-radio__inner) {
  background-color: #409eff !important;
  border-color: #409eff !important;
  &::after {
    background-color: #fff !important;
    transform: translate(-50%, -50%) scale(1);
  }
}
</style>
