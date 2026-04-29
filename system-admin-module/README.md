# 系统管理模块提取说明

## 概述

本文档说明了从主项目中提取的系统管理模块，包括用户管理、用户日志、参数管理（基础信息维护）、系统部分的功能和页面，以及相关的后台对接部分。

## 目录结构

```
system-admin-module/
├── api/                    # API接口模块
│   ├── http.ts            # HTTP请求配置
│   ├── user.ts            # 用户管理API
│   ├── sys-log-user.ts    # 用户日志API
│   ├── basic-info.ts      # 基础信息管理API
│   ├── dept.ts            # 部门管理API
│   ├── systemConfig.ts    # 系统配置API
│   └── system.ts          # 系统管理API
├── components/             # 组件
│   ├── BaseDialog.vue     # 基础对话框组件
│   ├── FormDialog.vue     # 表单对话框组件
│   └── ProfileDialog.vue  # 个人资料对话框组件
├── pages/                  # 页面组件
│   ├── UserManagement.vue      # 用户管理页面
│   ├── UserLogManagement.vue   # 用户日志管理页面
│   ├── BasicInfoManagement.vue # 基础信息维护页面
│   ├── DeptManagement.vue      # 部门管理页面
│   ├── SystemConfigView.vue    # 系统配置页面
│   ├── OperationLog.vue        # 操作日志页面
│   ├── BackupManagement.vue    # 数据备份页面
│   └── ProfileCenter.vue       # 个人中心页面
├── router/                 # 路由配置
│   ├── system.ts          # 系统管理路由
│   └── systemAdmin.ts     # 系统管理模块路由
├── stores/                 # 状态管理
│   ├── index.ts           # Store入口文件
│   └── modules/
│       ├── auth.ts        # 认证状态管理
│       ├── app.ts         # 应用状态管理
│       ├── dept.ts        # 部门管理状态
│       └── systemConfig.ts # 系统配置状态
├── types/                  # 类型定义
│   ├── user.ts            # 用户相关类型
│   ├── sys-log-user.ts    # 用户日志类型
│   ├── basic-info.ts      # 基础信息类型
│   ├── dept.ts            # 部门管理类型
│   ├── systemConfig.ts    # 系统配置类型
│   └── system.ts          # 系统相关类型
├── utils/                  # 工具函数
│   ├── request.ts         # 请求工具
│   ├── storage.ts         # 存储工具
│   └── form-fix.ts        # 表单修复工具
├── styles/                 # 样式文件
│   └── common.css         # 通用样式规范
├── permissions.ts          # 权限配置文件
├── STYLE_GUIDE.md         # 样式规范文档
└── README.md              # 本说明文档
```

## 功能模块说明

### 1. 用户管理 (UserManagement.vue)

**功能描述：**
- 用户信息的增删改查
- 用户角色管理
- 用户状态启用/禁用
- 密码重置功能

**API接口：**
- `pageUsersApi()` - 分页查询用户
- `createUserApi()` - 创建用户
- `updateUserApi()` - 更新用户信息
- `deleteUserApi()` - 删除用户
- `resetUserPasswordApi()` - 重置用户密码
- `toggleUserEnabledApi()` - 启用/禁用用户

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 2. 用户日志管理 (UserLogManagement.vue)

**功能描述：**
- 查看系统用户操作日志
- 日志筛选和搜索
- 日志导出功能
- 日志清理功能

**API接口：**
- `pageSysLogUserApi()` - 分页查询用户日志
- `getSysLogUserDetailApi()` - 获取日志详情
- `deleteSysLogUserApi()` - 删除日志
- `clearSysLogUserApi()` - 清空日志
- `exportSysLogUserApi()` - 导出日志

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 3. 部门管理 (DeptManagement.vue)

**功能描述：**
- 组织架构管理，包括创建、编辑、删除部门
- 部门层级关系管理
- 部门成员分配和管理
- 部门树形结构展示
- 部门详情查看

**API接口：**
- `getDeptTreeApi()` - 获取部门树形菜单（统一使用 tree 接口）
- `getUserDeptTreeApi()` - 获取当前用户的部门树
- `getDeptPageApi()` - 分页查询部门
- `getDeptByIdApi()` - 通过ID查询部门详情
- `getDeptByNameApi()` - 根据部门名称查询部门信息
- `addDeptApi()` - 添加部门
- `updateDeptApi()` - 编辑部门
- `deleteDeptApi()` - 删除部门
- `toggleDeptEnabledApi()` - 启用/停用部门
- `updateDeptUsersApi()` - 更新部门用户

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 4. 系统配置 (SystemConfigView.vue)

**功能描述：**
- 系统基础配置管理
- 公司名称、系统名称、版本号配置
- 配置预览功能
- 本地缓存和服务器同步

**API接口：**
- `getSystemConfigApi()` - 获取系统默认配置信息
- `updateSystemConfigApi()` - 更新系统配置
- `updateAllConfigsApi()` - 批量更新系统配置

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 5. 基础信息维护 (BasicInfoManagement.vue)

**功能描述：**
- 系统参数配置管理
- 支持多种参数类型：
  - 公司管理
  - 项目进度
  - 销售人员
  - 部门管理
  - 品类管理
  - 发货方式
  - 收货方式
  - 客户等级
  - 评估参数
  - 产品服务

