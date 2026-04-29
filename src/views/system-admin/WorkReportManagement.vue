<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>工序报工</h2>
          <div class="page-description">记录工单工序产出，自动联动工单进度。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="工单号/工序/产品/客户"
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="工单">
            <el-select
              v-model="query.workOrderId"
              clearable
              filterable
              placeholder="全部"
              style="width: 240px"
            >
              <el-option
                v-for="item in workOrderOptions"
                :key="item.id"
                :label="item.workOrderNo"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <div style="display: flex; gap: 8px">
          <el-button @click="handleExport">导出</el-button>
          <el-button type="primary" @click="openCreateDialog">新增报工</el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="workOrderNo" label="工单号" min-width="170" />
          <el-table-column prop="productName" label="产品" min-width="160" />
          <el-table-column prop="customerName" label="客户" min-width="120" />
          <el-table-column prop="processName" label="工序" min-width="120" />
          <el-table-column prop="reportQuantity" label="报工数" width="100" align="right" />
          <el-table-column prop="qualifiedQuantity" label="合格数" width="100" align="right" />
          <el-table-column prop="defectQuantity" label="不良数" width="100" align="right" />
          <el-table-column prop="reportUserName" label="报工人" width="110" />
          <el-table-column prop="reportTime" label="报工时间" min-width="170" />
          <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" title="新增报工" width="680px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-form-item label="工单" prop="workOrderId">
          <el-select
            v-model="formData.workOrderId"
            filterable
            style="width: 100%"
            placeholder="请选择工单"
          >
            <el-option
              v-for="item in reportableWorkOrders"
              :key="item.id"
              :label="`${item.workOrderNo} / ${item.productName}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工序" prop="processName"
          ><el-input v-model="formData.processName"
        /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="8"
            ><el-form-item label="报工数" prop="reportQuantity"
              ><el-input-number
                v-model="formData.reportQuantity"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="8"
            ><el-form-item label="合格数" prop="qualifiedQuantity"
              ><el-input-number
                v-model="formData.qualifiedQuantity"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
          <el-col :span="8"
            ><el-form-item label="不良数" prop="defectQuantity"
              ><el-input-number
                v-model="formData.defectQuantity"
                :min="0"
                :precision="2"
                style="width: 100%" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="报工时间"
          ><el-date-picker
            v-model="formData.reportTime"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
        /></el-form-item>
        <el-form-item label="备注"
          ><el-input v-model="formData.remark" type="textarea" :rows="2"
        /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import {
  createWorkReportApi,
  listWorkOrderApi,
  pageWorkReportApi,
  type WorkOrderRecord,
  type WorkReportCreateDto,
  type WorkReportRecord,
} from '@/api/system/workOrder'

interface Query {
  keyword: string
  workOrderId: string
}

const route = useRoute()
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<WorkReportRecord[]>([])
const workOrderOptions = ref<WorkOrderRecord[]>([])
const reportableWorkOrders = ref<WorkOrderRecord[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', workOrderId: '' })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<WorkReportCreateDto>({
  workOrderId: '',
  processName: '',
  reportQuantity: 0,
  qualifiedQuantity: 0,
  defectQuantity: 0,
  reportTime: '',
  remark: '',
})

const formRules: FormRules<WorkReportCreateDto> = {
  workOrderId: [{ required: true, message: '请选择工单', trigger: 'change' }],
  processName: [{ required: true, message: '请输入工序', trigger: 'blur' }],
  reportQuantity: [{ required: true, message: '请输入报工数', trigger: 'blur' }],
  qualifiedQuantity: [{ required: true, message: '请输入合格数', trigger: 'blur' }],
  defectQuantity: [{ required: true, message: '请输入不良数', trigger: 'blur' }],
}

const loadWorkOrders = async () => {
  try {
    const [allRes, reportRes] = await Promise.all([listWorkOrderApi(), listWorkOrderApi(2)])
    if ((allRes.code === 0 || allRes.code === 200) && allRes.data) {
      workOrderOptions.value = allRes.data
    }
    if ((reportRes.code === 0 || reportRes.code === 200) && reportRes.data) {
      reportableWorkOrders.value = reportRes.data
    }
    if (reportableWorkOrders.value.length === 0) {
      const running = (workOrderOptions.value || []).filter((item: WorkOrderRecord) =>
        [2, 3, 4].includes(item.status),
      )
      reportableWorkOrders.value = running
    }
  } catch (error) {
    console.error('加载工单失败:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageWorkReportApi({
      current: pagination.current,
      size: pagination.size,
      keyword: query.keyword || undefined,
      workOrderId: query.workOrderId || undefined,
    })
    if ((res.code === 0 || res.code === 200) && res.data) {
      tableData.value = res.data.records || []
      pagination.total = res.data.total || 0
    } else {
      tableData.value = []
      pagination.total = 0
      ElMessage.error(res.msg || '获取报工记录失败')
    }
  } catch (error) {
    console.error('获取报工记录失败:', error)
    ElMessage.error('获取报工记录失败')
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
  query.workOrderId = ''
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
  if (query.workOrderId) params.append('workOrderId', query.workOrderId)
  const url = `${baseUrl}/local/work-reports/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '工序报工记录.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出报工记录失败:', error)
    ElMessage.error('导出失败')
  }
}

const openCreateDialog = () => {
  formData.workOrderId = query.workOrderId || ''
  formData.processName = ''
  formData.reportQuantity = 0
  formData.qualifiedQuantity = 0
  formData.defectQuantity = 0
  formData.reportTime = ''
  formData.remark = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  if (
    Math.abs(formData.reportQuantity - formData.qualifiedQuantity - formData.defectQuantity) >
    0.0001
  ) {
    ElMessage.warning('合格数 + 不良数 必须等于报工数')
    return
  }
  submitLoading.value = true
  try {
    const res = await createWorkReportApi(formData)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('新增成功')
      dialogVisible.value = false
      loadData()
      loadWorkOrders()
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (error) {
    console.error('新增报工失败:', error)
    ElMessage.error('新增报工失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  const routeWorkOrderId = String(route.query.workOrderId || '').trim()
  if (routeWorkOrderId) {
    query.workOrderId = routeWorkOrderId
  }
  loadWorkOrders()
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
