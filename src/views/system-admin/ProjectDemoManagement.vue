<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>项目管理示例</h2>
          <div class="page-description">代表性页面：项目全生命周期管理（含状态与进度）。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="项目名称/编码/负责人"
              clearable
              style="width: 260px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部状态" style="width: 160px">
              <el-option label="规划中" :value="0" />
              <el-option label="进行中" :value="1" />
              <el-option label="已完成" :value="2" />
              <el-option label="已暂停" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="openCreateDialog">新增项目</el-button>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="projectCode" label="项目编码" min-width="150" />
          <el-table-column prop="projectName" label="项目名称" min-width="180" />
          <el-table-column prop="ownerName" label="负责人" min-width="120" />
          <el-table-column prop="priority" label="优先级" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="priorityTagType(row.priority)">{{
                priorityText(row.priority)
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="statusTagType(row.status)">{{ statusText(row.status) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="进度" min-width="180">
            <template #default="{ row }">
              <el-progress :percentage="row.progress" :stroke-width="12" />
            </template>
          </el-table-column>
          <el-table-column prop="startDate" label="开始日期" min-width="120" />
          <el-table-column prop="endDate" label="结束日期" min-width="120" />
          <el-table-column prop="updateTime" label="更新时间" min-width="180" />
          <el-table-column label="操作" width="220" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="openDetailDialog(row)">详情</el-button>
              <el-button link type="primary" @click="openEditDialog(row)">编辑</el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="620px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="95px">
        <el-row :gutter="14">
          <el-col :span="12">
            <el-form-item label="项目编码" prop="projectCode">
              <el-input v-model="formData.projectCode" placeholder="请输入项目编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目名称" prop="projectName">
              <el-input v-model="formData.projectName" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="ownerName">
              <el-input v-model="formData.ownerName" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" style="width: 100%">
                <el-option label="高" :value="1" />
                <el-option label="中" :value="2" />
                <el-option label="低" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="规划中" :value="0" />
                <el-option label="进行中" :value="1" />
                <el-option label="已完成" :value="2" />
                <el-option label="已暂停" :value="3" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="进度(%)" prop="progress">
              <el-input-number
                v-model="formData.progress"
                :min="0"
                :max="100"
                :step="5"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="formData.startDate"
                value-format="YYYY-MM-DD"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="formData.endDate"
                value-format="YYYY-MM-DD"
                type="date"
                placeholder="选择结束日期"
                style="width: 100%"
              />
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

    <el-dialog v-model="detailDialogVisible" title="项目详情" width="620px" destroy-on-close>
      <el-descriptions :column="2" border v-if="detailData">
        <el-descriptions-item label="项目编码">{{ detailData.projectCode }}</el-descriptions-item>
        <el-descriptions-item label="项目名称">{{ detailData.projectName }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ detailData.ownerName }}</el-descriptions-item>
        <el-descriptions-item label="优先级">{{
          priorityText(detailData.priority)
        }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{
          statusText(detailData.status)
        }}</el-descriptions-item>
        <el-descriptions-item label="进度">{{ detailData.progress }}%</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{
          detailData.startDate || '-'
        }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{
          detailData.endDate || '-'
        }}</el-descriptions-item>
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
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createProjectApi,
  deleteProjectApi,
  pageProjectApi,
  updateProjectApi,
  type ProjectRecord,
} from '@/api/system/project'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface ProjectQuery {
  keyword: string
  status: number | undefined
}

interface ProjectFormData {
  id: string
  projectCode: string
  projectName: string
  ownerName: string
  priority: number
  status: number
  progress: number
  startDate: string
  endDate: string
  remark: string
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ProjectRecord[]>([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailData = ref<ProjectRecord | null>(null)
const dialogTitle = ref('新增项目')
const isEditMode = ref(false)
const formRef = ref<FormInstance>()

const query = reactive<ProjectQuery>({
  keyword: '',
  status: undefined,
})

const pagination = reactive({
  current: 1,
  size: 10,
  total: 0,
})

const formData = reactive<ProjectFormData>({
  id: '',
  projectCode: '',
  projectName: '',
  ownerName: '',
  priority: 2,
  status: 0,
  progress: 0,
  startDate: '',
  endDate: '',
  remark: '',
})

const formRules: FormRules<ProjectFormData> = {
  projectCode: [{ required: true, message: '请输入项目编码', trigger: 'blur' }],
  projectName: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  ownerName: [{ required: true, message: '请输入负责人', trigger: 'blur' }],
}

const priorityText = (value: number) => ({ 1: '高', 2: '中', 3: '低' })[value] || '中'
const priorityTagType = (value: number): 'danger' | 'warning' | 'info' =>
  value === 1 ? 'danger' : value === 2 ? 'warning' : 'info'
const statusText = (value: number) =>
  ({ 0: '规划中', 1: '进行中', 2: '已完成', 3: '已暂停' })[value] || '规划中'
const statusTagType = (value: number): 'info' | 'primary' | 'success' | 'warning' =>
  value === 1 ? 'primary' : value === 2 ? 'success' : value === 3 ? 'warning' : 'info'

const resetForm = () => {
  formData.id = ''
  formData.projectCode = ''
  formData.projectName = ''
  formData.ownerName = ''
  formData.priority = 2
  formData.status = 0
  formData.progress = 0
  formData.startDate = ''
  formData.endDate = ''
  formData.remark = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageProjectApi({
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
      ElMessage.error(res.msg || '项目数据加载失败')
    }
  } catch (error) {
    console.error('加载项目数据失败:', error)
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
  dialogTitle.value = '新增项目'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: ProjectRecord) => {
  isEditMode.value = true
  dialogTitle.value = '编辑项目'
  formData.id = row.id
  formData.projectCode = row.projectCode
  formData.projectName = row.projectName
  formData.ownerName = row.ownerName
  formData.priority = row.priority
  formData.status = row.status
  formData.progress = row.progress
  formData.startDate = row.startDate
  formData.endDate = row.endDate
  formData.remark = row.remark
  dialogVisible.value = true
}

const openDetailDialog = (row: ProjectRecord) => {
  detailData.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEditMode.value) {
      const res = await updateProjectApi(formData.id, { ...formData })
      if (res.code !== 0 && res.code !== 200) return
      ElMessage.success('更新成功')
    } else {
      const res = await createProjectApi({ ...formData })
      if (res.code !== 0 && res.code !== 200) return
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交项目数据失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: ProjectRecord) => {
  try {
    await ElMessageBox.confirm(`确认删除项目「${row.projectName}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    const res = await deleteProjectApi(row.id)
    if (res.code !== 0 && res.code !== 200) return
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除项目失败:', error)
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
</style>
