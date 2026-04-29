<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>佣金计算</h2>
          <div class="page-description">按回款计算佣金并管理发放状态。</div>
        </div>
      </div>
    </div>
    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="销售员"
            ><el-input v-model="query.salespersonName" clearable style="width: 180px"
          /></el-form-item>
          <el-form-item label="状态"
            ><el-select v-model="query.status" clearable style="width: 120px"
              ><el-option label="待发放" :value="0" /><el-option
                label="已发放"
                :value="1" /></el-select
          ></el-form-item>
          <el-form-item
            ><el-button type="primary" @click="handleSearch">查询</el-button
            ><el-button @click="handleReset">重置</el-button></el-form-item
          >
        </el-form>
        <div style="display: flex; gap: 8px">
          <el-button @click="handleExport">导出</el-button>
          <el-button type="primary" @click="openCalcDialog">计算佣金</el-button>
        </div>
      </div>
      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="contractNo" label="合同编号" min-width="170" />
          <el-table-column prop="customerName" label="客户" min-width="140" />
          <el-table-column prop="salespersonName" label="销售员" min-width="110" />
          <el-table-column prop="paymentAmount" label="回款金额" width="120" align="right" />
          <el-table-column prop="commissionRate" label="佣金比例(%)" width="120" align="right" />
          <el-table-column prop="commissionAmount" label="佣金金额" width="120" align="right" />
          <el-table-column prop="status" label="状态" width="100" align="center"
            ><template #default="{ row }"
              ><el-tag :type="row.status === 1 ? 'success' : 'warning'">{{
                row.status === 1 ? '已发放' : '待发放'
              }}</el-tag></template
            ></el-table-column
          >
          <el-table-column label="操作" width="160" align="center"
            ><template #default="{ row }"
              ><el-button v-if="row.status === 0" type="success" link @click="handlePay(row)"
                >标记发放</el-button
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

    <el-dialog v-model="dialogVisible" title="计算佣金" width="660px" destroy-on-close>
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
            ><el-form-item label="销售员" prop="salespersonName"
              ><el-input v-model="formData.salespersonName" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="销售ID"
              ><el-input v-model="formData.salespersonId" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="佣金比例" prop="commissionRate"
              ><el-input-number
                v-model="formData.commissionRate"
                :min="0"
                :max="100"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="备注"
          ><el-input v-model="formData.remark" type="textarea" :rows="2"
        /></el-form-item>
      </el-form>
      <template #footer
        ><el-button @click="dialogVisible = false">取消</el-button
        ><el-button type="primary" :loading="submitLoading" @click="handleCalc"
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
  pageCommissionApi,
  calculateCommissionApi,
  payCommissionApi,
  deleteCommissionApi,
  type CommissionRecord,
} from '@/api/system/commission'
import { pageContractApi, type ContractRecord } from '@/api/system/contract'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  salespersonName: string
  status: number | undefined
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<CommissionRecord[]>([])
const contractOptions = ref<ContractRecord[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ salespersonName: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive({
  contractId: '',
  salespersonId: '',
  salespersonName: '',
  commissionRate: 5,
  remark: '',
})

const formRules: FormRules = {
  contractId: [{ required: true, message: '请选择合同', trigger: 'change' }],
  salespersonName: [{ required: true, message: '请输入销售员名称', trigger: 'blur' }],
}

const loadContracts = async () => {
  const res = await pageContractApi({ current: 1, size: 1000 })
  if ((res.code === 0 || res.code === 200) && res.data) {
    contractOptions.value = res.data.records || []
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageCommissionApi({
      current: pagination.current,
      size: pagination.size,
      status: query.status,
      salespersonName: query.salespersonName || undefined,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
      ElMessage.error(res.msg || '获取佣金失败')
    }
  } catch (error) {
    console.error('获取佣金失败:', error)
    ElMessage.error('获取佣金失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  loadData()
}
const handleReset = () => {
  query.salespersonName = ''
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

const openCalcDialog = () => {
  formData.contractId = ''
  formData.salespersonId = ''
  formData.salespersonName = ''
  formData.commissionRate = 5
  formData.remark = ''
  dialogVisible.value = true
}

const handleCalc = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const res = await calculateCommissionApi(formData.contractId, {
      salespersonId: formData.salespersonId,
      salespersonName: formData.salespersonName,
      commissionRate: formData.commissionRate,
      remark: formData.remark,
    })
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('计算成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '计算失败')
    }
  } catch (error) {
    console.error('计算佣金失败:', error)
    ElMessage.error('计算佣金失败')
  } finally {
    submitLoading.value = false
  }
}

const handlePay = async (row: CommissionRecord) => {
  const res = await payCommissionApi(row.id)
  if (res.code === 0 || res.code === 200) {
    ElMessage.success('已标记发放')
    loadData()
  } else {
    ElMessage.error(res.msg || '操作失败')
  }
}

const handleDelete = async (row: CommissionRecord) => {
  try {
    await ElMessageBox.confirm('确定删除该佣金记录吗？', '提示', { type: 'warning' })
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('删除操作未完成')
    return
  }
  const res = await deleteCommissionApi(row.id)
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
  if (query.salespersonName) params.append('salespersonName', query.salespersonName)
  if (query.status !== undefined) params.append('status', String(query.status))
  const url = `${baseUrl}/local/commissions/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '佣金列表.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出佣金失败:', error)
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
