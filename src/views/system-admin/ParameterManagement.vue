<template>
  <div class="page-view">
    <!-- 统一页面头部 -->
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>基础信息维护</h2>
          <div class="page-description">维护系统各类基础参数、分类数据和配置信息</div>
        </div>
      </div>
    </div>

    <!-- 页面内容卡片 -->
    <div class="content-card">
      <div class="tab-content">
        <!-- 搜索操作面板 -->
        <div class="search-actions-panel">
          <el-form :model="query" inline class="filter-form" @submit.prevent>
            <el-form-item label="名称">
              <el-input
                v-model="query.keyWord"
                placeholder="名称搜索"
                clearable
                style="width: 200px"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSearch">查询</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-form>
          <div class="actions">
            <el-button type="primary" :icon="Plus" @click="handleCreate">
              新增{{ currentTypeLabel }}
            </el-button>
          </div>
        </div>

        <!-- 数据类型切换 -->
        <div class="type-tabs-container">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="公司管理" name="COMPANY">
              <template #label>
                <el-icon><OfficeBuilding /></el-icon>
                <span>公司管理</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="项目进度" name="PROJECT_PROGRESS">
              <template #label>
                <el-icon><TrendCharts /></el-icon>
                <span>项目进度</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="销售人员" name="SALESPERSON">
              <template #label>
                <el-icon><User /></el-icon>
                <span>销售人员</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="部门管理" name="DEPARTMENT">
              <template #label>
                <el-icon><Collection /></el-icon>
                <span>部门管理</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="品类管理" name="CATEGORY">
              <template #label>
                <el-icon><Menu /></el-icon>
                <span>品类管理</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="发货类型" name="SHIPMENT_TYPE">
              <template #label>
                <el-icon><Upload /></el-icon>
                <span>发货类型</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="收货类型" name="RECEIVE_TYPE">
              <template #label>
                <el-icon><Download /></el-icon>
                <span>收货类型</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="客户等级" name="CUSTOMER_LEVEL">
              <template #label>
                <el-icon><Star /></el-icon>
                <span>客户等级</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="工序名称" name="PROCESS_STEP">
              <template #label>
                <el-icon><Operation /></el-icon>
                <span>工序名称</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="工艺库名" name="PROCESS_LIBRARY">
              <template #label>
                <el-icon><Collection /></el-icon>
                <span>工艺库名</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="存储位置" name="STORAGE_LOCATION">
              <template #label>
                <el-icon><Location /></el-icon>
                <span>存储位置</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="物流公司" name="LOGISTICS_COMPANY">
              <template #label>
                <el-icon><Van /></el-icon>
                <span>物流公司</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="资产类型" name="ASSET_TYPE">
              <template #label>
                <el-icon><Collection /></el-icon>
                <span>资产类型</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="设备类型" name="EQUIPMENT_TYPE">
              <template #label>
                <el-icon><Operation /></el-icon>
                <span>设备类型</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="扫码枪关联" name="SCANNER_MAPPING">
              <template #label>
                <el-icon><Connection /></el-icon>
                <span>扫码枪关联</span>
              </template>
            </el-tab-pane>
            <el-tab-pane label="产品类型" name="PRODUCT_TYPE">
              <template #label>
                <el-icon><Goods /></el-icon>
                <span>产品类型</span>
              </template>
            </el-tab-pane>
          </el-tabs>
        </div>

        <!-- 数据表格 -->
        <div class="table-container">
          <!-- 扫码枪工序关联表格 -->
          <el-table
            v-if="activeTab === 'SCANNER_MAPPING'"
            :data="parameterStore.scanBindingProcesses"
            v-loading="parameterStore.loading"
            border
            stripe
            highlight-current-row
          >
            <el-table-column prop="scanAssetNumber" label="扫码枪资产编号" min-width="150" />
            <el-table-column prop="identifier" label="标识" min-width="120" />
            <el-table-column label="工序名称" min-width="150">
              <template #default="{ row }">
                <span>{{ row.processName || getProcessStepName(row.processId) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 统一基础信息表格 -->
          <el-table
            v-else
            :data="parameterStore.basicInfos"
            v-loading="parameterStore.loading"
            border
            stripe
            highlight-current-row
          >
            <el-table-column prop="name" :label="`${currentTypeLabel}名称`" min-width="200" />
            <el-table-column prop="createTime" label="创建时间" width="180" />

            <el-table-column label="操作" width="160" fixed="right" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="pagination.currentPage"
              v-model:page-size="pagination.pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="
                activeTab === 'SCANNER_MAPPING'
                  ? parameterStore.scanBindingTotal
                  : parameterStore.total
              "
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 基础信息维护弹窗 -->
    <FormDialog
      v-model="formVisible"
      :title="isEdit ? `编辑${currentTypeLabel}` : `新增${currentTypeLabel}`"
      :form-data="formData"
      :rules="formRules"
      :loading="parameterStore.loading"
      width="500px"
      @submit="handleFormSubmit"
    >
      <template #default="{ formData }">
        <el-form-item :label="`${currentTypeLabel}名称`" prop="name">
          <el-input v-model="formData.name" :placeholder="`请输入${currentTypeLabel}名称`" />
        </el-form-item>
      </template>
    </FormDialog>

    <!-- 扫码枪工序关联弹窗 -->
    <FormDialog
      v-model="scanFormVisible"
      :title="isEdit ? '编辑扫码枪工序关联' : '新增扫码枪工序关联'"
      :form-data="scanFormData"
      :rules="scanFormRules"
      :loading="parameterStore.loading"
      width="500px"
      @submit="handleScanFormSubmit"
    >
      <template #default="{ formData }">
        <el-form-item label="资产编号" prop="scanAssetNumber">
          <el-input v-model="formData.scanAssetNumber" placeholder="请输入扫码枪资产编号" />
        </el-form-item>
        <el-form-item label="标识" prop="identifier">
          <el-input v-model="formData.identifier" placeholder="请输入标识" />
        </el-form-item>
        <el-form-item label="对应工序" prop="processId">
          <el-select v-model="formData.processId" placeholder="请选择对应工序" filterable>
            <el-option
              v-for="proc in parameterStore.processStepList"
              :key="proc.id"
              :label="proc.name"
              :value="proc.id"
            />
          </el-select>
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessageBox } from 'element-plus'
import {
  Search,
  Plus,
  OfficeBuilding,
  TrendCharts,
  User,
  Menu,
  Upload,
  Download,
  Star,
  Collection,
  Operation,
  Connection,
  Location,
  Van,
  Goods,
} from '@element-plus/icons-vue'
import { useParameterStore } from '@/stores/parameterStore'
import { PARAM_TYPE_MAP } from '@/types/parameter'
import type { ParamTypeKey, BasicInfoDto, ScanBindingProcessDto } from '@/types/parameter'
import FormDialog from '@/components/common/FormDialog.vue'

const parameterStore = useParameterStore()

// --- 状态变量 ---
const activeTab = ref<ParamTypeKey>('COMPANY')
const isEdit = ref(false)
const formVisible = ref(false)
const scanFormVisible = ref(false)

const query = reactive({
  keyWord: '',
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
})

const formData = reactive<BasicInfoDto>({
  name: '',
  type: PARAM_TYPE_MAP.COMPANY,
  parentId: undefined,
})

const scanFormData = reactive<ScanBindingProcessDto>({
  scanAssetNumber: '',
  identifier: '',
  processId: undefined,
})

// --- 计算属性 ---
const currentTypeLabel = computed(() => {
  const labels: Record<ParamTypeKey, string> = {
    COMPANY: '公司',
    PROJECT_PROGRESS: '项目进度',
    SALESPERSON: '销售人员',
    CATEGORY: '品类',
    SHIPMENT_TYPE: '发货类型',
    RECEIVE_TYPE: '收货类型',
    CUSTOMER_LEVEL: '客户等级',
    PROCESS_STEP: '工序名称',
    PROCESS_LIBRARY: '工艺库名',
    SCANNER_MAPPING: '扫码枪关联',
    STORAGE_LOCATION: '存储位置',
    LOGISTICS_COMPANY: '物流公司',
    ASSET_TYPE: '资产类型',
    EQUIPMENT_TYPE: '设备类型',
    DEPARTMENT: '部门',
    PRODUCT_TYPE: '产品类型',
  }
  return labels[activeTab.value]
})

const formRules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
}

