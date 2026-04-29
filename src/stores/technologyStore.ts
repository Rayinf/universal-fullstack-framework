import { defineStore, acceptHMRUpdate } from 'pinia'
import { ref, computed } from 'vue'
import request from '../utils/request'
import type {
  Product,
  ProductInfo,
  ProductQueryDTO,
  ProductSaveDTO,
  Process,
  ProcessRoute,
  Document,
  OutsourcedDocument,
  TestSpecification,
  DocumentVersion,
  ProductFilter,
  DocumentFilter,
  ProcessLibrary,
  ProcessLibraryItem,
  ProcessLibraryItemParam,
  ProcessLibrarySaveDTO,
  ProcessLibraryItemSaveDTO,
  ProcessLibraryItemParamBatchSaveDTO,
  ProcessLibraryItemMiddleDTO,
  PageResult,
  RoutFlowInfo,
  ProcessRouteInfo,
  ProcessRouteSaveDTO,
  ProcessRouteUpdateDTO,
  WorkInstructionInfo,
  WorkInstructionSaveDTO,
  WorkInstructionUpdateDTO,
  WorkInstructionQueryDTO,
  OutsourcedDocumentInfo,
  OutsourcedDocumentSaveDTO,
  OutsourcedDocumentUpdateDTO,
  OutsourcedDocumentQueryDTO,
  TestSpecificationInfo,
  TestSpecificationSaveDTO,
  TestSpecificationUpdateDTO,
  TestSpecificationQueryDTO,
} from '../types/technology'
import {
  getWorkInstructionPage,
  saveWorkInstruction,
  updateWorkInstructionFile,
  updateWorkInstructionInfo,
  changeWorkInstructionStatus,
  getWorkInstructionVersions,
  downloadWorkInstruction,
} from '@/api/workInstruction'
import {
  getOutsourcedDocumentPage,
  saveOutsourcedDocument,
  updateOutsourcedDocumentInfo,
  updateOutsourcedDocumentFile,
  changeOutsourcedDocumentStatus,
  getOutsourcedDocumentVersions,
} from '@/api/outsourced'
import {
  getTestSpecificationPage,
  saveTestSpecification,
  updateTestSpecificationInfo,
  updateTestSpecificationFile,
  changeTestSpecificationStatus,
  getTestSpecificationVersions,
} from '@/api/testSpecification'

