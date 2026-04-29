<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>回款跟踪</h2>
          <div class="page-description">登记与确认合同回款。</div>
        </div>
      </div>
    </div>
    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="合同"
            ><el-select
              v-model="query.contractId"
              clearable
              filterable
              style="width: 260px"
              placeholder="选择合同"
              ><el-option
                v-for="item in contractOptions"
                :key="item.id"
                :label="`${item.contractNo} / ${item.customerName}`"
                :value="item.id" /></el-select
          ></el-form-item>
          <el-form-item label="状态"
            ><el-select v-model="query.status" clearable style="width: 120px"
              ><el-option label="待确认" :value="0" /><el-option
                label="已确认"
                :value="1" /></el-select
          ></el-form-item>
          <el-form-item
            ><el-button type="primary" @click="handleSearch">查询</el-button
            ><el-button @click="handleReset">重置</el-button></el-form-item
          >
        </el-form>
        <div style="display: flex; gap: 8px">
          <el-button @click="handleExport">导出</el-button>
          <el-button type="primary" @click="openCreateDialog">新增回款</el-button>
        </div>
      </div>
      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="paymentNo" label="回款单号" min-width="170" />
          <el-table-column prop="contractNo" label="合同编号" min-width="170" />
          <el-table-column prop="customerName" label="客户" min-width="150" />
          <el-table-column prop="paymentAmount" label="回款金额" width="120" align="right" />
          <el-table-column prop="paymentDate" label="回款日期" width="120" />
          <el-table-column prop="paymentMethod" label="方式" width="100" align="center"
            ><template #default="{ row }">{{
              paymentMethodText(row.paymentMethod)
            }}</template></el-table-column
          >
          <el-table-column prop="status" label="状态" width="100" align="center"
            ><template #default="{ row }"
              ><el-tag :type="row.status === 1 ? 'success' : 'warning'">{{
                row.status === 1 ? '已确认' : '待确认'
              }}</el-tag></template
            ></el-table-column
          >
          <el-table-column label="操作" width="160" align="center"
            ><template #default="{ row }"
              ><el-button v-if="row.status === 0" type="success" link @click="handleConfirm(row)"
                >确认</el-button
              ><el-button type="danger" link @click="handleDelete(row)">删除</el-button></template
            ></el-table-column
          >
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

    <el-dialog v-model="dialogVisible" title="新增回款" width="680px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-form-item label="合同" prop="contractId"
          ><el-select v-model="formData.contractId" filterable style="width: 100%"
            ><el-option
              v-for="item in contractOptions"
              :key="item.id"
              :label="`${item.contractNo} / ${item.customerName}`"
              :value="item.id" /></el-select
        ></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"
            ><el-form-item label="回款金额" prop="paymentAmount"
              ><el-input-number
                v-model="formData.paymentAmount"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="回款日期"
              ><el-date-picker
                v-model="formData.paymentDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="回款方式"
              ><el-select v-model="formData.paymentMethod" style="width: 100%"
                ><el-option label="转账" :value="1" /><el-option
                  label="支票"
                  :value="2" /><el-option label="现金" :value="3" /><el-option
                  label="承兑"
                  :value="4" /></el-select></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="付款方"><el-input v-model="formData.payerName" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="备注"
          ><el-input v-model="formData.remark" type="textarea" :rows="2"
        /></el-form-item>
      </el-form>
      <template #footer
        ><el-button @click="dialogVisible = false">取消</el-button
        ><el-button type="primary" :loading="submitLoading" @click="handleSubmit"
          >确定</el-button
        ></template
      >
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  pagePaymentApi,
  createPaymentApi,
  confirmPaymentApi,
  deletePaymentApi,
  type PaymentRecord,
  type PaymentSaveDto,
} from '@/api/system/payment'
import { pageContractApi, type ContractRecord } from '@/api/system/contract'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  contractId: string
  status: number | undefined
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<PaymentRecord[]>([])
const contractOptions = ref<ContractRecord[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ contractId: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<PaymentSaveDto>({
  contractId: '',
  paymentAmount: 0,
  paymentDate: '',
  paymentMethod: 1,
  payerName: '',
  remark: '',
})

const formRules: FormRules<PaymentSaveDto> = {
  contractId: [{ required: true, message: '请选择合同', trigger: 'change' }],
  paymentAmount: [{ required: true, message: '请输入回款金额', trigger: 'blur' }],
}

const paymentMethodText = (v: number): string =>
  ({ 1: '转账', 2: '支票', 3: '现金', 4: '承兑' })[v] || '转账'

const loadContracts = async () => {
  const res = await pageContractApi({ current: 1, size: 1000 })
  if ((res.code === 0 || res.code === 200) && res.data) {
    contractOptions.value = res.data.records || []
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pagePaymentApi({
      current: pagination.current,
      size: pagination.size,
      contractId: query.contractId || undefined,
      status: query.status,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
      ElMessage.error(res.msg || '获取回款失败')
    }
  } catch (error) {
    console.error('获取回款失败:', error)
    ElMessage.error('获取回款失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}
const handleReset = () => {
  query.contractId = ''
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
  formData.contractId = ''
  formData.paymentAmount = 0
  formData.paymentDate = ''
  formData.paymentMethod = 1
  formData.payerName = ''
  formData.remark = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const res = await createPaymentApi(formData)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('新增成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (error) {
    console.error('新增回款失败:', error)
    ElMessage.error('新增回款失败')
  } finally {
    submitLoading.value = false
  }
}

const handleConfirm = async (row: PaymentRecord) => {
  const res = await confirmPaymentApi(row.id)
  if (res.code === 0 || res.code === 200) {
    ElMessage.success('确认成功')
    loadData()
  } else {
    ElMessage.error(res.msg || '确认失败')
  }
}

const handleDelete = async (row: PaymentRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除回款单“${row.paymentNo}”吗？`, '提示', { type: 'warning' })
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('删除操作未完成')
    return
  }
  const res = await deletePaymentApi(row.id)
  if (res.code === 0 || res.code === 200) {
    ElMessage.success('删除成功')
    loadData()
  } else {
    ElMessage.error(res.msg || '删除失败')
  }
}

const handleExport = async () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
  const params = new URLSearchParams()
  if (query.contractId) params.append('contractId', query.contractId)
  if (query.status !== undefined) params.append('status', String(query.status))
  const url = `${baseUrl}/local/payments/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '回款列表.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出回款失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(async () => {
  await loadContracts()
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
