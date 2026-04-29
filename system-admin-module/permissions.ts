/**
 * 角色权限配置文件
 * 定义每个角色ID对应的菜单访问权限
 */

/**
 * 角色ID定义
 */
export const ROLE_IDS = {
  SUPER_ADMIN: '1',    // 超级管理员
  LEADER: '2',         // 领导
  BUSINESS: '3',       // 业务人员
  WAREHOUSE: '4',      // 库房组
  SMT: '5',           // SMT组
  MANUAL_WELDING: '6', // 手工焊组
  INSPECTION: '7',     // 检验组
  PROCESS: '8',        // 工艺组
  PCB_DESIGN: '9'      // PCB设计
} as const

/**
 * 菜单标识符
 */
export const MENU_KEYS = {
  DASHBOARD: 'dashboard',                    // 系统概览
  ORDER: 'order',                           // 订单管理
  PROCESS: 'process',                       // 工艺评审管理
  PACKAGING: 'packaging',                   // 包装发货管理
  EQUIPMENT: 'equipment',                   // 设备资产台账管理
  WAREHOUSE: 'warehouse',                   // 元辅料仓库管理
  DOCUMENT: 'document',                     // 资料文件
  CUSTOMER: 'customer',                     // 客户信息
  SYSTEM: 'system',                         // 系统管理
  MONITOR: 'monitor',                       // 大屏监控
  DEPT_MANAGEMENT: 'dept-management',       // 部门管理
  SYSTEM_CONFIG: 'system-config'            // 系统配置
} as const

/**
 * 角色权限映射表
 * 定义每个角色可以访问的菜单
 */
export const ROLE_PERMISSIONS: Record<string, string[]> = {
  // 1. 超级管理员 - 所有功能和按钮
  [ROLE_IDS.SUPER_ADMIN]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.EQUIPMENT,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT,
    MENU_KEYS.CUSTOMER,
    MENU_KEYS.SYSTEM,
    MENU_KEYS.MONITOR,
    MENU_KEYS.DEPT_MANAGEMENT,
    MENU_KEYS.SYSTEM_CONFIG
  ],
  
  // 2. 领导 - 除系统管理之外的所有功能
  [ROLE_IDS.LEADER]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.EQUIPMENT,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT,
    MENU_KEYS.CUSTOMER,
    MENU_KEYS.MONITOR
  ],
  
  // 3. 业务人员 - 除系统管理之外的所有功能
  [ROLE_IDS.BUSINESS]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.EQUIPMENT,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT,
    MENU_KEYS.CUSTOMER,
    MENU_KEYS.MONITOR
  ],
  
  // 4. 库房组 - 系统概览、订单管理、包装发货、元辅料仓库、资料文件
  [ROLE_IDS.WAREHOUSE]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT
  ],
  
  // 5. SMT组 - 系统概览、订单管理、资料文件
  [ROLE_IDS.SMT]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.DOCUMENT
  ],
  
  // 6. 手工焊组 - 系统概览、订单管理、资料文件
  [ROLE_IDS.MANUAL_WELDING]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.DOCUMENT
  ],
  
  // 7. 检验组 - 除系统管理之外的所有功能
  [ROLE_IDS.INSPECTION]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.EQUIPMENT,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT,
    MENU_KEYS.CUSTOMER,
    MENU_KEYS.MONITOR
  ],
  
  // 8. 工艺组 - 系统概览、订单管理、工艺评审管理、资料文件
  [ROLE_IDS.PROCESS]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.DOCUMENT
  ],
  
  // 9. PCB设计 - 除系统管理之外的所有功能
  [ROLE_IDS.PCB_DESIGN]: [
    MENU_KEYS.DASHBOARD,
    MENU_KEYS.ORDER,
    MENU_KEYS.PROCESS,
    MENU_KEYS.PACKAGING,
    MENU_KEYS.EQUIPMENT,
    MENU_KEYS.WAREHOUSE,
    MENU_KEYS.DOCUMENT,
    MENU_KEYS.CUSTOMER,
    MENU_KEYS.MONITOR
  ]
}

/**
 * 菜单路径到菜单标识符的映射
 */
