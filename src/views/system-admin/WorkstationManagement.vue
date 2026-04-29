<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>工位信息管理</h2>
          <div class="page-description">
            管理生产工位的基础信息，包括工位编号、名称、类型及关联产线等。
          </div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="query" class="filter-form" inline @submit.prevent>
          <el-form-item label="工位查询">
            <el-input v-model="query.keywords" placeholder="工位编号/名称" clearable>
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="所属组织">
            <OrgTreeSelector
              v-model="queryDeptVal"
              placeholder="请选择产线"
              clearable
              style="width: 200px"
            />
          </el-form-item>
          <el-form-item label="工位类型">
            <el-select
              v-model="query.workstationType"
              placeholder="全部类型"
              clearable
              style="width: 160px"
            >
              <el-option label="装配工位" :value="1" />
              <el-option label="测试工位" :value="2" />
              <el-option label="包装工位" :value="3" />
              <el-option label="维修工位" :value="4" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 120px">
              <el-option label="启用" :value="1" />
              <el-option label="禁用" :value="0" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">
              <el-icon> <Search /> </el-icon>查询
            </el-button>
            <el-button @click="handleReset">
              <el-icon> <RefreshLeft /> </el-icon>重置
            </el-button>
          </el-form-item>
        </el-form>
        <div class="action-area">
          <el-button type="primary" @click="handleCreate">
            <el-icon> <Plus /> </el-icon>新增工位
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table :data="tableData" stripe highlight-current-row class="unified-table">
          <el-table-column prop="workstationNo" label="工位编号" min-width="120" />
          <el-table-column prop="workstationName" label="工位名称" min-width="140" />
          <el-table-column prop="workstationType" label="工位类型" width="120">
            <template #default="{ row }">
              <el-tag>{{ getWorkstationTypeLabel(row.workstationType) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="deptId" label="所属组织" min-width="120">
            <template #default="{ row }">
              {{ row.deptName || deptMap[row.deptId] || row.deptId || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="processName" label="关联工序" min-width="120">
            <template #default="{ row }">
              {{ formatProcessNames(row.processLibraryId) }}
            </template>
          </el-table-column>
          <el-table-column prop="responsiblePerson" label="负责人" min-width="100">
            <template #default="{ row }">
              {{
                row.responsiblePersonName ||
                userMap[row.responsiblePerson] ||
                row.responsiblePerson ||
                '-'
              }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'danger'" effect="dark">
                {{ row.status === 1 ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createTime" label="创建时间" min-width="160" />
          <el-table-column label="操作" fixed="right" width="210" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button
                link
                :type="row.status === 1 ? 'warning' : 'success'"
                @click="handleToggleStatus(row)"
              >
                {{ row.status === 1 ? '禁用' : '启用' }}
              </el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑工位弹窗 -->
    <FormDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :form-data="formData"
      :rules="formRules"
      :loading="formLoading"
      width="600px"
      @submit="handleSubmit"
      @cancel="dialogVisible = false"
    >
      <template #default="{ formData }">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工位编号" prop="workstationNo">
              <el-input
                v-model.number="formData.workstationNo"
                placeholder="请输入工位编号"
                :disabled="isEdit"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工位名称" prop="workstationName">
              <el-input v-model="formData.workstationName" placeholder="请输入工位名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="工位类型" prop="workstationType">
              <el-select
                v-model="formData.workstationType"
                placeholder="请选择类型"
                style="width: 100%"
              >
                <el-option label="装配工位" :value="1" />
                <el-option label="测试工位" :value="2" />
                <el-option label="包装工位" :value="3" />
                <el-option label="维修工位" :value="4" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属组织" prop="deptId">
              <OrgTreeSelector
                v-model="formDeptVal"
                placeholder="请选择所属组织"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="关联工序" prop="processLibraryId">
              <el-select
                v-model="selectedProcessIds"
                placeholder="请选择工序"
                clearable
                filterable
                multiple
                collapse-tags
                collapse-tags-tooltip
                style="width: 100%"
              >
                <el-option
                  v-for="item in technologyStore.processLibraries"
                  :key="item.id"
                  :label="item.processName"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="responsiblePerson">
              <el-select
                v-model="formData.responsiblePerson"
                placeholder="请选择负责人"
                filterable
                clearable
                style="width: 100%"
              >
                <el-option
                  v-for="user in userList"
                  :key="user.userId"
                  :label="(user as any).nickname || user.realName || user.username"
                  :value="user.userId"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-radio-group v-model="formData.status">
                <el-radio :label="1">启用</el-radio>
                <el-radio :label="0">禁用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="备注" prop="remarks">
          <el-input v-model="formData.remarks" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, watch } from 'vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import OrgTreeSelector from '@/components/common/OrgTreeSelector.vue'
import { getDeptTreeApi } from '@/api/system/dept'
import {
  pageWorkstationsApi,
  createWorkstationApi,
  updateWorkstationApi,
  deleteWorkstationApi,
  toggleWorkstationStatusApi,
} from '@/api/system/workstation'
import { getAllUsersApi } from '@/api/system/user'
import type {
  WorkstationRecord,
  WorkstationQuery,
  WorkstationDTO,
} from '@/types/system/workstation'
import type { UserRecord } from '@/types/system/user'
import type { DeptTreeNode } from '@/types/system/dept'
import FormDialog from '@/components/system/FormDialog.vue'
import { useTechnologyStore } from '@/stores/technologyStore'

const technologyStore = useTechnologyStore()

// Selected processes for multiple choice
const selectedProcessIds = ref<string[]>([])

// Dept Data
const deptMap = ref<Record<string, string>>({})
const queryDeptVal = ref('')
const formDeptVal = ref('')

const stripDeptId = (val: string | undefined | null) => {
  if (!val) return ''
  if (val.includes(':')) {
    const parts = val.split(':')
    return parts.length > 1 ? parts[1] : val
  }
  return val
}

const buildDeptMap = (nodes: DeptTreeNode[]) => {
  if (!nodes) return

  nodes.forEach((node) => {
    const id = String(node.id)
    const name = node.name
    if (id && name) {
      deptMap.value[id] = name
    }
    if (node.children) {
      buildDeptMap(node.children)
    }
  })
}

const loadDeptData = async () => {
  try {
    const res = await getDeptTreeApi()
    if ((res.code === 0 || res.code === 200) && res.data) {
      buildDeptMap(res.data)
    }
  } catch (error) {
    console.error('加载部门数据失败:', error)
  }
}

// User Data
const userList = ref<UserRecord[]>([])
const userMap = ref<Record<string, string>>({})

const loadUsers = async () => {
  try {
    const res = await getAllUsersApi()
    if (res.code === 0 || res.code === 200) {
      const payload = res.data
      const users = Array.isArray(payload)
        ? payload
        : Array.isArray(payload?.data)
          ? payload.data
          : []

      userList.value = users

      // Build user map
      userMap.value = {}
      userList.value.forEach((user) => {
        const name = user.realName || user.username
        if (user.userId) {
          userMap.value[String(user.userId)] = name
        }
      })
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// Watchers for OrgTreeSelector
watch(queryDeptVal, (val) => {
  const realId = stripDeptId(val)
  query.deptId = realId
})

watch(formDeptVal, (val) => {
  const realId = stripDeptId(val)
  formData.deptId = realId
})

const query = reactive<WorkstationQuery>({
  workstationName: '',
  keywords: '',
  workstationType: undefined,
  status: undefined,
  deptId: '',
})

const tableData = ref<WorkstationRecord[]>([])
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0,
})

const loadData = async () => {
  try {
    const params = {
      ...query,
      page: pagination.currentPage,
      size: pagination.pageSize,
      sortColumn: 'create_time',
      sortType: 'desc',
    }
    const res = await pageWorkstationsApi(params)
    if (res && res.data) {
      tableData.value = res.data.records
      pagination.total = res.data.total
    }
  } catch (error) {
    console.error('加载工位数据失败:', error)
    ElNotification.error('加载工位数据失败')
  }
}

const formatProcessNames = (processLibraryId?: string) => {
  if (!processLibraryId) return '-'

  return processLibraryId
    .split(',')
    .map((id: string) => {
      return (
        technologyStore.processLibraries.find((p) => String(p.id) === String(id))?.processName || id
      )
    })
    .join(', ')
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  query.workstationName = ''
  query.keywords = ''
  query.workstationType = undefined
  query.status = undefined
  queryDeptVal.value = ''
  query.deptId = ''
  pagination.currentPage = 1
  loadData()
}

const handleSizeChange = (size: number) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadData()
}

const handleCurrentChange = (page: number) => {
  pagination.currentPage = page
  loadData()
}

// Dialog Logic
const dialogVisible = ref(false)
const dialogTitle = ref('新增工位')
const formLoading = ref(false)
const isEdit = ref(false)

const formData = reactive<WorkstationDTO>({
  workstationNo: 0,
  workstationName: '',
  workstationType: 1,
  status: 1,
  responsiblePerson: '',
  deptId: '',
  processLibraryId: '',
  remarks: '',
})

const formRules = {
  workstationNo: [{ required: true, message: '请输入工位编号', trigger: 'blur' }],
  workstationName: [{ required: true, message: '请输入工位名称', trigger: 'blur' }],
  workstationType: [{ required: true, message: '请选择工位类型', trigger: 'change' }],
}

const resetForm = () => {
  formData.id = undefined
  formData.workstationNo = 0
  formData.workstationName = ''
  formData.workstationType = 1
  formData.status = 1
  formData.responsiblePerson = ''
  formData.deptId = ''
  formData.processLibraryId = ''
  formData.remarks = ''
  formDeptVal.value = ''
  selectedProcessIds.value = []
}

const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新增工位'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: WorkstationRecord) => {
  isEdit.value = true
  dialogTitle.value = '编辑工位'
  Object.assign(formData, {
    id: row.id,
    workstationNo: row.workstationNo,
    workstationName: row.workstationName,
    workstationType: row.workstationType,
    status: row.status,
    responsiblePerson: row.responsiblePerson,
    deptId: row.deptId,
    processLibraryId: row.processLibraryId,
    remarks: row.remarks,
  })
  formDeptVal.value = row.deptId || ''

  // Initialize selectedProcessIds
  if (row.processLibraryId) {
    selectedProcessIds.value = row.processLibraryId.split(',')
  } else {
    selectedProcessIds.value = []
  }

  dialogVisible.value = true
}

const handleSubmit = async () => {
  formLoading.value = true
  try {
    // Update formData.processLibraryId from selectedProcessIds
    formData.processLibraryId = selectedProcessIds.value.join(',')

    if (isEdit.value) {
      await updateWorkstationApi(formData)
      ElNotification.success('工位更新成功')
    } else {
      await createWorkstationApi(formData)
      ElNotification.success('工位创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('保存工位失败:', error)
  } finally {
    formLoading.value = false
  }
}

const handleDelete = async (row: WorkstationRecord) => {
  try {
    await ElMessageBox.confirm(`确认要删除工位 ${row.workstationName} 吗？`, '删除工位', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteWorkstationApi(row.id)
    ElNotification.success('工位删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const handleToggleStatus = async (row: WorkstationRecord) => {
  const newStatus = row.status === 1 ? 0 : 1
  const actionText = newStatus === 1 ? '启用' : '禁用'
  try {
    await toggleWorkstationStatusApi(row.id, newStatus)
    ElNotification.success(`工位已${actionText}`)
    loadData()
  } catch (error) {
    console.error(error)
  }
}

const getWorkstationTypeLabel = (type: number) => {
  const map: Record<number, string> = {
    1: '装配工位',
    2: '测试工位',
    3: '包装工位',
    4: '维修工位',
  }
  return map[type] || '未知'
}

onMounted(() => {
  loadData()
  loadDeptData()
  loadUsers()
  technologyStore.fetchProcessLibraries({ size: 1000 })
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  gap: 16px;
}

.table-container {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unified-table {
  width: 100%;
  max-height: calc(100vh - 380px);
  overflow-y: auto;
}

.action-area {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
