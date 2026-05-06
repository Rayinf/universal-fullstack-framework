# 项目基座培训手册

本文面向第一次接触本仓库的同事，目标是先建立正确的“系统地图”。

## 1. 先讲清楚：这个仓库到底是什么

截至 **2026-03-16**，这个仓库更准确的定位是：

- 一个基于 `Vue 3 + TypeScript + Element Plus + Pinia + Vite` 的前端基座
- 一个基于 `FastAPI + PostgreSQL` 的本地后端基座
- 一个已经接好登录、权限、菜单、系统管理、基础 CRUD、脚手架扩展、基座验证链路的可扩展业务系统底盘

它是一个可以持续扩展的业务系统框架，内置系统管理、示例业务域、脚手架和验证闭环。

## 2. 当前代码状态要以什么为准

培训时务必明确：

1. 当前仓库定位以根目录 `README.md`、`AGENTS.md` 和 `CLAUDE.md` 为准。
2. 当前实际启用的路由前缀以 `src/config/frameworkConfig.ts` 为准。
3. 当前实际启用模块有 3 个：
   - `system`
   - `sales`
   - `production`
4. 以下模块仍处于规划状态，没有正式启用：
   - `task`
   - `planning`
   - `process`
   - `quality`

因此，对新人要先建立一个认知：

“现在看到的 `sales` 和 `production` 页面是基座已经允许启用的示例业务域，可按实际项目替换为自己的业务分组。”

## 3. 用一句话概括项目结构

可以直接这样给新同事讲：

> 前端负责界面、状态、守卫、菜单渲染，后端负责菜单权威源、角色授权、业务接口和种子数据，二者通过 `functionCode / permission / menuId` 这条链路连起来。

## 4. 前端分层怎么理解

### 4.1 路由层

文件：`src/router/index.ts`

职责：

1. 定义页面入口
2. 配置登录页、首页、系统管理和示例业务域页面路由
3. 聚合脚手架追加的 `scaffoldedRoutes`
4. 在 `beforeEach` 中做登录与权限守卫
5. 把未启用模块或未知路径重定向到默认入口

对新人最重要的一点：

“这里不是单纯放页面路径的地方，它还是权限链路的一部分。”

### 4.2 菜单配置层

文件：`src/config/menuConfig.ts`

职责：

1. 定义前端兜底菜单结构
2. 提供图标、标题、层级、路径、`functionCode`
3. 聚合 `src/config/scaffoldMenuRegistry.ts` 中追加的菜单

需要强调：

- 真实导航优先以后端菜单树为准
- `menuConfig.ts` 更像“兜底菜单”和“稳定聚合层”
- 新增模块优先写 registry，而不是持续把主文件改大

### 4.3 框架开关层

文件：`src/config/frameworkConfig.ts`

职责：

1. 定义哪些模块已经启用
2. 定义默认兜底入口 `FRAMEWORK_DEFAULT_ROUTE`
3. 提供 `isFrameworkEnabledRoute()` 给布局和路由守卫使用

新人很容易忽略这一层，结果会出现：

- 路由加了
- 菜单也加了
- 但还是被拦截或被过滤

### 4.4 布局层

文件：`src/layouts/MainLayout.vue`

职责：

1. 顶部栏
2. 侧栏
3. 移动端抽屉导航
4. 用户菜单
5. 通知入口
6. 按当前启用模块过滤菜单

这里要讲清两个来源：

1. 优先用后端返回的菜单树
2. 如果后端菜单未就绪，则回退到前端静态菜单

这套设计的好处是界面不容易彻底空白，但坏处是会掩盖权限问题。  
所以培训时必须提醒：

“菜单看得见，不等于权限一定正确；还要看路由守卫和 `allowedMenuIds`。”

### 4.5 状态层

关键文件：

- `src/stores/userStore.ts`
- `src/stores/menuStore.ts`

`userStore` 负责：

1. Token 恢复
2. 当前用户信息
3. 租户名称
4. 当前角色
5. 用户列表
6. 登录和登出

`menuStore` 负责：

1. 拉完整菜单树
2. 拉当前角色可访问菜单 ID
3. 生成导航菜单
4. 判断菜单是否授权
5. 提供页内 tab 权限判断

### 4.6 请求层

文件：`src/utils/request.ts`

职责：

1. Axios 实例封装
2. 自动注入 `Authorization`
3. 统一处理 `401` 和 `424`
4. 统一错误提示
5. 请求队列与优先级管理

对新人要讲透一件事：

“这个项目里不要绕开统一请求封装乱写请求，因为登录态、退登、错误处理都依赖这里。”

## 5. 后端分层怎么理解

### 5.1 启动入口

文件：`backend/main.py`

职责：

1. 加载环境变量
2. 初始化 JWT、密码哈希、数据库运行时
3. 配置 CORS 与安全校验
4. 注册所有 router
5. 在启动时调用 `init_db()`

这个文件要给同事的认知是：

“它不是业务堆积点，而是总装配入口。”

### 5.2 Bootstrap 层

目录：`backend/app/bootstrap/`

主要职责：

1. 初始化数据库结构
2. 初始化种子数据
3. 管理 router registry
4. 管理脚手架追加的 router 注册

几个关键文件：

- `init_db.py`
- `init_db_schema.py`
- `init_db_seed.py`
- `router_registry.py`
- `scaffold_router_registry.py`