export const MENU_PATH_TO_KEY: Record<string, string> = {
  '/dashboard': MENU_KEYS.DASHBOARD,
  '/orders': MENU_KEYS.ORDER,
  '/process': MENU_KEYS.PROCESS,
  '/packaging': MENU_KEYS.PACKAGING,
  '/equipment': MENU_KEYS.EQUIPMENT,
  '/warehouse': MENU_KEYS.WAREHOUSE,
  '/documents': MENU_KEYS.DOCUMENT,
  '/customers': MENU_KEYS.CUSTOMER,
  '/system': MENU_KEYS.SYSTEM,
  '/monitor': MENU_KEYS.MONITOR
}

/**
 * 根据角色ID获取允许的菜单键列表
 * @param roleId 角色ID
 * @returns 菜单键列表
 */
export function getMenuKeysByRoleId(roleId: string): string[] {
  return ROLE_PERMISSIONS[roleId] || []
}

/**
 * 检查角色是否有权限访问某个菜单
 * @param roleId 角色ID
 * @param menuPath 菜单路径
 * @returns 是否有权限
 */
export function hasMenuPermission(roleId: string, menuPath: string): boolean {
  const menuKey = MENU_PATH_TO_KEY[menuPath]
  if (!menuKey) return false
  
  const allowedMenuKeys = getMenuKeysByRoleId(roleId)
  return allowedMenuKeys.includes(menuKey)
}

/**
 * 根据角色ID列表获取合并后的菜单权限
 * @param roleIds 角色ID列表
 * @returns 合并后的菜单键列表
 */
export function getMergedMenuPermissions(roleIds: string[]): string[] {
  const allMenuKeys = new Set<string>()
  
  roleIds.forEach(roleId => {
    const menuKeys = getMenuKeysByRoleId(roleId)
    menuKeys.forEach(key => allMenuKeys.add(key))
  })
  
  return Array.from(allMenuKeys)
}

/**
 * 检查是否为超级管理员
 * @param roleIds 角色ID列表
 * @returns 是否为超级管理员
 */
export function isSuperAdmin(roleIds: string[]): boolean {
  return roleIds.includes(ROLE_IDS.SUPER_ADMIN)
}

/**
 * 订单详情标签页标识符
 */
export const ORDER_DETAIL_TABS = {
  BASIC: 'basic',                          // 基本信息
  MANUFACTURING: 'manufacturing',          // 制造信息
  FINANCIAL: 'financial',                  // 财务信息
  PROGRESS: 'progress',                    // 生产进度
  DOCUMENTS: 'documents',                  // 绑定资料
  EXPRESS: 'express',                      // 快递信息
  GOLD_REMOVAL: 'gold-removal',           // 去金搪锡操作记录
  BAKING_RECORDS: 'baking-records',       // SMT元器件烘烤除湿记录
  MATERIAL_ANOMALY: 'material-anomaly',   // 物料来料异常处理
  BOM_MANAGEMENT: 'bom-management',       // BOM信息在线编辑
  INSPECTION_PHOTOS: 'inspection-photos'  // 过程检测图片
} as const

/**
 * 订单详情标签页权限配置
 * 定义每个角色可以访问的订单详情标签页
 */
