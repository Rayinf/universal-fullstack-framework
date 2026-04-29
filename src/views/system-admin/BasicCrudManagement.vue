<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>本地基础CRUD</h2>
          <div class="page-description">基于本地 Python 后端的增删改查示例页面。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="名称/编码"
              clearable
              style="width: 240px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="openCreateDialog">新增</el-button>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="name" label="名称" min-width="160" />
          <el-table-column prop="code" label="编码" min-width="140" />
          <el-table-column prop="remark" label="备注" min-width="220" show-overflow-tooltip />
          <el-table-column prop="status" label="状态" width="120" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 0 ? 'success' : 'warning'">
                {{ row.status === 0 ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" style="width: 100%">
            <el-option :value="0" label="启用" />
            <el-option :value="1" label="停用" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailDialogVisible" title="记录详情" width="520px" destroy-on-close>
      <el-descriptions :column="1" border v-if="detailData">
        <el-descriptions-item label="名称">{{ detailData.name }}</el-descriptions-item>
        <el-descriptions-item label="编码">{{ detailData.code }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          {{ detailData.status === 0 ? '启用' : '停用' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注">{{ detailData.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailData.createTime }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailData.updateTime }}</el-descriptions-item>
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
  createBasicCrudApi,
  deleteBasicCrudApi,
  pageBasicCrudApi,
  updateBasicCrudApi,
  type BasicCrudRecord,
} from '@/api/system/basicCrud'
import { usePageQuery } from '@/composables/usePageQuery'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface CrudFormData {
  id: string
  name: string
  code: string
  remark: string
  status: number
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<BasicCrudRecord[]>([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailData = ref<BasicCrudRecord | null>(null)
const dialogTitle = ref('新增记录')
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const { query, pagination, loadData, handleSearch, handleReset, handleSizeChange, handleCurrentChange } =
  usePageQuery({
    initialQuery: {
      keyword: '',
    },
    load: async ({ query, pagination }) => {
      loading.value = true
      try {
        const res = await pageBasicCrudApi({
          current: pagination.current,
          size: pagination.size,
          keyword: query.keyword || undefined,
        })
        if ((res.code === 0 || res.code === 200) && res.data) {
          tableData.value = res.data.records || []
          pagination.total = res.data.total || 0
        } else {
          tableData.value = []
          pagination.total = 0
          ElMessage.error(res.msg || '加载失败')
        }
      } catch (error) {
        console.error('加载基础CRUD数据失败:', error)
        tableData.value = []
        pagination.total = 0
        ElMessage.error('加载失败，请检查本地后端服务')
      } finally {
        loading.value = false
      }
    },
  })

const formData = reactive<CrudFormData>({
  id: '',
  name: '',
  code: '',
  remark: '',
  status: 0,
})

const formRules: FormRules<CrudFormData> = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入编码', trigger: 'blur' }],
}

const resetForm = () => {
  formData.id = ''
  formData.name = ''
  formData.code = ''
  formData.remark = ''
  formData.status = 0
}

const openCreateDialog = () => {
  isEditMode.value = false
  dialogTitle.value = '新增记录'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: BasicCrudRecord) => {
  isEditMode.value = true
  dialogTitle.value = '编辑记录'
  formData.id = row.id
  formData.name = row.name
  formData.code = row.code
  formData.remark = row.remark || ''
  formData.status = row.status
  dialogVisible.value = true
}

const openDetailDialog = (row: BasicCrudRecord) => {
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
      await updateBasicCrudApi(formData.id, {
        name: formData.name,
        code: formData.code,
        remark: formData.remark,
        status: formData.status,
      })
      ElMessage.success('更新成功')
    } else {
      await createBasicCrudApi({
        name: formData.name,
        code: formData.code,
        remark: formData.remark,
        status: formData.status,
      })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交基础CRUD数据失败:', error)
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: BasicCrudRecord) => {
  try {
    await ElMessageBox.confirm(`确认删除记录「${row.name}」吗？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteBasicCrudApi(row.id)
    ElMessage.success('删除成功')
    if (tableData.value.length === 1 && pagination.current > 1) {
      pagination.current -= 1
    }
    loadData()
  } catch (error) {
    if (!isMessageBoxCancel(error)) {
      console.error('删除基础CRUD数据失败:', error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
