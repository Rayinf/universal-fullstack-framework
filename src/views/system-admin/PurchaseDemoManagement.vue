<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>采购订单示例</h2>
          <div class="page-description">代表性页面：单据状态流转（草稿→提交→审批→作废）。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input v-model="query.keyword" placeholder="采购单号/供应商/物料" clearable style="width: 260px"
              @keyup.enter="handleSearch" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部状态" style="width: 160px">
              <el-option label="草稿" :value="0" />
              <el-option label="待审批" :value="1" />
              <el-option label="已审批" :value="2" />
              <el-option label="已作废" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="openCreateDialog">新增采购单</el-button>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="orderNo" label="采购单号" min-width="180" />
          <el-table-column prop="supplierName" label="供应商" min-width="180" />
          <el-table-column prop="itemName" label="物料" min-width="150" />
          <el-table-column prop="quantity" label="数量" width="100" align="right" />
          <el-table-column prop="unitPrice" label="单价" width="110" align="right">
            <template #default="{ row }">¥{{ row.unitPrice.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="totalAmount" label="总额" width="120" align="right">
            <template #default="{ row }">¥{{ row.totalAmount.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="applicant" label="申请人" width="120" />
          <el-table-column prop="updateTime" label="更新时间" min-width="180" />
          <el-table-column label="操作" width="320" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetailDialog(row)">详情</el-button>
              <el-button link type="info" @click="openApprovalStatusDialog(row)">审批状态</el-button>
              <el-button v-if="isEditable(row.status)" link type="primary" @click="openEditDialog(row)">
                编辑
              </el-button>

              <el-button v-if="row.status === 0" link type="success" @click="handleSubmitFlow(row.id)">
                提交
              </el-button>
              <el-button v-if="row.status === 1" link type="success" @click="openApproveDialog(row)">
                审批
              </el-button>

              <el-dropdown v-if="row.status === 0 || row.status === 1" trigger="click"
                @command="(cmd: string) => handleCommand(cmd, row)" style="margin-left: 12px; vertical-align: middle">
                <el-button link type="info">
                  更多<el-icon class="el-icon--right">
                    <ArrowDown />
                  </el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="cancel"
                      :disabled="row.status !== 0 && row.status !== 1">作废</el-dropdown-item>
                    <el-dropdown-item v-if="row.status === 0" command="delete" divided
                      style="color: var(--el-color-danger)">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination v-model:current-page="pagination.current" v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50]" :total="pagination.total" layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange" @current-change="handleCurrentChange" />
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="95px">
        <el-row :gutter="14">
          <el-col :span="12">
            <el-form-item label="采购单号" prop="orderNo">
              <el-input v-model="formData.orderNo" placeholder="不填则自动生成" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="申请人" prop="applicant">
              <el-input v-model="formData.applicant" placeholder="请输入申请人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商" prop="supplierName">
              <el-input v-model="formData.supplierName" placeholder="请输入供应商" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物料" prop="itemName">
              <el-input v-model="formData.itemName" placeholder="请输入物料名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="formData.quantity" :min="1" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单价" prop="unitPrice">
              <el-input-number v-model="formData.unitPrice" :min="0" :precision="2" :step="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="草稿" :value="0" />
                <el-option label="待审批" :value="1" />
                <el-option label="已审批" :value="2" />
                <el-option label="已作废" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="总额">
              <el-input :model-value="`¥${computedTotalAmount.toFixed(2)}`" readonly />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="采购单详情" width="640px" destroy-on-close>
      <el-descriptions :column="2" border v-if="detailData">
        <el-descriptions-item label="采购单号">{{ detailData.orderNo }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{
          statusText(detailData.status)
          }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ detailData.supplierName }}</el-descriptions-item>
        <el-descriptions-item label="物料">{{ detailData.itemName }}</el-descriptions-item>
        <el-descriptions-item label="数量">{{ detailData.quantity }}</el-descriptions-item>
        <el-descriptions-item label="单价">¥{{ detailData.unitPrice.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="总额">¥{{ detailData.totalAmount.toFixed(2) }}</el-descriptions-item>
        <el-descriptions-item label="申请人">{{ detailData.applicant }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailData.createTime }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailData.updateTime }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{
          detailData.remark || '-'
          }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="approvalStatusVisible"
      :title="approvalStatusData ? `审批状态 - ${approvalStatusData.orderNo}` : '审批状态'" width="760px" destroy-on-close>
      <div v-loading="approvalStatusLoading">
        <el-empty v-if="!approvalStatusData || approvalStatusData.nodes.length === 0" description="暂无审批节点" />
        <el-steps v-else :active="approvalStatusActive" process-status="process" finish-status="success" align-center>
          <el-step v-for="node in approvalStatusData.nodes" :key="node.nodeIndex" :title="node.nodeName">
            <template #description>
              <div class="approval-node-desc">
                <el-tag size="small" :type="nodeStatusTagType(node.nodeStatus)">
                  {{ nodeStatusText(node.nodeStatus) }}
                </el-tag>
                <div class="approval-node-people">
                  审批人：{{ (node.approvalPeopleName || []).join(' / ') || node.roleName || '-' }}
                </div>
                <div v-if="node.actionTime" class="approval-node-time">
                  处理时间：{{ node.actionTime }}
                </div>
              </div>
            </template>
          </el-step>
        </el-steps>
      </div>
      <template #footer>
        <el-button type="primary" @click="approvalStatusVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="approveDialogVisible"
      :title="approveStatusData ? `审批处理 - ${approveStatusData.orderNo}` : '审批处理'" width="760px" destroy-on-close>
      <div v-loading="approveDialogLoading">
        <el-alert title="将基于当前审批规则推进到下一节点；仅当前节点配置的审批人可操作。" type="info" :closable="false" style="margin-bottom: 16px" />
        <el-empty v-if="!approveStatusData || approveStatusData.nodes.length === 0" description="暂无审批节点" />
        <el-steps v-else :active="approveStatusActive" process-status="process" finish-status="success" align-center>
          <el-step v-for="node in approveStatusData.nodes" :key="node.nodeIndex" :title="node.nodeName">
            <template #description>
              <div class="approval-node-desc">
                <el-tag size="small" :type="nodeStatusTagType(node.nodeStatus)">
                  {{ nodeStatusText(node.nodeStatus) }}
                </el-tag>
                <div class="approval-node-people">
                  审批人：{{ (node.approvalPeopleName || []).join(' / ') || node.roleName || '-' }}
                </div>
                <div v-if="node.actionTime" class="approval-node-time">
                  处理时间：{{ node.actionTime }}
                </div>
              </div>
            </template>
          </el-step>
        </el-steps>
      </div>
      <template #footer>
        <el-button @click="approveDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="approveSubmitting" :disabled="!canApproveCurrentNode"
          @click="handleApproveConfirm">
          通过当前节点
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  approvePurchaseOrderApi,
  cancelPurchaseOrderApi,
  createPurchaseOrderApi,
  deletePurchaseOrderApi,
  getPurchaseOrderApprovalStatusApi,
  pagePurchaseOrderApi,
  submitPurchaseOrderApi,
  updatePurchaseOrderApi,
  type PurchaseOrderApprovalStatus,
  type PurchaseOrderRecord,
} from '@/api/system/purchaseOrder'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface PurchaseQuery {
  keyword: string
  status: number | undefined
}

