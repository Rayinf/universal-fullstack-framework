<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import {
  Plus,
  Delete,
  Rank,
  Expand,
  Close,
  Check,
  Search,
  Fold,
  Bottom,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormLayoutConfig, TableCell, SubTableConfig } from '@/types/formConfig'
import type { ProcessLibraryItemParam } from '@/types/technology'
import { createDefaultLayout, getTableGrid, getLogicalColumnCount } from '@/utils/tableMatrix'
import FieldConfigPanel from './FieldConfigPanel.vue'
import DynamicFormRenderer from './DynamicFormRenderer.vue'
import SubTableRenderer from './SubTableRenderer.vue'
import { useTechnologyStore } from '@/stores/technologyStore'

const technologyStore = useTechnologyStore()

interface Props {
  modelValue: string | undefined
  availableFields: ProcessLibraryItemParam[]
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue', 'close'])

const activeMode = ref<'design' | 'preview'>('design')
const previewData = ref<Record<string, any>>({})
const visible = ref(false)
const layout = ref<FormLayoutConfig>(createDefaultLayout())
const selectedCellId = ref<string | null>(null)
const fieldSearch = ref('')

// 初始化
watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      try {
        layout.value = JSON.parse(val)
      } catch (e) {
        layout.value = createDefaultLayout()
      }
    } else {
      layout.value = createDefaultLayout()
    }
  },
  { immediate: true },
)

const selectedCell = computed(() => {
  for (const row of layout.value.rows) {
    const cell = row.cells.find((c) => c.id === selectedCellId.value)
    if (cell) return cell
  }
  return null
})

const selectedField = computed(() => {
  if (selectedCell.value?.content.type === 'field' && selectedCell.value.content.value) {
    return props.availableFields.find(
      (f) => String(f.id) === String(selectedCell.value!.content.value),
    )
  }
  return null
})

const logicalColumnCount = computed(() => getLogicalColumnCount(layout.value))

// 过滤重复字段显示
const uniqueAvailableFields = computed(() => {
  const seen = new Set()
  return props.availableFields.filter((f) => {
    if (seen.has(f.id)) return false
    seen.add(f.id)
    return true
  })
})

const filteredUniqueFields = computed(() => {
  return uniqueAvailableFields.value.filter((f) =>
    f.paramName.toLowerCase().includes(fieldSearch.value.toLowerCase()),
  )
})

const handleFieldConfigUpdate = async (newJson: string) => {
  if (selectedField.value) {
    selectedField.value.jsonConfig = newJson
    try {
      // 检查是否切换为子表单
      const config = JSON.parse(newJson)
      if (config.widgetType === 'subTable') {
        makeCellFullRow(selectedCellId.value)
      }

      await technologyStore.updateProcessLibraryItemParam({
        id: selectedField.value.id,
        paramName: selectedField.value.paramName,
        paramType: selectedField.value.paramType,
        jsonConfig: newJson,
      })
    } catch (e) {
      console.error('自动保存字段配置失败', e)
    }
  }
}

const makeCellFullRow = (cellId: string | null) => {
  if (!cellId) return

  let targetRow: any = null
  let targetCellIndex = -1

  for (const row of layout.value.rows) {
    const idx = row.cells.findIndex((c) => c.id === cellId)
    if (idx !== -1) {
      targetRow = row
      targetCellIndex = idx
      break
    }
  }

  if (targetRow) {
    // 如果已经是整行，直接返回
    if (
      targetRow.cells.length === 1 &&
      (targetRow.cells[0].colspan || 1) === logicalColumnCount.value
    ) {
      return
    }

    ElMessageBox.confirm(
      '子表单控件建议独占一行，是否自动合并单元格？(这将清除该行其他单元格的内容)',
      '自动调整布局',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' },
    )
      .then(() => {
        const cell = targetRow.cells[targetCellIndex]
        cell.colspan = logicalColumnCount.value
        // 重置 rowspan 防止布局错乱
        cell.rowspan = 1
        targetRow.cells = [cell]
        ElMessage.success('已自动设置为整行显示')
      })
      .catch(() => {
        // 用户取消，不做操作
      })
  }
}

