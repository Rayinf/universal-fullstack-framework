import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus' // Added for user feedback in store actions
import request from '@/utils/request' // 导入request工具

/**
 * 参数配置Store
 *
 * 评估参数接口已统一：
 * - 所有评估参数的增删改操作都通过 updateEvaluationParamWithItems 方法
 * - 使用统一的 /manage/api/evaluationParam/edit 接口
 * - 移除了冗余的 saveItem、editItem、deleteItem 相关方法
 */

// 客户参数接口定义
export interface ClientParamCategory {
  id: string
  name: string
}

export interface JobLevel {
  id: string
  level: string
  description: string
}

export interface Competitor {
  id: string
  name: string
  products: string // 产品及服务
}

export interface CustomerSource {
  id: string
  name: string
}

// 定义竞争对手分类
export interface CompetitorCategory {
  id: string
  name: string
}

// 定义客户来源分类
export interface CustomerSourceCategory {
  id: string
  name: string
}

// 项目参数接口定义（可根据需要扩展）
export interface ProjectParamCategory {
  id: string
  name: string
  children?: ProjectParamCategory[]
  parentId?: string
}

// 工作参数接口定义（可根据需要扩展）
export interface WorkParamCategory {
  id: string
  name: string
  children?: WorkParamCategory[]
  parentId?: string
}

// 定义项目状态类型，不再包含关键工作和输出项
export interface ProjectStatus {
  id: string
  name: string
  description: string
  // keyWorks?: Array<{
  //   workName: string
  //   outputItems: string
  // }>
}

// 定义业务类型接口
export interface BusinessType {
  id: string
  name: string
  description: string // 可选，为了与ProjectParams.vue的通用表单兼容
}

// 产品及服务类型，移除单位和标准毛利
export interface ProductService {
  id: number
  name: string // 服务名称
  serviceType: string // 业务类型
  productType: string // 产品类型
  tenantCode?: string
  createBy?: number
  createTime?: string
  updateBy?: number
  updateTime?: string
}

// 工作分类接口定义
export interface SalesType {
  id: number
  name: string // 分类名称
  parentId: number
  level: number // 分类级别1大类 2二级分类
  sequence: string
  tenantCode?: string
  createBy?: number
  createTime?: string
  updateBy?: number
  updateTime?: string
}

// 资金来源接口定义
export interface FundingSource {
  id: string
  name: string // 资金来源名称
  description: string // 描述
}

// 采购方式接口定义
export interface ProcurementMethod {
  id: string
  name: string // 采购方式名称
  description: string // 描述
}

// 角色接口定义
export interface ProjectRole {
  id: string
  name: string // 角色名称
  description: string // 描述
}

// 核心诉求接口定义
export interface CoreDemand {
  id: string
  name: string // 核心诉求名称
  description: string // 描述
}

// 竞争优劣势接口定义
export interface CompetitiveAdvantage {
  id: string
  name: string // 优劣势名称
  description?: string // 描述 - CHANGED TO OPTIONAL
}

// 项目流失原因接口定义
export interface ProjectLossReason {
  id: string
  name: string // 流失原因名称
  description?: string // 描述 - CHANGED TO OPTIONAL
}

// NEW: Interfaces for WorkParams to be managed in store
export interface WorkTypeMainCategory {
  id: string
  name: string
}

export interface BaseParam {
  id: string
}

export interface WorkTypeParam extends BaseParam {
  mainCategory: string
  subCategory: string
  definition: string
}

export interface TargetProgressParam extends BaseParam {
  targetProgressName: string
  definition: string
}

export interface TaskProgressParam extends BaseParam {
  taskProgressName: string
  definition: string
}

export interface TargetStatusParam extends BaseParam {
  targetStatusName: string
  definition: string
}

export interface TaskStatusParam extends BaseParam {
  taskStatusName: string
  definition: string
}

export type AnyParam =
  | WorkTypeParam
  | TargetProgressParam
  | TaskProgressParam
  | TargetStatusParam
  | TaskStatusParam

// 添加项目落单率评分项接口定义
export interface ScoringCriteriaItem {
  id: string
  label: string
  maxScore: number
  tooltip: string
  options: Array<{ label: string; value: number }>
}

// API返回的字典大类接口
export interface SysDictCategory {
  id: string // Is string in API response e.g. "1"
  name: string
  colName: string | null
  value: string // Category code e.g. "1001"
  remark: string | null // e.g. "客户参数"
  systemFlag: string
  delFlag: number
  tenantCode: string
  createBy: string | null // Is string or null in API response
  createTime: string
  updateBy: string | null // Is string or null in API response
  updateTime: string | null
}

// API返回的字典项接口
export interface SysDictItem {
  id: string // Is string in API response e.g. "1"
  dictId: string // Is string in API response e.g. "1"
  name: string
  value: string // This is the "parameter id" for the item e.g. "100101"
  sortOrder: number
  remark: string | null // Can be empty string or have content
  delFlag: number
  tenantCode: string
  createBy: string | null // Is string or null in API response
  createTime: string
  updateBy: string | null // Is string or null in API response
  updateTime: string | null
}

