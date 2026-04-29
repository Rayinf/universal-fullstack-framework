<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>合同管理</h2>
          <div class="page-description">报价转合同、合同执行与终止管理。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="合同编号/客户/合同名称"
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部" style="width: 140px">
              <el-option label="待签" :value="0" />
              <el-option label="已签" :value="1" />
              <el-option label="执行中" :value="2" />
              <el-option label="已完结" :value="3" />
              <el-option label="已终止" :value="4" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <div style="display: flex; gap: 8px">
          <el-button @click="handleExport">导出</el-button>
          <el-button @click="handleFromQuotation">从报价转合同</el-button>
          <el-button type="primary" @click="openCreateDialog">新增合同</el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="contractNo" label="合同编号" min-width="170" />
          <el-table-column prop="customerName" label="客户" min-width="150" />
          <el-table-column prop="contractName" label="合同名称" min-width="180" />
          <el-table-column prop="totalAmount" label="合同金额" width="120" align="right" />
          <el-table-column prop="paidAmount" label="已回款" width="120" align="right" />
          <el-table-column label="回款进度" width="180">
            <template #default="{ row }">
              <el-progress
                :percentage="
                  row.totalAmount > 0
                    ? Number(((row.paidAmount * 100) / row.totalAmount).toFixed(2))
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
          <el-table-column label="操作" width="210" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
              <el-button type="warning" link @click="handleTerminate(row)" v-if="row.status !== 4"
                >终止</el-button
              >
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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
            ><el-form-item label="客户名称" prop="customerName"
              ><el-input v-model="formData.customerName" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="合同名称" prop="contractName"
              ><el-input v-model="formData.contractName" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="合同编号"
              ><el-input v-model="formData.contractNo" placeholder="留空自动生成" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="合同金额"
              ><el-input-number
                v-model="formData.totalAmount"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="签订日期"
              ><el-date-picker
                v-model="formData.signedDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="开始日期"
              ><el-date-picker
                v-model="formData.startDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="结束日期"
              ><el-date-picker
                v-model="formData.endDate"
                type="date"
                value-format="YYYY-MM-DD"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="状态"
              ><el-select v-model="formData.status" style="width: 100%"
                ><el-option label="待签" :value="0" /><el-option
                  label="已签"
                  :value="1" /><el-option label="执行中" :value="2" /><el-option
                  label="已完结"
                  :value="3" /><el-option label="已终止" :value="4" /></el-select></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="付款条款"
          ><el-input v-model="formData.paymentTerms" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="备注"
          ><el-input v-model="formData.remark" type="textarea" :rows="2"
        /></el-form-item>
        <el-form-item label="业务附件">
          <div class="attachment-wrapper">
            <AttachmentPanel v-if="formData.id" biz-type="contract" :biz-id="formData.id" />
            <el-alert
              v-else
              title="请先保存合同，再上传附件。"
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
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import AttachmentPanel from '@/components/common/AttachmentPanel.vue'
import {
  pageContractApi,
  createContractApi,
  updateContractApi,
  deleteContractApi,
  terminateContractApi,
  createContractFromQuotationApi,
  type ContractRecord,
  type ContractSaveDto,
} from '@/api/system/contract'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  keyword: string
  status: number | undefined
}

