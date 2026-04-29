<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import type {
  FormLayoutConfig,
  TableCell,
  FieldWidgetConfig,
  SubTableConfig,
} from '@/types/formConfig'
import type { ProcessLibraryItemParam } from '@/types/technology'
import OrgTreeSelector from '@/components/common/OrgTreeSelector.vue'
import SubTableRenderer from './SubTableRenderer.vue'

interface Props {
  layoutConfig: string | FormLayoutConfig | undefined
  fields: ProcessLibraryItemParam[]
  modelValue: Record<string, any>
  disabled?: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

// 使用本地 ref 而不是 computed，避免循环更新
const formData = ref<Record<string, any>>({})
const isInternalUpdate = ref(false)

// 监听 props.modelValue 变化
watch(
  () => props.modelValue,
  (newVal) => {
    // 先检查数据是否真的变化了
    const dataChanged = JSON.stringify(newVal) !== JSON.stringify(formData.value)

    if (dataChanged) {
      // 数据变化了，需要更新
      // 即使是内部更新触发的，如果父组件修改了数据，也要接受
      if (isInternalUpdate.value) {
        isInternalUpdate.value = false
      }
      formData.value = { ...newVal }
    } else {
      // 数据没变化，如果是内部更新，只需重置标志
      if (isInternalUpdate.value) {
        isInternalUpdate.value = false
      }
    }
  },
  { deep: true, immediate: true },
)

// 监听 formData 变化，向父组件 emit
watch(
  formData,
  (newVal) => {
    // 只有当数据真正变化时才 emit，避免循环
    if (JSON.stringify(newVal) !== JSON.stringify(props.modelValue)) {
      isInternalUpdate.value = true
      emit('update:modelValue', { ...newVal })
    }
  },
  { deep: true },
)

const layout = computed<FormLayoutConfig | null>(() => {
  if (!props.layoutConfig) return null

  // 如果已经是对象，直接返回
  if (typeof props.layoutConfig === 'object') {
    return props.layoutConfig as FormLayoutConfig
  }

  // 如果是字符串，尝试解析
  try {
    return JSON.parse(props.layoutConfig)
  } catch (e) {
    console.error('DynamicFormRenderer: 解析布局配置失败', e)
    return null
  }
})

const fieldConfigMap = computed(() => {
  const map = new Map<string, FieldWidgetConfig>()
  props.fields.forEach((field) => {
    if (field.jsonConfig) {
      try {
        // 始终深拷贝配置，避免修改原始 props 导致循环更新
        const config =
          typeof field.jsonConfig === 'object'
            ? JSON.parse(JSON.stringify(field.jsonConfig))
            : JSON.parse(field.jsonConfig)

        // 修复选项 value 为空的问题
        if (config?.options) {
          config.options = config.options.map((opt: any, index: number) => {
            // 如果 value 为空或 undefined，使用 label 作为 value
            if (opt.value === '' || opt.value === undefined || opt.value === null) {
              console.warn(
                `⚠️ 字段 ${field.id} 的选项 "${opt.label}" 没有配置 value，将使用 label 作为 value`,
              )
              return { ...opt, value: opt.label || `option_${index}` }
            }
            return opt
          })
        }

        map.set(String(field.id), config)
      } catch (e) {
        console.error(`解析字段 ${field.paramName} 配置失败`, e)
      }
    }
  })
  return map
})

const getFieldConfig = (fieldId: string): FieldWidgetConfig | undefined => {
  if (!fieldId) return undefined
  return fieldConfigMap.value.get(String(fieldId))
}

const getFieldComponent = (type: string | undefined) => {
  const map: Record<string, any> = {
    input: 'el-input',
    number: 'el-input-number',
    textarea: 'el-input',
    select: 'el-select',
    radio: 'el-radio-group',
    checkbox: 'el-checkbox-group',
    date: 'el-date-picker',
    userSelect: 'el-select',
    deptSelect: OrgTreeSelector,
    text: 'span',
    subTable: SubTableRenderer,
  }
  return map[type || 'input'] || 'el-input'
}

const getFieldProps = (config: FieldWidgetConfig | null | undefined) => {
  if (!config) return {}
  const base: Record<string, any> = {
    placeholder: config.props?.placeholder || '请输入',
    disabled: props.disabled,
    clearable: config.props?.clearable !== false,
    style: { width: '100%' },
  }

  if (config.widgetType === 'textarea') {
    base.type = 'textarea'
    base.rows = config.props?.rows || 2
  } else if (config.widgetType === 'number') {
    base.precision = config.props?.precision || 0
    base.controlsPosition = 'right'
  } else if (config.widgetType === 'date') {
    base.type = 'date'
    base.valueFormat = 'YYYY-MM-DD'
  }

  return base
}
</script>

<template>
  <div class="dynamic-form-container" v-if="layout && layout.rows">
    <el-form :model="formData" label-width="0">
      <table class="render-table" :class="{ 'has-border': layout.border }">
        <tbody>
          <tr v-for="(row, rIndex) in layout.rows" :key="rIndex">
            <td
              v-for="cell in row.cells"
              :key="cell.id"
              :rowspan="cell.rowspan || 1"
              :colspan="cell.colspan || 1"
              :class="{
                'no-padding':
                  cell.content.type === 'field' &&
                  getFieldConfig(cell.content.value)?.widgetType === 'subTable',
              }"
              :style="{
                textAlign: cell.style?.align || 'left',
                backgroundColor: cell.style?.backgroundColor,
                fontWeight: cell.style?.fontWeight,
                width: cell.style?.width,
              }"
            >
              <div class="cell-inner">
                <!-- 静态文本内容 -->
                <template v-if="cell.content.type === 'static'">
                  <div class="static-text">{{ cell.content.value }}</div>
                </template>

                <!-- 绑定字段输入项 -->
                <template v-else-if="cell.content.value">
                  <el-form-item :prop="cell.content.value" style="margin: 0">
                    <template v-if="getFieldConfig(cell.content.value)?.widgetType === 'subTable'">
                      <SubTableRenderer
                        :config="getFieldConfig(cell.content.value) as SubTableConfig"
                        v-model="formData[cell.content.value]"
                        :disabled="disabled"
                      />
                    </template>
                    <component
                      v-else
                      :is="getFieldComponent(getFieldConfig(cell.content.value)?.widgetType)"
                      v-model="formData[cell.content.value]"
                      v-bind="getFieldProps(getFieldConfig(cell.content.value))"
                    >
                      <!-- 处理选项 -->
                      <template v-if="getFieldConfig(cell.content.value)?.options">
                        <!-- Select Options -->
                        <template
                          v-if="getFieldConfig(cell.content.value)?.widgetType === 'select'"
                        >
                          <el-option
                            v-for="opt in getFieldConfig(cell.content.value)!.options"
                            :key="opt.value"
                            :label="opt.label"
                            :value="opt.value"
                          />
                        </template>
                        <!-- Radio Options -->
                        <template v-if="getFieldConfig(cell.content.value)?.widgetType === 'radio'">
                          <el-radio
                            v-for="opt in getFieldConfig(cell.content.value)!.options"
                            :key="opt.value"
                            :value="opt.value"
                            :label="opt.value"
                          >
                            {{ opt.label }}
                          </el-radio>
                        </template>
                        <!-- Checkbox Options -->
                        <template
                          v-if="getFieldConfig(cell.content.value)?.widgetType === 'checkbox'"
                        >
                          <el-checkbox
                            v-for="opt in getFieldConfig(cell.content.value)!.options"
                            :key="opt.value"
                            :label="opt.value"
                          >
                            {{ opt.label }}
                          </el-checkbox>
                        </template>
                      </template>
                    </component>
                  </el-form-item>
                </template>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </el-form>
  </div>
  <div v-else class="empty-placeholder">
    <el-empty description="表单布局配置无效或为空" :image-size="100" />
  </div>
