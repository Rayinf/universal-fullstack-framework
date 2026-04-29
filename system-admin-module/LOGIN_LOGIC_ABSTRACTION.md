# GK-CRM 系统登录逻辑抽象说明

本文档详细说明了 GK-CRM 系统的登录流程、技术实现及安全机制。

## 1. 登录流程概览

系统采用基于 OAuth2 的密码模式（Password Grant）进行身份验证。

### 1.1 前端交互流程
1.  **用户输入**：用户在登录页输入租户授权码 (`tenantCode`)、用户名 (`username`) 和密码 (`password`)。
2.  **密码加密**：前端使用 AES 算法对明文密码进行加密。
3.  **发起请求**：将加密后的密码及相关参数以 `application/x-www-form-urlencoded` 格式发送至授权接口。
4.  **获取 Token**：后端验证通过后返回 `access_token`、`refresh_token` 和 `token_type`。
5.  **用户信息获取**：登录成功后，前端立即调用 `/admin/user/info` 接口获取用户详细资料（如姓名、角色、部门、权限等）。
6.  **系统初始化**：获取用户信息后，自动触发系统参数配置（下拉框数据、评估参数等）的初始化加载。

## 2. 核心技术实现

### 2.1 密码加密机制
为了保证传输安全，密码在发送前会进行前端加密：
-   **算法**：AES (Advanced Encryption Standard)
-   **加密模式**：CFB
-   **填充方式**：NoPadding
-   **Key/IV**：`thanks,pig4cloud`
-   **依赖库**：`crypto-js`

### 2.2 登录接口参数
请求头包含固定 Base64 授权信息：`Authorization: Basic cGlnOnBpZw==`

**请求参数列表：**
| 参数名 | 说明 |
| :--- | :--- |
| `username` | 用户名 |
| `password` | AES加密后的密码 |
| `grant_type` | 固定为 `password` |
| `scope` | 固定为 `server` |
| `randomStr` | 随机字符串，用于防止重放攻击 |
| `tenantCode` | 租户授权码 |

### 2.3 状态持久化
系统支持“记住我”功能，根据用户勾选情况决定存储介质：
-   **勾选“记住我”**：Token 存储在 `localStorage` 中，支持跨会话保持登录。
-   **未勾选**：Token 存储在 `sessionStorage` 中，浏览器关闭即失效。

### 2.4 Token 自动注入
通过 Axios 请求拦截器实现：
```typescript
// src/utils/request.ts
service.interceptors.request.use((config) => {
  const tokenType = userStore.tokenType
  const accessToken = userStore.accessToken
  if (tokenType && accessToken) {
    config.headers.Authorization = `${tokenType} ${accessToken}`
  }
  return config
})
```

## 3. 安全与异常处理

### 3.1 权限控制
-   **路由守卫**：`router.beforeEach` 拦截需要授权的页面。如果 Token 存在但用户信息缺失，会触发 `initializeUserState` 重新拉取用户信息。
-   **角色重定向**：超级管理员（角色 ID 为 1 且租户为 0000）登录后会被强制重定向至系统管理模块，隐藏业务功能页面。

### 3.2 Token 失效处理
响应拦截器统一处理身份失效：
-   **401 (Unauthorized)**：Token 过期或无效，提示并强制退出。
-   **424 (Failed Dependency)**：会话异常，强制退出并重定向至登录页。

### 3.3 退出登录 (`logout`)
执行以下清理操作：
-   清空 Pinia Store 中的用户状态和 Token。
-   从 `localStorage` 和 `sessionStorage` 中移除所有 Token 相关数据。
-   重置所有加载标记位。

## 4. 相关文件索引

-   **登录页面**：`src/views/LoginView.vue`
-   **状态管理**：`src/stores/userStore.ts`
-   **网络请求**：`src/utils/request.ts`
-   **路由守卫**：`src/router/index.ts`
-   **API 定义**：`system-admin-module/api/user.ts`