// 确保选中单元格时 style 对象存在
watch(selectedCell, (cell) => {
  if (cell && !cell.style) {
    cell.style = { align: 'left' }
  }
})

// --- 表格操作 ---

const addRow = () => {
  const colCount = logicalColumnCount.value || 1
  const newCells: TableCell[] = []
  for (let i = 0; i < colCount; i++) {
    newCells.push({
      id: Math.random().toString(36).substr(2, 9),
      content: { type: 'static', value: '' },
      style: { align: 'left' },
      colspan: 1,
      rowspan: 1,
    })
  }
  layout.value.rows.push({ cells: newCells })
}

const addCol = () => {
  addColumn()
}

const addColumn = () => {
  layout.value.rows.forEach((row) => {
    row.cells.push({
      id: Math.random().toString(36).substr(2, 9),
      content: { type: 'static', value: '' },
      style: { align: 'left' },
      colspan: 1,
      rowspan: 1,
    })
  })
}

const removeRow = async (index: number) => {
  if (layout.value.rows.length <= 1) return
  selectedCellId.value = null
  await nextTick()
  layout.value.rows.splice(index, 1)
}

const insertRow = (index: number) => {
  const colCount = logicalColumnCount.value || 1
  const newCells: TableCell[] = []
  for (let i = 0; i < colCount; i++) {
    newCells.push({
      id: Math.random().toString(36).substr(2, 9),
      content: { type: 'static', value: '' },
      style: { align: 'left' },
      colspan: 1,
      rowspan: 1,
    })
  }
  layout.value.rows.splice(index, 0, { cells: newCells })
}

const deleteColumn = async (colIndex: number) => {
  if (logicalColumnCount.value <= 1) return

  selectedCellId.value = null
  await nextTick()

  const grid = getTableGrid(layout.value)
  const cellIdsToRemove = new Set<string>()
  const cellIdsToShrink = new Set<string>()

  grid.forEach((rowGrid) => {
    const cellId = rowGrid[colIndex]
    if (cellId) {
      for (const row of layout.value.rows) {
        const cell = row.cells.find((c) => c.id === cellId)
        if (cell) {
          if ((cell.colspan || 1) > 1) {
            cellIdsToShrink.add(cellId)
          } else {
            cellIdsToRemove.add(cellId)
          }
          break
        }
      }
    }
  })

  layout.value.rows.forEach((row) => {
    row.cells.forEach((cell) => {
      if (cellIdsToShrink.has(cell.id)) {
        cell.colspan = (cell.colspan || 1) - 1
      }
    })
    row.cells = row.cells.filter((cell) => !cellIdsToRemove.has(cell.id))
  })

  ElMessage.success(`已删除第 ${colIndex + 1} 列`)
}

const handleDrop = (cell: TableCell, event: any) => {
  const fieldId = event.dataTransfer?.getData('fieldId')
  if (fieldId) {
    cell.content = {
      type: 'field',
      value: fieldId,
    }

    // 检查字段类型，如果是子表单，提示占满整行
    const field = props.availableFields.find((f) => String(f.id) === String(fieldId))
    if (field && field.jsonConfig) {
      try {
        const c = JSON.parse(field.jsonConfig)
        if (c.widgetType === 'subTable') {
          makeCellFullRow(cell.id)
        }
      } catch (e) {
        // ignore
      }
    }

    ElMessage.success(`绑定字段: ${getFieldName(fieldId)}`)
  }
}

const onDragStart = (event: DragEvent, field: ProcessLibraryItemParam) => {
  if (event.dataTransfer) {
    event.dataTransfer.setData('fieldId', String(field.id))
    event.dataTransfer.effectAllowed = 'copy'
  }
}

const onDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'copy'
  }
}

const getFieldName = (id: string) => {
  return props.availableFields.find((f) => String(f.id) === String(id))?.paramName || '未知字段'
}