// Define a generic structure for parameters that will be sourced from SysDictItem
// This can be used by components if they adapt to it.
export interface ApiBackedParam {
  id: string // Corresponds to SysDictItem.value (the functional parameter ID)
  name: string // Corresponds to SysDictItem.name
  description: string | null // Corresponds to SysDictItem.remark
  _sysDictItemId: string // Corresponds to SysDictItem.id (the DB id of the dict item for CUD)
  _dictId: string // Corresponds to SysDictItem.dictId (the category id)
}

// NEW: Interface for Evaluation Parameters - Updated for new API structure
export interface EvaluationParamType {
  id: string // Parameter type ID
  name: string // Parameter type name
  totalScore: number // Total score for this parameter type
  remark: string // Description for this parameter type
  deptId?: number
  deptName?: string
  userName?: string
  tenantCode?: string
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
  itemVOList: EvaluationParamItem[] // List of levels under this parameter type
}

export interface EvaluationParamItem {
  id: string // Level item ID
  paramId: string // Reference to parameter type ID
  levelName: string // Level name
  levelScore: number // Score for this level
  remark: string // Description for this level
  userName?: string
  tenantCode?: string
  createBy?: string
  createTime?: string
  updateBy?: string
  updateTime?: string
}

// 定义参数配置 Store
export const useParamConfigStore = defineStore('paramConfig', () => {
  // Refs for data fetched from API
  const apiParamCategories = ref<SysDictCategory[]>([])
  const apiParamItems = ref<Record<string, SysDictItem[]>>({}) // dictId -> SysDictItem[]
  const isLoadingCategories = ref(false) // New loading flag
  const hasLoadedOnceFromApi = ref(false) // New flag to track if API fetch has completed once

  // Refs for Evaluation Params - Updated
  const evaluationParamTypes = ref<EvaluationParamType[]>([])
  const isLoadingEvaluationParams = ref(false)

  // --- START: Existing hardcoded state - to be reviewed/removed/refactored ---
  // These will be gradually replaced or fed by apiParamItems
  const clientCategories = ref<any[]>([]) // Example: { id: '100101', name: '高校', description: '...' }
  const jobLevels = ref<any[]>([])
  const competitors = ref<any[]>([])
  const customerSources = ref<any[]>([])

  const projectCategories = ref<ProjectParamCategory[]>([])
  const projectStatuses = ref<any[]>([]) // Was ProjectStatus[]
  const businessTypes = ref<any[]>([]) // Was BusinessType[]
  const productServices = ref<ProductService[]>([]) // 产品及服务数据
  const isLoadingProductServices = ref(false) // 产品服务加载状态
  const fundingSources = ref<any[]>([])
  const procurementMethods = ref<any[]>([])
  const projectRoles = ref<any[]>([])
  const coreDemands = ref<any[]>([])
  const competitiveAdvantages = ref<any[]>([])
  const projectLossReasons = ref<any[]>([])
  const scoringCriteriaItems = ref<ScoringCriteriaItem[]>([
    // 注意：此硬编码数据已被弃用，现在使用动态的 evaluationParamTypes
    // 保留此处仅为向后兼容，建议迁移到 evaluationParamTypes
    {
      id: '1',
      label: '顾客及项目基本信息',
      maxScore: 10,
      tooltip: `...`,
      options: [
        { label: '10分：完全掌握', value: 10 },
        { label: '5分：部分掌握', value: 5 },
        { label: '0分：不掌握', value: 0 },
      ],
    },
    // ... other scoring items
  ])

  const workCategories = ref<WorkParamCategory[]>([])
  const workTypeMainCategoriesData = ref<WorkTypeMainCategory[]>([
    /* ... hardcoded ... */
  ])
  const workParamValuesData = ref<Record<string, Array<AnyParam>>>({
    /* ... hardcoded ... */
  })
  const salesTypes = ref<SalesType[]>([]) // 工作分类数据
  const isLoadingSalesTypes = ref(false) // 工作分类加载状态
  // --- END: Existing hardcoded state ---

  const fetchApiParamItems = async (dictId: string) => {
    try {
      const response = await request.get<SysDictItem[]>(`/manage/api/sysDict/items/${dictId}`)
      if (response.code === 200) {
        apiParamItems.value[dictId] = response.data
      } else {
        ElMessage.error(`加载参数项(ID: ${dictId})失败: ${response.msg || '未知错误'}`)
        apiParamItems.value[dictId] = [] // Ensure it's an empty array on failure to prevent issues
      }
    } catch (error) {
      ElMessage.error(`加载参数项(ID: ${dictId})时发生网络错误`)
      apiParamItems.value[dictId] = [] // Ensure it's an empty array on error
      console.error(`Error fetching API param items for dictId ${dictId}:`, error)
    }
  }

  const fetchApiParamCategories = async (forceRefresh = false) => {
    if (isLoadingCategories.value && !forceRefresh) {
      console.log('API categories fetch already in progress.')
      return
    }
    if (hasLoadedOnceFromApi.value && !forceRefresh) {
      console.log('API categories already loaded once, skipping redundant fetch unless forced.')
      return
    }

    isLoadingCategories.value = true
    ElMessage.info('开始加载参数配置...')
    try {
      const response = await request.get<SysDictCategory[]>('/manage/api/sysDict/all')
      if (response.code === 200) {
        apiParamCategories.value = response.data
        const itemFetchPromises = []
        for (const category of response.data) {
          // No await here, collect all promises
          itemFetchPromises.push(fetchApiParamItems(category.id))
        }
        await Promise.all(itemFetchPromises) // Wait for all item fetches to complete

        // 动态生成参数分类
        generateProjectCategories()
        generateWorkCategories()

        ElMessage.success('参数大类及子项加载成功')
        hasLoadedOnceFromApi.value = true // Mark that API fetch has been done
      } else {
        ElMessage.error(`加载参数大类失败: ${response.msg || '未知错误'}`)
        apiParamCategories.value = [] // Clear categories on failure
        apiParamItems.value = {} // Clear items on failure
      }
    } catch (error) {
      ElMessage.error('加载参数大类时发生网络错误')
      console.error('Error fetching API param categories:', error)
      apiParamCategories.value = []
      apiParamItems.value = {}
    } finally {
      isLoadingCategories.value = false
    }
  }

  // Fetch Evaluation Parameters - Updated for new API structure
  const fetchEvaluationParams = async (forceRefresh = false) => {
    if (isLoadingEvaluationParams.value && !forceRefresh) {
      console.log('Evaluation params fetch already in progress.')
      return
    }

    isLoadingEvaluationParams.value = true

    try {
      const response = await request.get<{
        code: number
        msg: string
        data: EvaluationParamType[]
      }>('/manage/api/evaluationParam/getList')
      console.log('API Response for evaluation params:', response)
      if (response.code === 200) {
        // Ensure that response.data is an array before assigning
        evaluationParamTypes.value = Array.isArray(response.data) ? response.data : []
        console.log('Processed evaluation param types:', evaluationParamTypes.value)
      } else {
        ElMessage.error(`加载落单率评估参数失败: ${response.msg || '未知错误'}`)
        evaluationParamTypes.value = []
      }
    } catch (error) {
      ElMessage.error('加载落单率评估参数时发生网络错误')
      console.error('Error fetching evaluation params:', error)
      evaluationParamTypes.value = []
    } finally {
      isLoadingEvaluationParams.value = false
    }
  }

  // 获取产品及服务数据
  const fetchProductServices = async (forceRefresh = false) => {
    if (isLoadingProductServices.value && !forceRefresh) {
      console.log('Product services fetch already in progress.')
      return
    }

    isLoadingProductServices.value = true

    try {
      const response = await request.get<{ code: number; msg: string; data: ProductService[] }>(
        'manage/api/productService/list',
      )
      if (response.code === 200) {
        productServices.value = Array.isArray(response.data) ? response.data : []
      } else {
        ElMessage.error(`加载产品及服务数据失败: ${response.msg || '未知错误'}`)
        productServices.value = []
      }
    } catch (error) {
      ElMessage.error('加载产品及服务数据时发生网络错误')
      console.error('Error fetching product services:', error)
      productServices.value = []
    } finally {
      isLoadingProductServices.value = false
    }
  }

  // 添加产品服务
  const addProductService = async (
    serviceData: Omit<
      ProductService,
      'id' | 'createTime' | 'updateTime' | 'createBy' | 'updateBy' | 'tenantCode'
    >,
  ) => {
    try {
      // 构建完整的请求体，包含必要的字段
      const payload = {
        id: 0, // 新增时ID为0
        name: serviceData.name,
        serviceType: serviceData.serviceType,
        productType: serviceData.productType,
        tenantCode: '',
        createBy: 0,
        createTime: '',
        updateBy: 0,
        updateTime: '',
      }

      const response = await request.post<{ code: number; msg: string; data: ProductService }>(
        'manage/api/productService/save',
        payload,
      )
      if (response.code === 200 && response.data) {
        await fetchProductServices(true)
        ElMessage.success('产品服务添加成功')
      } else {
        ElMessage.error(`产品服务添加失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('产品服务添加时发生网络错误')
      console.error('Error adding product service:', error)
    }
  }

  // 更新产品服务
  const updateProductService = async (
    serviceId: number,
    updatedData: Partial<
      Omit<
        ProductService,
        'id' | 'createTime' | 'updateTime' | 'createBy' | 'updateBy' | 'tenantCode'
      >
    >,
  ) => {
    try {
      // 先获取当前的产品服务数据
      const currentService = productServices.value.find((service) => service.id === serviceId)
      if (!currentService) {
        ElMessage.error('未找到要更新的产品服务')
        return
      }

      // 构建完整的请求体，保留原有字段并更新指定字段
      const payload = {
        id: serviceId,
        name: updatedData.name ?? currentService.name,
        serviceType: updatedData.serviceType ?? currentService.serviceType,
        productType: updatedData.productType ?? currentService.productType,
        tenantCode: currentService.tenantCode || '',
        createBy: currentService.createBy || 0,
        createTime: '',
        updateBy: 0,
        updateTime: '',
      }

      const response = await request.post('manage/api/productService/edit', payload)
      if (response.code === 200) {
        await fetchProductServices(true)
        ElMessage.success('产品服务更新成功')
      } else {
        ElMessage.error(`产品服务更新失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('产品服务更新时发生网络错误')
      console.error(`Error updating product service ${serviceId}:`, error)
    }
  }

  // 删除产品服务
  const deleteProductService = async (serviceId: number) => {
    try {
      const response = await request.delete(`manage/api/productService/delete/${serviceId}`)
      if (response.code === 200) {
        await fetchProductServices(true)
        ElMessage.success('产品服务删除成功')
      } else {
        ElMessage.error(`产品服务删除失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('产品服务删除时发生网络错误')
      console.error(`Error deleting product service ${serviceId}:`, error)
    }
  }

  // 获取工作分类数据
  const fetchSalesTypes = async (forceRefresh = false) => {
    if (isLoadingSalesTypes.value && !forceRefresh) {
      console.log('Sales types fetch already in progress.')
      return
    }

    isLoadingSalesTypes.value = true

    try {
      const response = await request.get<{ code: number; msg: string; data: SalesType[] }>(
        'manage/api/salesType/getList',
      )
      if (response.code === 200) {
        salesTypes.value = Array.isArray(response.data) ? response.data : []
      } else {
        ElMessage.error(`加载工作分类数据失败: ${response.msg || '未知错误'}`)
        salesTypes.value = []
      }
    } catch (error) {
      ElMessage.error('加载工作分类数据时发生网络错误')
      console.error('Error fetching sales types:', error)
      salesTypes.value = []
    } finally {
      isLoadingSalesTypes.value = false
    }
  }

  // 添加工作分类
  const addSalesType = async (
    salesTypeData: Omit<
      SalesType,
      'id' | 'createTime' | 'updateTime' | 'createBy' | 'updateBy' | 'tenantCode'
    >,
  ) => {
    try {
      // 构建完整的请求体
      const payload = {
        id: 0, // 新增时ID为0
        name: salesTypeData.name,
        parentId: salesTypeData.parentId || 0,
        level: salesTypeData.level,
        sequence: salesTypeData.sequence,
        tenantCode: '',
        createBy: 0,
        createTime: '',
        updateBy: 0,
        updateTime: '',
      }

      const response = await request.post<{ code: number; msg: string; data: SalesType }>(
        'manage/api/salesType/save',
        payload,
      )
      if (response.code === 200 && response.data) {
        await fetchSalesTypes(true)
        ElMessage.success('工作分类添加成功')
      } else {
        ElMessage.error(`工作分类添加失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('工作分类添加时发生网络错误')
      console.error('Error adding sales type:', error)
    }
  }

  // 更新工作分类
  const updateSalesType = async (
    salesTypeId: number,
    updatedData: Partial<
      Omit<SalesType, 'id' | 'createTime' | 'updateTime' | 'createBy' | 'updateBy' | 'tenantCode'>
    >,
  ) => {
    try {
      // 先获取当前的工作分类数据
      const currentSalesType = salesTypes.value.find((item) => item.id === salesTypeId)
      if (!currentSalesType) {
        ElMessage.error('未找到要更新的工作分类')
        return
      }

      // 构建完整的请求体，保留原有字段并更新指定字段
      const payload = {
        id: salesTypeId,
        name: updatedData.name ?? currentSalesType.name,
        parentId: updatedData.parentId ?? currentSalesType.parentId,
        level: updatedData.level ?? currentSalesType.level,
        sequence: updatedData.sequence ?? currentSalesType.sequence,
        tenantCode: currentSalesType.tenantCode || '',
        createBy: currentSalesType.createBy || 0,
        createTime: '',
        updateBy: 0,
        updateTime: '',
      }

      const response = await request.post('manage/api/salesType/edit', payload)
      if (response.code === 200) {
        await fetchSalesTypes(true)
        ElMessage.success('工作分类更新成功')
      } else {
        ElMessage.error(`工作分类更新失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('工作分类更新时发生网络错误')
      console.error(`Error updating sales type ${salesTypeId}:`, error)
    }
  }

  // 删除工作分类
  const deleteSalesType = async (salesTypeId: number) => {
    try {
      const response = await request.delete(`manage/api/salesType/delete/${salesTypeId}`)
      if (response.code === 200) {
        await fetchSalesTypes(true)
        ElMessage.success('工作分类删除成功')
      } else {
        ElMessage.error(`工作分类删除失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('工作分类删除时发生网络错误')
      console.error(`Error deleting sales type ${salesTypeId}:`, error)
    }
  }

  // Helper to get a mapped list of params for a given dictId
  const getMappedParams = (dictId: string): ApiBackedParam[] => {
    const items = apiParamItems.value[dictId] || []
    return items
      .filter((item) => item !== null && item !== undefined)
      .map((item) => ({
        id: item.value, // Functional ID
        name: item.name,
        description: item.remark,
        _sysDictItemId: item.id, // DB ID
        _dictId: item.dictId,
      }))
  }

  // CRUD operations for SysDictItems (modifies local store, persists via localStorage)
  const addApiParamItem = async (
    dictId: string,
    // newItemData contains the functional data: name, description (remark), and value (functional id)
    newItemData: {
      name: string
      description: string | null
      value: string | null // Allow null if backend auto-generates the functional ID
    },
  ) => {
    if (!apiParamItems.value[dictId]) {
      // Initialize if it's the first item for this category, though typically categories exist.
      apiParamItems.value[dictId] = []
    }

    const payload = {
      dictId: dictId,
      name: newItemData.name,
      value: newItemData.value, // This can now be null
      sortOrder: (apiParamItems.value[dictId]?.length || 0) + 1, // Basic sort order
      remark: newItemData.description,
      // parentName: "string", // Not available in current data model, omitting
    }

    try {
      // Assuming API returns an object like { code: 200, msg: "...", data: SysDictItem }
      const response = await request.post<{ code: number; msg: string; data: SysDictItem }>(
        '/manage/api/sysDict/saveItem',
        payload,
      )
      if (response.code === 200 && response.data) {
        // 添加成功后，重新拉取该分类的参数项，保证数据和顺序一致
        await fetchApiParamItems(dictId)
        ElMessage.success('参数项添加成功')
      } else {
        ElMessage.error(`参数项添加失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('参数项添加时发生网络错误')
      console.error(`Error adding API param item to dictId ${dictId}:`, error)
    }
  }

  const updateApiParamItem = async (
    dictId: string,
    sysDictItemId: string, // This is the actual DB ID of the SysDictItem
    updatedData: Partial<Omit<ApiBackedParam, '_sysDictItemId' | '_dictId'>>, // 'id' here is the functional value
  ) => {
    const items = apiParamItems.value[dictId]
    if (!items) {
      ElMessage.error('参数类别不存在')
      return
    }

    const itemIndex = items.findIndex((item) => item.id === sysDictItemId)
    if (itemIndex === -1) {
      ElMessage.error('未找到要更新的参数项')
      return
    }

    const currentItem = items[itemIndex]

    const payload = {
      id: sysDictItemId, // The database primary key of the item
      dictId: currentItem.dictId, // The ID of the dictionary category
      name: updatedData.name !== undefined ? updatedData.name : currentItem.name,
      value: updatedData.id !== undefined ? updatedData.id : currentItem.value, // 'updatedData.id' is the functional value
      sortOrder: currentItem.sortOrder, // Keep existing sortOrder as UI doesn't change it
      remark: updatedData.description !== undefined ? updatedData.description : currentItem.remark,
      // parentName: "string", // Not available in current data model, omitting
    }

    try {
      const response = await request.post('/manage/api/sysDict/updateItem', payload)
      if (response.code === 200) {
        // Update local store on successful API call
        items[itemIndex] = {
          ...currentItem,
          name: payload.name,
          value: payload.value,
          remark: payload.remark,
          // Assuming API doesn't return the full updated item with a new updateTime,
          // or if it does, response.data should be used.
          // For now, client-side timestamp:
          updateTime: new Date().toISOString(),
        }
        ElMessage.success('参数项更新成功')
      } else {
        ElMessage.error(`参数项更新失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('参数项更新时发生网络错误')
      console.error(`Error updating API param item ${sysDictItemId} in dictId ${dictId}:`, error)
    }
  }

  const deleteApiParamItem = async (dictId: string, sysDictItemId: string) => {
    const items = apiParamItems.value[dictId]
    if (!items) {
      ElMessage.error('参数类别不存在')
      return
    }
    const itemIndex = items.findIndex((item) => item.id === sysDictItemId)
    if (itemIndex === -1) {
      ElMessage.error('未找到要删除的参数项')
      return
    }

    try {
      // The API endpoint is /manage/api/sysDict/deleteItem/{id}
      const response = await request.get(`/manage/api/sysDict/deleteItem/${sysDictItemId}`)
      if (response.code === 200) {
        items.splice(itemIndex, 1)
        ElMessage.success('参数项删除成功')
      } else {
        ElMessage.error(`参数项删除失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('参数项删除时发生网络错误')
      console.error(`Error deleting API param item ${sysDictItemId} from dictId ${dictId}:`, error)
    }
  }

  // CRUD operations for EvaluationParamType - Simplified to use unified edit endpoint
  const addEvaluationParamType = async (
    paramData: Omit<
      EvaluationParamType,
      | 'id'
      | 'createTime'
      | 'updateTime'
      | 'createBy'
      | 'updateBy'
      | 'tenantCode'
      | 'deptId'
      | 'deptName'
      | 'userName'
      | 'itemVOList'
    >,
  ) => {
    try {
      // Prepare the payload using the same structure as the unified edit endpoint
      const payload = {
        projectEvaluationParamDO: {
          id: 0, // New parameter type, backend will assign ID
          name: paramData.name,
          totalScore: paramData.totalScore,
          remark: paramData.remark || '',
          deptId: 0,
          tenantCode: '',
          createBy: 0,
          createTime: '',
          updateBy: 0,
          updateTime: '',
        },
        itemDOList: [], // Empty for new parameter type, levels can be added later
        delItemIdList: [], // Empty for new parameter type
      }

      console.log('Sending payload to save endpoint:', payload)

      const response = await request.post<{ code: number; msg: string; data: EvaluationParamType }>(
        '/manage/api/evaluationParam/save',
        payload,
      )
      if (response.code === 200 && response.data) {
        await fetchEvaluationParams(true)
        ElMessage.success('评估参数类型添加成功')
      } else {
        ElMessage.error(`评估参数类型添加失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('评估参数类型添加时发生网络错误')
      console.error('Error adding evaluation param type:', error)
    }
  }

  const deleteEvaluationParamType = async (paramId: string) => {
    try {
      const response = await request.delete(`/manage/api/evaluationParam/delete/${paramId}`)
      if (response.code === 200) {
        await fetchEvaluationParams(true)
        ElMessage.success('评估参数类型删除成功')
      } else {
        ElMessage.error(`评估参数类型删除失败: ${response.msg || '未知错误'}`)
      }
    } catch (error) {
      ElMessage.error('评估参数类型删除时发生网络错误')
      console.error(`Error deleting evaluation param type ${paramId}:`, error)
    }
  }

  // Unified edit endpoint for all evaluation parameter operations
  const updateEvaluationParamWithItems = async (
    paramId: string,
    paramData: Partial<EvaluationParamType>,
    itemsToUpdate: EvaluationParamItem[] = [],
    itemIdsToDelete: string[] = [],
  ) => {
    try {
      const currentParamType = evaluationParamTypes.value.find((p) => p.id === paramId)
      if (!currentParamType) {
        ElMessage.error('未找到要更新的参数类型')
        return false
      }

      const payload = {
        projectEvaluationParamDO: {
          id: parseInt(paramId),
          name: paramData.name || currentParamType.name,
          totalScore: paramData.totalScore || currentParamType.totalScore,
          remark: paramData.remark || currentParamType.remark || '',
          deptId: currentParamType.deptId || 0,
          tenantCode: currentParamType.tenantCode || '',
          createBy: parseInt(currentParamType.createBy || '0'),
          createTime: '',
          updateBy: 0,
          updateTime: '',
        },
        itemDOList: itemsToUpdate.map((item) => ({
          id: item.id === '0' ? 0 : parseInt(item.id),
          paramId: parseInt(paramId),
          levelName: item.levelName,
          levelScore: item.levelScore,
          remark: item.remark || '',
          tenantCode: item.tenantCode || '',
          createBy: parseInt(item.createBy || '0'),
          createTime: '',
          updateBy: 0,
          updateTime: '',
        })),
        delItemIdList: itemIdsToDelete
          .map((id) => parseInt(id))
          .filter((id) => !isNaN(id) && id > 0),
      }

      console.log('Sending payload to unified edit endpoint:', payload)

      const response = await request.post('/manage/api/evaluationParam/edit', payload)
      if (response.code === 200) {
        await fetchEvaluationParams(true)
        return true
      } else {
        ElMessage.error(`操作失败: ${response.msg || '未知错误'}`)
        return false
      }
    } catch (error) {
      ElMessage.error('操作时发生网络错误')
      console.error('Error updating evaluation param with items:', error)
      return false
    }
  }

  // Simplified wrapper methods using the unified endpoint
  const updateEvaluationParamType = async (
    paramId: string,
    updatedData: Partial<Pick<EvaluationParamType, 'name' | 'totalScore' | 'remark'>>,
  ) => {
    const currentParamType = evaluationParamTypes.value.find((p) => p.id === paramId)
    if (!currentParamType) {
      ElMessage.error('未找到要更新的参数类型')
      return
    }

    const success = await updateEvaluationParamWithItems(
      paramId,
      updatedData,
      currentParamType.itemVOList || [],
      [],
    )
    if (success) {
      ElMessage.success('评估参数类型更新成功')
    }
  }

  const addEvaluationParamItem = async (
    paramId: string,
    itemData: Pick<EvaluationParamItem, 'levelName' | 'levelScore' | 'remark'>,
  ) => {
    const currentParamType = evaluationParamTypes.value.find((p) => p.id === paramId)
    if (!currentParamType) {
      ElMessage.error('未找到要添加级别的参数类型')
      return
    }

    const newItem: EvaluationParamItem = {
      id: '0',
      paramId: paramId,
      levelName: itemData.levelName,
      levelScore: itemData.levelScore,
      remark: itemData.remark,
      tenantCode: '',
      createBy: '0',
      createTime: '',
      updateBy: '0',
      updateTime: '',
    }

    const allItems = [...(currentParamType.itemVOList || []), newItem]
    const success = await updateEvaluationParamWithItems(paramId, {}, allItems, [])
    if (success) {
      ElMessage.success('评估参数级别添加成功')
    }
  }

  const updateEvaluationParamItem = async (
    itemId: string,
    updatedData: Partial<Pick<EvaluationParamItem, 'levelName' | 'levelScore' | 'remark'>>,
  ) => {
    let currentParamType: EvaluationParamType | undefined
    let currentItem: EvaluationParamItem | undefined

    for (const paramType of evaluationParamTypes.value) {
      const item = paramType.itemVOList?.find((item) => item.id === itemId)
      if (item) {
        currentParamType = paramType
        currentItem = item
        break
      }
    }

    if (!currentParamType || !currentItem) {
      ElMessage.error('未找到要更新的级别项')
      return
    }

    const updatedItem: EvaluationParamItem = {
      ...currentItem,
      levelName: updatedData.levelName ?? currentItem.levelName,
      levelScore: updatedData.levelScore ?? currentItem.levelScore,
      remark: updatedData.remark ?? currentItem.remark,
      updateTime: new Date().toISOString(),
    }

    const allItems = (currentParamType.itemVOList || []).map((item) =>
      item.id === itemId ? updatedItem : item,
    )

    const success = await updateEvaluationParamWithItems(currentParamType.id, {}, allItems, [])
    if (success) {
      ElMessage.success('评估参数级别更新成功')
    }
  }

  const deleteEvaluationParamItem = async (itemId: string) => {
    let currentParamType: EvaluationParamType | undefined

    for (const paramType of evaluationParamTypes.value) {
      const item = paramType.itemVOList?.find((item) => item.id === itemId)
      if (item) {
        currentParamType = paramType
        break
      }
    }

    if (!currentParamType) {
      ElMessage.error('未找到要删除的级别项')
      return
    }

    const remainingItems = (currentParamType.itemVOList || []).filter((item) => item.id !== itemId)
    const success = await updateEvaluationParamWithItems(currentParamType.id, {}, remainingItems, [
      itemId,
    ])
    if (success) {
      ElMessage.success('评估参数级别删除成功')
    }
  }

  // 保存和加载配置
  const saveParamConfig = () => {
    // Only save API related data if it has been successfully fetched at least once
    if (hasLoadedOnceFromApi.value) {
      localStorage.setItem('apiParamCategories', JSON.stringify(apiParamCategories.value))
      localStorage.setItem('apiParamItems', JSON.stringify(apiParamItems.value))
      localStorage.setItem('hasLoadedOnceFromApi', JSON.stringify(hasLoadedOnceFromApi.value))
    }
    // Save other potentially still local/complex data always
    localStorage.setItem('scoringCriteriaItems', JSON.stringify(scoringCriteriaItems.value))
    localStorage.setItem(
      'workTypeMainCategoriesData',
      JSON.stringify(workTypeMainCategoriesData.value),
    )
    localStorage.setItem('workParamValuesData', JSON.stringify(workParamValuesData.value))
    // Save evaluation params - updated reference
    localStorage.setItem('evaluationParamTypes', JSON.stringify(evaluationParamTypes.value))
    // Save product services
    localStorage.setItem('productServices', JSON.stringify(productServices.value))
    // Save sales types
    localStorage.setItem('salesTypes', JSON.stringify(salesTypes.value))
    // Old hardcoded refs - remove if fully replaced by API
    localStorage.setItem('clientCategories_local', JSON.stringify(clientCategories.value))
    localStorage.setItem('jobLevels_local', JSON.stringify(jobLevels.value))
    // ... and so on for all other hardcoded refs that are being phased out
  }

  watch(
    [
      apiParamCategories,
      apiParamItems,
      scoringCriteriaItems,
      workTypeMainCategoriesData,
      workParamValuesData,
      hasLoadedOnceFromApi,
      evaluationParamTypes, // Updated reference
      productServices, // Watch productServices for changes
      salesTypes, // Watch salesTypes for changes
    ],
    saveParamConfig,
    { deep: true },
  )

  const loadParamConfig = () => {
    const storedHasLoadedOnce = localStorage.getItem('hasLoadedOnceFromApi')
    if (storedHasLoadedOnce) {
      try {
        hasLoadedOnceFromApi.value = JSON.parse(storedHasLoadedOnce)
      } catch (e) {
        console.error('Failed to parse hasLoadedOnceFromApi', e)
        hasLoadedOnceFromApi.value = false // Reset if parsing fails
      }
    }

    // Load API data only if it was previously fetched and saved
    if (hasLoadedOnceFromApi.value) {
      const storedApiParamCategories = localStorage.getItem('apiParamCategories')
      if (storedApiParamCategories)
        try {
          apiParamCategories.value = JSON.parse(storedApiParamCategories)
        } catch (e) {
          console.error('Failed to parse apiParamCategories', e)
        }

      const storedApiParamItems = localStorage.getItem('apiParamItems')
      if (storedApiParamItems)
        try {
          apiParamItems.value = JSON.parse(storedApiParamItems)
        } catch (e) {
          console.error('Failed to parse apiParamItems', e)
        }
    }

    // Load other potentially still local/complex data always
    const storedScoringCriteriaItems = localStorage.getItem('scoringCriteriaItems')
    if (storedScoringCriteriaItems)
      try {
        scoringCriteriaItems.value = JSON.parse(storedScoringCriteriaItems)
      } catch (e) {
        console.error('Failed to parse scoringCriteriaItems', e)
      }

    const storedWorkTypeMainCategoriesData = localStorage.getItem('workTypeMainCategoriesData')
    if (storedWorkTypeMainCategoriesData)
      try {
        workTypeMainCategoriesData.value = JSON.parse(storedWorkTypeMainCategoriesData)
      } catch (e) {
        console.error('Failed to parse workTypeMainCategoriesData', e)
      }

    const storedWorkParamValuesData = localStorage.getItem('workParamValuesData')
    if (storedWorkParamValuesData)
      try {
        workParamValuesData.value = JSON.parse(storedWorkParamValuesData)
      } catch (e) {
        console.error('Failed to parse workParamValuesData', e)
      }

    // Load evaluation params - updated reference
    const storedEvaluationParams = localStorage.getItem('evaluationParamTypes')
    if (storedEvaluationParams) {
      try {
        evaluationParamTypes.value = JSON.parse(storedEvaluationParams)
      } catch (e) {
        console.error('Failed to parse evaluationParamTypes', e)
      }
    }

    // Load product services
    const storedProductServices = localStorage.getItem('productServices')
    if (storedProductServices) {
      try {
        productServices.value = JSON.parse(storedProductServices)
      } catch (e) {
        console.error('Failed to parse productServices', e)
      }
    }

    // Load sales types
    const storedSalesTypes = localStorage.getItem('salesTypes')
    if (storedSalesTypes) {
      try {
        salesTypes.value = JSON.parse(storedSalesTypes)
      } catch (e) {
        console.error('Failed to parse salesTypes', e)
      }
    }

    // Removed the automatic call to fetchApiParamCategories from here.
    // It will be called from ParamsManager.vue onMounted instead.
  }

  loadParamConfig()

  // 动态生成项目参数分类
  const generateProjectCategories = () => {
    const projectApiCategories = apiParamCategories.value.filter((cat) => cat.remark === '项目参数')
    projectCategories.value = projectApiCategories.map((category) => ({
      id: category.id,
      name: category.name,
    }))
  }

  // 动态生成工作参数分类
  const generateWorkCategories = () => {
    const workApiCategories = apiParamCategories.value.filter((cat) => cat.remark === '工作参数')
    workCategories.value = workApiCategories.map((category) => ({
      id: category.id,
      name: category.name,
    }))
  }

  return {
    apiParamCategories,
    apiParamItems,
    isLoadingCategories, // Expose loading state
    hasLoadedOnceFromApi,
    fetchApiParamCategories,
    // fetchApiParamItems, // No longer need to expose, called internally
    getMappedParams,
    addApiParamItem,
    updateApiParamItem,
    deleteApiParamItem,

    // Still exposing these for now, will be refactored or removed
    clientCategories, // To be replaced by getMappedParams(dictIdForClientCategories)
    jobLevels, // To be replaced
    competitors,
    customerSources,

    projectCategories, // This array defines the *structure* of the project params tab, names and IDs might need to align with apiParamCategories
    projectStatuses, // To be replaced by getMappedParams(dictIdForProjectStatuses)
    businessTypes,
    productServices, // 产品及服务数据
    isLoadingProductServices, // 产品服务加载状态
    fundingSources,
    procurementMethods,
    projectRoles,
    coreDemands,
    competitiveAdvantages,
    projectLossReasons,
    scoringCriteriaItems, // Complex type, likely remains local

    workCategories, // Similar to projectCategories, defines structure of work params tab
    workTypeMainCategoriesData, // Complex, review separately
    workParamValuesData, // Complex, review separately

    // Actions for complex types (if they remain local)
    addWorkTypeMainCategory: (name: string) => {
      /* existing logic */
    },
    updateWorkTypeMainCategory: (id: string, newName: string) => {
      /* existing logic */
    },
    deleteWorkTypeMainCategory: (id: string) => {
      /* existing logic */
    },
    addWorkParamItem: (categoryId: string, itemData: Omit<AnyParam, 'id'>) => {
      /* existing logic */
    },
    updateWorkParamItem: (
      categoryId: string,
      itemId: string,
      itemData: Partial<Omit<AnyParam, 'id'>>,
    ) => {
      /* existing logic */
    },
    deleteWorkParamItem: (categoryId: string, itemId: string) => {
      /* existing logic */
    },

    // Evaluation Params - Updated references and methods
    evaluationParamTypes,
    isLoadingEvaluationParams,
    fetchEvaluationParams,
    addEvaluationParamType,
    updateEvaluationParamType,
    deleteEvaluationParamType,
    addEvaluationParamItem,
    updateEvaluationParamItem,
    deleteEvaluationParamItem,
    updateEvaluationParamWithItems, // New unified update method

    // New product services related methods
    fetchProductServices,
    addProductService,
    updateProductService,
    deleteProductService,

    // New work category related methods
    fetchSalesTypes,
    addSalesType,
    updateSalesType,
    deleteSalesType,

    salesTypes, // 工作分类数据
    isLoadingSalesTypes, // 工作分类加载状态

    // 动态生成参数分类的方法
    generateProjectCategories,
    generateWorkCategories,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useParamConfigStore, import.meta.hot))
}
