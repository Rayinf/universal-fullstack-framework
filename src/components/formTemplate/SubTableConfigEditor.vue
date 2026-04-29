<script setup lang="ts">
import { ref, watch } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { SubTableConfig, SubTableColumn, WidgetType } from '@/types/formConfig'

interface Props {
  modelValue: SubTableConfig
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue'])

const ensureValidConfig = (val: SubTableConfig): SubTableConfig => {
  if (!val) return { widgetType: 'subTable', columns: [] } as SubTableConfig

  // Clone to avoid mutating prop and ensure we have a fresh object
  const c = JSON.parse(JSON.stringify(val))

  if (!c.columns) c.columns = []

  // Ensure every column has props and options initialized
  c.columns = c.columns.map((col: any) => ({
    ...col,
    props: col.props || {},
    options: col.options || [],
  }))

  return c
}

// Initialize with valid config
const config = ref<SubTableConfig>(ensureValidConfig(props.modelValue))

// Watch config changes
watch(
  config,
  (newVal) => {
    emit('update:modelValue', newVal)
  },
  { deep: true },
)

// Watch props changes to sync
watch(
  () => props.modelValue,
  (val) => {
    // Compare stringified versions to avoid infinite loops and unnecessary updates
    if (val && JSON.stringify(val) !== JSON.stringify(config.value)) {
      config.value = ensureValidConfig(val)
    }
  },
  { deep: true }, // removed immediate: true as we init in setup
)

const activeColumnIndices = ref<string[]>([])

const widgetTypeOptions = [
  { label: '单行文本', value: 'input' },
  { label: '数字输入', value: 'number' },
  { label: '下拉选择', value: 'select' },
  { label: '单选框', value: 'radio' },
  { label: '复选框', value: 'checkbox' },
  { label: '日期选择', value: 'date' },
]

const addColumn = () => {
  const index = config.value.columns.length + 1
  const newKey = `col_${Math.random().toString(36).substring(2, 8)}`
  config.value.columns.push({
    key: newKey,
    label: `列${index}`,
    widgetType: 'input',
    width: '150px',
    required: false,
    props: {},
    options: [],
  })
  // Auto expand the new column
  activeColumnIndices.value = [newKey]
}

const removeColumn = (index: number) => {
  config.value.columns.splice(index, 1)
}

const addOption = (col: SubTableColumn) => {
  if (!col.options) col.options = []
  const idx = col.options.length + 1
  col.options.push({
    label: `选项${idx}`,
    value: `opt_${idx}`,
  })
}

const removeOption = (col: SubTableColumn, optIndex: number) => {
  col.options?.splice(optIndex, 1)
}

const showOptions = (type: WidgetType) => ['select', 'radio', 'checkbox'].includes(type)
</script>

<template>
  <div class="sub-table-config-editor">
    <el-divider content-position="left">表格列配置</el-divider>

    <div class="table-settings">
      <el-form label-width="80px" size="small">
        <el-form-item label="最大行数">
          <el-input-number
            v-model="config.maxRows"
            :min="0"
            :step="1"
            placeholder="默认不限"
            style="width: 100%"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item label="功能开关">
          <div class="checkbox-group">
            <el-checkbox v-model="config.showIndex">显示序号</el-checkbox>
            <el-checkbox v-model="config.allowAdd">允许添加</el-checkbox>
            <el-checkbox v-model="config.allowDelete">允许删除</el-checkbox>
          </div>
        </el-form-item>
      </el-form>
    </div>

    <div class="columns-list">
      <el-collapse v-model="activeColumnIndices" accordion>
        <el-collapse-item v-for="(col, index) in config.columns" :key="col.key" :name="col.key">
          <template #title>
            <div class="column-header">
              <span class="col-title">
                <strong>{{ col.label || `列${index + 1}` }}</strong>
                <span class="col-type-tag">
                  {{ widgetTypeOptions.find((t) => t.value === col.widgetType)?.label }}
                </span>
              </span>
              <el-button
                type="danger"
                :icon="Delete"
                link
                size="small"
                @click.stop="removeColumn(index)"
              >
                删除
              </el-button>
            </div>
          </template>

          <div class="column-config-form">
            <el-form label-width="80px" size="small">
              <el-form-item label="列标题">
                <el-input v-model="col.label" placeholder="请输入列标题" />
              </el-form-item>

              <el-form-item label="字段Key">
                <el-input v-model="col.key" placeholder="唯一标识" />
              </el-form-item>

              <el-form-item label="列宽">
                <el-input v-model="col.width" placeholder="如 150px" />
              </el-form-item>

              <el-form-item label="控件类型">
                <el-select v-model="col.widgetType" style="width: 100%">
                  <el-option
                    v-for="opt in widgetTypeOptions"
                    :key="opt.value"
                    :label="opt.label"
                    :value="opt.value"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="是否必填">
                <el-switch v-model="col.required" />
              </el-form-item>

