# 部门管理树形接口统一修改说明

## 修改概述

将系统组织架构管理的外层接口统一使用 `/admin/dept/tree` 接口，不再使用 `/admin/dept/getDeptTreeList` 接口，并在编辑操作后调用 `tree` 接口刷新数据。

## 修改背景

- **原有方案**：外层使用 `getDeptTreeList` 接口，内部选择用户时使用 `tree` 接口
- **新方案**：统一使用 `tree` 接口，简化接口调用逻辑
- **优势**：减少接口维护成本，统一数据格式，提高系统一致性

## 修改内容

### 1. Store 层修改 (`stores/modules/dept.ts`)

#### 修改 `fetchDeptTreeList` 方法
```typescript
// 修改前
const response = await request.post<any[]>('/admin/dept/getDeptTreeList', queryParams)

// 修改后  
const response = await request.get<any[]>('/admin/dept/tree')
```

#### 修改刷新调用
所有编辑操作后的刷新调用从 `fetchDeptTreeList()` 改为 `fetchDeptTree()`：

- `addDept()` - 添加部门后刷新
- `updateDept()` - 更新部门后刷新  
- `deleteDept()` - 删除部门后刷新
- `toggleDeptEnabled()` - 启用/禁用部门后刷新

### 2. 页面组件修改 (`pages/DeptManagement.vue`)

#### 初始化调用
```typescript
// 修改前
onMounted(async () => {
  await deptStore.fetchDeptTreeList()
})

// 修改后
onMounted(async () => {
  await deptStore.fetchDeptTree()
})
```

#### 删除操作后刷新
```typescript
// 修改前
await deptStore.fetchDeptTreeList()

// 修改后  
await deptStore.fetchDeptTree()
```

### 3. API 文件修改 (`api/dept.ts`)

#### 移除 getDeptTreeListApi
```typescript
// 移除的方法
export const getDeptTreeListApi = (params?: DeptQueryParams): Promise<ApiResponse<any[]>> => {
  const queryParams: DeptQueryParams = {
    sortColumn: 'sort_order',
    sortType: 'asc',
    ...params,
  }
  return request.post('/admin/dept/getDeptTreeList', queryParams)
}
```

#### 更新注释
```typescript
/**
 * 获取部门树形菜单（统一使用 tree 接口）
 */
export const getDeptTreeApi = (userId?: number, isAdmin?: number): Promise<ApiResponse<any[]>> => {
  // ... 现有实现保持不变
}
```

### 4. 文档更新

#### README.md
- 移除 `getDeptTreeListApi()` 的 API 接口说明
- 更新 `getDeptTreeApi()` 的描述为"获取部门树形菜单（统一使用 tree 接口）"

#### INTEGRATION_SUMMARY.md  
- 更新接口列表，移除 `getDeptTreeListApi`
- 更新主要方法说明，`fetchDeptTreeList()` 改为 `fetchDeptTree()`
- 更新示例代码中的初始化调用

#### USAGE_EXAMPLE_DEPT_SYSTEM.md
- 更新所有示例代码中的方法调用
- 更新 API 直接调用示例
- 更新错误处理示例
- 更新单元测试示例

## 接口对比

### 修改前
```typescript
// 外层树形结构
POST /admin/dept/getDeptTreeList
{
  "sortColumn": "sort_order",
  "sortType": "asc"
}

// 用户选择树形结构  
GET /admin/dept/tree
```

### 修改后
```typescript
// 统一使用
GET /admin/dept/tree
```

## 数据格式

两个接口返回的数据格式基本一致，都包含：
- 部门信息（id, name, parentId, sortOrder, enabled 等）
- 用户信息（userList 数组）
- 树形结构（children 数组）

`convertTreeNode` 方法可以正常处理两种接口返回的数据。

## 影响范围

### 直接影响
- `system-admin-module/stores/modules/dept.ts`
- `system-admin-module/pages/DeptManagement.vue`  
- `system-admin-module/api/dept.ts`

### 文档影响
- `system-admin-module/README.md`
- `system-admin-module/INTEGRATION_SUMMARY.md`
- `system-admin-module/USAGE_EXAMPLE_DEPT_SYSTEM.md`

### 无影响
- 类型定义文件（接口返回格式一致）
- 组件样式文件
- 权限配置文件
- 其他 Store 模块

## 测试验证

### 功能测试
- ✅ 部门树形结构正常显示
- ✅ 添加部门后自动刷新
- ✅ 编辑部门后自动刷新  
- ✅ 删除部门后自动刷新
- ✅ 启用/禁用部门后自动刷新
- ✅ 用户选择功能正常

### 兼容性测试
- ✅ 数据格式兼容
- ✅ 组件渲染正常
- ✅ 交互功能完整

## 优势总结

1. **接口统一**：减少了一个 API 接口，降低维护成本
2. **逻辑简化**：统一使用 `tree` 接口，代码更清晰
3. **性能优化**：减少不必要的接口调用
4. **一致性**：外层和内层使用相同的数据源
5. **可维护性**：减少了代码重复，提高可维护性

## 注意事项

1. **向后兼容**：如果后端仍需要支持 `getDeptTreeList` 接口，需要保留该接口
2. **权限控制**：确保 `tree` 接口有适当的权限控制
3. **性能考虑**：`tree` 接口应该有合适的缓存策略
4. **错误处理**：统一错误处理逻辑，确保用户体验

## 后续计划

1. **监控观察**：观察修改后的系统稳定性
2. **性能评估**：评估接口调用频率和响应时间
3. **用户反馈**：收集用户使用反馈
4. **文档完善**：根据实际使用情况完善文档

---

**修改时间**：2026-01-08  
**修改人员**：开发团队  
**版本**：v1.1.0
