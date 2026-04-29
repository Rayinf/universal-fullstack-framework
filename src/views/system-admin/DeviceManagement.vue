<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>设备基础信息管理</h2>
          <div class="page-description">
            管理生产设备的基础信息，包括设备编号、名称、型号、资产类型及状态管理。
          </div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="search-actions-panel">
        <el-form :model="query" class="filter-form" inline @submit.prevent>
          <el-form-item label="设备查询">
            <el-input
              v-model="query.keyWord"
              placeholder="设备编号/名称"
              clearable
              style="width: 200px"
            >
              <template #prefix>
                <el-icon>
                  <Search />
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="资产类型">
            <el-select
              v-model="query.deviceCategoryId"
              placeholder="请选择"
              clearable
              style="width: 160px"
            >
              <el-option
                v-for="item in parameterStore.assetTypes"
                :key="item.id"
                :label="item.name"
                :value="String(item.id)"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="所属工位">
            <el-select
              v-model="query.workstationId"
              placeholder="请选择"
              clearable
              filterable
              style="width: 160px"
            >
              <el-option
                v-for="item in workstationList"
                :key="item.id"
                :label="item.workstationName"
                :value="String(item.id)"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 120px">
              <el-option label="启用" :value="1" />
              <el-option label="停用" :value="2" />
              <el-option label="报废" :value="3" />
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
            <el-icon> <Plus /> </el-icon>新增设备
          </el-button>
        </div>
      </div>

      <div class="table-container">
        <el-table
          :data="deviceStore.deviceList"
          stripe
          highlight-current-row
          v-loading="deviceStore.loading"
          class="unified-table"
        >
          <el-table-column prop="deviceNumber" label="设备编号" min-width="120" />
          <el-table-column prop="deviceName" label="设备名称" min-width="140" />
          <el-table-column prop="model" label="设备型号" min-width="120" />
          <el-table-column prop="deviceCategoryId" label="资产类型" min-width="120">
            <template #default="{ row }">
              {{ getAssetTypeName(row.deviceCategoryId, row.deviceCategoryName) }}
            </template>
          </el-table-column>
          <el-table-column prop="workstationId" label="所属工位" min-width="120">
            <template #default="{ row }">
              {{ getWorkstationName(row.workstationId, row.workstationName) }}
            </template>
          </el-table-column>
          <el-table-column prop="responsiblePerson" label="责任人" min-width="100">
            <template #default="{ row }">
              {{ getUserName(row.responsiblePerson) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="getStatusType(row.status)" effect="dark">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="scrapReason"
            label="报废原因"
            min-width="150"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              {{ row.scrapReason || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="remarks" label="备注" min-width="150" show-overflow-tooltip />
          <el-table-column prop="createTime" label="创建时间" min-width="160" />
          <el-table-column label="操作" fixed="right" width="240" align="center">
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(row)"
                :disabled="Number(row.status) === 3"
                >编辑</el-button
              >

              <el-button
                type="warning"
                link
                size="small"
                @click="handleStatusChange(row)"
                :disabled="Number(row.status) === 3"
              >
                状态变更
              </el-button>

              <!-- <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button> -->
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.currentPage"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="deviceStore.total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </div>
    </div>

    <!-- 新增/编辑设备弹窗 -->
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
            <el-form-item label="设备编号" prop="deviceNumber">
              <el-input v-model="formData.deviceNumber" placeholder="请输入设备编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="deviceName">
              <el-input v-model="formData.deviceName" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备型号" prop="model">
              <el-input v-model="formData.model" placeholder="请输入设备型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资产类型" prop="deviceCategoryId">
              <el-select
                v-model="formData.deviceCategoryId"
                placeholder="请选择资产类型"
                style="width: 100%"
              >
                <el-option
                  v-for="item in parameterStore.assetTypes"
                  :key="item.id"
                  :label="item.name"
                  :value="String(item.id)"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所属工位" prop="workstationId">
              <el-select
                v-model="formData.workstationId"
                placeholder="请选择所属工位"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="item in workstationList"
                  :key="item.id"
                  :label="item.workstationName"
                  :value="String(item.id)"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="责任人" prop="responsiblePerson">
              <el-select
                v-model="formData.responsiblePerson"
                placeholder="请选择责任人"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="user in userList"
                  :key="user.userId"
                  :label="userMap[String(user.userId)] || user.realName || user.username"
                  :value="user.userId"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item v-if="Number(formData.status) === 3" label="报废原因">
          <el-input v-model="formData.scrapReason" type="textarea" disabled />
        </el-form-item>

        <el-form-item label="备注" prop="remarks">
          <el-input v-model="formData.remarks" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 状态变更弹窗 -->
    <FormDialog
      v-model="statusDialogVisible"
      title="状态变更"
      :form-data="statusFormData"
      :rules="statusFormRules"
      :loading="formLoading"
      width="500px"
      @submit="submitStatusChange"
      @cancel="statusDialogVisible = false"
    >
      <template #default="{ formData }">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusType(currentStatus)" effect="dark">
            {{ getStatusLabel(currentStatus) }}
          </el-tag>
        </el-form-item>

        <el-form-item label="变更状态" prop="targetStatus">
          <el-select
            v-model="formData.targetStatus"
            placeholder="请选择目标状态"
            style="width: 100%"
          >
            <el-option
              v-for="item in availableStatusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item v-if="formData.targetStatus === 3" label="报废原因" prop="scrapReason">
          <el-input
            v-model="formData.scrapReason"
            type="textarea"
            placeholder="请输入报废原因"
            :rows="3"
          />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { Search, RefreshLeft, Plus } from '@element-plus/icons-vue'
import { useDeviceStore } from '@/stores/deviceStore'
import { useParameterStore } from '@/stores/parameterStore'
import { getAllWorkstationsApi } from '@/api/system/workstation'
import { getAllUsersApi } from '@/api/system/user'
import type { DeviceQuery, DeviceRecord, DeviceDTO } from '@/types/system/device'
import type { WorkstationRecord } from '@/types/system/workstation'
import type { UserRecord } from '@/types/system/user'
import FormDialog from '@/components/common/FormDialog.vue'

const deviceStore = useDeviceStore()
const parameterStore = useParameterStore()

// --- Data Lists ---
const workstationList = ref<WorkstationRecord[]>([])
const userList = ref<UserRecord[]>([])
const userMap = ref<Record<string, string>>({})
const workstationMap = ref<Record<string, string>>({})

// --- Query & Pagination ---
const query = reactive<DeviceQuery>({
  keyWord: '',
  deviceCategoryId: undefined,
  workstationId: undefined,
  status: undefined,
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
})

// --- Dialog & Form ---
const dialogVisible = ref(false)
const dialogTitle = ref('新增设备')
const isEdit = ref(false)
const formLoading = ref(false)

const formData = reactive<DeviceDTO>({
  deviceName: '',
  deviceNumber: '',
  model: '',
  deviceCategoryId: '',
  workstationId: '',
  responsiblePerson: '',
  status: 1,
  remarks: '',
  scrapReason: '',
})

const formRules = {
  deviceName: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  deviceNumber: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  model: [{ required: true, message: '请输入设备型号', trigger: 'blur' }],
  deviceCategoryId: [{ required: true, message: '请选择资产类型', trigger: 'change' }],
  workstationId: [{ required: true, message: '请选择所属工位', trigger: 'change' }],
  responsiblePerson: [{ required: true, message: '请选择责任人', trigger: 'change' }],
}

// --- Status Dialog ---
const statusDialogVisible = ref(false)
const currentStatus = ref(1)
const currentDeviceId = ref('')

const statusFormData = reactive({
  targetStatus: undefined as number | undefined,
  scrapReason: '',
})

const statusFormRules = {
  targetStatus: [{ required: true, message: '请选择目标状态', trigger: 'change' }],
  scrapReason: [
    {
      validator: (_rule: unknown, value: unknown, callback: (error?: Error) => void) => {
        if (statusFormData.targetStatus === 3 && !value) {
          callback(new Error('请输入报废原因'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

const availableStatusOptions = computed(() => {
  const options = [
    { label: '启用', value: 1 },
    { label: '停用', value: 2 },
    { label: '报废', value: 3 },
  ]
  // Optional: filter out current status
  return options.filter((opt) => opt.value !== Number(currentStatus.value))
})

const parseListPayload = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) {
    return payload
  }

  if (payload && typeof payload === 'object') {
    const raw = payload as { data?: unknown; records?: unknown }
    if (Array.isArray(raw.data)) {
      return raw.data
    }
    if (Array.isArray(raw.records)) {
      return raw.records
    }
  }

  return []
}

// --- Loading Data Methods ---

const loadData = () => {
  deviceStore.fetchDeviceList({
    ...query,
    current: pagination.currentPage,
    size: pagination.pageSize,
    sortColumn: 'create_time',
    sortType: 'desc',
  })
}

const loadWorkstations = async () => {
  try {
    const res = await getAllWorkstationsApi()
    if (res.code === 0 || res.code === 200) {
      workstationList.value = parseListPayload<WorkstationRecord>(res.data)
      // Build map
      workstationMap.value = {}
      workstationList.value.forEach((w) => {
        workstationMap.value[String(w.id)] = w.workstationName
      })
    }
  } catch (error) {
    console.error('加载工位列表失败', error)
  }
}

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

      userMap.value = {}
      userList.value.forEach((user) => {
        const name = user.realName || user.username
        if (user.userId) {
          userMap.value[String(user.userId)] = name
        }
      })
    }
  } catch (error) {
    console.error('加载用户列表失败', error)
  }
}

// --- Event Handlers ---

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  query.keyWord = ''
  query.deviceCategoryId = undefined
  query.workstationId = undefined
  query.status = undefined
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

// --- Actions ---

const resetForm = () => {
  formData.id = undefined
  formData.deviceName = ''
  formData.deviceNumber = ''
  formData.model = ''
  formData.deviceCategoryId = ''
  formData.workstationId = ''
  formData.responsiblePerson = ''
  formData.status = 1
  formData.remarks = ''
  formData.scrapReason = ''
}

const handleCreate = () => {
  isEdit.value = false
  dialogTitle.value = '新增设备'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row: DeviceRecord) => {
  isEdit.value = true
  dialogTitle.value = '编辑设备'
  resetForm()
  Object.assign(formData, {
    id: row.id,
    deviceName: row.deviceName,
    deviceNumber: row.deviceNumber,
    model: row.model,
    deviceCategoryId: String(row.deviceCategoryId),
    workstationId: String(row.workstationId),
    responsiblePerson: String(row.responsiblePerson),
    status: row.status,
    remarks: row.remarks,
    scrapReason: row.scrapReason,
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  formLoading.value = true
  try {
    let success = false
    if (isEdit.value) {
      success = await deviceStore.updateDevice(formData)
    } else {
      success = await deviceStore.createDevice(formData)
    }

    if (success) {
      dialogVisible.value = false
      loadData()
    }
  } finally {
    formLoading.value = false
  }
}

const handleStatusChange = (row: DeviceRecord) => {
  currentDeviceId.value = row.id
  currentStatus.value = Number(row.status)
  statusFormData.targetStatus = undefined
  statusFormData.scrapReason = ''
  statusDialogVisible.value = true
}

const submitStatusChange = async () => {
  if (!statusFormData.targetStatus) return

  formLoading.value = true
  try {
    const success = await deviceStore.changeDeviceStatus(
      currentDeviceId.value,
      statusFormData.targetStatus,
      statusFormData.scrapReason,
    )
    if (success) {
      statusDialogVisible.value = false
      loadData()
    }
  } finally {
    formLoading.value = false
  }
}

// --- Helpers ---

const getStatusLabel = (status: number) => {
  const map: Record<number, string> = {
    1: '启用',
    2: '停用',
    3: '报废',
  }
  return map[status] || '未知'
}

const getStatusType = (status: number) => {
  const map: Record<number, string> = {
    1: 'success',
    2: 'warning',
    3: 'danger',
  }
  return map[status] || 'info'
}

const getAssetTypeName = (id: string | number, name?: string) => {
  const found = parameterStore.assetTypes.find((t) => String(t.id) === String(id))
  return found ? found.name : name || String(id)
}

const getWorkstationName = (id: string, name?: string) => {
  return workstationMap.value[String(id)] || name || String(id)
}

const getUserName = (id: string) => {
  return userMap.value[id] || id
}

// --- Lifecycle ---

onMounted(() => {
  loadData()
  loadWorkstations()
  loadUsers()
  parameterStore.fetchAssetTypes()
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
