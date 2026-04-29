<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>__PAGE_TITLE__</h2>
          <div class="page-description">__PAGE_DESCRIPTION__</div>
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
        <el-button type="primary" @click="openCreateDialog">新增__MODULE_TAG__</el-button>
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
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <FormDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :form-data="formData"
      :rules="formRules"
      :loading="submitLoading"
      width="520px"
      @submit="handleSubmit"
      @cancel="dialogVisible = false"
    >
      <template #default="{ formData }">
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item label="编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入编码" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status">
            <el-option :value="0" label="启用" />
            <el-option :value="1" label="停用" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </template>
    </FormDialog>

    <BaseDialog v-model="detailDialogVisible" title="__MODULE_TAG__详情" width="520px" :show-footer="false">
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
    </BaseDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'
import type { FormRules } from 'element-plus'
import { ElMessageBox } from 'element-plus'
import FormDialog from '@/components/common/FormDialog.vue'
import BaseDialog from '@/components/common/BaseDialog.vue'
import { usePageQuery } from '@/composables/usePageQuery'
import { use__MODULE_PASCAL__Store } from '@/stores/__STORE_DIR__/__MODULE_CAMEL__'
import type { __MODULE_PASCAL__Record, __MODULE_PASCAL__SaveDto } from '@/types/__TYPE_DIR__/__MODULE_CAMEL__'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface __MODULE_PASCAL__FormData extends __MODULE_PASCAL__SaveDto {
  id: string
}

const __MODULE_CAMEL__Store = use__MODULE_PASCAL__Store()
const { loading, pagination: storePagination, recordList, total } = storeToRefs(__MODULE_CAMEL__Store)

const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const detailData = ref<__MODULE_PASCAL__Record | null>(null)
const dialogTitle = ref('新增__MODULE_TAG__')
const isEditMode = ref(false)
const tableData = computed(() => recordList.value)
const { query, pagination, handleSearch, handleReset, handleSizeChange, handleCurrentChange } =
  usePageQuery({
    initialQuery: {
      keyword: '',
    },
    initialPagination: storePagination.value,
    load: async ({ query, pagination }) => {
      storePagination.value.current = pagination.current
      storePagination.value.size = pagination.size
      await __MODULE_CAMEL__Store.fetch__MODULE_PASCAL__Page({
        current: pagination.current,
        size: pagination.size,
        keyword: query.keyword || undefined,
      })
    },
    resetQuery: (query) => {
      query.keyword = ''
    },
  })

const formData = reactive<__MODULE_PASCAL__FormData>({
  id: '',
  name: '',
  code: '',
  remark: '',
  status: 0,
})

const formRules: FormRules<__MODULE_PASCAL__FormData> = {
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

const buildSavePayload = (): __MODULE_PASCAL__SaveDto => ({
  name: formData.name,
  code: formData.code,
  remark: formData.remark,
  status: formData.status,
})

const openCreateDialog = () => {
  isEditMode.value = false
  dialogTitle.value = '新增__MODULE_TAG__'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: __MODULE_PASCAL__Record) => {
  isEditMode.value = true
  dialogTitle.value = '编辑__MODULE_TAG__'
  formData.id = row.id
  formData.name = row.name
  formData.code = row.code
  formData.remark = row.remark || ''
  formData.status = row.status
  dialogVisible.value = true
}

const openDetailDialog = (row: __MODULE_PASCAL__Record) => {
  detailData.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  submitLoading.value = true
  try {
    const success = isEditMode.value
      ? await __MODULE_CAMEL__Store.update__MODULE_PASCAL__(formData.id, buildSavePayload())
      : await __MODULE_CAMEL__Store.create__MODULE_PASCAL__(buildSavePayload())

    if (success) {
      dialogVisible.value = false
      await handleSearch()
    }
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: __MODULE_PASCAL__Record) => {
  try {
    await ElMessageBox.confirm(`确认删除「${row.name}」吗？`, '提示', {
      type: 'warning',
    })
  } catch (action) {
    if (isMessageBoxCancel(action)) {
      return
    }
    throw action
  }

  const success = await __MODULE_CAMEL__Store.delete__MODULE_PASCAL__(row.id)
  if (success) {
    if (tableData.value.length === 1 && pagination.current > 1) {
      pagination.current -= 1
    }
    await handleCurrentChange(pagination.current)
  }
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';
</style>