export const useTechnologyStore = defineStore('technology', () => {
  // ===== 产品信息 =====

  const products = ref<Product[]>([])
  const productsLoading = ref(false)
  const productTotal = ref(0)

  // 辅助函数：将后端 ProductInfo 转换为前端 Product
  const convertProductInfoToProduct = (info: ProductInfo): Product => {
    const statusMap: Record<number, '有效' | '试产' | '停产'> = {
      1: '有效',
      2: '试产',
      3: '停产',
    }

    return {
      id: String(info.id),
      productCode: info.productNo,
      productName: info.productName,
      productModel: info.productModel,
      productSeries: '', // 后端没有 productSeries,可根据 productCategory 映射
      productCategory: String(info.productCategory),
      status: statusMap[info.progressStatus] || '有效',
      description: info.remarks || '',
      processIds: [], // 后端暂无关联工序数据
      createdBy: String(info.createBy || ''),
      createdAt: info.createTime || '',
      updatedAt: info.updateTime || '',
    }
  }

  // 辅助函数：将前端 Product 数据转换为后端 ProductSaveDTO
  const convertProductToSaveDTO = (product: Partial<Product>, id?: string): ProductSaveDTO => {
    const statusMap: Record<string, number> = {
      有效: 1,
      试产: 2,
      停产: 3,
    }

    return {
      id: id ? Number(id) : undefined,
      productName: product.productName || '',
      productNo: product.productCode || '',
      productCategory: Number(product.productCategory) || 0,
      productModel: product.productModel || '',
      progressStatus: statusMap[product.status || '有效'] || 1,
      remarks: product.description || '',
    }
  }

  // 获取产品列表
  const fetchProducts = async (filter?: ProductFilter & { current?: number; size?: number }) => {
    productsLoading.value = true
    try {
      const queryParams: ProductQueryDTO & { current?: number; size?: number } = {
        keyword: filter?.keyword,
        productCategory: filter?.productCategory ? Number(filter.productCategory) : undefined,
        progressStatus: filter?.status ? { 有效: 1, 试产: 2, 停产: 3 }[filter.status] : undefined,
        startDate: filter?.dateRange?.[0],
        endDate: filter?.dateRange?.[1],
        sortColumn: filter?.sortBy || 'create_time',
        sortType: filter?.sortOrder || 'desc',
        current: filter?.current || 1,
        size: filter?.size || 10,
      }

      const res = await request.get<PageResult<ProductInfo>>(
        '/manage/api/projectInfo/page',
        queryParams,
      )

      if (isSuccess(res.code)) {
        let records: ProductInfo[] = []
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          productTotal.value = res.data.total || 0
        } else if (Array.isArray(res.data)) {
          records = res.data
          productTotal.value = records.length
        }

        products.value = records.map(convertProductInfoToProduct)
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Fetch Products Error:', error)
      return { success: false, message: '获取产品列表失败' }
    } finally {
      productsLoading.value = false
    }
  }

  // 创建产品
  const createProduct = async (data: Partial<Product>) => {
    try {
      const saveDTO = convertProductToSaveDTO(data)
      const res = await request.post('/manage/api/projectInfo/save', saveDTO)

      if (isSuccess(res.code)) {
        await fetchProducts()
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Create Product Error:', error)
      return { success: false, message: '创建产品失败' }
    }
  }

  // 更新产品
  const updateProduct = async (id: string, data: Partial<Product>) => {
    try {
      const updateDTO = convertProductToSaveDTO(data, id)
      const res = await request.post('/manage/api/projectInfo/update', updateDTO)

      if (isSuccess(res.code)) {
        await fetchProducts()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Update Product Error:', error)
      return { success: false, message: '更新产品失败' }
    }
  }

  // 删除产品
  const deleteProduct = async (id: string) => {
    try {
      const res = await request.delete(`/manage/api/projectInfo/${id}`)

      if (isSuccess(res.code)) {
        await fetchProducts()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Delete Product Error:', error)
      return { success: false, message: '删除产品失败' }
    }
  }

  // 通过ID获取产品详情
  const getProductDetail = async (id: string) => {
    try {
      const res = await request.get<ProductInfo>(`/manage/api/projectInfo/${id}`)

      if (isSuccess(res.code) && res.data) {
        return convertProductInfoToProduct(res.data)
      }
      return null
    } catch (error) {
      console.error('Get Product Detail Error:', error)
      return null
    }
  }

  // ===== 工序库 (Process Library - Level 1) =====
  const processLibraries = ref<ProcessLibrary[]>([])
  const processLibrariesLoading = ref(false)
  const processLibraryTotal = ref(0)

  // 辅助函数：判断响应是否成功 (兼容 0 和 200)
  const isSuccess = (code: number) => code === 0 || code === 200

  // 获取工艺库列表
  const fetchProcessLibraries = async (params: any = {}) => {
    processLibrariesLoading.value = true
    try {
      // 接口要求参数平铺，不区分 page 和 dto
      // 默认分页参数
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        ...params,
      }

      // 移除可能存在的嵌套对象，防止 axios 序列化异常
      delete queryParams.page
      delete queryParams.dto

      const res = await request.get<PageResult<ProcessLibrary>>('/manage/api/processLibrary/page', {
        sortColumn: 'create_time',
        sortType: 'desc',
        ...queryParams,
      })

      // 修正：后端可能返回 code: 200，且 data 结构可能直接是 PageResult 或包裹在 records 中
      // 根据用户提供的 PageResult 定义：{ records: [], total: 0, ... }
      if (isSuccess(res.code)) {
        let records: any[] = []
        let total = 0

        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }

        // 数据标准化：确保数值类型字段正确 (后端可能返回字符串 "1")
        processLibraries.value = records.map((item: any) => ({
          ...item,
          isKey: Number(item.isKey),
          processStatus: Number(item.processStatus),
          // 确保 items 存在
          items: item.items || [],
        })) as ProcessLibrary[]

        processLibraryTotal.value = total
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Fetch Process Libraries Error:', error)
      return { success: false, message: '获取工艺库列表失败' }
    } finally {
      processLibrariesLoading.value = false
    }
  }

  // 内部辅助函数：解析 JSON 字符串
  const safeParse = (jsonStr: any) => {
    if (!jsonStr) return null
    if (typeof jsonStr === 'object') return jsonStr
    try {
      return JSON.parse(jsonStr)
    } catch (e) {
      return null
    }
  }

  // 修改 getProcessLibraryDetail 方法
  const getProcessLibraryDetail = async (libId: string, orderId?: string) => {
    try {
      const res = await request.get<any>('/manage/api/processLibrary/getProcessLibraryItemInfo', {
        processLibraryId: libId,
        orderId: orderId, // 尝试传递 orderId 供回显使用
      })
      if (isSuccess(res.code) && res.data) {
        const lib = res.data.processLibraryVO || {}
        const items = res.data.processLibraryItemAllVO || []

        const normalizedItems = items.map((wrapper: any) => {
          const itemVO = wrapper.processLibraryItemVO || {}
          const paramVOS = wrapper.processLibraryItemParamVOS || []

          return {
            ...itemVO,
            id: String(itemVO.processLibraryItemId || itemVO.id),
            jsonConfig: safeParse(itemVO.jsonConfig),
            params: paramVOS.map((p: any) => ({
              ...p,
              id: String(p.id),
              jsonConfig: safeParse(p.jsonConfig),
              // 保留已填写的参数值供回显
              paramValue: p.paramValue,
            })),
          }
        })

        return {
          ...lib,
          id: String(lib.id),
          items: normalizedItems,
        }
      }
      return null
    } catch (error) {
      return null
    }
  }

  // 创建工序
  const createProcessLibrary = async (data: ProcessLibrarySaveDTO) => {
    try {
      const res = await request.post('/manage/api/processLibrary/save', data)
      // 修改：save 接口返回 null data，但 code 为 200 表示成功
      if (isSuccess(res.code)) {
        await fetchProcessLibraries()
        // 无法返回 ID，前端需要处理后续流程
        return { success: true, data: null }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建失败' }
    }
  }

  // 更新工序
  const updateProcessLibrary = async (data: ProcessLibrarySaveDTO) => {
    try {
      const res = await request.post('/manage/api/processLibrary/update', data)
      if (isSuccess(res.code)) {
        await fetchProcessLibraries()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新失败' }
    }
  }

  // 删除工序
  const deleteProcessLibrary = async (id: string) => {
    try {
      const res = await request.delete(`/manage/api/processLibrary/${id}`)
      if (isSuccess(res.code)) {
        await fetchProcessLibraries()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '删除失败' }
    }
  }

  // ===== 表单分组 (Process Library Item - Level 2) =====

  // 获取工艺库详情 (包含子项)
  const fetchProcessLibraryDetail = async (id: string, orderId?: string) => {
    try {
      const res = await request.get(`/manage/api/processLibrary/getProcessLibraryItemInfo`, {
        processLibraryId: id,
        orderId: orderId,
      })
      if (isSuccess(res.code)) {
        // 数据适配：确保返回 items 字段
        const data = res.data || {}
        if (data.processLibraryItemAllVO) {
          // 结构扁平化：从 { processLibraryItemVO: {...} } 中提取 item 信息
          data.items = data.processLibraryItemAllVO.map((wrapper: any) => {
            const itemVO = wrapper.processLibraryItemVO || {}
            const realId = itemVO.processLibraryItemId || itemVO.id
            const paramVOS = wrapper.processLibraryItemParamVOS || []
            return {
              ...itemVO,
              id: String(realId), // Use business ID
              jsonConfig: safeParse(itemVO.jsonConfig),
              params: paramVOS.map((p: any) => ({
                ...p,
                id: String(p.id),
                jsonConfig: safeParse(p.jsonConfig),
                paramValue: p.paramValue,
              })),
            }
          })
        }
        return { success: true, data: data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取详情失败' }
    }
  }

  // 获取分组列表 (独立页面用)
  const fetchProcessLibraryItems = async (params: any = {}) => {
    try {
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      }
      delete queryParams.page
      delete queryParams.dto

      const res = await request.get<PageResult<ProcessLibraryItem>>(
        '/manage/api/processLibraryItem/page',
        queryParams,
      )

      if (isSuccess(res.code)) {
        let records: ProcessLibraryItem[] = []
        let total = 0
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }
        // 确保 id 为字符串
        return {
          success: true,
          data: {
            records: records.map((r) => ({ ...r, id: String(r.id) })),
            total: total,
          },
        }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error(error)
      return { success: false, message: '获取分组列表失败' }
    }
  }

  // 创建分组
  const createProcessLibraryItem = async (data: ProcessLibraryItemSaveDTO) => {
    try {
      const res = await request.post('/manage/api/processLibraryItem/save', data)
      if (isSuccess(res.code)) {
        return { success: true, data: res.data || {} }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建分组失败' }
    }
  }

  const updateProcessLibraryItem = async (data: ProcessLibraryItemSaveDTO) => {
    try {
      const res = await request.post('/manage/api/processLibraryItem/update', data)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新分组失败' }
    }
  }

  const deleteProcessLibraryItem = async (id: string) => {
    try {
      const res = await request.delete(`/manage/api/processLibraryItem/${id}`)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '删除分组失败' }
    }
  }

  // 获取 Item 详情（包含 Params）
  const getProcessLibraryItemDetail = async (
    itemId: string,
    orderId?: string,
    sorterIndex?: number,
  ) => {
    try {
      const params: any = { itemId }
      if (orderId) params.orderId = orderId
      if (sorterIndex !== undefined) params.sorterIndex = sorterIndex

      const url =
        orderId || sorterIndex !== undefined
          ? `/manage/api/processLibraryItem/getItemDetailByIdAndIndex`
          : `/manage/api/processLibraryItem/getItemDetailById`

      const res = await request.get(url, params)
      if (isSuccess(res.code) && res.data) {
        // 如果后端返回的是数组，取第一个; 否则直接使用对象
        const itemWrapper = Array.isArray(res.data) ? res.data[0] : res.data

        // 处理嵌套结构: { processLibraryItemVO: {...}, processLibraryItemParamVOS: [...] }
        // 兼容直接返回 Item 对象 (旧结构)
        const item = itemWrapper.processLibraryItemVO || itemWrapper

        // 映射 params
        // 优先使用 processLibraryItemParamVOS，其次 params，最后默认为空数组
        if (Array.isArray(itemWrapper.processLibraryItemParamVOS)) {
          item.params = itemWrapper.processLibraryItemParamVOS
        } else if (Array.isArray(item.params)) {
          // 如果已经是 params 字段名，直接使用
          item.params = item.params
        } else {
          item.params = []
        }
        return item
      }
      return null
    } catch (error) {
      return null
    }
  }

  // ===== 参数字段 (Process Library Item Param - Level 3) =====

  // 获取字段库列表 (独立)
  const fetchProcessLibraryItemParams = async (params: any = {}) => {
    try {
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      }
      delete queryParams.page
      delete queryParams.dto

      const res = await request.get<PageResult<ProcessLibraryItemParam>>(
        '/manage/api/processLibraryItemParam/page',
        queryParams,
      )

      if (isSuccess(res.code)) {
        let records: ProcessLibraryItemParam[] = []
        let total = 0
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }
        return {
          success: true,
          data: {
            records: records.map((r) => ({ ...r, id: String(r.id) })),
            total: total,
          },
        }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取字段列表失败' }
    }
  }

  const createProcessLibraryItemParam = async (data: any) => {
    try {
      const res = await request.post('/manage/api/processLibraryItemParam/save', data)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建字段失败' }
    }
  }

  const updateProcessLibraryItemParam = async (data: any) => {
    try {
      const res = await request.post('/manage/api/processLibraryItemParam/update', data)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新字段失败' }
    }
  }

  const deleteProcessLibraryItemParam = async (id: string) => {
    try {
      const res = await request.delete(`/manage/api/processLibraryItemParam/${id}`)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '删除字段失败' }
    }
  }

  // ===== 关联操作 =====

  // 关联工序与分组 (Level 1 <-> Level 2)
  const connectLibraryAndItems = async (dto: ProcessLibraryItemMiddleDTO) => {
    try {
      // 对应 /api/processLibrary/saveItemParams
      const res = await request.post('/manage/api/processLibrary/saveItemParams', dto)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '关联失败' }
    }
  }

  // 批量保存分组下的参数 (Level 2 <-> Level 3)
  const saveItemParams = async (dto: ProcessLibraryItemParamBatchSaveDTO) => {
    try {
      // 对应 /api/processLibraryItem/saveItemParam
      const res = await request.post('/manage/api/processLibraryItem/saveItemParam', dto)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '保存字段失败' }
    }
  }

  // ===== 工序库 (Standard Process - Old Mock Data for other pages) =====
  // 保持原有 mock 数据以防破坏其他页面
  const processes = ref<Process[]>([])
  const processesLoading = ref(false)
  const mockProcesses: Process[] = [] // 清空 Mock

  const fetchProcesses = async () => {
    // 尝试调用真实接口，如果失败则返回空
    processesLoading.value = true
    try {
      // 猜测旧接口路径，或暂时留空等待后续对接
      // const res = await request.get('/manage/api/process/list')
      // if (res.code === 0) processes.value = res.data
      processes.value = []
      return { success: true }
    } catch (e) {
      return { success: false }
    } finally {
      processesLoading.value = false
    }
  }

  // ... keep other mock functions for Standard Process ...
  const createProcess = async (data: Partial<Process>) => {
    return { success: true }
  }
  const updateProcess = async (id: string, data: Partial<Process>) => {
    return { success: true }
  }
  const deleteProcess = async (id: string) => {
    return { success: true }
  }
  const isProcessReferenced = (id: string) => false
  const getProcessReferences = (id: string) => []
  // ===== 工艺路线 (Process Route) =====
  const processRoutes = ref<ProcessRouteInfo[]>([])
  const routesLoading = ref(false)
  const routeTotal = ref(0)

  // 获取工艺路线列表
  const fetchProcessRoutes = async (params: any = {}) => {
    routesLoading.value = true
    try {
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      }
      delete queryParams.page
      delete queryParams.dto

      const res = await request.get<PageResult<ProcessRouteInfo>>(
        '/manage/api/processRoute/page',
        queryParams,
      )

      if (isSuccess(res.code)) {
        let records: any[] = []
        let total = 0
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }

        processRoutes.value = records.map((r) => ({
          ...r,
          id: String(r.id),
          projectInfoId: String(r.projectInfoId),
          processStatus: Number(r.processStatus), // 1：生效 2：草稿
        }))
        routeTotal.value = total
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取工艺路线列表失败' }
    } finally {
      routesLoading.value = false
    }
  }

  // 获取工艺路线详情
  const getProcessRouteDetail = async (id: string) => {
    try {
      const res = await request.get<any>('/manage/api/processRoute/detailByProcessRouteId', {
        detailByProcessRouteId: id,
      })
      if (isSuccess(res.code) && res.data) {
        const data = res.data
        const mainInfo = data.processRouteVO || {}
        const flowList = data.processRouteLibraryFlowList || []
        const deptList = data.processRouteLibraryDeptMiddleVOList || []

        return {
          ...mainInfo,
          id: String(mainInfo.id),
          projectInfoId: String(mainInfo.projectInfoId),
          processStatus: Number(mainInfo.processStatus),
          // 映射工序序列
          routFlowInfos: flowList.map((f: any) => {
            // 匹配班组信息
            const dept = deptList.find(
              (d: any) => String(d.projectLibraryId) === String(f.processLibraryId),
            )
            return {
              ...f,
              id: String(f.id),
              processRouteId: String(f.processRouteId),
              processLibraryId: String(f.processLibraryId),
              processName: f.processLibraryName || f.processName,
              deptName: dept ? dept.name : '', // 注入班组名称
            }
          }),
        }
      }
      return null
    } catch (error) {
      return null
    }
  }

  // 保存工艺路线基本信息 (全量提交, 统一调 save)
  const saveProcessRoute = async (data: ProcessRouteSaveDTO) => {
    try {
      const res = await request.post('/manage/api/processRoute/save', data)
      if (isSuccess(res.code)) {
        await fetchProcessRoutes()
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '保存失败' }
    }
  }

  // 新增工艺路线
  const createProcessRoute = async (data: ProcessRouteSaveDTO) => {
    try {
      const res = await request.post('/manage/api/processRoute/save', data)
      if (isSuccess(res.code)) {
        await fetchProcessRoutes()
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建失败' }
    }
  }

  // 更新工艺路线
  const updateProcessRoute = async (data: ProcessRouteSaveDTO) => {
    try {
      const res = await request.post('/manage/api/processRoute/update', data)
      if (isSuccess(res.code)) {
        await fetchProcessRoutes()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新失败' }
    }
  }

  const deleteProcessRoute = async (id: string) => {
    try {
      const res = await request.delete(`/manage/api/processRoute/${id}`)
      if (isSuccess(res.code)) {
        await fetchProcessRoutes()
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '删除失败' }
    }
  }

  // 保存工艺路线工序排序信息 (统一调 saveRoutFlowInfo)
  const saveRouteFlowInfo = async (list: RoutFlowInfo[]) => {
    try {
      const res = await request.post('/manage/api/processRoute/saveRoutFlowInfo', list)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '保存排序失败' }
    }
  }

  // ===== 作业指导书 (Work Instruction) =====
  const workInstructions = ref<WorkInstructionInfo[]>([])
  const workInstructionsLoading = ref(false)
  const workInstructionTotal = ref(0)

  // 获取作业指导书列表 (分页)
  const fetchWorkInstructions = async (params: WorkInstructionQueryDTO = {}) => {
    workInstructionsLoading.value = true
    try {
      const queryParams: WorkInstructionQueryDTO = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: 'create_time',
        sortType: 'desc',
        ...params,
      }

      const res = await getWorkInstructionPage(queryParams)

      if (isSuccess(res.code)) {
        let records: any[] = []
        if (Array.isArray(res.data)) {
          records = res.data
        } else if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          workInstructionTotal.value = res.data.total
        }

        workInstructions.value = records.map((r) => ({
          ...r,
          id: String(r.id),
          createBy: String(r.createBy),
          updateBy: String(r.updateBy),
        }))
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Fetch Work Instructions Error:', error)
      return { success: false, message: '获取作业指导书列表失败' }
    } finally {
      workInstructionsLoading.value = false
    }
  }

  // 创建作业指导书
  const createWorkInstruction = async (data: WorkInstructionSaveDTO) => {
    try {
      const formData = new FormData()
      Object.keys(data).forEach((key) => {
        // 排除 createTime 和 updateTime 字段
        if (key === 'createTime' || key === 'updateTime') return

        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })

      const res = await saveWorkInstruction(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建失败' }
    }
  }

  // 更新作业指导书 (文件/修订)
  const updateWorkInstruction = async (data: WorkInstructionUpdateDTO) => {
    try {
      const formData = new FormData()

      // 白名单：只传递修订文件时需要的字段
      const allowedFields = [
        'originalFileName',
        'fileType',
        'version',
        'remark',
        'fileStatus',
        'revisedContent',
        'changeReason',
        'suffixName',
        'files',
        'libraryWorkInstructionFileId',
      ]

      allowedFields.forEach((key) => {
        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })

      const res = await updateWorkInstructionFile(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新失败' }
    }
  }

  // 更新作业指导书基础信息
  const updateWorkInstructionInfoAction = async (data: any) => {
    try {
      // 排除 createTime 和 updateTime 字段
      const { createTime, updateTime, ...rest } = data
      const res = await updateWorkInstructionInfo(rest)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新信息失败' }
    }
  }

  // 修改作业指导书状态
  const updateWorkInstructionStatus = async (id: string, status: number) => {
    try {
      const res = await changeWorkInstructionStatus(id, status)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '状态修改失败' }
    }
  }

  // 获取作业指导书版本历史
  const fetchWorkInstructionVersions = async (fileId: string) => {
    try {
      const res = await getWorkInstructionVersions(fileId)
      if (isSuccess(res.code)) {
        const versions = (res.data || []).map((v: any) => ({
          ...v,
          id: String(v.id),
          createBy: String(v.createBy),
          updateBy: String(v.updateBy),
        }))
        return { success: true, data: versions }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取历史版本失败' }
    }
  }

  // Old mock documents (Deprecated but kept for now if used elsewhere)
  const documents = ref<Document[]>([])
  const documentsLoading = ref(false)
  const publishedDocuments = computed(() => documents.value)
  const fetchDocuments = async (params?: any) => {
    return { success: true }
  }
  const uploadDocument = async (data?: any) => {
    return { success: true }
  }
  const updateDocumentVersion = async (data?: any) => {
    return { success: true }
  }
  const publishDocument = async (id?: any) => {
    return { success: true }
  }

  // ===== 委外设计文件 =====
  const outsourcedDocuments = ref<OutsourcedDocumentInfo[]>([])
  const outsourcedDocumentsLoading = ref(false)
  const outsourcedDocumentTotal = ref(0)

  const fetchOutsourcedDocuments = async (params: OutsourcedDocumentQueryDTO = {}) => {
    outsourcedDocumentsLoading.value = true
    try {
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: params.sortColumn || 'create_time',
        sortType: params.sortType || 'desc',
        ...params,
      }
      const res = await getOutsourcedDocumentPage(queryParams)
      if (isSuccess(res.code)) {
        let records: OutsourcedDocumentInfo[] = []
        let total = 0
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }

        outsourcedDocuments.value = records.map((r) => ({
          ...r,
          id: String(r.id),
          createBy: String(r.createBy),
          updateBy: String(r.updateBy),
        }))
        outsourcedDocumentTotal.value = total
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      console.error('Fetch Outsourced Documents Error:', error)
      return { success: false, message: '获取委外文件列表失败' }
    } finally {
      outsourcedDocumentsLoading.value = false
    }
  }

  const createOutsourcedDocument = async (data: OutsourcedDocumentSaveDTO) => {
    try {
      const formData = new FormData()
      Object.keys(data).forEach((key) => {
        if (key === 'createTime' || key === 'updateTime') return
        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })
      const res = await saveOutsourcedDocument(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建失败' }
    }
  }

  const updateOutsourcedDocument = async (data: OutsourcedDocumentUpdateDTO) => {
    try {
      const formData = new FormData()

      // 白名单：只传递修订文件时需要的字段
      const allowedFields = [
        'originalFileName',
        'fileType',
        'version',
        'remark',
        'fileStatus',
        'revisedContent',
        'changeReason',
        'suffixName',
        'files',
        'libraryOutsourcedFileId',
      ]

      allowedFields.forEach((key) => {
        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })

      const res = await updateOutsourcedDocumentFile(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新失败' }
    }
  }

  const updateOutsourcedDocumentInfoAction = async (data: any) => {
    try {
      const { createTime, updateTime, ...rest } = data
      const res = await updateOutsourcedDocumentInfo(rest)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新信息失败' }
    }
  }

  const updateOutsourcedDocumentStatus = async (id: string, status: number) => {
    try {
      const res = await changeOutsourcedDocumentStatus(id, status)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '状态修改失败' }
    }
  }

  const fetchOutsourcedDocumentVersions = async (fileId: string) => {
    try {
      const res = await getOutsourcedDocumentVersions(fileId)
      if (isSuccess(res.code)) {
        return { success: true, data: res.data || [] }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取版本历史失败' }
    }
  }

  // ===== 测试规范 =====
  const testSpecifications = ref<TestSpecificationInfo[]>([])
  const testSpecificationsLoading = ref(false)
  const testSpecificationTotal = ref(0)

  const fetchTestSpecifications = async (params: TestSpecificationQueryDTO = {}) => {
    testSpecificationsLoading.value = true
    try {
      const queryParams = {
        current: params.current || 1,
        size: params.size || 10,
        sortColumn: params.sortColumn || 'create_time',
        sortType: params.sortType || 'desc',
        ...params,
      }
      const res = await getTestSpecificationPage(queryParams)
      if (isSuccess(res.code)) {
        let records: TestSpecificationInfo[] = []
        let total = 0
        if (res.data && Array.isArray(res.data.records)) {
          records = res.data.records
          total = res.data.total
        } else if (Array.isArray(res.data)) {
          records = res.data
          total = records.length
        }

        testSpecifications.value = records.map((r: any) => ({
          ...r,
          id: String(r.id),
          originalFileName: r.specificationName || r.originalFileName, // Map specificationName
          createBy: String(r.createBy),
          updateBy: String(r.updateBy),
        }))
        testSpecificationTotal.value = total
        return { success: true, data: res.data }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取测试规范列表失败' }
    } finally {
      testSpecificationsLoading.value = false
    }
  }

  const createTestSpecification = async (data: TestSpecificationSaveDTO) => {
    try {
      const formData = new FormData()
      Object.keys(data).forEach((key) => {
        if (key === 'createTime' || key === 'updateTime') return
        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })
      const res = await saveTestSpecification(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '创建失败' }
    }
  }

  const updateTestSpecification = async (data: TestSpecificationUpdateDTO) => {
    try {
      const formData = new FormData()

      // 白名单：只传递修订文件时需要的字段
      const allowedFields = [
        'originalFileName',
        'fileType',
        'version',
        'remark',
        'fileStatus',
        'revisedContent',
        'changeReason',
        'suffixName',
        'files',
        'libraryTestSpecFileId',
      ]

      allowedFields.forEach((key) => {
        const value = (data as any)[key]
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            value.forEach((item) => formData.append(key, String(item)))
          } else {
            formData.append(key, value)
          }
        }
      })

      const res = await updateTestSpecificationFile(formData)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新失败' }
    }
  }

  const updateTestSpecificationInfoAction = async (data: any) => {
    try {
      const { createTime, updateTime, ...rest } = data
      const res = await updateTestSpecificationInfo(rest)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '更新信息失败' }
    }
  }

  const updateTestSpecificationStatus = async (id: string, status: number) => {
    try {
      const res = await changeTestSpecificationStatus(id, status)
      if (isSuccess(res.code)) {
        return { success: true }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '状态修改失败' }
    }
  }

  const fetchTestSpecificationVersions = async (fileId: string) => {
    try {
      const res = await getTestSpecificationVersions(fileId)
      if (isSuccess(res.code)) {
        return { success: true, data: res.data || [] }
      }
      return { success: false, message: res.msg }
    } catch (error) {
      return { success: false, message: '获取版本历史失败' }
    }
  }

  // 版本历史
  const documentVersions = ref<DocumentVersion[]>([])
  const fetchDocumentVersions = async (id?: any) => {
    return { success: true }
  }

  // 计算属性
  const activeProducts = computed(() => products.value.filter((p) => p.status === '有效'))
  const activeProcesses = computed(() => processes.value.filter((p) => p.isEnabled))

  return {
    // 产品信息
    products,
    productsLoading,
    activeProducts,
    fetchProducts,
    productTotal,
    createProduct,
    updateProduct,
    deleteProduct,
    getProductDetail,

    // 工序库 (Standard Process - Old)
    processes,
    processesLoading,
    activeProcesses,
    fetchProcesses,
    createProcess,
    updateProcess,
    deleteProcess,
    isProcessReferenced,
    getProcessReferences,

    // ==========================================
    // 工艺路线 (Process Route) Real Actions
    // ==========================================
    processRoutes,
    routesLoading,
    fetchProcessRoutes,
    routeTotal,
    saveProcessRoute,
    createProcessRoute,
    updateProcessRoute,
    deleteProcessRoute,
    getProcessRouteDetail,
    saveRouteFlowInfo,

    // 作业指导书
    documents,
    documentsLoading,
    publishedDocuments,
    fetchDocuments,
    uploadDocument,
    updateDocumentVersion,
    publishDocument,

    // 委外设计文件
    outsourcedDocuments,
    outsourcedDocumentsLoading,
    outsourcedDocumentTotal,
    fetchOutsourcedDocuments,
    createOutsourcedDocument,
    updateOutsourcedDocument,
    updateOutsourcedDocumentInfoAction,
    updateOutsourcedDocumentStatus,
    fetchOutsourcedDocumentVersions,

    // 测试规范
    testSpecifications,
    testSpecificationsLoading,
    testSpecificationTotal,
    fetchTestSpecifications,
    createTestSpecification,
    updateTestSpecification,
    updateTestSpecificationInfoAction,
    updateTestSpecificationStatus,
    fetchTestSpecificationVersions,

    // 版本历史
    documentVersions,
    fetchDocumentVersions,

    // ==========================================
    // 工艺库 (Process Library) Real Actions
    // ==========================================
    processLibraries,
    processLibrariesLoading,
    fetchProcessLibraries,
    processLibraryTotal,
    fetchProcessLibraryDetail,
    createProcessLibrary,
    updateProcessLibrary,
    deleteProcessLibrary,
    getProcessLibraryDetail,

    // 分组与参数操作
    createProcessLibraryItem,
    updateProcessLibraryItem,
    deleteProcessLibraryItem,
    getProcessLibraryItemDetail,
    fetchProcessLibraryItems,
    fetchProcessLibraryItemParams,
    createProcessLibraryItemParam,
    updateProcessLibraryItemParam,
    deleteProcessLibraryItemParam,
    connectLibraryAndItems,
    saveItemParams,

    // 作业指导书 (New Real Implementation)
    workInstructions,
    workInstructionsLoading,
    workInstructionTotal,
    fetchWorkInstructions,
    createWorkInstruction,
    updateWorkInstruction,
    updateWorkInstructionInfoAction,
    updateWorkInstructionStatus,
    fetchWorkInstructionVersions,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useTechnologyStore, import.meta.hot))
}
