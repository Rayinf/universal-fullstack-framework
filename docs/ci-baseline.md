# 基座 CI 与本地验收

当前仓库已补齐最小可执行验收链路，目标不是做复杂发布平台，而是把“脚手架 + 基座回归 + 前端构建”固定下来。

## 1. 本地统一验收

推荐直接执行：

```bash
bash scripts/verify_framework_baseline.sh
```

默认会使用：

- `backend/.venv/bin/python`
- 当前仓库根目录的 `npm`

如需切换 Python，可覆盖：

```bash
PYTHON_BIN=/path/to/python bash scripts/verify_framework_baseline.sh
```

脚本会依次执行：

1. Python 编译检查
2. 后端基座回归
3. PostgreSQL HTTP smoke
4. 前端类型检查
5. 前端生产构建检查

成功结束会输出：

```text
BASELINE_VERIFY_OK
```

## 2. CI 工作流

仓库提供 GitHub Actions 示例：

- `docs/github-actions-ci.yml`

将该文件复制到 `.github/workflows/ci.yml` 后即可启用 CI。

当前工作流包含两个 job：

- `backend`
  - 安装 `backend/requirements.txt`
  - 启动 PostgreSQL service
  - 执行 Python 编译检查
  - 执行后端基座回归
- `frontend`
  - 安装前端依赖
  - 执行 `npm run type-check`
  - 执行 `npm run build-only`

## 3. 适用场景

建议以下变更都跑这条链路：

- 修改 `backend/main.py`
- 修改后端模块路由 / service / repository
- 修改前端路由 / 菜单 / 权限守卫
- 修改脚手架
- 新增或调整注册表

## 4. 当前边界

这条 CI 目前只覆盖“编译 + 单测 + 前端构建”，还没有包含：

- 数据库迁移 smoke
- 发布回滚脚本
- 灰度或多环境部署策略

当前已新增 `backend/tests/test_http_smoke.py`，覆盖：

- `/health`
- `/auth/oauth2/token`
- `/admin/user/info`
- `/admin/menu/tree`
- `/auth/oauth2/refresh`
- `/local/crud/page`
- `/local/crud`

也就是说，当前已完成的是“编译 + 单测 + PostgreSQL HTTP smoke + 前端构建”的基础工程化入口，但还不是完整发布平台。