export const ORDER_DETAIL_TAB_PERMISSIONS: Record<string, string[]> = {
  // 1. 超级管理员 - 所有标签页
  [ROLE_IDS.SUPER_ADMIN]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.FINANCIAL,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.GOLD_REMOVAL,
    ORDER_DETAIL_TABS.BAKING_RECORDS,
    ORDER_DETAIL_TABS.MATERIAL_ANOMALY,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ],
  
  // 2. 领导 - 所有标签页
  [ROLE_IDS.LEADER]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.FINANCIAL,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.GOLD_REMOVAL,
    ORDER_DETAIL_TABS.BAKING_RECORDS,
    ORDER_DETAIL_TABS.MATERIAL_ANOMALY,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ],
  
  // 3. 业务人员 - 基本信息、制造信息、财务信息、生产进度、绑定资料、快递信息、BOM在线编辑
  [ROLE_IDS.BUSINESS]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.FINANCIAL,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT
  ],
  
  // 4. 库房组 - 基本信息、制造信息、生产进度、绑定资料、快递信息、去金搪锡、SMT烘烤、物料来料异常、BOM在线编辑
  [ROLE_IDS.WAREHOUSE]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.GOLD_REMOVAL,
    ORDER_DETAIL_TABS.BAKING_RECORDS,
    ORDER_DETAIL_TABS.MATERIAL_ANOMALY,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT
  ],
  
  // 5. SMT组 - 基本信息、制造信息、生产进度、过程检测图片
  [ROLE_IDS.SMT]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ],
  
  // 6. 手工焊组 - 基本信息、制造信息、生产进度、过程检测图片
  [ROLE_IDS.MANUAL_WELDING]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ],
  
  // 7. 检验组 - 所有标签页
  [ROLE_IDS.INSPECTION]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.FINANCIAL,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.GOLD_REMOVAL,
    ORDER_DETAIL_TABS.BAKING_RECORDS,
    ORDER_DETAIL_TABS.MATERIAL_ANOMALY,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ],
  
  // 8. 工艺组 - 基本信息、制造信息、生产进度、绑定资料
  [ROLE_IDS.PROCESS]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS
  ],
  
  // 9. PCB设计 - 基本信息、制造信息、财务信息、生产进度、绑定资料、快递信息、去金搪锡、SMT烘烤、物料来料异常、BOM在线编辑、过程检测图片
  [ROLE_IDS.PCB_DESIGN]: [
    ORDER_DETAIL_TABS.BASIC,
    ORDER_DETAIL_TABS.MANUFACTURING,
    ORDER_DETAIL_TABS.FINANCIAL,
    ORDER_DETAIL_TABS.PROGRESS,
    ORDER_DETAIL_TABS.DOCUMENTS,
    ORDER_DETAIL_TABS.EXPRESS,
    ORDER_DETAIL_TABS.GOLD_REMOVAL,
    ORDER_DETAIL_TABS.BAKING_RECORDS,
    ORDER_DETAIL_TABS.MATERIAL_ANOMALY,
    ORDER_DETAIL_TABS.BOM_MANAGEMENT,
    ORDER_DETAIL_TABS.INSPECTION_PHOTOS
  ]
}

/**
 * 按钮权限标识符
 */
