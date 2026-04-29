<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>生产工单管理</h2>
          <div class="page-description">生产工单建单、审批、执行状态跟踪。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="工单号/合同号/客户/产品"
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部" style="width: 140px">
              <el-option label="草稿" :value="0" />
              <el-option label="待审批" :value="1" />
              <el-option label="已审批" :value="2" />
              <el-option label="生产中" :value="3" />
              <el-option label="待入库" :value="4" />
              <el-option label="已完结" :value="5" />
              <el-option label="已驳回" :value="6" />
              <el-option label="已作废" :value="7" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <div style="display: flex; gap: 8px">
          <el-button @click="handleExport">导出</el-button>
          <el-button type="primary" @click="openCreateDialog">新增工单</el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="workOrderNo" label="工单号" min-width="170" />
          <el-table-column prop="contractNo" label="合同号" min-width="150" />
          <el-table-column prop="customerName" label="客户" min-width="120" />
          <el-table-column prop="productName" label="产品" min-width="160" />
          <el-table-column prop="planQuantity" label="计划数" width="90" align="right" />
          <el-table-column prop="qualifiedQuantity" label="合格数" width="90" align="right" />
          <el-table-column prop="inboundQuantity" label="入库数" width="90" align="right" />
          <el-table-column label="进度" width="180">
            <template #default="{ row }">
              <el-progress
                :percentage="
                  row.planQuantity > 0
                    ? Number(((row.qualifiedQuantity * 100) / row.planQuantity).toFixed(2))
                    : 0
                "
                :stroke-width="12"
              />
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" min-width="170" />
          <el-table-column label="操作" width="360" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button
                type="success"
                link
                @click="handleSubmitApproval(row)"
                v-if="row.status === 0"
                >提交</el-button
              >
              <el-button type="success" link @click="handleApprove(row)" v-if="row.status === 1"
                >通过</el-button
              >
              <el-button type="warning" link @click="handleReject(row)" v-if="row.status === 1"
                >驳回</el-button
              >
              <el-button
                type="warning"
                link
                @click="handleCancel(row)"
                v-if="[0, 1, 6].includes(row.status)"
                >作废</el-button
              >
              <el-button
                type="danger"
                link
                @click="handleDelete(row)"
                v-if="[0, 6, 7].includes(row.status)"
                >删除</el-button
              >
              <el-button
                type="primary"
                link
                @click="goReport(row)"
                v-if="[2, 3, 4].includes(row.status)"
                >报工</el-button
              >
              <el-button
                type="primary"
                link
                @click="goInbound(row)"
                v-if="[3, 4, 5].includes(row.status)"
                >入库</el-button
              >
              <el-button type="info" link @click="showApprovalStatus(row)">审批流</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="760px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="12"
            ><el-form-item label="工单号"
              ><el-input v-model="formData.workOrderNo" placeholder="留空自动生成" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="合同号"><el-input v-model="formData.contractNo" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="客户"><el-input v-model="formData.customerName" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="产品编码"
              ><el-input v-model="formData.productCode" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="产品名称" prop="productName"
              ><el-input v-model="formData.productName" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="计划数量" prop="planQuantity"
              ><el-input-number
                v-model="formData.planQuantity"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="优先级"
              ><el-select v-model="formData.priority" style="width: 100%"
                ><el-option label="高" :value="1" /><el-option label="中" :value="2" /><el-option
                  label="低"
                  :value="3" /></el-select></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="申请人"><el-input v-model="formData.applicant" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="开始日期"
              ><el-date-picker
                v-model="formData.plannedStartDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="结束日期"
              ><el-date-picker
                v-model="formData.plannedEndDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="备注"
          ><el-input v-model="formData.remark" type="textarea" :rows="2"
        /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="approvalVisible" title="审批状态" width="620px" destroy-on-close>
      <el-timeline>
        <el-timeline-item
          v-for="item in approvalNodes"
          :key="item.nodeIndex"
          :timestamp="item.actionTime || `节点${item.nodeIndex}`"
        >
          <div style="display: flex; justify-content: space-between; align-items: center">
            <span>{{ item.nodeName }}</span>
            <el-tag :type="approvalNodeTag(item.nodeStatus)">{{
              approvalNodeText(item.nodeStatus)
            }}</el-tag>
          </div>
          <div style="color: #909399; margin-top: 4px">审批人：{{ item.approverName || '-' }}</div>
        </el-timeline-item>
      </el-timeline>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  approveWorkOrderApi,
  cancelWorkOrderApi,
  createWorkOrderApi,
  deleteWorkOrderApi,
  getWorkOrderApprovalStatusApi,
  pageWorkOrderApi,
  rejectWorkOrderApi,
  submitWorkOrderApi,
  updateWorkOrderApi,
  type WorkOrderRecord,
  type WorkOrderSaveDto,
} from '@/api/system/workOrder'
import type { WorkOrderApprovalNode } from '@/types/system/workOrder'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  keyword: string
  status: number | undefined
}

