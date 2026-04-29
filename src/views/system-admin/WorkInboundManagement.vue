<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>完工入库</h2>
          <div class="page-description">按工单执行成品入库并同步库存流水。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="入库单号/工单号/产品/客户"
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
          <el-button type="primary" @click="openCreateDialog">新增入库</el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="inboundNo" label="入库单号" min-width="170" />
          <el-table-column prop="workOrderNo" label="工单号" min-width="170" />
          <el-table-column prop="productName" label="产品" min-width="160" />
          <el-table-column prop="customerName" label="客户" min-width="120" />
          <el-table-column prop="quantity" label="入库数量" width="100" align="right" />
          <el-table-column prop="warehouseName" label="仓库" width="100" />
          <el-table-column prop="operatorName" label="操作人" width="100" />
          <el-table-column prop="inboundTime" label="入库时间" min-width="170" />
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

    <el-dialog v-model="dialogVisible" title="新增入库" width="680px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-form-item label="工单" prop="workOrderId">
          <el-select
            v-model="formData.workOrderId"
            filterable
            style="width: 100%"
            placeholder="请选择工单"
          >
            <el-option
              v-for="item in inboundableWorkOrders"
              :key="item.id"
              :label="`${item.workOrderNo} / ${item.productName}`"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"
            ><el-form-item label="入库单号"
              ><el-input v-model="formData.inboundNo" placeholder="留空自动生成" /></el-form-item
          ></el-col>
          <el-col :span="12"
            ><el-form-item label="仓库"><el-input v-model="formData.warehouseName" /></el-form-item
          ></el-col>
        </el-row>
        <el-form-item label="入库数量" prop="quantity"
          ><el-input-number v-model="formData.quantity" :min="0" :precision="2" style="width: 100%"
        /></el-form-item>
        <el-form-item label="入库时间"
          ><el-date-picker
            v-model="formData.inboundTime"
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
  createWorkInboundApi,
  listWorkOrderApi,
  pageWorkInboundApi,
  type WorkInboundCreateDto,
  type WorkInboundRecord,
  type WorkOrderRecord,
} from '@/api/system/workOrder'

interface Query {
  keyword: string
  workOrderId: string
}

const route = useRoute()
const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<WorkInboundRecord[]>([])
const workOrderOptions = ref<WorkOrderRecord[]>([])
const inboundableWorkOrders = ref<WorkOrderRecord[]>([])
const dialogVisible = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', workOrderId: '' })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<WorkInboundCreateDto>({
  workOrderId: '',
  inboundNo: '',
  quantity: 0,
  warehouseName: '成品仓',
  inboundTime: '',
  remark: '',
})

const formRules: FormRules<WorkInboundCreateDto> = {
  workOrderId: [{ required: true, message: '请选择工单', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入入库数量', trigger: 'blur' }],
}

const loadWorkOrders = async () => {
  try {
    const res = await listWorkOrderApi()
    if ((res.code === 0 || res.code === 200) && res.data) {
      workOrderOptions.value = res.data
      inboundableWorkOrders.value = res.data.filter((item: WorkOrderRecord) =>
        [3, 4, 5].includes(item.status),
      )
    }
  } catch (error) {
    console.error('加载工单失败:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageWorkInboundApi({
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
      ElMessage.error(res.msg || '获取入库记录失败')
    }
  } catch (error) {
    console.error('获取入库记录失败:', error)
    ElMessage.error('获取入库记录失败')
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
  const url = `${baseUrl}/local/work-inbounds/export${params.toString() ? `?${params.toString()}` : ''}`
  try {
    const resp = await fetch(url, { headers: token ? { Authorization: `Bearer ${token}` } : {} })
    const blob = await resp.blob()
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = '完工入库记录.xlsx'
    a.click()
    URL.revokeObjectURL(a.href)
  } catch (error) {
    console.error('导出入库记录失败:', error)
    ElMessage.error('导出失败')
  }
}

const openCreateDialog = () => {
  formData.workOrderId = query.workOrderId || ''
  formData.inboundNo = ''
  formData.quantity = 0
  formData.warehouseName = '成品仓'
  formData.inboundTime = ''
  formData.remark = ''
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const res = await createWorkInboundApi(formData)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('新增成功')
      dialogVisible.value = false
      loadData()
      loadWorkOrders()
    } else {
      ElMessage.error(res.msg || '新增失败')
    }
  } catch (error) {
    console.error('新增入库失败:', error)
    ElMessage.error('新增入库失败')
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