const getFieldConfig = (id: string) => {
  const field = props.availableFields.find((f) => String(f.id) === String(id))
  if (!field?.jsonConfig) return null
  try {
    return typeof field.jsonConfig === 'string'
      ? JSON.parse(field.jsonConfig)
      : field.jsonConfig
  } catch (e) {
    return null
  }
}

const isSubTableField = (id: string) => {
  const config = getFieldConfig(id)
  return config?.widgetType === 'subTable'
}

const save = () => {
  emit('update:modelValue', JSON.stringify(layout.value))
  ElMessage.success('布局已暂存')
}

const mergeRight = (rowIndex: number, cellIndex: number) => {
  const row = layout.value.rows[rowIndex]
  const cell = row.cells[cellIndex]
  const grid = getTableGrid(layout.value)
  const colStart = grid[rowIndex].indexOf(cell.id)
  const colEnd = colStart + (cell.colspan || 1)

  if (colEnd >= logicalColumnCount.value) {
    return ElMessage.warning('右侧没有可合并的列')
  }

  const targetCellId = grid[rowIndex][colEnd]
  if (!targetCellId || targetCellId === cell.id) {
    return ElMessage.warning('右侧单元格不可合并')
  }

  // 移除目标单元格并增加当前单元格跨度
  const targetCellIdx = row.cells.findIndex((c) => c.id === targetCellId)
  if (targetCellIdx > -1) {
    row.cells.splice(targetCellIdx, 1)
    cell.colspan = (cell.colspan || 1) + 1
    ElMessage.success('向右合并成功')
  }
}

const mergeDown = (rowIndex: number, cellIndex: number) => {
  const row = layout.value.rows[rowIndex]
  const cell = row.cells[cellIndex]
  const grid = getTableGrid(layout.value)

  // 获取当前单元格的逻辑列起始位置和跨度
  const colStart = grid[rowIndex].indexOf(cell.id)
  const currentColspan = cell.colspan || 1
  const currentRowspan = cell.rowspan || 1

  // 计算下方目标行的索引
  const targetRowIndex = rowIndex + currentRowspan

  // 边界检查
  if (targetRowIndex >= layout.value.rows.length) {
    return ElMessage.warning('下方没有可合并的行')
  }

  // 获取下方单元格的 ID
  const targetCellId = grid[targetRowIndex][colStart]

  // 验证目标单元格
  if (!targetCellId || targetCellId === cell.id) {
    return ElMessage.warning('下方单元格不可合并')
  }

  // 检查下方单元格
  const targetRow = layout.value.rows[targetRowIndex]
  const targetCellIdx = targetRow.cells.findIndex((c) => c.id === targetCellId)
  const targetCell = targetRow.cells[targetCellIdx]

  // 检查 colspan 是否匹配
  const targetColspan = targetCell.colspan || 1
  if (currentColspan !== targetColspan) {
    return ElMessage.warning('下方单元格列跨度不匹配，无法合并')
  }

  // 获取下方单元格的 rowspan
  const targetRowspan = targetCell.rowspan || 1

  // 从目标行中移除下方单元格
  targetRow.cells.splice(targetCellIdx, 1)

  // 增加当前单元格的 rowspan（累加下方单元格的 rowspan）
  cell.rowspan = currentRowspan + targetRowspan

  ElMessage.success('向下合并成功')
}

const splitCell = (rowIndex: number, cellIndex: number) => {
  const row = layout.value.rows[rowIndex]
  const cell = row.cells[cellIndex]
  if ((cell.colspan || 1) > 1) {
    cell.colspan = (cell.colspan || 1) - 1
    row.cells.splice(cellIndex + 1, 0, {
      id: Math.random().toString(36).substr(2, 9),
      content: { type: 'static', value: '' },
      style: { align: 'left' },
      colspan: 1,
      rowspan: 1,
    })
  } else if ((cell.rowspan || 1) > 1) {
    const grid = getTableGrid(layout.value)
    const colIndex = grid[rowIndex].indexOf(cell.id)
    cell.rowspan = (cell.rowspan || 1) - 1

    // 在下方的行中正确插入释放出来的单元格
    const freedRowIndex = rowIndex + cell.rowspan
    const targetRow = layout.value.rows[freedRowIndex]

    // 寻找插入位置：找到第一个逻辑列大于当前列的单元格
    const freedGrid = grid[freedRowIndex]
    let insertIdx = targetRow.cells.length
    for (let i = 0; i < targetRow.cells.length; i++) {
      const c = targetRow.cells[i]
      if (freedGrid.indexOf(c.id) > colIndex) {
        insertIdx = i
        break
      }
    }

    targetRow.cells.splice(insertIdx, 0, {
      id: Math.random().toString(36).substr(2, 9),
      content: { type: 'static', value: '' },
      style: { align: 'left' },
      colspan: 1,
      rowspan: 1,
    })
  } else {
    ElMessage.warning('此单元格未合并，无法拆分')
  }
}
</script>

