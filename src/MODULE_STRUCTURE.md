# 基础框架目录说明

## 当前状态

当前仓库已收敛为“系统管理完整功能 + 预留扩展框架”。

- 已保留页面目录：`/src/views/system-admin/`
- 预留但未启用模块：任务、计划、工艺、生产、质量等业务域

## Views目录

### `/src/views/system-admin/`

系统管理模块（当前核心业务）：

- 本地基础CRUD示例
- 组织架构管理
- 账户管理
- 客户管理
- 角色管理
- 工位与设备管理
- 参数与编码规则
- 审批规则
- 用户/操作日志
- 系统配置与备份
- 个人中心

### `/src/views/`

框架通用页面：

- `HomeView.vue`：基础框架首页（已启用模块 + 预留模块展示）
- `LoginView.vue`：登录页
- `PlaceholderView.vue`：通用占位页

## 扩展约定

后续新增业务模块时，按下述路径扩展：

- `src/views/<module>/`
- `src/api/<module>/`
- `src/stores/<module>/`
- `src/types/<module>/`

并同步更新：

- `src/config/frameworkConfig.ts`（模块开关）
- `src/config/menuConfig.ts`（菜单）
- `src/router/index.ts`（路由）