### 5.3 模块层

目录：`backend/app/modules/**`

这里的组织思路是模块化：

1. 一个业务模块一个目录
2. 模块内部再拆 router、deps、services、repositories 等层
3. 通过统一注册表把模块挂到主应用上

### 5.4 菜单权威源

文件：`backend/app/modules/system_admin/menu.py`

这是培训时最值得反复强调的后端文件之一。

它承担 3 件事：

1. 定义后端基础菜单树
2. 定义每个菜单节点的 `permission`
3. 把脚手架写入的 `scaffold_menu_registry.py` 自动 merge 回完整菜单树

也就是说，前端菜单展示和路由权限判断，最终都要回到这里的菜单语义上。

## 6. 登录、权限、菜单、路由是怎么串起来的

可以直接按下面顺序给新人讲。

### 6.1 登录阶段

1. 用户登录成功后，前端拿到：
   - `token_type`
   - `access_token`
   - `refresh_token`
2. `userStore.login()` 持久化 token
3. 接着调用 `/admin/user/info`
4. 把用户基础信息和角色 ID 写入前端状态

### 6.2 菜单解析阶段

1. `menuStore.fetchMenuTree()` 先请求 `/admin/menu/tree`
2. 再根据当前角色请求角色菜单 ID
3. 把所有角色可访问的菜单 ID 合并为 `allowedMenuIds`
4. 导航菜单由后端完整菜单树裁剪而来

### 6.3 布局渲染阶段

1. `MainLayout.vue` 优先使用后端菜单树生成的导航
2. 只保留当前框架已启用模块的菜单
3. 如果后端菜单暂时不可用，则回退到前端静态菜单

### 6.4 路由守卫阶段

`src/router/index.ts` 的守卫会做四层检查：

1. 当前页面是否要求登录
2. 用户是否已有有效 token 或已恢复的用户态
3. 目标路径是否属于已启用模块
4. 当前角色是否拥有对应菜单权限

### 6.5 具体是怎么判权限的

判定链路是：

1. 从目标路由拿到 `meta.functionCode`
2. 在后端菜单树中找 `permission === functionCode` 的节点
3. 如果没找到，才退化成按路径找菜单节点
4. 找到菜单节点后，再看菜单 ID 是否在 `allowedMenuIds` 里

这就是为什么培训时要一直强调：

`meta.functionCode` 和后端 `permission` 必须保持一致。

## 7. 后端种子数据为什么会影响前端效果

因为这个项目不是靠前端 mock 撑起来的。

后端启动时会跑 `init_db()`，而 `init_db_seed_system.py` 中会根据完整菜单树生成默认授权：

1. 先拿 `default_menu_ids = flatten_menu_ids(menu_tree())`
2. 再把这些菜单授权给默认角色

这意味着：

1. 菜单树变了，默认角色授权也会变
2. 新增菜单如果没进菜单树，就不会自动进默认授权
3. 培训和联调时要优先依赖后端 seed，而不是在前端临时造假数据

## 8. 新模块应该沿着什么路径接入

### 8.1 前端侧

优先路径：

1. `src/types/...`
2. `src/api/...`
3. `src/views/...`
4. 可选 `src/stores/...`
5. `src/router/scaffoldedRoutes.ts`
6. `src/config/scaffoldMenuRegistry.ts`

### 8.2 后端侧

优先路径：

1. `backend/app/modules/<module>/`
2. `backend/app/bootstrap/scaffold_router_registry.py`
3. `backend/app/modules/system_admin/scaffold_menu_registry.py`

### 8.3 联动点

新增模块后至少要同步检查：

1. 前端路由
2. 前端菜单
3. 后端菜单注册
4. `meta.functionCode`
5. 后端 `permission`
6. `frameworkConfig.ts` 是否允许该路由前缀
7. 布局过滤逻辑是否允许该路径显示

## 9. 最容易踩的坑

### 9.1 只改页面，不改联动链路

常见结果：

- 页面文件存在
- 路由能进或不能进
- 菜单不显示
- 点击后被重定向

根因通常不是页面代码，而是联动链没接全。

### 9.2 只改前端，不改后端菜单树

这个项目登录后的主导航优先依赖后端菜单树。  
所以前端配了菜单、后端没同步时，实际菜单仍可能缺失。

### 9.3 忘记框架开关

就算你把路由和菜单都配好了，如果前缀不在 `frameworkConfig.ts` 的启用范围内，最终还是会被过滤。

### 9.4 `functionCode` 和 `permission` 不一致

这是权限链路最常见的硬错误。  
症状通常是：

1. 菜单看起来像有
2. 但守卫判无权限
3. 最后跳回默认页

### 9.5 把“菜单可见”误当成“权限已正确”

由于 `MainLayout` 有前端兜底菜单机制，界面上能看到菜单，不代表后端权限已经真正解析完成。

真正要看的是：

1. `menuStore.allowedMenuIds`
2. 路由守卫是否放行
3. 后端 `/admin/menu/tree` 和 `/admin/menu/tree/{roleId}` 返回是否正确

## 10. 给新人的一句总结

这个仓库最核心的理解不是“某个页面怎么写”，而是：

> 新功能必须沿着“路由、菜单、权限码、后端菜单、框架开关、种子数据、验证脚本”这条链路一起接入，缺任何一环都会表现成页面不可见、权限异常或联调不稳定。
