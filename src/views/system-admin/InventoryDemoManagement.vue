<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>库存管理示例</h2>
          <div class="page-description">代表性页面：库存主数据 + 出入库流水联动。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <el-tabs v-model="activeTab" class="inventory-tabs">
        <el-tab-pane name="items">
          <template #label>
            <div class="tab-label">
              <el-icon><Box /></el-icon>
              <span>库存主数据</span>
            </div>
          </template>

          <div class="search-actions-panel">
            <el-form inline @submit.prevent>
              <el-form-item label="关键词">
                <el-input
                  v-model="itemQuery.keyword"
                  placeholder="物料编码/名称"
                  clearable
                  style="width: 240px"
                  @keyup.enter="loadItemData"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadItemData">查询</el-button>
                <el-button @click="resetItemQuery">重置</el-button>
              </el-form-item>
            </el-form>
            <el-button type="primary" @click="openCreateItemDialog">
              <el-icon><Plus /></el-icon>新增物料
            </el-button>
          </div>

          <div class="table-container">
            <el-table :data="itemTableData" stripe highlight-current-row v-loading="itemLoading">
              <el-table-column prop="sku" label="物料编码" min-width="140" show-overflow-tooltip />
              <el-table-column
                prop="itemName"
                label="物料名称"
                min-width="180"
                show-overflow-tooltip
              />
              <el-table-column prop="unit" label="单位" width="80" align="center" />
              <el-table-column prop="stockQty" label="库存数量" width="120" align="right">
                <template #default="{ row }">
                  <span :class="{ 'text-danger': row.isLowStock, 'fw-bold': row.isLowStock }">
                    {{ row.stockQty }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="safetyQty" label="安全库存" width="120" align="right" />
              <el-table-column label="库存状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.isLowStock ? 'danger' : 'success'" size="small">
                    {{ row.isLowStock ? '低库存' : '正常' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="updateTime" label="更新时间" width="170" align="center" />
              <el-table-column label="操作" width="220" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openItemDetailDialog(row)">详情</el-button>
                  <el-button link type="primary" @click="openEditItemDialog(row)">编辑</el-button>
                  <el-button link type="danger" @click="handleDeleteItem(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-container">
              <el-pagination
                v-model:current-page="itemPagination.current"
                v-model:page-size="itemPagination.size"
                :page-sizes="[10, 20, 50]"
                :total="itemPagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleItemSizeChange"
                @current-change="handleItemCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane name="transactions">
          <template #label>
            <div class="tab-label">
              <el-icon><List /></el-icon>
              <span>出入库流水</span>
            </div>
          </template>

          <div class="search-actions-panel">
            <el-form inline @submit.prevent>
              <el-form-item label="关键词">
                <el-input
                  v-model="txQuery.keyword"
                  placeholder="编码/名称/单号"
                  clearable
                  style="width: 260px"
                  @keyup.enter="loadTransactionData"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              <el-form-item label="方向">
                <el-select
                  v-model="txQuery.direction"
                  clearable
                  placeholder="全部"
                  style="width: 120px"
                >
                  <el-option label="入库" :value="1" />
                  <el-option label="出库" :value="2" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="loadTransactionData">查询</el-button>
                <el-button @click="resetTransactionQuery">重置</el-button>
              </el-form-item>
            </el-form>
            <el-button type="success" @click="openCreateTransactionDialog">
              <el-icon><Plus /></el-icon>新增流水
            </el-button>
          </div>

          <div class="table-container">
            <el-table :data="txTableData" stripe highlight-current-row v-loading="txLoading">
              <el-table-column prop="sku" label="物料编码" width="130" show-overflow-tooltip />
              <el-table-column
                prop="itemName"
                label="物料名称"
                min-width="150"
                show-overflow-tooltip
              />
              <el-table-column label="方向" width="80" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.direction === 1 ? 'success' : 'warning'" size="small">
                    {{ row.direction === 1 ? '入库' : '出库' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="quantity" label="变动数量" width="100" align="right">
                <template #default="{ row }">
                  <span :class="row.direction === 1 ? 'text-success' : 'text-warning'">
                    {{ row.direction === 1 ? '+' : '-' }}{{ row.quantity }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="afterStock" label="变动后库存" width="110" align="right" />
              <el-table-column
                prop="businessNo"
                label="业务单号"
                width="150"
                show-overflow-tooltip
              />
              <el-table-column prop="operatorName" label="操作人" width="100" />
              <el-table-column prop="createTime" label="创建时间" width="170" align="center" />
              <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
              <el-table-column label="操作" width="90" align="center" fixed="right">
                <template #default="{ row }">
                  <el-button link type="primary" @click="openTxDetailDialog(row)">详情</el-button>
                </template>
              </el-table-column>
            </el-table>

            <div class="pagination-container">
              <el-pagination
                v-model:current-page="txPagination.current"
                v-model:page-size="txPagination.size"
                :page-sizes="[10, 20, 50]"
                :total="txPagination.total"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleTxSizeChange"
                @current-change="handleTxCurrentChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <div class="dialog-container">
      <el-dialog
        v-model="itemDialogVisible"
        :title="itemDialogTitle"
        width="520px"
        destroy-on-close
      >
        <el-form ref="itemFormRef" :model="itemFormData" :rules="itemFormRules" label-width="90px">
          <el-form-item label="物料编码" prop="sku">
            <el-input v-model="itemFormData.sku" placeholder="请输入物料编码" />
          </el-form-item>
          <el-form-item label="物料名称" prop="itemName">
            <el-input v-model="itemFormData.itemName" placeholder="请输入物料名称" />
          </el-form-item>
          <el-form-item label="单位">
            <el-input v-model="itemFormData.unit" placeholder="例如 pcs" />
          </el-form-item>
          <el-form-item label="库存数量" prop="stockQty">
            <el-input-number
              v-model="itemFormData.stockQty"
              :min="0"
              :step="1"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="安全库存" prop="safetyQty">
            <el-input-number
              v-model="itemFormData.safetyQty"
              :min="0"
              :step="1"
              style="width: 100%"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="itemDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="itemSubmitLoading" @click="submitItemForm"
            >确定</el-button
          >
        </template>
      </el-dialog>

      <el-dialog v-model="txDialogVisible" title="新增库存流水" width="520px" destroy-on-close>
        <el-form ref="txFormRef" :model="txFormData" :rules="txFormRules" label-width="90px">
          <el-form-item label="物料" prop="itemId">
            <el-select
              v-model="txFormData.itemId"
              filterable
              placeholder="请选择物料"
              style="width: 100%"
            >
              <el-option
                v-for="item in summaryList"
                :key="item.id"
                :label="`${item.sku} / ${item.itemName}`"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="方向" prop="direction">
            <el-select v-model="txFormData.direction" style="width: 100%">
              <el-option label="入库" :value="1" />
              <el-option label="出库" :value="2" />
            </el-select>
          </el-form-item>
          <el-form-item label="数量" prop="quantity">
            <el-input-number v-model="txFormData.quantity" :min="1" :step="1" style="width: 100%" />
          </el-form-item>
          <el-form-item label="业务单号">
            <el-input v-model="txFormData.businessNo" placeholder="可选" />
          </el-form-item>
          <el-form-item label="操作人" prop="operatorName">
            <el-input v-model="txFormData.operatorName" placeholder="请输入操作人" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="txFormData.remark" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="txDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="txSubmitLoading" @click="submitTransactionForm"
            >确定</el-button
          >
        </template>
      </el-dialog>

      <el-dialog v-model="itemDetailDialogVisible" title="物料详情" width="560px" destroy-on-close>
        <el-descriptions :column="2" border v-if="itemDetailData">
          <el-descriptions-item label="物料编码">{{ itemDetailData.sku }}</el-descriptions-item>
          <el-descriptions-item label="物料名称">{{
            itemDetailData.itemName
          }}</el-descriptions-item>
          <el-descriptions-item label="单位">{{ itemDetailData.unit }}</el-descriptions-item>
          <el-descriptions-item label="库存状态">
            {{ itemDetailData.isLowStock ? '低库存' : '正常' }}
          </el-descriptions-item>
          <el-descriptions-item label="库存数量">{{
            itemDetailData.stockQty
          }}</el-descriptions-item>
          <el-descriptions-item label="安全库存">{{
            itemDetailData.safetyQty
          }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{
            itemDetailData.createTime
          }}</el-descriptions-item>
          <el-descriptions-item label="更新时间">{{
            itemDetailData.updateTime
          }}</el-descriptions-item>
        </el-descriptions>
        <template #footer>
          <el-button type="primary" @click="itemDetailDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>

      <el-dialog
        v-model="txDetailDialogVisible"
        title="库存流水详情"
        width="560px"
        destroy-on-close
      >
        <el-descriptions :column="2" border v-if="txDetailData">
          <el-descriptions-item label="物料编码">{{ txDetailData.sku }}</el-descriptions-item>
          <el-descriptions-item label="物料名称">{{ txDetailData.itemName }}</el-descriptions-item>
          <el-descriptions-item label="方向">
            {{ txDetailData.direction === 1 ? '入库' : '出库' }}
          </el-descriptions-item>
          <el-descriptions-item label="变动数量">{{ txDetailData.quantity }}</el-descriptions-item>
          <el-descriptions-item label="变动后库存">{{
            txDetailData.afterStock
          }}</el-descriptions-item>
          <el-descriptions-item label="业务单号">{{
            txDetailData.businessNo || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="操作人">{{
            txDetailData.operatorName || '-'
          }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">{{
            txDetailData.createTime
          }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{
            txDetailData.remark || '-'
          }}</el-descriptions-item>
        </el-descriptions>
        <template #footer>
          <el-button type="primary" @click="txDetailDialogVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { Box, List, Search, Plus } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createInventoryItemApi,
  createInventoryTransactionApi,
  deleteInventoryItemApi,
  getInventorySummaryApi,
  pageInventoryItemApi,
  pageInventoryTransactionApi,
  updateInventoryItemApi,
  type InventoryItemRecord,
  type InventoryTransactionRecord,
} from '@/api/system/inventory'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface InventoryItemQuery {
  keyword: string
}

interface InventoryTxQuery {
  keyword: string
  direction: number | undefined
}

interface InventoryItemFormData {
  id: string
  sku: string
  itemName: string
  unit: string
  stockQty: number
  safetyQty: number
}

interface InventoryTxFormData {
  itemId: string
  direction: number
  quantity: number
  businessNo: string
  operatorName: string
  remark: string
}

const activeTab = ref('items')
const itemLoading = ref(false)
const txLoading = ref(false)
const itemSubmitLoading = ref(false)
const txSubmitLoading = ref(false)

const itemTableData = ref<InventoryItemRecord[]>([])
const txTableData = ref<InventoryTransactionRecord[]>([])
const summaryList = ref<InventoryItemRecord[]>([])

const itemDialogVisible = ref(false)
const txDialogVisible = ref(false)
const itemDetailDialogVisible = ref(false)
const txDetailDialogVisible = ref(false)
const itemDialogTitle = ref('新增物料')
const isEditItemMode = ref(false)
const itemDetailData = ref<InventoryItemRecord | null>(null)
const txDetailData = ref<InventoryTransactionRecord | null>(null)
const itemFormRef = ref<FormInstance>()
const txFormRef = ref<FormInstance>()

const itemQuery = reactive<InventoryItemQuery>({
  keyword: '',
})

const txQuery = reactive<InventoryTxQuery>({
  keyword: '',
  direction: undefined,
})

const itemPagination = reactive({
  current: 1,
  size: 10,
  total: 0,
})

const txPagination = reactive({
  current: 1,
  size: 10,
  total: 0,
})

const itemFormData = reactive<InventoryItemFormData>({
  id: '',
  sku: '',
  itemName: '',
  unit: 'pcs',
  stockQty: 0,
  safetyQty: 0,
})

const txFormData = reactive<InventoryTxFormData>({
  itemId: '',
  direction: 1,
  quantity: 1,
  businessNo: '',
  operatorName: '系统管理员',
  remark: '',
})

const itemFormRules: FormRules<InventoryItemFormData> = {
  sku: [{ required: true, message: '请输入物料编码', trigger: 'blur' }],
  itemName: [{ required: true, message: '请输入物料名称', trigger: 'blur' }],
}

const txFormRules: FormRules<InventoryTxFormData> = {
  itemId: [{ required: true, message: '请选择物料', trigger: 'change' }],
  direction: [{ required: true, message: '请选择方向', trigger: 'change' }],
  operatorName: [{ required: true, message: '请输入操作人', trigger: 'blur' }],
}

const summaryStats = computed(() => {
  const totalItems = summaryList.value.length
  const lowStockItems = summaryList.value.filter((item) => item.isLowStock).length
  const totalStock = summaryList.value.reduce((sum, item) => sum + item.stockQty, 0)
  return { totalItems, lowStockItems, totalStock }
})

const loadSummaryData = async () => {
  try {
    const res = await getInventorySummaryApi()
    if ((res.code === 0 || res.code === 200) && Array.isArray(res.data)) {
      summaryList.value = res.data
    } else {
      summaryList.value = []
    }
  } catch (error) {
    console.error('加载库存汇总失败:', error)
    summaryList.value = []
  }
}

const loadItemData = async () => {
  itemLoading.value = true
  try {
    const res = await pageInventoryItemApi({
      current: itemPagination.current,
      size: itemPagination.size,
      keyword: itemQuery.keyword || undefined,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      itemTableData.value = res.data.records || []
      itemPagination.total = res.data.total || 0
    } else {
      itemTableData.value = []
      itemPagination.total = 0
      ElMessage.error(res.msg || '库存主数据加载失败')
    }
  } catch (error) {
    console.error('加载库存主数据失败:', error)
    itemTableData.value = []
    itemPagination.total = 0
    ElMessage.error('库存主数据加载失败')
  } finally {
    itemLoading.value = false
  }
}

const loadTransactionData = async () => {
  txLoading.value = true
  try {
    const res = await pageInventoryTransactionApi({
      current: txPagination.current,
      size: txPagination.size,
      keyword: txQuery.keyword || undefined,
      direction: txQuery.direction,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      txTableData.value = res.data.records || []
      txPagination.total = res.data.total || 0
    } else {
      txTableData.value = []
      txPagination.total = 0
      ElMessage.error(res.msg || '库存流水加载失败')
    }
  } catch (error) {
    console.error('加载库存流水失败:', error)
    txTableData.value = []
    txPagination.total = 0
    ElMessage.error('库存流水加载失败')
  } finally {
    txLoading.value = false
  }
}

const refreshAll = async () => {
  await Promise.all([loadSummaryData(), loadItemData(), loadTransactionData()])
}

const resetItemQuery = () => {
  itemQuery.keyword = ''
  itemPagination.current = 1
  loadItemData()
}

const resetTransactionQuery = () => {
  txQuery.keyword = ''
  txQuery.direction = undefined
  txPagination.current = 1
  loadTransactionData()
}

const handleItemSizeChange = (size: number) => {
  itemPagination.size = size
  itemPagination.current = 1
  loadItemData()
}

const handleItemCurrentChange = (current: number) => {
  itemPagination.current = current
  loadItemData()
}

const handleTxSizeChange = (size: number) => {
  txPagination.size = size
  txPagination.current = 1
  loadTransactionData()
}

const handleTxCurrentChange = (current: number) => {
  txPagination.current = current
  loadTransactionData()
}

const resetItemForm = () => {
  itemFormData.id = ''
  itemFormData.sku = ''
  itemFormData.itemName = ''
  itemFormData.unit = 'pcs'
  itemFormData.stockQty = 0
  itemFormData.safetyQty = 0
}

const resetTxForm = () => {
  txFormData.itemId = ''
  txFormData.direction = 1
  txFormData.quantity = 1
  txFormData.businessNo = ''
  txFormData.operatorName = '系统管理员'
  txFormData.remark = ''
}

const openCreateItemDialog = () => {
  isEditItemMode.value = false
  itemDialogTitle.value = '新增物料'
  resetItemForm()
  itemDialogVisible.value = true
}

const openEditItemDialog = (row: InventoryItemRecord) => {
  isEditItemMode.value = true
  itemDialogTitle.value = '编辑物料'
  itemFormData.id = row.id
  itemFormData.sku = row.sku
  itemFormData.itemName = row.itemName
  itemFormData.unit = row.unit
  itemFormData.stockQty = row.stockQty
  itemFormData.safetyQty = row.safetyQty
  itemDialogVisible.value = true
}

const openItemDetailDialog = (row: InventoryItemRecord) => {
  itemDetailData.value = row
  itemDetailDialogVisible.value = true
}

const openCreateTransactionDialog = () => {
  resetTxForm()
  txDialogVisible.value = true
}

const openTxDetailDialog = (row: InventoryTransactionRecord) => {
  txDetailData.value = row
  txDetailDialogVisible.value = true
}

const submitItemForm = async () => {
  if (!itemFormRef.value) return
  const valid = await itemFormRef.value.validate().catch(() => false)
  if (!valid) return

  itemSubmitLoading.value = true
  try {
    const payload = {
      sku: itemFormData.sku,
      itemName: itemFormData.itemName,
      unit: itemFormData.unit,
      stockQty: itemFormData.stockQty,
      safetyQty: itemFormData.safetyQty,
    }
    const res = isEditItemMode.value
      ? await updateInventoryItemApi(itemFormData.id, payload)
      : await createInventoryItemApi(payload)
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success(isEditItemMode.value ? '更新成功' : '新增成功')
    itemDialogVisible.value = false
    await refreshAll()
  } catch (error) {
    console.error('提交物料失败:', error)
  } finally {
    itemSubmitLoading.value = false
  }
}

const submitTransactionForm = async () => {
  if (!txFormRef.value) return
  const valid = await txFormRef.value.validate().catch(() => false)
  if (!valid) return

  txSubmitLoading.value = true
  try {
    const res = await createInventoryTransactionApi({
      itemId: txFormData.itemId,
      direction: txFormData.direction,
      quantity: txFormData.quantity,
      businessNo: txFormData.businessNo,
      operatorName: txFormData.operatorName,
      remark: txFormData.remark,
    })
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success('新增库存流水成功')
    txDialogVisible.value = false
    await refreshAll()
  } catch (error) {
    console.error('提交库存流水失败:', error)
  } finally {
    txSubmitLoading.value = false
  }
}

const handleDeleteItem = async (row: InventoryItemRecord) => {
  try {
    await ElMessageBox.confirm(`确认删除物料「${row.itemName}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    const res = await deleteInventoryItemApi(row.id)
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success('删除成功')
    await refreshAll()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除物料失败:', error)
    }
  }
}

onMounted(() => {
  refreshAll()
})
</script>

<style scoped>
@import '@/styles/common.css';

.inventory-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.inventory-tabs :deep(.el-tabs__header) {
  margin: 0;
  padding: 0 24px;
  background-color: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.inventory-tabs :deep(.el-tabs__content) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
}

.inventory-tabs :deep(.el-tab-pane) {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  gap: 16px;
}

.table-container {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.table-container :deep(.el-table) {
  flex: 1;
  width: 100%;
}

.text-danger {
  color: var(--el-color-danger);
}

.text-success {
  color: var(--el-color-success);
}

.text-warning {
  color: var(--el-color-warning);
}

.fw-bold {
  font-weight: bold;
}
</style>