</template>

<style scoped lang="scss">
.dynamic-form-container {
  width: 100%;
  background-color: #fff;
}

.render-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
  background-color: #fff;

  &.has-border td {
    border: 1px solid #333;
  }

  td {
    padding: 10px;
    min-height: 44px;
    vertical-align: middle;

    &.no-padding {
      padding: 0;

      // 包含子表单的单元格，让子表单的边框作为单元格边框
      // 移除单元格自身的内边框，避免双重边框
      border: 1px solid #333 !important;

      // 确保子表单完全填充单元格
      > .cell-inner {
        width: 100%;
        height: 100%;
        display: block;
      }
    }
  }
}

.static-text {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  word-break: break-all;
  white-space: pre-wrap;
  line-height: 1.4;
}

.cell-inner {
  width: 100%;
  display: block;
}

.empty-placeholder {
  padding: 40px;
  text-align: center;
}

:deep(.el-form-item__content) {
  margin-left: 0 !important;
}

/* --- 填写项体验优化 --- */

/* 为可编辑的输入框添加浅色背景，突出显示“填写项” */
:deep(.el-input:not(.is-disabled) .el-input__wrapper),
:deep(.el-textarea:not(.is-disabled) .el-textarea__inner),
:deep(.el-select:not(.is-disabled) .el-input__wrapper) {
  background-color: #f2f8fe; /* 极浅的蓝色 */
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  transition: all 0.3s;
}

/* 聚焦时高亮 */
:deep(.el-input:not(.is-disabled) .el-input__wrapper.is-focus),
:deep(.el-textarea:not(.is-disabled) .el-textarea__inner:focus),
:deep(.el-select:not(.is-disabled) .el-input__wrapper.is-focus) {
  background-color: #fff;
  box-shadow: 0 0 0 1px #409eff inset;
}

/* 针对 InputNumber 的特殊处理 */
:deep(.el-input-number:not(.is-disabled) .el-input__wrapper) {
  background-color: #f2f8fe;
}

/* --- 只读模式显示优化 (针对 disabled 状态) --- */

/* 1. 基础输入组件背景与边框 */
:deep(.el-input.is-disabled .el-input__wrapper),
:deep(.el-textarea.is-disabled .el-textarea__inner),
:deep(.el-select.is-disabled .el-input__wrapper),
:deep(.el-input-number.is-disabled .el-input__wrapper),
:deep(.el-date-editor.is-disabled.el-input__wrapper) {
  background-color: #fff !important;
  box-shadow: 0 0 0 1px #dcdfe6 inset !important;
  cursor: default !important;

  .el-input__suffix {
    display: none; /* 隐藏禁用状态下的下拉/清除图标，减少干扰 */
  }
}

/* 2. 文字颜色覆盖 (解决变灰看不清的问题) */
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

/* 3. 单选框/多选框图标状态 */
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

/* 选项类控件增加一点内边距和背景，使其成块 */
:deep(.el-radio-group),
:deep(.el-checkbox-group) {
  padding: 4px 8px;
  border-radius: 4px;
  // background-color: #fcfcfc;
}
</style>