**API接口：**
- `pageBasicInfoApi()` - 分页查询基础信息
- `listBasicInfoByTypeApi()` - 根据类型获取分类列表
- `saveBasicInfoApi()` - 新增分类
- `updateBasicInfoApi()` - 修改分类
- `deleteBasicInfoApi()` - 删除分类

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 6. 操作日志 (OperationLog.vue)

**功能描述：**
- 系统操作日志查看
- 日志筛选和搜索

**API接口：**
- `fetchLogsApi()` - 获取操作日志

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 7. 数据备份 (BackupManagement.vue)

**功能描述：**
- 数据备份管理
- 备份记录查看
- 手动触发备份

**API接口：**
- `fetchBackupApi()` - 获取备份记录
- `triggerBackupApi()` - 触发备份

**权限控制：**
- 仅超级管理员（roleId='1'）可访问

### 8. 个人中心 (ProfileCenter.vue)

**功能描述：**
- 个人信息查看和修改
- 密码修改
- 个人设置

**权限控制：**
- 所有登录用户可访问

## 后台对接说明

### API 基础配置

**HTTP配置文件：** `api/http.ts`
- 请求拦截器：自动添加认证token
- 响应拦截器：统一处理错误和数据格式
- 基础URL配置

### 认证相关

**认证状态管理：** `stores/modules/auth.ts`
- 用户登录状态管理
- Token管理（access_token, refresh_token）
- 用户信息缓存
- 菜单权限管理

### 权限系统

**权限配置：** `permissions.ts`
- 角色定义和权限映射
- 菜单访问权限控制
- 按钮级权限控制
- 超级管理员特殊权限处理

### 数据类型定义

**用户相关类型：** `types/user.ts`
- UserRecord：用户记录类型
- UserCreateDto：用户创建DTO
- UserUpdateDto：用户更新DTO
- UserPageQuery：用户分页查询参数

**日志相关类型：** `types/sys-log-user.ts`
- SysLogUserRecord：日志记录类型
- SysLogUserPageQuery：日志查询参数
- LogType：日志类型枚举
- ClearType：清理类型枚举

**基础信息类型：** `types/basic-info.ts`
- BasicInfoRecord：基础信息记录类型
- BasicInfoDto：基础信息DTO
- BasicInfoPageQuery：分页查询参数

## 部署和集成说明

### 1. 依赖要求

```json
{
  "vue": "^3.x",
  "vue-router": "^4.x",
  "pinia": "^2.x",
  "element-plus": "^2.x",
  "axios": "^1.x"
}
```

### 2. 集成步骤

1. **安装依赖**
   ```bash
   npm install vue vue-router pinia element-plus axios
   ```

2. **配置路由**
   ```typescript
   import { systemRoutes } from './router/system'
   
   const router = createRouter({
     routes: [
       systemRoutes,
       // 其他路由...
     ]
   })
   ```

3. **配置状态管理**
   ```typescript
   import { createPinia } from 'pinia'
   import { useAuthStore } from './stores/modules/auth'
   
   const pinia = createPinia()
   app.use(pinia)
   ```

4. **配置权限**
   ```typescript
   import { hasMenuPermission } from './permissions'
   
   // 在路由守卫中使用
   router.beforeEach((to, from, next) => {
     const userRoles = getUserRoles()
     if (hasMenuPermission(userRoles, to.path)) {
       next()
     } else {
       next('/403')
     }
   })
   ```

### 3. 环境配置

**API基础URL配置：**
```typescript
// api/http.ts
const baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8080'
```

**环境变量示例：**
```env
# .env.development
VUE_APP_API_BASE_URL=http://localhost:8080

# .env.production
VUE_APP_API_BASE_URL=https://api.example.com
```

## 特殊说明

### 1. 超级管理员权限

- 当用户角色为管理员（roleId='1'）且租户代码为'0000'时，被识别为超级管理员
- 超级管理员登录后只能看到系统管理菜单，其他菜单被隐藏
- 路由守卫会自动重定向超级管理员到用户管理页面

### 2. 样式规范统一

- 所有页面组件遵循统一的 GK-CRM 系统样式规范
- 使用 Element Plus 标准配色方案和设计语言
- 统一的页面布局结构和组件样式
- 响应式设计支持，适配桌面端和移动端
- 详细样式规范请参考 `STYLE_GUIDE.md`

### 3. ID字段类型处理

- 所有ID字段统一使用string类型，避免大数字精度丢失问题
- API返回数据时自动将ID字段转换为string类型
- 前端处理时使用String()而非parseInt()进行转换

### 4. 数据显示优化

- 直接使用后端提供的xxxName字段（如employeeRankName、typeName等）
- 避免手动格式化代码值，提高显示效率

## 维护和扩展

### 1. 添加新的系统管理功能

1. 在`pages/`目录下创建新的页面组件
2. 在`api/`目录下添加对应的API接口
3. 在`types/`目录下定义相关类型
4. 在`router/system.ts`中添加路由配置
5. 在`permissions.ts`中配置权限

### 2. 修改权限配置

- 编辑`permissions.ts`文件
- 修改`ROLE_PERMISSIONS`对象添加或移除权限
- 更新`BUTTON_PERMISSION_CONFIG`配置按钮权限

### 3. API接口扩展

- 在对应的API文件中添加新的接口函数
- 更新类型定义文件
- 在页面组件中调用新的API接口

## 联系方式

如有问题或需要技术支持，请联系开发团队。

---

**版本：** 1.0.0  
**更新时间：** 2026-01-08  
**维护者：** 开发团队