export const BUTTON_PERMISSIONS = {
  // ==================== 订单管理模块 ====================
  // 订单列表页面按钮
  ORDER_CREATE: 'order_create',                              // 新增订单
  ORDER_EDIT: 'order_edit',                                  // 编辑订单
  ORDER_DELETE: 'order_delete',                              // 删除订单
  ORDER_VALIDATE: 'order_validate',                          // 验证订单
  ORDER_COPY: 'order_copy',                                  // 复制订单
  ORDER_BARCODE: 'order_barcode',                           // 条形码（所有人）
  
  // 订单详情-生产进度
  ORDER_PROGRESS_LINK_PROCESS: 'order_progress_link_process',  // 关联工艺库
  ORDER_PROGRESS_EDIT_ITEM: 'order_progress_edit_item',        // 条目编辑
  
  // 订单详情-绑定资料
  ORDER_DOCUMENT_UPDATE_VERSION: 'order_document_update_version',  // 更新版本
  ORDER_DOCUMENT_HISTORY: 'order_document_history',                // 历史版本（所有人）
  ORDER_DOCUMENT_BOM_COMPARE: 'order_document_bom_compare',        // BOM比对（所有人）
  ORDER_DOCUMENT_BATCH_DOWNLOAD: 'order_document_batch_download',  // 批量下载（所有人）
  ORDER_DOCUMENT_UPLOAD: 'order_document_upload',                  // 上传文件
  ORDER_DOCUMENT_DELETE: 'order_document_delete',                  // 删除文件
  ORDER_DOCUMENT_VIEW: 'order_document_view',                      // 查看文件（所有人）
  ORDER_DOCUMENT_DOWNLOAD: 'order_document_download',              // 下载文件（所有人）
  
  // 订单详情-快递信息
  ORDER_EXPRESS_RECEIVE: 'order_express_receive',            // 录入收货
  ORDER_EXPRESS_SEND: 'order_express_send',                  // 录入发货
  
  // 订单详情-去金搪锡
  ORDER_GOLD_REMOVAL_CREATE: 'order_gold_removal_create',    // 新增记录
  ORDER_GOLD_REMOVAL_EDIT: 'order_gold_removal_edit',        // 编辑
  ORDER_GOLD_REMOVAL_DELETE: 'order_gold_removal_delete',    // 删除
  
  // 订单详情-SMT元器件烘烤除湿记录
  ORDER_BAKING_CREATE: 'order_baking_create',                // 新增记录
  ORDER_BAKING_EDIT: 'order_baking_edit',                    // 编辑
  ORDER_BAKING_DELETE: 'order_baking_delete',                // 删除
  
  // 订单详情-物料来料异常处理
  ORDER_MATERIAL_ANOMALY_CREATE: 'order_material_anomaly_create',  // 新增记录
  ORDER_MATERIAL_ANOMALY_EDIT: 'order_material_anomaly_edit',      // 编辑
  ORDER_MATERIAL_ANOMALY_DELETE: 'order_material_anomaly_delete',  // 删除
  
  // 订单详情-BOM信息在线编辑
  ORDER_BOM_CREATE_IMPORT: 'order_bom_create_import',        // 新增+批量导入
  ORDER_BOM_EXPORT_TEMPLATE: 'order_bom_export_template',    // 导出模版（所有人）
  ORDER_BOM_EDIT: 'order_bom_edit',                          // 编辑
  ORDER_BOM_DELETE: 'order_bom_delete',                      // 删除
  
  // 订单详情-过程检测图片
  ORDER_INSPECTION_PHOTO: 'order_inspection_photo',          // 拍照
  
  // ==================== 资料文件模块 ====================
  // 资料文件库
  DOCUMENT_LIBRARY_UPLOAD: 'document_library_upload',        // 上传资料
  DOCUMENT_LIBRARY_PREVIEW: 'document_library_preview',      // 预览（所有人）
  DOCUMENT_LIBRARY_DOWNLOAD: 'document_library_download',    // 下载/批量下载（所有人）
  DOCUMENT_LIBRARY_EDIT_CUSTOMER: 'document_library_edit_customer',    // 编辑-客户资料文件类型
  DOCUMENT_LIBRARY_EDIT_PRODUCTION: 'document_library_edit_production',// 编辑-生产过程资料
  DOCUMENT_LIBRARY_DELETE_CUSTOMER: 'document_library_delete_customer',// 删除-客户资料文件类型
  DOCUMENT_LIBRARY_DELETE_PRODUCTION: 'document_library_delete_production',// 删除-生产过程资料
  DOCUMENT_PRODUCTION_ALL: 'document_production_all',        // 生产过程资料库-所有按钮
  
  // ==================== 元辅仓库管理模块 ====================
  WAREHOUSE_QUERY_SCAN: 'warehouse_query_scan',              // 查询和扫码按钮（所有人）
  WAREHOUSE_OTHER_BUTTONS: 'warehouse_other_buttons'         // 其他按钮（排除查询和扫码）
} as const

/**
 * 按钮权限配置
 * 定义每个角色可以使用的按钮
 */
