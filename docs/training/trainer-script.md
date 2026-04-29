# 培训讲稿与演示脚本

本文适合直接照着讲。  
默认对象是“完全不了解本项目，但接下来要借助 AI 持续开发本项目”的同事。

## 1. 培训目标

培训结束后，对方至少要能独立完成四件事：

1. 说清楚项目基座的前后端联动结构
2. 说清楚 skill、脚手架、registry、验证链路各自负责什么
3. 知道如何给 AI 提供正确上下文，并让 AI 稳定继续开发
4. 在新增模块时知道应该先看哪里、先跑什么、最后验证什么

## 2. 建议时长与节奏

建议总时长：90 分钟

1. 10 分钟：讲项目定位
2. 15 分钟：讲 AI 在这个仓库里的正确角色
3. 20 分钟：讲前后端联动链路
4. 15 分钟：讲 skill 的设计与使用
5. 15 分钟：讲脚手架、registry 与 baseline 验证
6. 10 分钟：做现场演示
7. 5 分钟：总结与答疑

## 3. 开场白建议

可以直接这样讲：

> 这个仓库不要把它理解成“一个已经写完的 MES 页面集合”，更应该把它理解成“一个可扩展的业务系统基座”。  
> 它已经把登录、权限、菜单、系统管理、前后端接口、本地化后端、脚手架和验证闭环这些底层能力搭好了。  
> 我们今天不是学某个页面怎么写，而是学这个基座为什么这样设计，以及以后怎么在它上面稳定扩展。

## 4. 第一部分：项目基座全景

### 4.1 要讲的核心点

1. 当前代码现状以 2026-03-16 为准
2. 实际已启用模块是：
   - `system`
   - `sales`
   - `production`
3. 规划中但未启用的模块还有：
   - `task`
   - `planning`
   - `process`
   - `quality`

### 4.2 建议打开的文件

1. `src/config/frameworkConfig.ts`
2. `src/router/index.ts`
3. `src/config/menuConfig.ts`
4. `src/layouts/MainLayout.vue`
5. `backend/main.py`
6. `backend/app/modules/system_admin/menu.py`

### 4.3 建议讲法

可以这样说：

> 前端不是单独靠静态菜单跑的，后端菜单树才是权威源。  
> 前端路由、菜单、布局过滤只是展示和守卫层。  
> 真正的权限含义由后端菜单树里的 `permission` 决定。

## 5. 第二部分：先讲 AI 应该怎么用

### 5.1 要讲的核心点

1. AI 不是来替代项目结构的
2. AI 应该先读项目约束，再开始改代码
3. AI 在这个仓库里最适合做的是：
   - 梳理上下文
   - 执行脚手架流程
   - 排查联动问题
   - 做 review 和验证
4. AI 最怕的是：
   - 不看当前代码
   - 不看 AGENTS 约束
   - 不跑 baseline 就交付

### 5.2 建议打开的文件

1. `docs/training/ai-collaboration-guide.md`
2. `docs/training/ai-prompt-playbook.md`
3. `AGENTS.md`

### 5.3 建议直接说的话

> 在这个仓库里，AI 不能只当聊天机器人来用。  
> 正确的用法是：先让 AI 进入项目上下文，再让它沿着基座、skill、脚手架、registry、验证这条链路工作。

## 6. 第三部分：登录、权限、菜单、路由联动

### 6.1 要讲的链路

按这 7 步讲最容易理解：

1. 登录接口返回 token
2. `userStore` 恢复用户和角色
3. `menuStore` 拉完整菜单树
4. `menuStore` 拉角色可访问菜单 ID
5. `MainLayout` 渲染导航
6. `router.beforeEach` 再做守卫判断
7. 页面才真正可访问

### 6.2 建议强调的关键词

1. `meta.functionCode`
2. 后端 `permission`
3. `allowedMenuIds`
4. `isFrameworkEnabledRoute`

### 6.3 建议直接说的话

> 在这个项目里，页面不是“有路由就能进”。  
> 它至少要同时满足：模块启用、菜单可见、角色授权、权限码一致。  
> 这也是为什么新增模块不能只改一个文件。

## 7. 第四部分：skill 的作用

### 7.1 要讲的核心点

1. skill 不是知识库
2. skill 是可触发的标准工作流
3. 它的作用是把高频、易错、多文件联动的任务做成稳定方法
4. 这个仓库最关键的 skill 是：
   - `universal-fullstack-framework`
   - `skill-creator`

### 7.2 建议打开的文件

1. `docs/training/skills-training.md`
2. `/Users/rayyy/.cc-switch/skills/universal-fullstack-framework/SKILL.md`
3. `/Users/rayyy/.codex/skills/.system/skill-creator/SKILL.md`

### 7.3 建议讲法

> 基座定义了系统的结构，skill 定义了操作这个结构的标准方法。  
> 没有 skill，agent 每次都在临场发挥；有了 skill，扩展和排错都有固定路径。

## 8. 第五部分：脚手架与 registry

### 8.1 要讲的三个脚手架

