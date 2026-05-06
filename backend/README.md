# 本地 Python 后端

本后端是 Universal Fullstack Framework 的本地 FastAPI 服务，负责认证、系统管理、菜单权限、示例业务接口和本地 CRUD 演示。

## 1. 安装依赖

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 启动服务

```bash
cd backend
source .venv/bin/activate
python main.py
```

默认启动地址：`http://127.0.0.1:8000`

如果在项目根目录使用 npm 脚本：

```bash
# 默认走 PostgreSQL
npm run backend:dev

# 显式 PostgreSQL
npm run backend:dev:pg
```

## 3. 环境变量（建议）

可在项目根目录 `.env` 或系统环境中配置：

> 说明：推荐使用 `APP_*` 通用环境变量前缀。当前代码仍兼容读取旧前缀，便于从历史项目平滑迁移。

```bash
# development | production
APP_ENV=development

# PostgreSQL 连接
# 方式1：完整 DSN
APP_PG_DSN=
# 方式2：拆分参数
APP_PG_HOST=127.0.0.1
APP_PG_PORT=5432
APP_PG_DATABASE=app_local
APP_PG_USER=postgres
APP_PG_PASSWORD=

# 生产环境必须配置强密钥（>= 32位）
APP_JWT_SECRET=please_replace_with_a_strong_random_secret_32_chars_min

# token有效期（秒）
APP_ACCESS_TOKEN_EXPIRE_SECONDS=28800
APP_REFRESH_TOKEN_EXPIRE_SECONDS=604800

# CORS 白名单（逗号分隔）
APP_CORS_ORIGINS=http://localhost:5174,http://127.0.0.1:5174
# 可选：正则白名单
APP_CORS_ORIGIN_REGEX=
```

> 生产模式下会做安全校验：未配置强密钥、`CORS=*`、未配置 CORS 白名单会启动失败。

## 3.1 PostgreSQL 运行说明（当前阶段）

- 当前仓库已收敛为 PostgreSQL-only 运行模式。
- 后端通过 `psycopg` 连接 PostgreSQL。
- 为避免一次性重写全部仓储 SQL，运行时暂时保留了少量 legacy SQL 兼容转换：
  - `?` 占位符
  - `INSERT OR IGNORE`
  - `PRAGMA table_info(...)`

### 3.2 项目根目录快捷命令

在项目根目录可直接使用：

```bash
# PostgreSQL 模式启动后端
npm run backend:dev:pg
```

> 快捷命令已内置默认参数，可通过 `APP_PG_*` 覆盖数据库连接信息。

## 4. 接口文档（中文）

### 4.1 在线文档入口

- Swagger UI：`http://127.0.0.1:8000/docs`
- ReDoc：`http://127.0.0.1:8000/redoc`

> 说明：文档摘要、接口说明、分组标签已统一为中文，并补充了统一返回格式注释。

### 4.2 统一返回格式注释

所有接口统一返回：

```json
{
  "code": 0,
  "msg": "success",
  "data": {}
}
```

- `code = 0`：成功
- `code != 0`：业务失败（HTTP 状态码通常仍为 200，由 `code` 判定业务结果）

### 4.3 主要接口分组说明（中文）

- **系统与认证**：`/health`、`/auth/oauth2/token`、`/auth/oauth2/refresh`
- **系统配置**：`/manage/api/systemConfig/*`
- **菜单与权限**：`/admin/menu/*`
- **组织与用户**：`/admin/dept/*`、`/admin/role/*`、`/admin/user/*`
- **示例业务数据**：`/manage/api/customers/*`
- **示例资源配置**：`/manage/api/processLibrary/*`、`/manage/api/workstation/*`、`/manage/api/deviceInfo/*`
- **基础参数**：`/manage/api/basicInformation/*`、`/manage/api/scanBindingProcess/*`、`/manage/api/codeRule/*`
- **日志与备份**：`/admin/api/sysLogUser*`、`/manage/api/sysLog*`、`/manage/api/sysBakInfo*`
- **审批流**：`/manage/api/approvalFlow*`、`/manage/api/approvalFlowResult*`
- **本地示例接口**：`/local/crud/*`、`/local/projects/*`、`/local/purchase-orders/*`、`/local/inventory/*`

## 5. 默认账号

- 用户名：`admin`
- 密码：`admin123`

> 说明：密码已改为 PBKDF2 哈希存储，兼容历史明文并在启动时自动迁移。

## 6. 后端模块脚手架

当前仓库已提供标准后端模块脚手架，可直接基于模板生成新的模块骨架：

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py example_record \
  --tag "示例记录" \
  --resource-path /manage/api/exampleRecord \
  --table-name example_records
```

默认会输出到 `backend/app/modules/<module_name>/`，并生成：

- `router.py`
- `deps.py`
- `helpers.py`
- `serializers.py`
- `routes/<module_name>_routes.py`
- `services/errors.py`
- `services/<module_name>_query_service.py`
- `services/<module_name>_command_service.py`
- `repositories/<module_name>_repo.py`

相关说明可参考：

- `backend/docs/backend-module-template.md`
- `backend/app/modules/_template/`
