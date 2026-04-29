# 前端 CRUD 模块模板

本目录提供仓库内前端 CRUD 模块脚手架模板，供 `scripts/scaffold_frontend_module.py` 使用。

当前模板组成：

- `types.ts.tpl`
  - 标准类型骨架，默认字段为 `id/name/code/status/remark`
- `api.ts.tpl`
  - 标准分页 + 新增 + 编辑 + 删除 API 封装
- `view.api.vue.tpl`
  - 直接调用 API 的 CRUD 页面骨架
- `store.ts.tpl`
  - 可选生成的 Pinia Composition Store
- `view.store.vue.tpl`
  - 接入 Store 的 CRUD 页面骨架

生成后的默认字段只是一套“最小可运行样板”，落地业务模块时必须尽快替换：

- 页面标题和描述
- 列表列定义
- 查询条件
- 表单字段
- 接口路径和错误文案

同时不要忘记补齐这 4 处联动：

1. 前端路由
2. 前端菜单
3. 后端菜单树 / 权限码
4. 布局过滤 / 守卫配置