interface PurchaseFormData {
  id: string
  orderNo: string
  supplierName: string
  itemName: string
  quantity: number
  unitPrice: number
  totalAmount: number
  status: number
  applicant: string
  remark: string
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<PurchaseOrderRecord[]>([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailData = ref<PurchaseOrderRecord | null>(null)
const approvalStatusVisible = ref(false)
const approvalStatusLoading = ref(false)
const approvalStatusData = ref<PurchaseOrderApprovalStatus | null>(null)
const approveDialogVisible = ref(false)
const approveDialogLoading = ref(false)
const approveSubmitting = ref(false)
const approveStatusData = ref<PurchaseOrderApprovalStatus | null>(null)
const approveTargetOrderId = ref('')
const dialogTitle = ref('新增采购单')
const isEditMode = ref(false)
const formRef = ref<FormInstance>()

const query = reactive<PurchaseQuery>({
  keyword: '',
  status: undefined,
})

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0,
})

const formData = reactive<PurchaseFormData>({
  id: '',
  orderNo: '',
  supplierName: '',
  itemName: '',
  quantity: 1,
  unitPrice: 0,
  totalAmount: 0,
  status: 0,
  applicant: '系统管理员',
  remark: '',
})

const computedTotalAmount = computed(() =>
  Number((formData.quantity * formData.unitPrice).toFixed(2)),
)

const formRules: FormRules<PurchaseFormData> = {
  supplierName: [{ required: true, message: '请输入供应商', trigger: 'blur' }],
  itemName: [{ required: true, message: '请输入物料', trigger: 'blur' }],
  applicant: [{ required: true, message: '请输入申请人', trigger: 'blur' }],
}

const isEditable = (status: number) => status === 0 || status === 1
const statusText = (value: number) =>
  ({ 0: '草稿', 1: '待审批', 2: '已审批', 3: '已作废' })[value] || '草稿'
const statusTagType = (value: number): 'info' | 'warning' | 'success' | 'danger' =>
  value === 1 ? 'warning' : value === 2 ? 'success' : value === 3 ? 'danger' : 'info'
const nodeStatusText = (value: number) =>
  ({ 0: '待处理', 1: '待审批', 2: '已通过', 4: '已终止' })[value] || '未知'
const nodeStatusTagType = (value: number): 'info' | 'warning' | 'success' | 'danger' =>
  value === 1 ? 'warning' : value === 2 ? 'success' : value === 4 ? 'danger' : 'info'

const approvalStatusActive = computed(() => {
  if (!approvalStatusData.value) return 0
  const firstPendingIndex = approvalStatusData.value.nodes.findIndex(
    (item) => item.nodeStatus === 1,
  )
  if (firstPendingIndex >= 0) return firstPendingIndex
  const doneCount = approvalStatusData.value.nodes.filter((item) => item.nodeStatus === 2).length
  return doneCount
})

const approveStatusActive = computed(() => {
  if (!approveStatusData.value) return 0
  const firstPendingIndex = approveStatusData.value.nodes.findIndex((item) => item.nodeStatus === 1)
  if (firstPendingIndex >= 0) return firstPendingIndex
  const doneCount = approveStatusData.value.nodes.filter((item) => item.nodeStatus === 2).length
  return doneCount
})

const canApproveCurrentNode = computed(() =>
  Boolean(approveStatusData.value?.nodes.some((item) => item.nodeStatus === 1)),
)

const resetForm = () => {
  formData.id = ''
  formData.orderNo = ''
  formData.supplierName = ''
  formData.itemName = ''
  formData.quantity = 1
  formData.unitPrice = 0
  formData.totalAmount = 0
  formData.status = 0
  formData.applicant = '系统管理员'
  formData.remark = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pagePurchaseOrderApi({
      current: pagination.current,
      size: pagination.size,
      keyword: query.keyword || undefined,
      status: query.status,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
      ElMessage.error(res.msg || '采购单数据加载失败')
    }
  } catch (error) {
    console.error('加载采购单数据失败:', error)
    tableData.value = []
    pagination.total = 0
    ElMessage.error('加载失败，请检查本地后端服务')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}

const handleReset = () => {
  query.keyword = ''
  query.status = undefined
  pagination.current = 1
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.size = size
  pagination.current = 1
  loadData()
}

const handleCurrentChange = (current: number) => {
  pagination.current = current
  loadData()
}

const openCreateDialog = () => {
  isEditMode.value = false
  dialogTitle.value = '新增采购单'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: PurchaseOrderRecord) => {
  isEditMode.value = true
  dialogTitle.value = '编辑采购单'
  formData.id = row.id
  formData.orderNo = row.orderNo
  formData.supplierName = row.supplierName
  formData.itemName = row.itemName
  formData.quantity = row.quantity
  formData.unitPrice = row.unitPrice
  formData.totalAmount = row.totalAmount
  formData.status = row.status
  formData.applicant = row.applicant
  formData.remark = row.remark
  dialogVisible.value = true
}

const openDetailDialog = (row: PurchaseOrderRecord) => {
  detailData.value = row
  detailDialogVisible.value = true
}

const fetchApprovalStatus = async (orderId: string) => {
  const res = await getPurchaseOrderApprovalStatusApi(orderId)
  if ((res.code === 0 || res.code === 200) && res.data) {
    return res.data
  }
  ElMessage.warning(res.msg || '获取审批状态失败')
  return null
}

const openApprovalStatusDialog = async (row: PurchaseOrderRecord) => {
  approvalStatusVisible.value = true
  approvalStatusLoading.value = true
  try {
    approvalStatusData.value = await fetchApprovalStatus(row.id)
  } catch (error) {
    approvalStatusData.value = null
    console.error('获取审批状态失败:', error)
    ElMessage.error('获取审批状态失败，请稍后重试')
  } finally {
    approvalStatusLoading.value = false
  }
}

const openApproveDialog = async (row: PurchaseOrderRecord) => {
  approveDialogVisible.value = true
  approveDialogLoading.value = true
  approveStatusData.value = null
  approveTargetOrderId.value = row.id
  try {
    approveStatusData.value = await fetchApprovalStatus(row.id)
  } catch (error) {
    console.error('加载审批处理弹窗失败:', error)
    ElMessage.error('加载审批状态失败，请稍后重试')
  } finally {
    approveDialogLoading.value = false
  }
}

const handleApproveConfirm = async () => {
  if (!approveTargetOrderId.value) return
  if (!canApproveCurrentNode.value) {
    ElMessage.warning('当前没有可处理的审批节点')
    return
  }

  approveSubmitting.value = true
  try {
    const res = await approvePurchaseOrderApi(approveTargetOrderId.value)
    if (res.code !== 0 && res.code !== 200) {
      ElMessage.warning(res.msg || '审批失败')
      return
    }
    ElMessage.success(res.msg || '审批通过')
    approveDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('审批失败:', error)
    ElMessage.error('审批失败，请稍后重试')
  } finally {
    approveSubmitting.value = false
  }
}

const submitFormRequest = async () => {
  const payload = {
    orderNo: formData.orderNo,
    supplierName: formData.supplierName,
    itemName: formData.itemName,
    quantity: formData.quantity,
    unitPrice: formData.unitPrice,
    totalAmount: computedTotalAmount.value,
    status: formData.status,
    applicant: formData.applicant,
    remark: formData.remark,
  }
  if (isEditMode.value) {
    return updatePurchaseOrderApi(formData.id, payload)
  }
  return createPurchaseOrderApi(payload)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    const res = await submitFormRequest()
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success(isEditMode.value ? '更新成功' : '新增成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交采购单失败:', error)
  } finally {
    submitLoading.value = false
  }
}

interface FlowActionResult {
  code: number
  msg?: string
}

const runFlowAction = async (message: string, action: () => Promise<FlowActionResult>) => {
  try {
    const res = await action()
    if (res.code !== 0 && res.code !== 200) {
      if (res.msg) {
        ElMessage.warning(res.msg)
      }
      return
    }
    ElMessage.success(res.msg || message)
    loadData()
  } catch (error) {
    console.error(`${message}失败:`, error)
  }
}

const handleSubmitFlow = (id: string) => runFlowAction('提交成功', () => submitPurchaseOrderApi(id))
const handleCancelFlow = (id: string) => runFlowAction('作废成功', () => cancelPurchaseOrderApi(id))

const handleCommand = (command: string, row: PurchaseOrderRecord) => {
  if (command === 'cancel') {
    handleCancelFlow(row.id)
  } else if (command === 'delete') {
    handleDelete(row)
  }
}

const handleDelete = async (row: PurchaseOrderRecord) => {
  try {
    await ElMessageBox.confirm(`确认删除采购单「${row.orderNo}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    const res = await deletePurchaseOrderApi(row.id)
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除采购单失败:', error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 18px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.table-container {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.approval-node-desc {
  margin-top: 8px;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.approval-node-people,
.approval-node-time {
  margin-top: 6px;
  line-height: 1.4;
}
</style>
