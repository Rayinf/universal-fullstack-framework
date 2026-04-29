<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>客户管理</h2>
          <div class="page-description">管理系统客户基本信息与分级</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="queryForm" inline class="filter-form">
          <el-form-item label="客户编号">
            <el-input
              v-model="queryForm.customerCode"
              placeholder="输入编号"
              clearable
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="关键字">
            <el-input
              v-model="queryForm.searchKey"
              placeholder="客户名称/联系人"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="客户级别">
            <el-select
              v-model="queryForm.customerLevel"
              placeholder="选择级别"
              clearable
              style="width: 120px"
            >
              <el-option label="一级" :value="1" />
              <el-option label="二级" :value="2" />
              <el-option label="三级" :value="3" />
            </el-select>
          </el-form-item>
          <el-form-item label="创建时间">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              style="width: 240px"
              @change="handleDateRangeChange"
            />
          </el-form-item>
        </el-form>
        <div class="actions">
          <el-button type="primary" :icon="Search" @click="handleSearch">查询</el-button>
          <el-button :icon="RefreshLeft" @click="resetQuery">重置</el-button>
          <el-divider direction="vertical" />
          <el-button type="primary" :icon="Plus" @click="handleAdd">新增客户</el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table
          :data="customerStore.customerList"
          v-loading="customerStore.loading"
          border
          stripe
        >
          <el-table-column prop="customerCode" label="客户编号" width="120" />
          <el-table-column
            prop="customerName"
            label="客户名称"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column prop="customerLevel" label="客户级别" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getLevelTag(row.customerLevel)">{{ row.customerLevel }}级</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="accountManagerName" label="客户经理" width="120" />
          <el-table-column prop="introducerName" label="介绍人" width="120" />
          <el-table-column prop="creator" label="创建人" width="100" />
          <el-table-column prop="createTime" label="创建时间" width="170" />
          <el-table-column label="操作" width="150" fixed="right" align="center">
            <template #default="{ row }">
              <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="customerStore.pagination.current"
            v-model:page-size="customerStore.pagination.size"
            :total="customerStore.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 客户表单对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑客户' : '新增客户'"
      width="600px"
      destroy-on-close
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="客户名称" prop="customerName">
          <el-input v-model="form.customerName" placeholder="请输入客户全称" />
        </el-form-item>
        <el-form-item label="客户编号" prop="customerCode">
          <el-input v-model="form.customerCode" placeholder="请输入客户唯一编号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="客户经理" prop="accountManagerName">
              <el-input v-model="form.accountManagerName" placeholder="经理姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="介绍人" prop="introducerName">
              <el-input v-model="form.introducerName" placeholder="介绍人姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="客户级别" prop="customerLevel">
          <el-radio-group v-model="form.customerLevel">
            <el-radio :label="1">一级</el-radio>
            <el-radio :label="2">二级</el-radio>
            <el-radio :label="3">三级</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="特殊说明" prop="specialNotes">
          <el-input
            v-model="form.specialNotes"
            type="textarea"
            :rows="3"
            placeholder="填写客户特殊要求或说明"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="customerStore.loading" @click="submitForm"
          >确定</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import { useCustomerStore } from '@/stores/system/customer'
import { ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import type { Customer } from '@/types/system/customer'

const customerStore = useCustomerStore()
const queryForm = reactive({
  customerCode: '',
  searchKey: '',
  customerLevel: undefined,
  startDate: '',
  endDate: '',
})

const dateRange = ref<[string, string] | null>(null)

const handleDateRangeChange = (val: [string, string] | null) => {
  if (val) {
    queryForm.startDate = val[0]
    queryForm.endDate = val[1]
  } else {
    queryForm.startDate = ''
    queryForm.endDate = ''
  }
}

const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref<FormInstance>()
const form = reactive<Partial<Customer>>({
  customerName: '',
  customerCode: '',
  accountManagerName: '',
  introducerName: '',
  customerLevel: 1,
  specialNotes: '',
})

const rules: FormRules = {
  customerName: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
  customerCode: [{ required: true, message: '请输入客户编号', trigger: 'blur' }],
  customerLevel: [{ required: true, message: '请选择客户级别', trigger: 'change' }],
}

const handleSearch = () => {
  customerStore.pagination.current = 1
  customerStore.fetchCustomerPage(queryForm)
}

const resetQuery = () => {
  Object.assign(queryForm, {
    customerCode: '',
    searchKey: '',
    customerLevel: undefined,
    startDate: '',
    endDate: '',
  })
  dateRange.value = null
  handleSearch()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: undefined,
    customerName: '',
    customerCode: '',
    accountManagerName: '',
    introducerName: '',
    customerLevel: 1,
    specialNotes: '',
  })
  dialogVisible.value = true
}

const handleEdit = (row: Customer) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = (row: Customer) => {
  ElMessageBox.confirm(`确认删除客户 "${row.customerName}" 吗？`, '警告', {
    type: 'warning',
  }).then(async () => {
    const success = await customerStore.deleteCustomer(row.id)
    if (success) handleSearch()
  })
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      const success = isEdit.value
        ? await customerStore.updateCustomer(form)
        : await customerStore.saveCustomer(form)

      if (success) {
        dialogVisible.value = false
        handleSearch()
      }
    }
  })
}

const handleSizeChange = (val: number) => {
  customerStore.pagination.size = val
  handleSearch()
}

const handleCurrentChange = (val: number) => {
  customerStore.pagination.current = val
  handleSearch()
}

const getLevelTag = (level?: number) => {
  const map: Record<number, string> = {
    1: 'danger',
    2: 'warning',
    3: 'info',
  }
  return map[level || 3] || 'info'
}

onMounted(() => {
  handleSearch()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 24px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fff;
  gap: 16px;
}

.filter-form {
  flex: 1;
}

.actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding-top: 4px;
}

.table-container {
  flex: 1;
  padding: 20px 24px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