const scanFormRules = {
  scanAssetNumber: [{ required: true, message: '请输入资产编号', trigger: 'blur' }],
  identifier: [{ required: true, message: '请输入标识', trigger: 'blur' }],
  processId: [{ required: true, message: '请选择对应工序', trigger: 'change' }],
}

// --- 方法 ---

// 加载数据
const loadData = async () => {
  const type = PARAM_TYPE_MAP[activeTab.value]

  if (activeTab.value === 'SCANNER_MAPPING') {
    await parameterStore.fetchScanBindingProcesses({
      current: pagination.currentPage,
      size: pagination.pageSize,
      keyWord: query.keyWord,
      sortColumn: 'create_time',
      sortType: 'desc',
    })
    await parameterStore.fetchProcessStepList()
  } else {
    await parameterStore.fetchBasicInfos({
      current: pagination.currentPage,
      size: pagination.pageSize,
      type: type,
      keyWord: query.keyWord,
      sortColumn: 'create_time',
      sortType: 'desc',
    })
  }
}

const handleSearch = () => {
  pagination.currentPage = 1
  loadData()
}

const handleReset = () => {
  query.keyWord = ''
  pagination.currentPage = 1
  loadData()
}

const handleTabChange = () => {
  handleReset()
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

// 新增
const handleCreate = () => {
  isEdit.value = false
  if (activeTab.value === 'SCANNER_MAPPING') {
    Object.assign(scanFormData, {
      id: undefined,
      scanAssetNumber: '',
      identifier: '',
      processId: undefined,
    })
    scanFormVisible.value = true
  } else {
    Object.assign(formData, {
      id: undefined,
      name: '',
      type: PARAM_TYPE_MAP[activeTab.value],
      parentId: undefined,
    })
    formVisible.value = true
  }
}

// 编辑
const handleEdit = (row: any) => {
  isEdit.value = true
  if (activeTab.value === 'SCANNER_MAPPING') {
    Object.assign(scanFormData, {
      id: row.id,
      scanAssetNumber: row.scanAssetNumber,
      identifier: row.identifier,
      processId: row.processId,
    })
    scanFormVisible.value = true
  } else {
    Object.assign(formData, {
      id: row.id,
      name: row.name,
      type: row.type,
      parentId: row.parentId,
    })
    formVisible.value = true
  }
}

// 删除
const handleDelete = async (row: any) => {
  try {
    const title = activeTab.value === 'SCANNER_MAPPING' ? row.scanAssetNumber : row.name
    await ElMessageBox.confirm(`确定要删除 "${title}" 吗？`, '提示', {
      type: 'warning',
    })

    let success = false
    if (activeTab.value === 'SCANNER_MAPPING') {
      success = await parameterStore.removeScanBindingProcess(row.id)
    } else {
      success = await parameterStore.removeBasicInfo(row.id)
    }

    if (success) {
      loadData()
    }
  } catch (error) {
    // 用户取消
  }
}

// 提交表单
const handleFormSubmit = async (data: any) => {
  let success = false
  if (isEdit.value) {
    success = await parameterStore.updateBasicInfo(data as BasicInfoDto)
  } else {
    success = await parameterStore.createBasicInfo(data as BasicInfoDto)
  }

  if (success) {
    formVisible.value = false
    loadData()
  }
}

const handleScanFormSubmit = async (data: any) => {
  let success = false
  if (isEdit.value) {
    success = await parameterStore.updateScanBindingProcess(data as ScanBindingProcessDto)
  } else {
    success = await parameterStore.createScanBindingProcess(data as ScanBindingProcessDto)
  }

  if (success) {
    scanFormVisible.value = false
    loadData()
  }
}

// 辅助方法
const getAssetTypeName = (parentId: number) => {
  const found = parameterStore.assetTypes.find((t) => t.id === parentId)
  return found ? found.name : '未知'
}

const getProcessStepName = (processId: number) => {
  const found = parameterStore.processStepList.find((p) => p.id === processId)
  return found ? found.name : '未知'
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.tab-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

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

.type-tabs-container {
  padding: 0 24px;
  background-color: #fff;

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}

.table-container {
  flex: 1;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.text-muted {
  color: #909399;
}
</style>
