# 项目基座与 AI 协作开发培训材料

本目录用于给“完全不了解这个框架，但需要借助 AI 持续开发企业管理系统”的同事做培训和日常操作参考。

材料基于仓库在 **2026-03-16** 的实际代码状态整理。当前代码已经启用了 `system`、`sales`、`production` 三类模块，其中 `sales`、`production` 作为示例业务桶，用于演示业务域扩展、菜单挂载、路由前缀和权限码联动。

## 这套材料解决什么问题

看完并按顺序讲完后，受训同事应该能回答下面 6 个问题：

1. 这个仓库的可扩展基座定位。
2. 前端路由、菜单、权限、布局过滤为什么要一起改。
3. 后端菜单树、角色菜单、种子数据为什么会影响前端访问结果。
4. 为什么这里要引入 skill 固化 Agent 工作流。
5. 为什么新增模块优先走脚手架和 registry。
6. 为什么改完代码后必须跑固定的基座验收链路。

除此之外，这套材料还要解决一个更实际的问题：

“同事拿到这个仓库后，应该怎样把 AI 变成一个能持续接手开发的工程助手。”

## 材料清单

1. [`framework-baseline-training.md`](./framework-baseline-training.md)
   项目基座全景说明，先讲“这是什么系统、怎么分层、怎么联动”。
2. [`skills-training.md`](./skills-training.md)
   skill 的设计目的、结构、搭建思路、使用方式，以及它和项目基座的配合关系。
3. [`scaffold-registry-verify-training.md`](./scaffold-registry-verify-training.md)
   三类脚手架、注册表机制、基座验证闭环、推荐演示方式。
4. [`trainer-script.md`](./trainer-script.md)
   适合你直接照着讲的培训讲稿和演示节奏。
5. [`quick-reference.md`](./quick-reference.md)
   一页式速查表，适合培训结束后发给同事长期留存。
6. [`ai-collaboration-guide.md`](./ai-collaboration-guide.md)
   面向开发同事的 AI 协作开发实操手册，讲“如何给 AI 上下文、如何拆任务、如何验收 AI 输出”。
7. [`ai-prompt-playbook.md`](./ai-prompt-playbook.md)
   可直接复制给 AI 的提示词模板，覆盖新增模块、排查权限问题、代码审查、回归验证、多 agent 并行等场景。

## 推荐阅读顺序

如果目的是“让同事尽快用 AI 接手开发”，建议按下面顺序：

1. 先读 `ai-collaboration-guide.md`
2. 再读 `ai-prompt-playbook.md`
3. 然后读 `framework-baseline-training.md`
4. 再读 `skills-training.md`
5. 然后读 `scaffold-registry-verify-training.md`
6. 培训当天直接按 `trainer-script.md` 讲
7. 培训后把 `quick-reference.md` 发给对方做日常速查

如果目的是“先补项目全景认知，再学 AI 协作”，则把第 1 步和第 3 步对调。

## 建议培训时长

如果是首次培训，建议按 90 分钟准备：

1. 15 分钟讲项目定位与现状
2. 15 分钟讲“如何把 AI 用在这个仓库里”
3. 20 分钟讲前后端联动链路
4. 15 分钟讲 skill 和工作流
5. 15 分钟讲脚手架、registry、验证闭环
6. 10 分钟做现场演示和问答

## 建议演示环境

建议提前准备以下环境，避免培训时卡在非核心问题上：

1. 前端依赖已经安装完成
   `npm install`
2. 后端虚拟环境和依赖已经安装完成
   `./backend/.venv/bin/python -m pip install -r backend/requirements.txt`
3. PostgreSQL 本地库可用，并能按项目默认环境变量启动
4. 能正常执行
   `npm run backend:dev`
5. 能正常执行
   `npm run dev`
6. 能正常执行
   `bash scripts/verify_framework_baseline.sh`

## 建议演示账号

当前后端初始化种子数据会写入本地演示管理员账号：

- 用户名：`admin`
- 密码：`admin123`

这是本地演示数据。生产环境应配置独立账号和强口令策略。

## 核心定位

这套仓库的核心是建立一套 **可扩展的业务系统基座 + 可触发的 skill 工作流 + 可复用的脚手架 + 固定的基座验证闭环 + 可持续协作的 AI 开发方式**。