<template>
  <div class="designer-container">
    <!-- 页眉 -->
    <div class="designer-header">
      <div class="header-left">
        <h3>表单布局设计器</h3>
        <el-divider direction="vertical" />
        <el-radio-group v-model="activeMode" size="small">
          <el-radio-button label="design">设计布局</el-radio-button>
          <el-radio-button label="preview">预览输入</el-radio-button>
        </el-radio-group>
      </div>
      <div class="header-actions">
        <el-button @click="emit('close')">取消</el-button>
        <el-button type="primary" :icon="Check" @click="save">保存布局</el-button>
      </div>
    </div>

    <!-- 主体区域 -->
    <div class="designer-body">
      <!-- 左侧字段列表 -->
      <div class="side-panel fields-panel">
        <div class="panel-title">可用字段库</div>
        <div class="search-bar">
          <el-input
            v-model="fieldSearch"
            placeholder="搜索字段..."
            size="small"
            :prefix-icon="Search"
          />
        </div>
        <div class="field-list">
          <div
            v-for="element in filteredUniqueFields"
            :key="element.id"
            class="field-item"
            draggable="true"
            @dragstart="onDragStart($event, element)"
          >
            <el-icon><Rank /></el-icon>
            <span>{{ element.paramName }}</span>
          </div>
        </div>
      </div>

      <!-- 中间画布区域 -->
      <div class="main-canvas">
        <!-- 设计模式 -->
        <template v-if="activeMode === 'design'">
          <div class="canvas-toolbar">
            <el-button-group>
              <el-button size="small" :icon="Plus" @click="addRow">追加行</el-button>
              <el-button size="small" :icon="Plus" @click="addCol">追加列</el-button>
            </el-button-group>
          </div>

          <div class="table-container">
            <!-- 列操作栏 -->
            <div class="column-tools">
              <div v-for="cIdx in logicalColumnCount" :key="cIdx" class="col-tool-item">
                <el-tooltip content="删除此列" placement="top">
                  <el-button
                    :icon="Delete"
                    type="danger"
                    circle
                    size="small"
                    class="floating-btn"
                    @click="deleteColumn(cIdx - 1)"
                  />
                </el-tooltip>
              </div>
            </div>

            <table class="design-table" :class="{ 'has-border': layout.border }">
              <colgroup>
                <col v-for="n in logicalColumnCount" :key="n" />
                <col width="40" />
              </colgroup>
              <tbody>
                <template v-for="(row, rIndex) in layout.rows" :key="rIndex">
                  <!-- 行上方插入手柄 -->
                  <tr class="insert-handle-row" v-if="rIndex === 0">
                    <td :colspan="logicalColumnCount + 1" class="handle-cell">
                      <el-tooltip content="在此上方插入行" placement="right">
                        <div class="insert-handle-btn top" @click="insertRow(0)">
                          <el-icon><Plus /></el-icon>
                        </div>
                      </el-tooltip>
                    </td>
                  </tr>

                  <tr class="design-tr">
                    <td
                      v-for="(cell, cIndex) in row.cells"
                      :key="cell.id"
                      :rowspan="(cell.rowspan || 1) * 2 - 1"
                      :colspan="cell.colspan || 1"
                      :class="{ active: selectedCellId === cell.id }"
                      :style="{
                        textAlign: cell.style?.align || 'left',
                        backgroundColor: cell.style?.backgroundColor,
                      }"
                      @click="selectedCellId = cell.id"
                      @dragover.prevent="onDragOver($event)"
                      @drop="handleDrop(cell, $event)"
                    >
                      <div class="cell-content">
                        <!-- 静态文本 -->
                        <template v-if="cell.content.type === 'static'">
                          <el-input
                            v-model="cell.content.value"
                            size="small"
                            placeholder="输入文本..."
                            class="static-input"
                          />
                        </template>
                        <!-- 绑定字段 -->
                        <template v-else>
                          <!-- 子表单预览 -->
                          <template v-if="isSubTableField(cell.content.value)">
                            <div class="subtable-preview-wrapper">
                              <div class="field-tag subtable-tag">
                                <span class="label">子表单:</span>
                                <span class="name">{{ getFieldName(cell.content.value) }}</span>
                                <el-icon
                                  class="remove-btn"
                                  @click.stop="cell.content = { type: 'static', value: '' }"
                                >
                                  <Close />
                                </el-icon>
                              </div>
                              <SubTableRenderer
                                :config="getFieldConfig(cell.content.value) as SubTableConfig"
                                :model-value="[]"
                                :disabled="true"
                                class="subtable-preview"
                              />
                            </div>
                          </template>
                          <!-- 普通字段 -->
                          <template v-else>
                            <div class="field-tag">
                              <span class="label">字段:</span>
                              <span class="name">{{ getFieldName(cell.content.value) }}</span>
                              <el-icon
                                class="remove-btn"
                                @click.stop="cell.content = { type: 'static', value: '' }"
                              >
                                <Close />
                              </el-icon>
                            </div>
                          </template>
                        </template>

                        <!-- 单元格内快捷操作 (角标) -->
                        <div class="cell-ops" v-if="selectedCellId === cell.id">
                          <el-tooltip content="向右合并" placement="top">
                            <el-icon @click.stop="mergeRight(rIndex, cIndex)"><Expand /></el-icon>
                          </el-tooltip>
                          <el-tooltip content="向下合并" placement="top">
                            <el-icon @click.stop="mergeDown(rIndex, cIndex)"><Bottom /></el-icon>
                          </el-tooltip>
                          <el-tooltip content="拆分/还原" placement="top">
                            <el-icon @click.stop="splitCell(rIndex, cIndex)"><Fold /></el-icon>
                          </el-tooltip>
                        </div>
                      </div>
                    </td>
                    <!-- 行末删除手柄 (角标样式) -->
                    <td class="row-tool-cell">
                      <el-tooltip content="删除此行" placement="right">
                        <el-button
                          :icon="Delete"
                          type="danger"
                          circle
                          size="small"
                          class="floating-btn row-del"
                          @click="removeRow(rIndex)"
                        />
                      </el-tooltip>
                    </td>
                  </tr>

                  <!-- 行下方插入手柄 -->
                  <tr class="insert-handle-row">
                    <td :colspan="logicalColumnCount + 1" class="handle-cell">
                      <el-tooltip content="在此下方插入行" placement="right">
                        <div class="insert-handle-btn" @click="insertRow(rIndex + 1)">
                          <el-icon><Plus /></el-icon>
                        </div>
                      </el-tooltip>
                    </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </template>

        <!-- 预览模式 -->
        <template v-else>
          <div class="preview-container">
            <div class="preview-header">
              <el-alert
                title="预览模式：您可以模拟真实填写数据的体验。注意：预览数据仅供展示，不会保存。"
                type="success"
                :closable="false"
                show-icon
              />
            </div>
            <div class="form-wrapper">
              <DynamicFormRenderer
                :layout-config="layout"
                :fields="availableFields"
                v-model="previewData"
              />
            </div>
            <div class="data-preview">
              <div class="data-title">实时录入数据 (JSON):</div>
              <pre>{{ JSON.stringify(previewData, null, 2) }}</pre>
            </div>
          </div>
        </template>
      </div>

      <!-- 右侧属性面板 -->
      <div class="side-panel property-panel">
        <div class="panel-title">
          {{ selectedField ? '字段属性' : '单元格属性' }}
        </div>
        <el-empty v-if="!selectedCell" description="请选择单元格" />
        <div v-else-if="selectedCell.style">
          <!-- 字段配置 -->
          <template v-if="selectedField">
            <div class="field-info">
              <span class="label">当前字段:</span>
              <strong>{{ selectedField.paramName }}</strong>
            </div>
            <el-divider />
            <FieldConfigPanel
              :model-value="selectedField.jsonConfig"
              @update:model-value="handleFieldConfigUpdate"
            />
          </template>

          <!-- 布局与样式配置 -->
          <el-divider content-position="left">样式配置</el-divider>
          <el-form label-position="top" size="small">
            <el-form-item label="对齐方式">
              <el-radio-group v-model="selectedCell.style.align">
                <el-radio-button label="left">左</el-radio-button>
                <el-radio-button label="center">中</el-radio-button>
                <el-radio-button label="right">右</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="背景颜色">
              <el-color-picker v-model="selectedCell.style.backgroundColor" />
            </el-form-item>
            <el-form-item label="内容类型" v-if="!selectedField">
              <el-select v-model="selectedCell.content.type">
                <el-option label="静态文本" value="static" />
                <el-option label="绑定字段" value="field" />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.field-info {
  margin-bottom: 15px;
  font-size: 14px;
  .label {
    color: #909399;
    margin-right: 8px;
  }
}

