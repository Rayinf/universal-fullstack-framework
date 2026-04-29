# 后端模块模板目录

这里提供一套可编译的最小模板实现，供后续脚手架直接复制：

- `backend_module/router.py`：薄装配入口
- `backend_module/deps.py`：依赖收口
- `backend_module/helpers.py`：纯函数辅助
- `backend_module/serializers.py`：响应序列化
- `backend_module/routes/example_routes.py`：HTTP 层
- `backend_module/services/`：查询/写入服务与模块异常
- `backend_module/repositories/example_repo.py`：SQL 收口

建议后续生成脚手架时直接以 `backend/app/modules/_template/backend_module/` 为蓝本替换模块名。

当前可直接使用：

```bash
./backend/.venv/bin/python backend/scripts/scaffold_backend_module.py demo_quality \
  --tag "质检模块" \
  --resource-path /manage/api/demoQuality \
  --table-name demo_quality_records
```
