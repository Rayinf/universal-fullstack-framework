<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>产品目录管理</h2>
          <div class="page-description">报价模块基础数据：维护产品编码、规格和参考价格。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form inline @submit.prevent>
          <el-form-item label="关键词">
            <el-input
              v-model="query.keyword"
              placeholder="产品编码/名称/分类"
              clearable
              style="width: 240px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" clearable placeholder="全部" style="width: 140px">
              <el-option label="启用" :value="1" />
              <el-option label="停用" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
        <el-button type="primary" @click="openCreateDialog">新增产品</el-button>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row v-loading="loading">
          <el-table-column prop="productCode" label="产品编码" min-width="150" />
          <el-table-column prop="productName" label="产品名称" min-width="180" />
          <el-table-column prop="specification" label="规格" min-width="140" />
          <el-table-column prop="unit" label="单位" width="90" align="center" />
          <el-table-column prop="referencePrice" label="参考价" width="120" align="right" />
          <el-table-column prop="costPrice" label="成本价" width="120" align="right" />
          <el-table-column prop="category" label="分类" min-width="120" />
          <el-table-column prop="status" label="状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
                {{ row.status === 1 ? '启用' : '停用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="updateTime" label="更新时间" min-width="170" />
          <el-table-column label="操作" width="130" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="openEditDialog(row)">编辑</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="640px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="90px">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="产品编码" prop="productCode">
              <el-input v-model="formData.productCode" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产品名称" prop="productName">
              <el-input v-model="formData.productName" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格">
              <el-input v-model="formData.specification" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="formData.unit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参考价">
              <el-input-number
                v-model="formData.referencePrice"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本价">
              <el-input-number
                v-model="formData.costPrice"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="分类">
              <el-input v-model="formData.category" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="启用" :value="1" />
                <el-option label="停用" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="3" />
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
import {
  pageProductCatalogApi,
  createProductCatalogApi,
  updateProductCatalogApi,
  deleteProductCatalogApi,
  type ProductCatalogRecord,
  type ProductCatalogSaveDto,
} from '@/api/system/productCatalog'
import { isMessageBoxCancel } from '@/utils/elementPlus'

interface Query {
  keyword: string
  status: number | undefined
}

interface FormData extends ProductCatalogSaveDto {
  id: string
}

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref<ProductCatalogRecord[]>([])
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formRef = ref<FormInstance>()
const query = reactive<Query>({ keyword: '', status: undefined })
const pagination = reactive({ current: 1, size: 10, total: 0 })
const formData = reactive<FormData>({
  id: '',
  productCode: '',
  productName: '',
  specification: '',
  unit: 'pcs',
  referencePrice: 0,
  costPrice: 0,
  category: '',
  status: 1,
  remark: '',
})

const formRules: FormRules<FormData> = {
  productCode: [{ required: true, message: '请输入产品编码', trigger: 'blur' }],
  productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
}

const dialogTitle = ref('新增产品')

const resetForm = () => {
  formData.id = ''
  formData.productCode = ''
  formData.productName = ''
  formData.specification = ''
  formData.unit = 'pcs'
  formData.referencePrice = 0
  formData.costPrice = 0
  formData.category = ''
  formData.status = 1
  formData.remark = ''
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await pageProductCatalogApi({
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
      ElMessage.error(res.msg || '获取列表失败')
    }
  } catch (error) {
    console.error('获取产品目录失败:', error)
    tableData.value = []
    pagination.total = 0
    ElMessage.error('获取产品目录失败')
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
  dialogTitle.value = '新增产品'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: ProductCatalogRecord) => {
  isEditMode.value = true
  dialogTitle.value = '编辑产品'
  formData.id = row.id
  formData.productCode = row.productCode
  formData.productName = row.productName
  formData.specification = row.specification
  formData.unit = row.unit
  formData.referencePrice = row.referencePrice
  formData.costPrice = row.costPrice
  formData.category = row.category
  formData.status = row.status
  formData.remark = row.remark
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  submitLoading.value = true
  try {
    const payload: ProductCatalogSaveDto = {
      productCode: formData.productCode,
      productName: formData.productName,
      specification: formData.specification,
      unit: formData.unit,
      referencePrice: formData.referencePrice,
      costPrice: formData.costPrice,
      category: formData.category,
      status: formData.status,
      remark: formData.remark,
    }
    const res = isEditMode.value
      ? await updateProductCatalogApi(formData.id, payload)
      : await createProductCatalogApi(payload)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isEditMode.value ? '更新成功' : '新增成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || '保存失败')
    }
  } catch (error) {
    console.error('保存产品失败:', error)
    ElMessage.error('保存产品失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (row: ProductCatalogRecord) => {
  try {
    await ElMessageBox.confirm(`确定删除产品“${row.productName}”吗？`, '提示', {
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
    const res = await deleteProductCatalogApi(row.id)
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('删除成功')
      loadData()
    } else {
      ElMessage.error(res.msg || '删除失败')
    }
  } catch (error) {
    console.error('删除产品失败:', error)
    ElMessage.error('删除产品失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
@import '@/styles/common.css';
</style>