1. `backend/scripts/scaffold_backend_module.py`
2. `scripts/scaffold_frontend_module.py`
3. `scripts/scaffold_fullstack_module.py`

### 8.2 要讲的四个 registry

1. `src/router/scaffoldedRoutes.ts`
2. `src/config/scaffoldMenuRegistry.ts`
3. `backend/app/bootstrap/scaffold_router_registry.py`
4. `backend/app/modules/system_admin/scaffold_menu_registry.py`

### 8.3 建议讲法

> 主文件负责稳定聚合，registry 负责低冲突扩展，脚手架负责标准化生成。  
> 这样多人并行开发时，不会每个人都去主文件里抢位置。

## 9. 第六部分：现场演示顺序

演示建议在临时分支或培训专用仓库副本中进行，不要在主开发分支直接污染历史。

### 9.1 演示一：看基座

目标：

1. 让对方理解当前系统已启用哪些模块
2. 让对方理解前后端联动点在哪里

操作建议：

1. 打开 `frameworkConfig.ts`
2. 打开 `router/index.ts`
3. 打开 `menu.py`
4. 讲 `functionCode` 与 `permission` 的对应关系

### 9.2 演示二：看前端脚手架

命令示例：

```bash
./backend/.venv/bin/python scripts/scaffold_frontend_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --menu-parent production \
  --route-path /production/quality-report \
  --route-name production-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

要讲的点：

1. 生成了哪些文件
2. 为什么会同时写前端菜单和后端菜单注册
3. 为什么占位字段必须马上替换

### 9.3 演示三：看后端脚手架

命令示例：

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py quality_report \
  --tag "质检报告" \
  --resource-path /manage/api/qualityReport \
  --table-name quality_report_records
```

要讲的点：

1. 模块结构为什么要拆层
2. route 为什么不该直接写 SQL
3. 为什么 router 要写 registry

### 9.4 演示四：看全栈脚手架

命令示例：

```bash
./backend/.venv/bin/python scripts/scaffold_fullstack_module.py quality_report \
  --tag "质检报告" \
  --api-base-path /manage/api/qualityReport \
  --table-name quality_report_records \
  --menu-parent production \
  --route-path /production/quality-report \
  --route-name production-quality-report \
  --function-code SRS-FUNC-QUALITY-REPORT \
  --with-store
```

要讲的点：

1. 一次命令覆盖前后端
2. 自动接 registry
3. 自动同步权限码
4. 失败回滚意味着什么

### 9.5 演示五：看统一验收

命令：

```bash
bash scripts/verify_framework_baseline.sh
```

要讲的点：

1. 生成完不等于完成
2. 基座验证是交付闸门
3. 这 5 步分别兜底什么风险

### 9.6 演示六：给 AI 一个正确 prompt

建议直接从 `docs/training/ai-prompt-playbook.md` 里选一段模板，现场演示：

1. 先让 AI 读取哪些文件
2. 再怎样说明模块信息
3. 再怎样要求它汇报修改与验证结果

这样同事会更快理解“不是 AI 不行，而是上下文要给对”。

## 10. 培训时最该重复的 6 句话

1. 这个仓库是可扩展基座，不只是业务页面集合。
2. AI 要先读项目约束和当前代码，再开始改动。
3. 前端路由、菜单、权限、布局过滤必须一起看。
4. 后端菜单树是权限语义的权威源。
5. 新模块优先走脚手架和 registry，不要回到手工堆主文件。
6. 改完后必须过 baseline 验证。

## 11. 现场问答时常见问题

### 11.1 为什么前端菜单和后端菜单都要有

回答建议：

前端菜单负责展示和兜底，后端菜单负责权限语义和角色授权，两者缺一不可。

### 11.2 为什么菜单看到了还会被重定向

回答建议：

因为可见不等于授权成功。  
真正能否进入页面，要看守卫里按 `functionCode / permission / menuId` 的最终判定。

### 11.3 为什么要保留 registry，而不是直接改主文件更直观

回答建议：

短期看主文件直观，长期看 registry 更稳定、冲突更少、脚手架更容易自动化，也更便于回归测试。

### 11.4 skill 和脚手架是什么关系

回答建议：

skill 负责给出方法，脚手架负责执行生成，二者不是替代关系，而是工作流上下游关系。

### 11.5 为什么我让 AI 改了代码，结果还是不对

回答建议：

通常不是 AI “不会写代码”，而是以下几类上下文没给到位：

1. 没先让 AI 读 AGENTS 和当前代码
2. 没说明任务是前端、后端还是全栈
3. 没说明 `functionCode`、`menu_parent`、`route_path` 等接入信息
4. 没要求它跑验证

## 12. 收尾总结建议

可以用这段话收尾：

> 以后你在这个仓库里做事，不要先想“我要改哪个页面”，而要先想“这次改动会影响哪条联动链”。  
> 如果是新增模块，就先走脚手架；如果是联动问题，就先看路由、菜单、权限和后端菜单树；如果是基座级改动，就一定跑完整验证。  
> 如果是借助 AI 工作，就先把上下文给对，再让 AI 沿着这条链路执行。  
> 这就是这个项目能长期稳定扩展的根本原因。