interface FormData extends ContractSaveDto {
  id: string
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ContractRecord[]>([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<FormData>({
  id: '',
  contractNo: '',
  quotationId: '',
  customerId: '',
  customerName: '',
  contractName: '',
  totalAmount: 0,
  signedDate: '',
  startDate: '',
  endDate: '',
  paymentTerms: '',
  status: 0,
  remark: '',
})
const dialogTitle = ref('新增合同')

const formRules: FormRules<FormData> = {
  customerName: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  contractName: [{ required: true, message: '请输入合同名称', trigger: 'blur' }],
}

const statusText = (value: number): string =>
  ({ 0: '待签', 1: '已签', 2: '执行中', 3: '已完结', 4: '已终止' })[value] || '待签'
const statusTagType = (value: number): 'info' | 'warning' | 'success' | 'danger' =>
  (({ 0: 'info', 1: 'warning', 2: 'success', 3: 'success', 4: 'danger' })[value] as
    | 'info'
    | 'warning'
    | 'success'
    | 'danger') || 'info'

const resetForm = () => {
  formData.id = ''
  formData.contractNo = ''
  formData.quotationId = ''
  formData.customerId = ''
  formData.customerName = ''
  formData.contractName = ''
  formData.totalAmount = 0
  formData.signedDate = ''
  formData.startDate = ''
  formData.endDate = ''
  formData.paymentTerms = ''
  formData.status = 0
  formData.remark = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageContractApi({
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
      ElMessage.error(res.msg || '获取合同失败')
    }
  } catch (error) {
    console.error('获取合同失败:', error)
    ElMessage.error('获取合同失败')
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
  dialogTitle.value = '新增合同'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: ContractRecord) => {
  isEditMode.value = true
  dialogTitle.value = '编辑合同'
  formData.id = row.id
  formData.contractNo = row.contractNo
  formData.quotationId = row.quotationId
  formData.customerId = row.customerId
  formData.customerName = row.customerName
  formData.contractName = row.contractName
  formData.totalAmount = row.totalAmount
  formData.signedDate = row.signedDate
  formData.startDate = row.startDate
  formData.endDate = row.endDate
  formData.paymentTerms = row.paymentTerms
  formData.status = row.status
  formData.remark = row.remark
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const payload: ContractSaveDto = {
      contractNo: formData.contractNo || undefined,
      quotationId: formData.quotationId || undefined,
      customerId: formData.customerId,
      customerName: formData.customerName,
      contractName: formData.contractName,
      totalAmount: formData.totalAmount,
      signedDate: formData.signedDate,
      startDate: formData.startDate,
      endDate: formData.endDate,
      paymentTerms: formData.paymentTerms,
      status: formData.status,
      remark: formData.remark,
    }
    const res = isEditMode.value
      ? await updateContractApi(formData.id, payload)
      : await createContractApi(payload)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isEditMode.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存合同失败:', error)
    ElMessage.error('保存合同失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: ContractRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除合同“${row.contractNo}”吗？`, '提示', { type: 'warning' })
  } catch (error) {
    if (!isMessageBoxCancel(error)) ElMessage.error('删除操作未完成')
    return
  }
  const res = await deleteContractApi(row.id)
  if (res.code === 0 || res.code === 200) {
    ElMessage.success('删除成功')
    loadData()
  } else {
    ElMessage.error(res.msg || '删除失败')
  }
}

const handleTerminate = async (row: ContractRecord) => {
  const res = await terminateContractApi(row.id, '手动终止')
  if (res.code === 0 || res.code === 200) {
    ElMessage.success('终止成功')
    loadData()
  } else {
    ElMessage.error(res.msg || '终止失败')
  }
}

const handleFromQuotation = async () => {
  try {
    const result = await ElMessageBox.prompt('请输入已审批通过的报价单ID', '从报价转合同', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /.+/,
      inputErrorMessage: '报价单ID不能为空',
    })
    const quotationId = result.value.trim()
    const res = await createContractFromQuotationApi(quotationId)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('转合同成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '转合同失败')
    }
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('从报价转合同失败:', error)
      ElMessage.error('从报价转合同失败')
    }
  }
}

const handleExport = async () => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || '/api'
  const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token') || ''
  const params = new URLSearchParams()
  if (query.keyword) params.append('keyword', query.keyword)
  if (query.status !== undefined) params.append('status', String(query.status))
  const url = `${baseUrl}/local/contracts/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '合同列表.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出合同失败:', error)
    ElMessage.error('导出失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';

.attachment-wrapper {
  width: 100%;
}
</style>