              <!-- Input Props -->
              <template
                v-if="['input', 'textarea', 'number'].includes(col.widgetType) && col.props"
              >
                <el-form-item label="占位提示">
                  <el-input v-model="col.props.placeholder" placeholder="请输入..." />
                </el-form-item>
              </template>

              <!-- Number Props -->
              <template v-if="col.widgetType === 'number' && col.props">
                <el-form-item label="小数精度">
                  <el-input-number
                    v-model="col.props.precision"
                    :min="0"
                    :max="5"
                    controls-position="right"
                    style="width: 100%"
                  />
                </el-form-item>
              </template>

              <!-- Options Config -->
              <el-form-item label="选项列表" v-if="showOptions(col.widgetType)">
                <div class="options-config">
                  <div class="options-list">
                    <div v-for="(opt, optIdx) in col.options" :key="optIdx" class="option-item">
                      <el-input v-model="opt.label" placeholder="显示名" class="option-input" />
                      <el-input v-model="opt.value" placeholder="值" class="option-input" />
                      <el-button
                        type="danger"
                        :icon="Delete"
                        circle
                        size="small"
                        @click="removeOption(col, optIdx)"
                      />
                    </div>
                  </div>
                  <el-button
                    type="primary"
                    link
                    :icon="Plus"
                    size="small"
                    @click="addOption(col)"
                    class="add-option-btn"
                  >
                    添加选项
                  </el-button>
                  <el-empty
                    v-if="!col.options || col.options.length === 0"
                    description="暂无选项"
                    :image-size="40"
                  />
                </div>
              </el-form-item>
            </el-form>
          </div>
        </el-collapse-item>
      </el-collapse>

      <div class="add-col-btn">
        <el-button type="primary" plain :icon="Plus" @click="addColumn" style="width: 100%">
          添加列
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.sub-table-config-editor {
  background-color: transparent;
  border-radius: 0;
  padding: 0;
  max-width: 100%;
}

:deep(.el-divider__text) {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
}

.table-settings {
  padding: 0 10px;
  background-color: transparent;
  margin-bottom: 20px;

  .checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  :deep(.el-form-item) {
    margin-bottom: 12px;

    &:last-child {
      margin-bottom: 0;
    }
  }
}

.columns-list {
  max-width: 100%;
  overflow: visible;
  padding: 0 10px;

  :deep(.el-collapse) {
    border: none;
    --el-collapse-header-height: 48px;
  }

  :deep(.el-collapse-item) {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    margin-bottom: 8px;
    overflow: hidden;
    background-color: #fff;

    &.is-active {
      border-color: #dcdfe6;
    }
  }

  :deep(.el-collapse-item__header) {
    background-color: #fff;
    border-bottom: none;
    padding: 0 12px;
    height: 48px;
    line-height: 48px;
    font-size: 13px;
    color: #606266;
    border-radius: 4px;

    &.is-active {
      border-bottom: 1px solid #ebeef5;
      border-bottom-left-radius: 0;
      border-bottom-right-radius: 0;
      background-color: #fcfcfc;
    }
  }

  :deep(.el-collapse-item__wrap) {
    border: none;
    background-color: #fcfcfc;
  }

  :deep(.el-collapse-item__content) {
    padding: 16px;
    padding-bottom: 8px;
  }
}

.column-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
  overflow: hidden;

  .col-title {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    overflow: hidden;
    min-width: 0;

    strong {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 120px;
      display: inline-block;
      font-weight: 500;
      color: #303133;
    }
  }

  .col-type-tag {
    font-size: 12px;
    color: #909399;
    background-color: #f4f4f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-weight: normal;
    white-space: nowrap;
    flex-shrink: 0;
    line-height: 1.2;
  }
}

.column-config-form {
  max-width: 100%;
  overflow: visible;

  :deep(.el-form-item) {
    margin-bottom: 16px;
  }

  :deep(.el-form-item__label) {
    font-size: 13px;
    color: #606266;
  }
}

.options-config {
  width: 100%;
  background-color: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  box-sizing: border-box;

  .options-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 10px;
  }

  .option-item {
    display: flex;
    gap: 8px;
    align-items: center;

    .option-input {
      flex: 1;
      min-width: 0;
    }

    .el-button {
      flex-shrink: 0;
    }
  }

  .add-option-btn {
    width: 100%;
    justify-content: center;
    border: 1px dashed #dcdfe6;

    &:hover {
      border-color: #409eff;
      background-color: #ecf5ff;
    }
  }
}

.add-col-btn {
  margin: 15px 10px;

  .el-button {
    width: 100%;
    border-style: dashed;
    height: 40px;
    font-size: 14px;

    &:hover {
      background-color: #ecf5ff;
      border-color: #409eff;
      color: #409eff;
    }
  }
}
</style>