export const BUTTON_PERMISSION_CONFIG: Record<string, string[]> = {
  // 1. 超级管理员 - 所有按钮
  [ROLE_IDS.SUPER_ADMIN]: Object.values(BUTTON_PERMISSIONS),
  
  // 2. 领导 - 所有按钮
  [ROLE_IDS.LEADER]: Object.values(BUTTON_PERMISSIONS),
  
  // 3. 业务人员
  [ROLE_IDS.BUSINESS]: [
    // 订单管理
    BUTTON_PERMISSIONS.ORDER_CREATE,
    BUTTON_PERMISSIONS.ORDER_EDIT,
    BUTTON_PERMISSIONS.ORDER_DELETE,
    BUTTON_PERMISSIONS.ORDER_VALIDATE,
    BUTTON_PERMISSIONS.ORDER_COPY,
    BUTTON_PERMISSIONS.ORDER_BARCODE,
    
    // 订单详情-生产进度
    BUTTON_PERMISSIONS.ORDER_PROGRESS_LINK_PROCESS,
    
    // 订单详情-绑定资料
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_UPDATE_VERSION,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_HISTORY,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BOM_COMPARE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BATCH_DOWNLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_UPLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DELETE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_VIEW,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DOWNLOAD,
    
    // 订单详情-快递信息
    BUTTON_PERMISSIONS.ORDER_EXPRESS_RECEIVE,
    BUTTON_PERMISSIONS.ORDER_EXPRESS_SEND,
    
    // 订单详情-BOM
    BUTTON_PERMISSIONS.ORDER_BOM_CREATE_IMPORT,
    BUTTON_PERMISSIONS.ORDER_BOM_EXPORT_TEMPLATE,
    BUTTON_PERMISSIONS.ORDER_BOM_EDIT,
    BUTTON_PERMISSIONS.ORDER_BOM_DELETE,
    
    // 资料文件
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_PREVIEW,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DOWNLOAD,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_EDIT_CUSTOMER,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DELETE_CUSTOMER,
    
    // 元辅仓库
    BUTTON_PERMISSIONS.WAREHOUSE_QUERY_SCAN
  ],
  
  // 4. 库房组
  [ROLE_IDS.WAREHOUSE]: [
    // 订单管理
    BUTTON_PERMISSIONS.ORDER_BARCODE,
    
    // 订单详情-绑定资料（所有人权限）
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_HISTORY,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BOM_COMPARE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BATCH_DOWNLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_VIEW,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DOWNLOAD,
    
    // 订单详情-快递信息
    BUTTON_PERMISSIONS.ORDER_EXPRESS_RECEIVE,
    BUTTON_PERMISSIONS.ORDER_EXPRESS_SEND,
    
    // 订单详情-去金搪锡
    BUTTON_PERMISSIONS.ORDER_GOLD_REMOVAL_CREATE,
    BUTTON_PERMISSIONS.ORDER_GOLD_REMOVAL_EDIT,
    BUTTON_PERMISSIONS.ORDER_GOLD_REMOVAL_DELETE,
    
    // 订单详情-SMT烘烤
    BUTTON_PERMISSIONS.ORDER_BAKING_CREATE,
    BUTTON_PERMISSIONS.ORDER_BAKING_EDIT,
    BUTTON_PERMISSIONS.ORDER_BAKING_DELETE,
    
    // 订单详情-物料异常
    BUTTON_PERMISSIONS.ORDER_MATERIAL_ANOMALY_CREATE,
    BUTTON_PERMISSIONS.ORDER_MATERIAL_ANOMALY_EDIT,
    BUTTON_PERMISSIONS.ORDER_MATERIAL_ANOMALY_DELETE,
    
    // 订单详情-BOM
    BUTTON_PERMISSIONS.ORDER_BOM_CREATE_IMPORT,
    BUTTON_PERMISSIONS.ORDER_BOM_EXPORT_TEMPLATE,
    BUTTON_PERMISSIONS.ORDER_BOM_EDIT,
    BUTTON_PERMISSIONS.ORDER_BOM_DELETE,
    
    // 资料文件
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_PREVIEW,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DOWNLOAD,
    
    // 元辅仓库
    BUTTON_PERMISSIONS.WAREHOUSE_QUERY_SCAN,
    BUTTON_PERMISSIONS.WAREHOUSE_OTHER_BUTTONS
  ],
  
  // 5. SMT组
  [ROLE_IDS.SMT]: [
    // 订单管理
    BUTTON_PERMISSIONS.ORDER_BARCODE,
    
    // 订单详情-绑定资料（所有人权限）
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_HISTORY,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BOM_COMPARE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BATCH_DOWNLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_VIEW,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DOWNLOAD,
    
    // 订单详情-BOM
    BUTTON_PERMISSIONS.ORDER_BOM_EXPORT_TEMPLATE,
    
    // 订单详情-过程检测图片
    BUTTON_PERMISSIONS.ORDER_INSPECTION_PHOTO,
    
    // 资料文件
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_UPLOAD,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_PREVIEW,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DOWNLOAD,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_EDIT_PRODUCTION,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DELETE_PRODUCTION,
    BUTTON_PERMISSIONS.DOCUMENT_PRODUCTION_ALL,
    
    // 元辅仓库
    BUTTON_PERMISSIONS.WAREHOUSE_QUERY_SCAN
  ],
  
  // 6. 手工焊组
  [ROLE_IDS.MANUAL_WELDING]: [
    // 订单管理
    BUTTON_PERMISSIONS.ORDER_BARCODE,
    
    // 订单详情-绑定资料（所有人权限）
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_HISTORY,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BOM_COMPARE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BATCH_DOWNLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_VIEW,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DOWNLOAD,
    
    // 订单详情-BOM
    BUTTON_PERMISSIONS.ORDER_BOM_EXPORT_TEMPLATE,
    
    // 订单详情-过程检测图片
    BUTTON_PERMISSIONS.ORDER_INSPECTION_PHOTO,
    
    // 资料文件
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_UPLOAD,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_PREVIEW,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DOWNLOAD,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_EDIT_PRODUCTION,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DELETE_PRODUCTION,
    BUTTON_PERMISSIONS.DOCUMENT_PRODUCTION_ALL,
    
    // 元辅仓库
    BUTTON_PERMISSIONS.WAREHOUSE_QUERY_SCAN
  ],
  
  // 7. 检验组 - 所有按钮
  [ROLE_IDS.INSPECTION]: Object.values(BUTTON_PERMISSIONS),
  
  // 8. 工艺组
  [ROLE_IDS.PROCESS]: [
    // 订单管理
    BUTTON_PERMISSIONS.ORDER_BARCODE,
    
    // 订单详情-生产进度
    BUTTON_PERMISSIONS.ORDER_PROGRESS_LINK_PROCESS,
    BUTTON_PERMISSIONS.ORDER_PROGRESS_EDIT_ITEM,
    
    // 订单详情-绑定资料（所有人权限）
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_HISTORY,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BOM_COMPARE,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_BATCH_DOWNLOAD,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_VIEW,
    BUTTON_PERMISSIONS.ORDER_DOCUMENT_DOWNLOAD,
    
    // 订单详情-BOM
    BUTTON_PERMISSIONS.ORDER_BOM_EXPORT_TEMPLATE,
    
    // 资料文件
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_PREVIEW,
    BUTTON_PERMISSIONS.DOCUMENT_LIBRARY_DOWNLOAD,
    
    // 元辅仓库
    BUTTON_PERMISSIONS.WAREHOUSE_QUERY_SCAN
  ],
  
  // 9. PCB设计 - 所有按钮
  [ROLE_IDS.PCB_DESIGN]: Object.values(BUTTON_PERMISSIONS)
}