.designer-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: #f0f2f5;
  overflow: hidden;
}

.designer-header {
  height: 60px;
  background-color: #fff;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  border-bottom: 1px solid #dcdfe6;
  h3 {
    margin: 0;
    margin-right: 15px;
  }
  .header-left {
    display: flex;
    align-items: center;
  }
}

.designer-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.side-panel {
  width: 280px;
  background-color: #fff;
  border-right: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  &.property-panel {
    border-right: none;
    border-left: 1px solid #dcdfe6;
    padding: 0;
    overflow-y: auto;
    overflow-x: hidden;

    // 自定义滚动条样式
    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #f1f1f1;
    }

    &::-webkit-scrollbar-thumb {
      background: #c1c1c1;
      border-radius: 3px;

      &:hover {
        background: #a8a8a8;
      }
    }

    > .panel-title {
      position: sticky;
      top: 0;
      background-color: #fff;
      z-index: 10;
      margin: 0;
    }

    > div:not(.panel-title) {
      padding: 15px;
    }
  }
}

.panel-title {
  padding: 12px 15px;
  font-weight: 600;
  border-bottom: 1px solid #f0f2f5;
  color: #333;
}

.search-bar {
  padding: 10px;
}

.field-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.field-item {
  padding: 8px 12px;
  background-color: #f6f8fa;
  border: 1px solid #e1e4e8;
  border-radius: 4px;
  margin-bottom: 8px;
  cursor: move;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  &:hover {
    background-color: #eef1f6;
    border-color: #409eff;
  }
}

