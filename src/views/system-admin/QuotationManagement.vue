<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>报价单管理</h2>
          <div class="page-description">客户报价、明细维护与审批流闭环。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="报价单号/客户名称/联系人"
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部" style="width: 150px">
              <el-option label="草稿" :value="0" />
              <el-option label="待审批" :value="1" />
              <el-option label="已审批" :value="2" />
              <el-option label="已驳回" :value="3" />
              <el-option label="已转合同" :value="4" />
              <el-option label="已作废" :value="5" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="openCreateDialog">新增报价</el-button>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="quoteNo" label="报价单号" min-width="170" />
          <el-table-column prop="customerName" label="客户名称" min-width="160" />
          <el-table-column prop="contactPerson" label="联系人" min-width="120" />
          <el-table-column prop="totalAmount" label="原价金额" width="120" align="right" />
          <el-table-column prop="discountRate" label="折扣(%)" width="100" align="right" />
          <el-table-column prop="finalAmount" label="报价金额" width="120" align="right" />
          <el-table-column prop="status" label="状态" width="110" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" min-width="170" />
          <el-table-column label="操作" width="320" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetailDialog(row)">详情</el-button>
              <el-divider direction="vertical" />
              <el-button link type="info" @click="openApprovalStatus(row)">审批状态</el-button>
              <el-divider direction="vertical" v-if="[0, 3].includes(row.status)" />
              <el-button
                v-if="[0, 3].includes(row.status)"
                link
                type="primary"
                @click="openEditDialog(row)"
              >
                编辑
              </el-button>

              <el-divider direction="vertical" v-if="row.status === 0" />
              <el-button
                v-if="row.status === 0"
                link
                type="success"
                @click="handleSubmitForApproval(row)"
              >
                提交
              </el-button>
              <el-divider direction="vertical" v-if="row.status === 1" />
              <el-button v-if="row.status === 1" link type="success" @click="handleApprove(row)">
                通过
              </el-button>
              <el-divider direction="vertical" v-if="row.status === 1" />
              <el-button v-if="row.status === 1" link type="danger" @click="handleReject(row)">
                驳回
              </el-button>

              <el-divider direction="vertical" />
              <el-dropdown @command="(cmd: string) => handleMoreAction(cmd, row)" trigger="click">
                <span class="more-btn-wrapper">
                  <el-button link type="info" class="more-btn">
                    更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="cancel" :disabled="![0, 1, 3].includes(row.status)"
                      >作废</el-dropdown-item
                    >
                    <el-dropdown-item
                      v-if="row.status === 0"
                      command="delete"
                      divided
                      style="color: var(--el-color-danger)"
                      >删除</el-dropdown-item
                    >
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.current"
            v-model:page-size="pagination.size"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="980px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="客户名称" prop="customerName">
              <el-input v-model="formData.customerName" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="联系人">
              <el-input v-model="formData.contactPerson" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="有效天数">
              <el-input-number v-model="formData.validityDays" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="折扣(%)">
              <el-input-number
                v-model="formData.discountRate"
                :min="0"
                :max="100"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="申请人">
              <el-input v-model="formData.applicant" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="有效截止">
              <el-date-picker
                v-model="formData.validityEndDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="报价明细" prop="items">
          <div class="items-wrapper">
            <div class="items-toolbar">
              <el-button type="primary" link @click="addItem">新增行</el-button>
            </div>
            <el-table :data="formData.items" border size="small" style="width: 100%">
              <el-table-column label="产品编码" min-width="130">
                <template #default="{ row }"><el-input v-model="row.productCode" /></template>
              </el-table-column>
              <el-table-column label="产品名称" min-width="150">
                <template #default="{ row }"><el-input v-model="row.productName" /></template>
              </el-table-column>
              <el-table-column label="规格" min-width="120">
                <template #default="{ row }"><el-input v-model="row.specification" /></template>
              </el-table-column>
              <el-table-column label="单位" width="90">
                <template #default="{ row }"><el-input v-model="row.unit" /></template>
              </el-table-column>
              <el-table-column label="数量" width="110">
                <template #default="{ row }"
                  ><el-input-number
                    v-model="row.quantity"
                    :min="0"
                    :precision="2"
                    style="width: 100%"
                /></template>
              </el-table-column>
              <el-table-column label="单价" width="120">
                <template #default="{ row }"
                  ><el-input-number
                    v-model="row.unitPrice"
                    :min="0"
                    :precision="2"
                    style="width: 100%"
                /></template>
              </el-table-column>
              <el-table-column label="金额" width="120" align="right">
                <template #default="{ row }">{{ calcItemAmount(row) }}</template>
              </el-table-column>
              <el-table-column label="操作" width="80" align="center">
                <template #default="{ $index }">
                  <el-button type="danger" link @click="removeItem($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-form-item>

        <el-form-item label="金额汇总">
          <div class="amount-summary">
            <span>原价：{{ computedTotalAmount.toFixed(2) }}</span>
            <span>折后：{{ computedFinalAmount.toFixed(2) }}</span>
          </div>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" />
        </el-form-item>

        <el-form-item label="业务附件">
          <div class="attachment-wrapper">
            <AttachmentPanel v-if="formData.id" biz-type="quotation" :biz-id="formData.id" />
            <el-alert
              v-else
              title="请先保存报价单，再上传附件。"
              type="info"
              :closable="false"
              show-icon
            />
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="approvalDialogVisible" title="审批状态" width="680px" destroy-on-close>
      <el-steps
        :active="approvalActiveStep"
        finish-status="success"
        process-status="process"
        align-center
      >
        <el-step
          v-for="node in approvalNodes"
          :key="node.nodeIndex"
          :title="node.nodeName"
          :description="approvalNodeDesc(node)"
          :status="approvalNodeStepStatus(node.nodeStatus)"
        />
      </el-steps>
      <template #footer
        ><el-button type="primary" @click="approvalDialogVisible = false">关闭</el-button></template
      >
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import AttachmentPanel from '@/components/common/AttachmentPanel.vue'
import {
  pageQuotationApi,
  getQuotationDetailApi,
  createQuotationApi,
  updateQuotationApi,
  deleteQuotationApi,
  submitQuotationApi,
  approveQuotationApi,
  rejectQuotationApi,
  cancelQuotationApi,
  getQuotationApprovalStatusApi,
  type QuotationRecord,
  type QuotationSaveDto,
} from '@/api/system/quotation'
import type { QuotationNodeStatus } from '@/types/system/quotation'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  keyword: string
  status: number | undefined
}