/**
 * 根据角色ID获取允许的订单详情标签页
 * @param roleIds 角色ID列表
 * @returns 标签页键列表
 */
export function getAllowedOrderDetailTabs(roleIds: string[]): string[] {
  const allTabs = new Set<string>()
  
  roleIds.forEach(roleId => {
    const tabs = ORDER_DETAIL_TAB_PERMISSIONS[roleId] || []
    tabs.forEach(tab => allTabs.add(tab))
  })
  
  return Array.from(allTabs)
}

/**
 * 检查角色是否有权限访问某个标签页
 * @param roleIds 角色ID列表
 * @param tabName 标签页名称
 * @returns 是否有权限
 */
export function hasTabPermission(roleIds: string[], tabName: string): boolean {
  const allowedTabs = getAllowedOrderDetailTabs(roleIds)
  return allowedTabs.includes(tabName)
}

/**
 * 根据角色ID获取允许的按钮权限
 * @param roleIds 角色ID列表
 * @returns 按钮权限键列表
 */
export function getAllowedButtonPermissions(roleIds: string[]): string[] {
  const allButtons = new Set<string>()
  
  roleIds.forEach(roleId => {
    const buttons = BUTTON_PERMISSION_CONFIG[roleId] || []
    buttons.forEach(btn => allButtons.add(btn))
  })
  
  return Array.from(allButtons)
}

/**
 * 检查角色是否有权限使用某个按钮
 * @param roleIds 角色ID列表
 * @param buttonKey 按钮权限键
 * @returns 是否有权限
 */
export function hasButtonPermission(roleIds: string[], buttonKey: string): boolean {
  const allowedButtons = getAllowedButtonPermissions(roleIds)
  return allowedButtons.includes(buttonKey)
}