interface FormData extends WorkOrderSaveDto {
  id: string
}

const router = useRouter()
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<WorkOrderRecord[]>([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<FormData>({
  id: '',
  workOrderNo: '',
  contractId: '',
  contractNo: '',
  customerName: '',
  productId: '',
  productCode: '',
  productName: '',
  planQuantity: 0,
  status: 0,
  priority: 2,
  plannedStartDate: '',
  plannedEndDate: '',
  applicant: '',
  remark: '',
})
const dialogTitle = ref('新增工单')

const approvalVisible = ref(false)
const approvalNodes = ref<WorkOrderApprovalNode[]>([])

const formRules: FormRules<FormData> = {
  productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  planQuantity: [{ required: true, message: '请输入计划数量', trigger: 'blur' }],
}

const statusText = (value: number): string =>
  ({
    0: '草稿',
    1: '待审批',
    2: '已审批',
    3: '生产中',
    4: '待入库',
    5: '已完结',
    6: '已驳回',
    7: '已作废',
  })[value] || '草稿'
const statusTagType = (value: number): 'info' | 'warning' | 'success' | 'danger' =>
  (({
    0: 'info',
    1: 'warning',
    2: 'success',
    3: 'success',
    4: 'warning',
    5: 'success',
    6: 'danger',
    7: 'danger',
  })[value] as 'info' | 'warning' | 'success' | 'danger') || 'info'

const approvalNodeText = (value: number): string =>
  ({ 0: '待处理', 1: '审批中', 2: '已通过', 3: '已驳回', 4: '跳过' })[value] || '待处理'
const approvalNodeTag = (value: number): 'info' | 'warning' | 'success' | 'danger' =>
  (({ 0: 'info', 1: 'warning', 2: 'success', 3: 'danger', 4: 'info' })[value] as
    | 'info'
    | 'warning'
    | 'success'
    | 'danger') || 'info'

const resetForm = () => {
  formData.id = ''
  formData.workOrderNo = ''
  formData.contractId = ''
  formData.contractNo = ''
  formData.customerName = ''
  formData.productId = ''
  formData.productCode = ''
  formData.productName = ''
  formData.planQuantity = 0
  formData.status = 0
  formData.priority = 2
  formData.plannedStartDate = ''
  formData.plannedEndDate = ''
  formData.applicant = ''
  formData.remark = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageWorkOrderApi({
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
      ElMessage.error(res.msg || '获取工单失败')
    }
  } catch (error) {
    console.error('获取工单失败:', error)
    ElMessage.error('获取工单失败')
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

const handleExport = async () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
  const params = new URLSearchParams()
  if (query.keyword) params.append('keyword', query.keyword)
  if (query.status !== undefined) params.append('status', String(query.status))
  const url = `${baseUrl}/local/work-orders/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '生产工单列表.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出工单失败:', error)
    ElMessage.error('导出失败')
  }
}

const openCreateDialog = () => {
  isEditMode.value = false
  dialogTitle.value = '新增工单'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: WorkOrderRecord) => {
  if (![0, 6, 7].includes(row.status)) {
    ElMessage.warning('当前状态不允许编辑')
    return
  }
  isEditMode.value = true
  dialogTitle.value = '编辑工单'
  formData.id = row.id
  formData.workOrderNo = row.workOrderNo
  formData.contractId = row.contractId
  formData.contractNo = row.contractNo
  formData.customerName = row.customerName
  formData.productId = row.productId
  formData.productCode = row.productCode
  formData.productName = row.productName
  formData.planQuantity = row.planQuantity
  formData.status = row.status
  formData.priority = row.priority
  formData.plannedStartDate = row.plannedStartDate
  formData.plannedEndDate = row.plannedEndDate
  formData.applicant = row.applicant
  formData.remark = row.remark
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const payload: WorkOrderSaveDto = {
      workOrderNo: formData.workOrderNo || undefined,
      contractId: formData.contractId,
      contractNo: formData.contractNo,
      customerName: formData.customerName,
      productId: formData.productId,
      productCode: formData.productCode,
      productName: formData.productName,
      planQuantity: formData.planQuantity,
      status: formData.status,
      priority: formData.priority,
      plannedStartDate: formData.plannedStartDate,
      plannedEndDate: formData.plannedEndDate,
      applicant: formData.applicant,
      remark: formData.remark,
    }
    const res = isEditMode.value
      ? await updateWorkOrderApi(formData.id, payload)
      : await createWorkOrderApi(payload)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isEditMode.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存工单失败:', error)
    ElMessage.error('保存工单失败')
  } finally {
    submitLoading.value = false
  }
}

const handleSubmitApproval = async (row: WorkOrderRecord) => {
  try {
    const res = await submitWorkOrderApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('提交成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '提交失败')
    }
  } catch (error) {
    console.error('提交审批失败:', error)
    ElMessage.error('提交审批失败')
  }
}

const handleApprove = async (row: WorkOrderRecord) => {
  try {
    const res = await approveWorkOrderApi(row.id)
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

const handleReject = async (row: WorkOrderRecord) => {
  let remark = ''
  try {
    const promptRes = await ElMessageBox.prompt('请输入驳回原因（可选）', '驳回工单', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      inputPlaceholder: '驳回原因',
    })
    remark = promptRes.value || ''
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('驳回操作未完成')
    return
  }
  try {
    const res = await rejectWorkOrderApi(row.id, remark)
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

const handleCancel = async (row: WorkOrderRecord) => {
  try {
    await ElMessageBox.confirm(`确定作废工单“${row.workOrderNo}”吗？`, '提示', { type: 'warning' })
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('作废操作未完成')
    return
  }
  try {
    const res = await cancelWorkOrderApi(row.id)
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

const handleDelete = async (row: WorkOrderRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除工单“${row.workOrderNo}”吗？`, '提示', { type: 'warning' })
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('删除操作未完成')
    return
  }
  try {
    const res = await deleteWorkOrderApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      if (tableData.value.length === 1 && pagination.current > 1) pagination.current -= 1
      loadData()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

const showApprovalStatus = async (row: WorkOrderRecord) => {
  try {
    const res = await getWorkOrderApprovalStatusApi(row.id)
    if ((res.code === 0 || res.code === 200) && res.data) {
      approvalNodes.value = res.data.nodes || []
      approvalVisible.value = true
    } else {
      ElMessage.error(res.msg || '获取审批状态失败')
    }
  } catch (error) {
    console.error('获取审批状态失败:', error)
    ElMessage.error('获取审批状态失败')
  }
}

const goReport = (row: WorkOrderRecord) => {
  router.push({ path: '/production/work-reports', query: { workOrderId: row.id } })
}

const goInbound = (row: WorkOrderRecord) => {
  router.push({ path: '/production/work-inbounds', query: { workOrderId: row.id } })
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
