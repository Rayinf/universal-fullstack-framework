<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>{{ currentTypeLabel }}列表</h2>
          <div class="page-description">共 {{ currentType === 'scannerProcessMapping' ? scanBindingProcessData.length : tableData.length }} 条记录</div>
        </div>
      </div>
      <div class="header-actions">
        <el-button :type="systemButtons.create()" @click="handleCreate" style="width: 160px;">
          <el-icon><Plus /></el-icon>
          新增{{ currentTypeLabel }}
        </el-button>
      </div>
    </div>

    <div class="search-actions-panel">
      <el-form :model="query" class="filter-form" inline @submit.prevent>
        <el-form-item label="名称">
          <el-input v-model="query.keyWord" placeholder="名称" clearable>
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <div class="action-area">
        <el-button type="primary" @click="loadData" style="width: 100px;" >查询</el-button>
        <el-button @click="handleReset" style="width: 100px;">重置</el-button>
      </div>
    </div>

    <!-- 数据类型切换 -->
    <div class="content-card" style="margin-bottom: 16px;">
      <el-tabs v-model="currentType" @tab-change="handleTypeChange">
        <el-tab-pane label="公司管理" name="company">
          <template #label>
            <el-icon><OfficeBuilding /></el-icon>
            公司管理
          </template>
        </el-tab-pane>
        <el-tab-pane label="项目进度" name="projectProgress">
          <template #label>
            <el-icon><TrendCharts /></el-icon>
            项目进度
          </template>
        </el-tab-pane>
        <el-tab-pane label="销售人员" name="salesperson">
          <template #label>
            <el-icon><User /></el-icon>
            销售人员
          </template>
        </el-tab-pane>
        <el-tab-pane label="部门管理" name="department">
          <template #label>
            <el-icon><OfficeBuilding /></el-icon>
            部门管理
          </template>
        </el-tab-pane>
        <el-tab-pane label="品类管理" name="category">
          <template #label>
            <el-icon><Menu /></el-icon>
            品类管理
          </template>
        </el-tab-pane>
        <el-tab-pane label="发货类型" name="shipmentType">
          <template #label>
            <el-icon><Upload /></el-icon>
            发货类型
          </template>
        </el-tab-pane>
        <el-tab-pane label="工艺要求库名称" name="processLibraryName">
          <template #label>
            <el-icon><Collection /></el-icon>
            工艺要求库名称
          </template>
        </el-tab-pane>
        <el-tab-pane label="工序名称" name="processStep">
          <template #label>
            <el-icon><Operation /></el-icon>
            工序名称
          </template>
        </el-tab-pane>
        <el-tab-pane label="扫描枪工序关联" name="scannerProcessMapping">
          <template #label>
            <el-icon><Connection /></el-icon>
            扫描枪工序关联
          </template>
        </el-tab-pane>
        <el-tab-pane label="收货类型" name="receiveType">
          <template #label>
            <el-icon><Download /></el-icon>
            收货类型
          </template>
        </el-tab-pane>
        <el-tab-pane label="客户等级" name="customerLevel">
          <template #label>
            <el-icon><Star /></el-icon>
            客户等级
          </template>
        </el-tab-pane>
        <el-tab-pane label="存储位置" name="storageLocation">
          <template #label>
            <el-icon><Location /></el-icon>
            存储位置
          </template>
        </el-tab-pane>
        <el-tab-pane label="物流公司" name="logisticsCompany">
          <template #label>
            <el-icon><Van /></el-icon>
            物流公司
          </template>
        </el-tab-pane>
        <el-tab-pane label="资产类型" name="assetType">
          <template #label>
            <el-icon><Collection /></el-icon>
            资产类型
          </template>
        </el-tab-pane>
        <el-tab-pane label="设备类型" name="equipmentType">
          <template #label>
            <el-icon><Operation /></el-icon>
            设备类型
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 数据表格 -->
    <div class="content-card">
      <div class="table-container">
      
      <!-- 扫码枪工序关联表格 -->
      <el-table 
        v-if="currentType === 'scannerProcessMapping'" 
        :data="scanBindingProcessData" 
        stripe 
        highlight-current-row 
        empty-text="暂无数据" 
        class="unified-table"
      >
        <el-table-column prop="scanAssetNumber" label="扫码枪资产编号" min-width="180" />
        <el-table-column prop="identifier" label="标识" min-width="180" />
        <el-table-column label="工序名称" min-width="180">
          <template #default="{ row }">
            <span>{{ row.processName || getProcessStepName(row.processId) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right" align="center" class-name="col-actions">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button :type="systemButtons.edit()" size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 统一简化表格：仅显示名称 -->
      <el-table 
        v-else 
        :data="tableData" 
        stripe 
        highlight-current-row 
        empty-text="暂无数据" 
        class="unified-table"
      >
        <!-- 设备类型显示上级资产分类 -->
        <el-table-column 
          v-if="currentType === 'equipmentType'" 
          label="上级资产分类" 
          width="180" 
          align="center"
        >
          <template #default="{ row }">
            <span v-if="row.parentId">{{ getAssetTypeName(row.parentId) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="name" :label="`${currentTypeLabel}名称`" min-width="240" />
        <el-table-column label="操作" width="160" fixed="right" align="center" class-name="col-actions">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button :type="systemButtons.edit()" size="small" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 - 扫码枪工序关联 -->
      <div v-if="currentType === 'scannerProcessMapping'" class="pagination-container">
        <el-pagination
          v-model:current-page="scanBindingProcessPagination.currentPage"
          v-model:page-size="scanBindingProcessPagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="scanBindingProcessPagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
      
      <!-- 分页 - 其他类型 -->
      <div v-else class="pagination-container">
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

    <!-- 新增/编辑弹窗 -->
    <FormDialog
      v-model="formVisible"
      :title="isEdit ? `编辑${currentTypeLabel}` : `新增${currentTypeLabel}`"
      :form-data="formData"
      :rules="formRules"
      :loading="formLoading"
      width="700px"
      @submit="handleFormSubmit"
      @cancel="handleFormCancel"
    >
      <template #default="{ formData }">
        <!-- 设备类型需要选择上级资产分类 -->
        <el-form-item 
          v-if="currentType === 'equipmentType'" 
          label="上级资产分类" 
          prop="parentId"
        >
          <el-select 
            v-model="formData.parentId" 
            placeholder="请选择上级资产分类" 
            style="width: 100%;"
            filterable
            clearable
          >
            <el-option
              v-for="assetType in assetTypes"
              :key="assetType.id"
              :label="assetType.name"
              :value="assetType.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item :label="`${currentTypeLabel}`" prop="name">
          <el-input v-model="formData.name" :placeholder="`请输入${currentTypeLabel}名称`"  />
        </el-form-item>
      </template>
    </FormDialog>
    
    <!-- 扫码枪工序关联弹窗 -->
    <el-dialog
      v-model="scanBindingFormVisible"
      :title="scanBindingIsEdit ? '编辑扫码枪工序关联' : '新增扫码枪工序关联'"
      width="700px"
      :close-on-click-modal="false"
      destroy-on-close
      align-center
    >
      <el-form :model="scanBindingFormData" label-width="150px">
        <el-form-item label="扫码枪资产编号" required>
          <el-input 
            v-model="scanBindingFormData.scanAssetNumber" 
            placeholder="请输入扫码枪资产编号"
            style="width: 400px;"
          />
        </el-form-item>
        <el-form-item label="标识" required>
          <el-input 
            v-model="scanBindingFormData.identifier" 
            placeholder="请输入标识"
            style="width: 400px;"
          />
        </el-form-item>
        <el-form-item label="工序名称" required>
          <el-select 
            v-model="scanBindingFormData.processId" 
            placeholder="请选择工序名称" 
            style="width: 400px;"
            filterable
          >
            <el-option
              v-for="process in processStepList"
              :key="process.id"
              :label="process.name"
              :value="process.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleScanBindingFormCancel">取消</el-button>
          <el-button type="primary" :loading="scanBindingFormLoading" @click="handleScanBindingFormSubmit" style="margin-left: 12px;">
            {{ scanBindingIsEdit ? '保存' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, OfficeBuilding, TrendCharts, User, Menu, Search, Upload, Download, Star, Collection, Operation, Connection, Location, Van } from '@element-plus/icons-vue'
import { 
  pageBasicInfoApi, 
  saveBasicInfoApi, 
  updateBasicInfoApi, 
  deleteBasicInfoApi,
  listBasicInfoByTypeApi
} from '@/api/modules/basic-info'
import type { 
  BasicInfoRecord, 
  BasicInfoDto, 
  BasicInfoPageQuery 
} from '@/types/basic-info'
import {
  pageScanBindingProcessApi,
  saveScanBindingProcessApi,
  updateScanBindingProcessApi,
  deleteScanBindingProcessApi
} from '@/api/modules/scan-binding-process'
import type {
  ScanBindingProcessRecord,
  ScanBindingProcessDto
} from '@/types/scan-binding-process'
import FormDialog from '@/components/dialogs/FormDialog.vue'
import { useButtonColors } from '@/composables/useButtonColors'

const { systemButtons } = useButtonColors()

// 数据类型映射
const typeMapping = {
  company: 1,
  projectProgress: 2,
  salesperson: 3,
  department: 15, // 部门管理
  category: 4,
  shipmentType: 5,
  receiveType: 6,
  customerLevel: 7,
  processLibraryName: 9,  // 工艺要求库名称（与工序名称互换）
  processStep: 8,         // 工序名称（与工艺要求库名称互换）
  scannerProcessMapping: 10,
  storageLocation: 11,
  logisticsCompany: 12,
  assetType: 13,
  equipmentType: 14
}

// 当前数据类型
const currentType = ref<keyof typeof typeMapping>('company')

// 查询条件
const query = reactive<BasicInfoPageQuery>({
  keyWord: '',
  type: typeMapping[currentType.value],
  sortColumn: 'create_time',
  sortType: 'desc'
})

// 分页配置
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表格数据
const tableData = ref<BasicInfoRecord[]>([])

// 资产类型数据（用于设备类型的上级分类选择）
const assetTypes = ref<BasicInfoRecord[]>([])

// 扫码枪工序关联相关数据
const scanBindingProcessData = ref<ScanBindingProcessRecord[]>([])
const scanBindingProcessPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})
const scanBindingFormVisible = ref(false)
const scanBindingFormLoading = ref(false)
const scanBindingIsEdit = ref(false)
const scanBindingEditingId = ref<number>(0)
const scanBindingFormData = reactive<ScanBindingProcessDto>({
  scanAssetNumber: '',
  identifier: '',
  processId: undefined
})

// 工序列表（用于扫码枪工序关联的下拉选择）
const processStepList = ref<BasicInfoRecord[]>([])

// 加载资产类型数据（用于设备类型的上级分类选择）
const loadAssetTypes = async () => {
  try {
    const page = {
      records: [],
      total: 0,
      current: 1,
      size: 1000, // 获取所有资产类型
      optimizeJoinOfCountSql: true,
      pages: 0
    }
    
    const assetTypeQuery = {
      type: typeMapping.assetType, // 资产类型的type为13
      keyWord: ''
    }
    
    const res = await pageBasicInfoApi({ ...page, ...assetTypeQuery })
    if (res.code === 200 || res.code === 200) {
      assetTypes.value = res.data?.records || []
    }
  } catch (error) {
    console.error('加载资产类型数据失败:', error)
  }
}

// 加载工序列表（用于扫码枪工序关联的下拉选择）
const loadProcessStepList = async () => {
  try {
    const res = await listBasicInfoByTypeApi(typeMapping.processStep) // 工序名称的type为8
    if (res.code === 200 || res.code === 200) {
      processStepList.value = res.data || []
    }
  } catch (error) {
    console.error('加载工序列表失败:', error)
  }
}

// 加载扫码枪工序关联数据
const loadScanBindingProcessData = async () => {
  try {
    const page = {
      records: [],
      total: 0,
      current: scanBindingProcessPagination.currentPage,
      size: scanBindingProcessPagination.pageSize,
      optimizeJoinOfCountSql: true,
      pages: 0
    }
    
    const queryParams = {
      keyWord: query.keyWord || ''
    }
    
    const res = await pageScanBindingProcessApi({ ...page, ...queryParams })
    if (res.code === 200 || res.code === 200) {
      scanBindingProcessData.value = res.data?.records || []
      scanBindingProcessPagination.total = res.data?.total || 0
    }
  } catch (error) {
    console.error('加载扫码枪工序关联数据失败:', error)
    ElMessage.error('加载扫码枪工序关联数据失败')
  }
}

// 加载数据
const loadData = async () => {
  // 扫码枪工序关联使用独立的加载方法
  if (currentType.value === 'scannerProcessMapping') {
    await loadScanBindingProcessData()
    return
  }
  
  try {
    const page = {
      records: [],
      total: 0,
      current: pagination.currentPage,
      size: pagination.pageSize,
      optimizeJoinOfCountSql: true,
      pages: 0
    }
    
    // 更新查询条件中的类型
    query.type = typeMapping[currentType.value]
    
    const res = await pageBasicInfoApi({ ...page, ...query })
    if (res.code === 200 || res.code === 200) {
      tableData.value = res.data?.records || []
      pagination.total = res.data?.total || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  }
}

// 表单相关
const formVisible = ref(false)
const formLoading = ref(false)
const isEdit = ref(false)
const editingId = ref<number>(0)

const formData = reactive<BasicInfoDto>({
  name: '',
  type: typeMapping[currentType.value],
  parentId: undefined
})

// 当前类型标签
const currentTypeLabel = computed(() => {
  const labels = {
    company: '公司',
    projectProgress: '项目进度',
    salesperson: '销售人员',
    department: '部门',
    category: '品类',
    shipmentType: '发货类型',
    receiveType: '收货类型',
    customerLevel: '客户等级',
    processLibraryName: '工艺要求库名称',
    processStep: '工序名称',
    scannerProcessMapping: '扫描枪工序关联',
    storageLocation: '存储位置',
    logisticsCompany: '物流公司',
    assetType: '资产类型',
    equipmentType: '设备类型'
  }
  return labels[currentType.value]
})

// 根据 parentId 获取资产类型名称
const getAssetTypeName = (parentId: number | string) => {
  if (!parentId) return '未知'
  
  // 确保类型匹配，支持数字和字符串类型的ID
  const assetType = assetTypes.value.find(item => 
    item.id === parentId || item.id.toString() === parentId.toString()
  )
  return assetType ? assetType.name : '未知'
}

// 根据 processId 获取工序名称
const getProcessStepName = (processId: number | string) => {
  if (!processId) return '未知'
  
  const process = processStepList.value.find(item => 
    item.id === processId || item.id.toString() === processId.toString()
  )
  return process ? process.name : '未知'
}

// 表单验证规则
const formRules = computed(() => {
  const rules: any = {
    name: [{ required: true, message: `请输入${currentTypeLabel.value}名称`, trigger: 'blur' }]
  }
  
  // 设备类型需要选择上级资产分类
  if (currentType.value === 'equipmentType') {
    rules.parentId = [{ required: true, message: '请选择上级资产分类', trigger: 'change' }]
  }
  
  return rules
})

// 重置查询
const handleReset = () => {
  query.keyWord = ''
  query.type = typeMapping[currentType.value]
  pagination.currentPage = 1
  loadData()
}

// 标签页切换
const handleTypeChange = async (type: string | number) => {
  const typeKey = type as keyof typeof typeMapping
  currentType.value = typeKey
  
  // 如果切换到设备类型，需要加载资产类型数据
  if (typeKey === 'equipmentType') {
    await loadAssetTypes()
  }
  
  // 如果切换到扫码枪工序关联，需要加载工序列表
  if (typeKey === 'scannerProcessMapping') {
    await loadProcessStepList()
    scanBindingProcessPagination.currentPage = 1
  }
  
  // 重置查询条件并加载数据
  query.keyWord = ''
  query.type = typeMapping[typeKey]
  pagination.currentPage = 1
  await loadData()
}

// 分页事件处理
const handleSizeChange = (size: number) => {
  if (currentType.value === 'scannerProcessMapping') {
    scanBindingProcessPagination.pageSize = size
    scanBindingProcessPagination.currentPage = 1
    loadScanBindingProcessData()
  } else {
    pagination.pageSize = size
    pagination.currentPage = 1
    loadData()
  }
}

const handleCurrentChange = (page: number) => {
  if (currentType.value === 'scannerProcessMapping') {
    scanBindingProcessPagination.currentPage = page
    loadScanBindingProcessData()
  } else {
    pagination.currentPage = page
    loadData()
  }
}

// // 切换数据类型
// const handleTypeChange = () => {
//   handleReset()
// }

// 重置表单
const resetForm = () => {
  formData.name = ''
  formData.type = typeMapping[currentType.value]
  formData.parentId = undefined
}

// 新增
const handleCreate = async () => {
  // 扫码枪工序关联使用独立的表单
  if (currentType.value === 'scannerProcessMapping') {
    scanBindingIsEdit.value = false
    resetScanBindingForm()
    await loadProcessStepList()
    scanBindingFormVisible.value = true
    return
  }
  
  isEdit.value = false
  resetForm()
  
  // 如果是设备类型，需要加载资产类型数据
  if (currentType.value === 'equipmentType') {
    await loadAssetTypes()
  }
  
  formVisible.value = true
}

// 重置扫码枪工序关联表单
const resetScanBindingForm = () => {
  scanBindingFormData.scanAssetNumber = ''
  scanBindingFormData.identifier = ''
  scanBindingFormData.processId = undefined
}

// 编辑
const handleEdit = async (row: BasicInfoRecord | ScanBindingProcessRecord) => {
  // 扫码枪工序关联使用独立的表单
  if (currentType.value === 'scannerProcessMapping') {
    const scanRow = row as ScanBindingProcessRecord
    scanBindingIsEdit.value = true
    scanBindingEditingId.value = scanRow.id
    
    // 复制数据到表单
    scanBindingFormData.scanAssetNumber = scanRow.scanAssetNumber
    scanBindingFormData.identifier = scanRow.identifier
    scanBindingFormData.processId = scanRow.processId
    
    await loadProcessStepList()
    scanBindingFormVisible.value = true
    return
  }
  
  const basicRow = row as BasicInfoRecord
  isEdit.value = true
  editingId.value = basicRow.id
  
  // 复制数据到表单
  formData.id = basicRow.id
  formData.name = basicRow.name
  formData.type = basicRow.type
  formData.parentId = basicRow.parentId
  
  // 如果是设备类型，需要加载资产类型数据
  if (currentType.value === 'equipmentType') {
    await loadAssetTypes()
  }
  
  formVisible.value = true
}

// 表单提交
const handleFormSubmit = async (data: Record<string, any>) => {
  formLoading.value = true
  
  try {
    const submitData: BasicInfoDto = {
      name: data.name,
      type: typeMapping[currentType.value]
    }
    
    // 如果是设备类型，添加 parentId 字段
    if (currentType.value === 'equipmentType' && data.parentId) {
      submitData.parentId = data.parentId
    }
    
    if (isEdit.value) {
        // 更新
        submitData.id = editingId.value
        const response = await updateBasicInfoApi(submitData)
        if (response.code === 200 || response.code === 200) {
          ElMessage.success(`更新成功`)
        } else {
          // 新增
          ElMessage.error(response.msg || '更新失败')
        }
      }else{
          // 新增
          const responseSave = await saveBasicInfoApi(submitData)
          if (responseSave.code === 200 || responseSave.code === 200) {
            ElMessage.success(`创建成功`)
          } else {
            ElMessage.error(responseSave.msg || '创建失败')
          }
      }
    
    loadData()
    formVisible.value = false
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(`操作失败，请重试`)
  } finally {
    formLoading.value = false
  }
}

// 表单取消
const handleFormCancel = () => {
  formVisible.value = false
}

// 扫码枪工序关联表单提交
const handleScanBindingFormSubmit = async () => {
  // 验证表单
  if (!scanBindingFormData.scanAssetNumber) {
    ElMessage.warning('请输入扫码枪资产编号')
    return
  }
  if (!scanBindingFormData.identifier) {
    ElMessage.warning('请输入标识')
    return
  }
  if (!scanBindingFormData.processId) {
    ElMessage.warning('请选择工序名称')
    return
  }
  
  scanBindingFormLoading.value = true
  
  try {
    const submitData: ScanBindingProcessDto = {
      scanAssetNumber: scanBindingFormData.scanAssetNumber,
      identifier: scanBindingFormData.identifier,
      processId: scanBindingFormData.processId
    }
    
    if (scanBindingIsEdit.value) {
      // 更新
      submitData.id = scanBindingEditingId.value
      const response = await updateScanBindingProcessApi(submitData)
      if (response.code === 200 || response.code === 200) {
        ElMessage.success('更新成功')
      } else {
        ElMessage.error(response.msg || '更新失败')
        return
      }
    } else {
      // 新增
      const response = await saveScanBindingProcessApi(submitData)
      if (response.code === 200 || response.code === 200) {
        ElMessage.success('创建成功')
      } else {
        ElMessage.error(response.msg || '创建失败')
        return
      }
    }
    
    await loadScanBindingProcessData()
    scanBindingFormVisible.value = false
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error('操作失败，请重试')
  } finally {
    scanBindingFormLoading.value = false
  }
}

// 扫码枪工序关联表单取消
const handleScanBindingFormCancel = () => {
  scanBindingFormVisible.value = false
}

// 状态切换功能已移除，因为BasicInfoItem只保留name字段
// const handleToggleStatus = async (row: BasicInfoItem) => {
//   // 功能已简化，不再需要状态切换
// }

// 删除
const handleDelete = async (row: BasicInfoRecord | ScanBindingProcessRecord) => {
  // 扫码枪工序关联使用独立的删除方法
  if (currentType.value === 'scannerProcessMapping') {
    const scanRow = row as ScanBindingProcessRecord
    try {
      await ElMessageBox.confirm(
        `确定要删除扫码枪资产编号"${scanRow.scanAssetNumber}"的工序关联吗？此操作不可撤销。`,
        '删除确认',
        {
          confirmButtonText: '删除',
          cancelButtonText: '取消',
          type: 'warning',
          confirmButtonClass: 'el-button--danger',
          customClass: 'custom-message-box'
        }
      )
      
      const response = await deleteScanBindingProcessApi(scanRow.id)
      if (response.code === 200 || response.code === 200) {
        ElMessage.success('删除成功')
        await loadScanBindingProcessData()
      } else {
        ElMessage.error(response.msg || '删除失败')
      }
    } catch (error) {
      if (error !== 'cancel') {
        console.error('删除失败:', error)
        ElMessage.error('删除失败，请重试')
      }
    }
    return
  }
  
  const basicRow = row as BasicInfoRecord
  try {
    await ElMessageBox.confirm(
      `确定要删除${currentTypeLabel.value}"${basicRow.name}"吗？此操作不可撤销。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
        customClass: 'custom-message-box'
      }
    )
    
    await deleteBasicInfoApi(basicRow.id)
    ElMessage.success(`${currentTypeLabel.value}删除成功`)
    loadData()
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败，请重试')
    }
  }
}

// 监听类型变化，重新加载数据
watch(currentType, async (newType) => {
  // 如果切换到设备类型，需要加载资产类型数据
  if (newType === 'equipmentType') {
    await loadAssetTypes()
  }
  // 如果切换到扫码枪工序关联，需要加载工序列表
  if (newType === 'scannerProcessMapping') {
    await loadProcessStepList()
  }
  loadData()
})

onMounted(async () => {
  // 如果默认显示设备类型，需要加载资产类型数据
  if (currentType.value === 'equipmentType') {
    await loadAssetTypes()
  }
  // 如果默认显示扫码枪工序关联，需要加载工序列表
  if (currentType.value === 'scannerProcessMapping') {
    await loadProcessStepList()
  }
  loadData()
})
</script>

<style scoped lang="scss">
.color-preview {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  border: 1px solid var(--el-border-color-lighter);
  margin: 0 auto;
}

:deep(.el-tabs__header) {
  margin-bottom: 0;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  display: none;
}

</style>
