.main-canvas {
  flex: 1;
  overflow: hidden;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.canvas-toolbar {
  background-color: #fff;
  padding: 10px 15px;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.table-container {
  background-color: #fff;
  padding: 20px 40px 60px 40px; /* Reduced top padding, kept side and bottom */
  border-radius: 4px;
  /* min-height: 500px; Remove fixed min-height to allow flex scaling */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: auto;
  width: 100%;
  box-sizing: border-box;
  flex: 1;
  min-height: 0;
}

/* 列操作手柄 */
.column-tools {
  display: flex;
  margin-bottom: 5px;
  padding-right: 40px; /* 对应 row-tool-cell 的宽度 */
  margin-left: 0;
  position: sticky;
  top: 0;
  z-index: 30;
  background-color: #fff;
  padding-top: 10px; /* Add padding to separate from top edge */
  padding-bottom: 5px; /* Add padding to separate from table */
  border-bottom: 1px solid #f0f2f5; /* Optional: add separator */
}

.col-tool-item {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.floating-btn {
  opacity: 0;
  transition: all 0.2s;
  z-index: 10;
  &.row-del {
    margin-left: 10px;
  }
}

.col-tool-item:hover .floating-btn,
.design-tr:hover .floating-btn {
  opacity: 1;
}

/* 插入行手柄 */
.insert-handle-row {
  height: 2px;
  .handle-cell {
    padding: 0 !important;
    border: none !important;
    position: relative;
    height: 2px;
    &::after {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      top: 50%;
      height: 1px;
      background-color: transparent;
      transition: all 0.2s;
    }
  }
  &:hover .handle-cell::after {
    background-color: #409eff;
  }
}

.insert-handle-btn {
  position: absolute;
  left: -30px;
  width: 24px;
  height: 24px;
  background-color: #fff;
  border: 1px solid #409eff;
  border-radius: 50%;
  color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 20;
  opacity: 0;
  transform: translateY(-50%);
  transition: all 0.2s;
  &:hover {
    background-color: #409eff;
    color: #fff;
    transform: translateY(-50%) scale(1.2);
    opacity: 1 !important;
  }
  &.top {
    top: 50%;
  }
}

.insert-handle-row:hover .insert-handle-btn {
  opacity: 0.5;
}

.design-tr {
  &:hover {
    background-color: #fafafa;
  }
}

.row-tool-cell {
  width: 40px;
  padding: 0 !important;
  border: none !important;
  vertical-align: middle;
}

.design-table {
  width: 100%;
  border-collapse: collapse;
  /* table-layout: fixed;  Removed fixed layout to allow auto-sizing and full width usage */
  &.has-border td {
    border: 1px solid #dcdfe6;
  }
  td {
    height: auto;
    min-height: 60px;
    padding: 8px;
    position: relative;
    &.active {
      outline: 2px solid #409eff;
      z-index: 1;
    }
    &:hover .cell-ops {
      display: flex;
    }
  }
}

.cell-content {
  width: 100%;
  height: 100%;
  min-height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.static-input :deep(.el-input__wrapper) {
  background-color: transparent;
  box-shadow: none;
  &:hover {
    box-shadow: 0 0 0 1px #dcdfe6 inset;
  }
}

.field-tag {
  background-color: #ecf5ff;
  border: 1px solid #d9ecff;
  color: #409eff;
  padding: 4px 8px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;

  &.subtable-tag {
    background-color: #f0f9ff;
    border-color: #bae7ff;
    color: #1890ff;
    margin-bottom: 8px;
  }

  .label {
    opacity: 0.7;
  }
  .name {
    font-weight: 600;
  }
  .remove-btn {
    cursor: pointer;
    margin-left: auto;
    &:hover {
      color: #f56c6c;
    }
  }
}

.subtable-preview-wrapper {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.subtable-preview {
  pointer-events: none;
  opacity: 0.85;
  font-size: 12px;

  :deep(.el-table) {
    font-size: 12px;
  }

  :deep(.el-table th) {
    padding: 6px 0;
    font-size: 12px;
  }

  :deep(.el-table td) {
    padding: 6px 0;
  }

  :deep(.el-button) {
    transform: scale(0.9);
  }
}

.cell-ops {
  display: none;
  position: absolute;
  top: -12px;
  right: -12px;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 2px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 2;
  gap: 4px;
  .el-icon {
    padding: 4px;
    cursor: pointer;
    &:hover {
      color: #409eff;
      background-color: #f0f7ff;
    }
  }
}

.preview-container {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  /* min-height: 100%; Remove this to allow scrolling */
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow: auto; /* Allow scrolling within the container */
  height: 100%; /* Take full height of main-canvas */
}

.form-wrapper {
  padding: 40px;
  border: 1px solid #ebeef5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background-color: #fff;
}

.data-preview {
  background-color: #2d3436;
  color: #fab1a0;
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  font-size: 13px;
  .data-title {
    color: #dfe6e9;
    margin-bottom: 10px;
    border-bottom: 1px solid #636e72;
    padding-bottom: 5px;
  }
}
</style>
