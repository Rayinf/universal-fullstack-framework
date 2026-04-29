<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { FieldWidgetConfig, WidgetType } from '@/types/formConfig'
import SubTableConfigEditor from './SubTableConfigEditor.vue'

interface Props {
  modelValue: string | undefined
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const getDefaultConfig = (): FieldWidgetConfig => ({
  widgetType: 'input',
  props: {
    placeholder: '',
    clearable: true,
  },
  validation: {
    required: false,
  },
  options: [], // 明确初始化 options 为空数组
})

const config = ref<FieldWidgetConfig>(getDefaultConfig())

// 初始化配置
if (props.modelValue) {
  try {
    const parsed = JSON.parse(props.modelValue)
    config.value = { ...getDefaultConfig(), ...parsed }

    // 特殊处理 props 和 validation 的深度合并
    if (parsed.props) {
      config.value.props = { ...config.value.props, ...parsed.props }
    }
    if (parsed.validation) {
      config.value.validation = { ...config.value.validation, ...parsed.validation }
    }
  } catch (e) {
    console.error('解析字段配置失败:', e)
  }
}

// 监听配置变化并回传
watch(
  config,
  (newVal) => {
    emit('update:modelValue', JSON.stringify(newVal))
  },
  { deep: true },
)

watch(
  () => props.modelValue,
  (val) => {
    // 即使 val 为空，也应该重置为默认值
    const baseConfig = getDefaultConfig()

    if (val) {
      try {
        const parsed = JSON.parse(val)
        // 基于默认配置进行合并，而不是基于上一次的 config.value
        const newConfig = {
          ...baseConfig,
          ...parsed,
        }

        // 深度合并 props
        if (parsed.props) {
          newConfig.props = { ...baseConfig.props, ...parsed.props }
        }

        // 深度合并 validation
        if (parsed.validation) {
          newConfig.validation = { ...baseConfig.validation, ...parsed.validation }
        }

        config.value = newConfig
      } catch (e) {
        console.error('解析字段配置失败:', e)
        config.value = baseConfig // 解析失败时重置为默认
      }
    } else {
      config.value = baseConfig // 没值时重置为默认
    }
  },
)

const widgetTypes = [
  { label: '单行文本', value: 'input' },
  { label: '数字输入', value: 'number' },
  { label: '多行文本', value: 'textarea' },
  { label: '下拉选择', value: 'select' },
  { label: '单选框', value: 'radio' },
  { label: '复选框', value: 'checkbox' },
  { label: '日期选择', value: 'date' },
  { label: '人员选择', value: 'userSelect' },
  { label: '部门选择', value: 'deptSelect' },
  { label: '只读文本', value: 'text' },
  { label: '子表单', value: 'subTable' },
]

const addOption = () => {
  if (!config.value.options) config.value.options = []
  const index = config.value.options.length
  // 自动生成有意义的 value，避免空值导致的选择问题
  config.value.options.push({
    label: `新选项${index + 1}`,
    value: `option_${index + 1}`,
  })
}

const removeOption = (index: number) => {
  config.value.options?.splice(index, 1)
}

const showOptions = () => ['select', 'radio', 'checkbox'].includes(config.value.widgetType)
</script>

<template>
  <div class="field-config-panel">
    <el-divider content-position="left">控件配置</el-divider>

    <el-form-item label="控件类型">
      <el-select v-model="config.widgetType" placeholder="请选择控件类型" style="width: 100%">
        <el-option
          v-for="item in widgetTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
    </el-form-item>

    <el-form-item label="占位提示">
      <el-input v-model="config.props!.placeholder" placeholder="请输入占位提示文字" />
    </el-form-item>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-form-item label="是否必填">
          <el-switch v-model="config.validation!.required" />
        </el-form-item>
      </el-col>
      <el-col :span="12" v-if="config.widgetType === 'number'">
        <el-form-item label="数字精度">
          <el-input-number v-model="config.props!.precision" :min="0" :max="5" />
        </el-form-item>
      </el-col>
    </el-row>

    <!-- 选项编辑器 -->
    <template v-if="showOptions()">
      <el-form-item label="选项配置">
        <el-alert
          type="warning"
          :closable="false"
          style="margin-bottom: 10px; line-height: 1.4"
          show-icon
        >
          <template #title> 选项值需唯一且非空 </template>
        </el-alert>

        <div class="options-container">
          <div v-for="(opt, index) in config.options" :key="index" class="option-block">
            <div class="option-inputs">
              <el-input
                v-model="opt.label"
                placeholder="显示名称 (Label)"
                size="small"
                style="width: 100%"
              />
              <el-input
                v-model="opt.value"
                placeholder="绑定值 (Value)"
                size="small"
                :class="{ 'error-input': !opt.value || opt.value === '' }"
                style="width: 100%"
              />
            </div>
            <el-button
              type="danger"
              :icon="Delete"
              circle
              size="small"
              class="delete-btn"
              @click="removeOption(index)"
            />
          </div>
        </div>

        <el-button type="primary" :icon="Plus" link @click="addOption" style="margin-top: 5px">
          添加选项
        </el-button>
      </el-form-item>
    </template>

    <template v-if="config.widgetType === 'textarea'">
      <el-form-item label="默认行数">
        <el-input-number v-model="config.props!.rows" :min="1" :max="10" />
      </el-form-item>
    </template>

    <!-- 子表单列配置 -->
    <template v-if="config.widgetType === 'subTable'">
      <SubTableConfigEditor v-model="config as any" />
    </template>
  </div>
</template>

<style scoped lang="scss">
.field-config-panel {
  background-color: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-block {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: #fff;
  padding: 8px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.option-inputs {
  flex: 1; /* 自动占据剩余空间 */
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 120px; /* 保证最小宽度，防止塌陷 */
}

.delete-btn {
  flex-shrink: 0;
  margin-left: 5px; /* 与输入框保持距离 */
}

.error-input {
  :deep(.el-input__wrapper) {
    box-shadow: 0 0 0 1px #f56c6c inset !important;
  }
}
</style>