interface ItemForm {
  productId?: string
  productCode: string
  productName: string
  specification: string
  unit: string
  quantity: number
  unitPrice: number
  amount?: number
  sortOrder?: number
  remark?: string
}

interface FormData {
  id: string
  quoteNo: string
  customerId: string
  customerName: string
  contactPerson: string
  discountRate: number
  validityDays: number
  validityEndDate: string
  status: number
  applicant: string
  version: number
  remark: string
  items: ItemForm[]
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<QuotationRecord[]>([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<FormData>({
  id: '',
  quoteNo: '',
  customerId: '',
  customerName: '',
  contactPerson: '',
  discountRate: 100,
  validityDays: 30,
  validityEndDate: '',
  status: 0,
  applicant: '',
  version: 1,
  remark: '',
  items: [],
})
const dialogTitle = ref('新增报价')

const approvalDialogVisible = ref(false)
const approvalNodes = ref<QuotationNodeStatus[]>([])
const approvalActiveStep = ref(0)

const formRules: FormRules<FormData> = {
  customerName: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
}

const statusText = (value: number) => {
  return (
    {
      0: '草稿',
      1: '待审批',
      2: '已审批',
      3: '已驳回',
      4: '已转合同',
      5: '已作废',
    }[value] || '草稿'
  )
}

const statusTagType = (value: number): 'info' | 'warning' | 'success' | 'danger' => {
  return (
    (
      { 0: 'info', 1: 'warning', 2: 'success', 3: 'danger', 4: 'success', 5: 'info' } as Record<
        number,
        'info' | 'warning' | 'success' | 'danger'
      >
    )[value] || 'info'
  )
}

const calcItemAmount = (item: ItemForm): number => {
  return Number((item.quantity * item.unitPrice).toFixed(2))
}

const computedTotalAmount = computed(() => {
  return formData.items.reduce((sum, item) => sum + calcItemAmount(item), 0)
})

const computedFinalAmount = computed(() => {
  return Number(((computedTotalAmount.value * formData.discountRate) / 100).toFixed(2))
})

const defaultItem = (): ItemForm => ({
  productCode: '',
  productName: '',
  specification: '',
  unit: 'pcs',
  quantity: 1,
  unitPrice: 0,
})

const resetForm = () => {
  formData.id = ''
  formData.quoteNo = ''
  formData.customerId = ''
  formData.customerName = ''
  formData.contactPerson = ''
  formData.discountRate = 100
  formData.validityDays = 30
  formData.validityEndDate = ''
  formData.status = 0
  formData.applicant = ''
  formData.version = 1
  formData.remark = ''
  formData.items = [defaultItem()]
}

const toSaveDto = (): QuotationSaveDto => ({
  quoteNo: formData.quoteNo || undefined,
  customerId: formData.customerId,
  customerName: formData.customerName,
  contactPerson: formData.contactPerson,
  discountRate: formData.discountRate,
  validityDays: formData.validityDays,
  validityEndDate: formData.validityEndDate,
  status: formData.status,
  applicant: formData.applicant,
  version: formData.version,
  remark: formData.remark,
  items: formData.items.map((item, index) => ({
    ...item,
    amount: calcItemAmount(item),
    sortOrder: index + 1,
  })),
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageQuotationApi({
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
      ElMessage.error(res.msg || '获取报价单失败')
    }
  } catch (error) {
    console.error('获取报价单失败:', error)
    ElMessage.error('获取报价单失败')
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
  dialogTitle.value = '新增报价'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = async (row: QuotationRecord) => {
  if (![0, 3].includes(row.status)) {
    ElMessage.warning('仅草稿/已驳回状态可编辑')
    return
  }
  isEditMode.value = true
  dialogTitle.value = '编辑报价'
  const res = await getQuotationDetailApi(row.id)
  if (!(res.code === 0 || res.code === 200) || !res.data) {
    ElMessage.error(res.msg || '获取详情失败')
    return
  }
  const detail = res.data
  formData.id = detail.id
  formData.quoteNo = detail.quoteNo
  formData.customerId = detail.customerId
  formData.customerName = detail.customerName
  formData.contactPerson = detail.contactPerson
  formData.discountRate = detail.discountRate
  formData.validityDays = detail.validityDays
  formData.validityEndDate = detail.validityEndDate
  formData.status = detail.status
  formData.applicant = detail.applicant
  formData.version = detail.version
  formData.remark = detail.remark
  formData.items = (detail.items || []).map((item) => ({
    productId: item.productId,
    productCode: item.productCode,
    productName: item.productName,
    specification: item.specification,
    unit: item.unit,
    quantity: item.quantity,
    unitPrice: item.unitPrice,
    amount: item.amount,
    sortOrder: item.sortOrder,
    remark: item.remark,
  }))
  if (formData.items.length === 0) formData.items = [defaultItem()]
  dialogVisible.value = true
}

const openDetailDialog = (row: QuotationRecord) => {
  openApprovalStatus(row)
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  if (formData.items.length === 0) {
    ElMessage.warning('请至少填写一条报价明细')
    return
  }
  submitLoading.value = true
  try {
    const payload = toSaveDto()
    const res = isEditMode.value
      ? await updateQuotationApi(formData.id, payload)
      : await createQuotationApi(payload)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isEditMode.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存报价失败:', error)
    ElMessage.error('保存报价失败')
  } finally {
    submitLoading.value = false
  }
}

const handleSubmitForApproval = async (row: QuotationRecord) => {
  try {
    const res = await submitQuotationApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('提交审批成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '提交审批失败')
    }
  } catch (error) {
    console.error('提交审批失败:', error)
    ElMessage.error('提交审批失败')
  }
}

const handleApprove = async (row: QuotationRecord) => {
  try {
    const res = await approveQuotationApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('审批通过')
      loadData()
    } else {
      ElMessage.error(res.msg || '审批失败')
    }
  } catch (error) {
    console.error('审批失败:', error)
    ElMessage.error('审批失败')
  }
}

const handleReject = async (row: QuotationRecord) => {
  try {
    const res = await rejectQuotationApi(row.id, '驳回')
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('已驳回')
      loadData()
    } else {
      ElMessage.error(res.msg || '驳回失败')
    }
  } catch (error) {
    console.error('驳回失败:', error)
    ElMessage.error('驳回失败')
  }
}

const openApprovalStatus = async (row: QuotationRecord) => {
  try {
    const res = await getQuotationApprovalStatusApi(row.id)
    if ((res.code === 0 || res.code === 200) && res.data) {
      approvalNodes.value = res.data.nodes || []
      const activeIdx = approvalNodes.value.findIndex((node) => node.nodeStatus === 1)
      approvalActiveStep.value = activeIdx >= 0 ? activeIdx : approvalNodes.value.length
      approvalDialogVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取审批状态失败')
    }
  } catch (error) {
    console.error('获取审批状态失败:', error)
    ElMessage.error('获取审批状态失败')
  }
}

const handleDelete = async (row: QuotationRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除报价单“${row.quoteNo}”吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      ElMessage.error('删除操作未完成')
    }
    return
  }
  try {
    const res = await deleteQuotationApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

const handleCancel = async (row: QuotationRecord) => {
  try {
    const res = await cancelQuotationApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('作废成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '作废失败')
    }
  } catch (error) {
    console.error('作废失败:', error)
    ElMessage.error('作废失败')
  }
}

const handleMoreAction = (command: string, row: QuotationRecord) => {
  if (command === 'approval-status') {
    openApprovalStatus(row)
    return
  }
  if (command === 'cancel') {
    handleCancel(row)
    return
  }
  if (command === 'delete') {
    handleDelete(row)
  }
}

const addItem = () => {
  formData.items.push(defaultItem())
}

const removeItem = (index: number) => {
  formData.items.splice(index, 1)
  if (formData.items.length === 0) {
    formData.items.push(defaultItem())
  }
}

const approvalNodeStepStatus = (status: number): 'wait' | 'process' | 'success' | 'error' => {
  if (status === 1) return 'process'
  if (status === 2) return 'success'
  if (status === 3 || status === 4) return 'error'
  return 'wait'
}

const approvalNodeDesc = (node: QuotationNodeStatus): string => {
  if (node.nodeStatus === 1) return '待审批'
  if (node.nodeStatus === 2) return `已通过 ${node.approverName || ''}`.trim()
  if (node.nodeStatus === 3) return '已驳回'
  if (node.nodeStatus === 4) return '已终止'
  return '未开始'
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';

.items-wrapper {
  width: 100%;
}

.items-toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 8px;
}

.amount-summary {
  display: flex;
  gap: 24px;
  color: #303133;
  font-weight: 600;
}

.attachment-wrapper {
  width: 100%;
}

.more-btn-wrapper {
  display: inline-flex;
  align-items: center;
  height: 100%;
  vertical-align: middle;
}

.more-btn {
  display: inline-flex;
  align-items: center;
  padding: 0;
  height: 24px;
  line-height: 24px;
  font-size: 14px;
}

.more-btn :deep(.el-icon--right) {
  margin-left: 2px;
  margin-top: 1px;
}
</style>
