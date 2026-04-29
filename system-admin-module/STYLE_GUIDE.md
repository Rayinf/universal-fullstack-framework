# GK-CRM 系统管理模块样式规范

## 概述

本文档定义了 GK-CRM 系统管理模块的样式规范，确保所有组件和页面的视觉一致性。

## 设计原则

### 1. 一致性
- 所有页面使用统一的布局结构
- 统一的配色方案和字体规范
- 一致的间距和圆角设计

### 2. 简洁性
- 简洁明了的界面设计
- 合理的信息层级
- 避免过度装饰

### 3. 可访问性
- 良好的对比度
- 清晰的视觉层次
- 响应式设计支持

## 配色方案

### 主色调
基于 Element Plus 的配色方案：

```css
:root {
  /* 主色调 */
  --el-color-primary: #409EFF;
  --el-color-primary-light-3: #57AEFF;
  
  /* 功能色 */
  --el-color-success: #67c23a;
  --el-color-warning: #e6a23c;
  --el-color-danger: #f56c6c;
  --el-color-info: #909399;
}
```

### 文字颜色
```css
:root {
  --el-text-color-primary: #303133;    /* 主要文字 */
  --el-text-color-regular: #606266;    /* 常规文字 */
  --el-text-color-secondary: #909399;  /* 次要文字 */
  --el-text-color-placeholder: #c0c4cc; /* 占位符文字 */
}
```

### 边框和背景色
```css
:root {
  /* 边框颜色 */
  --el-border-color: #dcdfe6;
  --el-border-color-light: #e4e7ed;
  --el-border-color-lighter: #ebeef5;
  --el-border-color-extra-light: #f2f6fc;
  
  /* 背景颜色 */
  --el-bg-color: #ffffff;
  --el-bg-color-page: #f2f3f5;
  --el-fill-color: #f0f2f5;
  --el-fill-color-light: #f5f7fa;
}
```

### 系统特定颜色
```css
:root {
  /* 页面背景渐变 */
  --system-gradient-bg: linear-gradient(100deg, rgba(43, 151, 240, 0.05), rgba(143, 154, 255, 0.122));
  
  /* 标题装饰渐变 */
  --system-accent-gradient: linear-gradient(to bottom, #409EFF, #57AEFF);
  
  /* 头部背景渐变 */
  --system-header-gradient: linear-gradient(135deg, #409EFF, #57AEFF);
}
```

## 布局规范

### 页面结构
所有页面遵循统一的布局结构：

```html
<div class="page-view">
  <div class="page-header">
    <div class="title-container">
      <div class="title-accent"></div>
      <div class="title-row">
        <h2>页面标题</h2>
        <div class="page-description">页面描述</div>
      </div>
    </div>
    <div class="header-stats">
      <!-- 统计数据 -->
    </div>
  </div>
  
  <div class="content-card">
    <!-- 页面内容 -->
  </div>
</div>
```

### 尺寸规范

#### 间距
- 页面外边距：`24px`
- 卡片内边距：`20px` - `24px`
- 元素间距：`12px` - `20px`
- 小元素间距：`8px` - `12px`

#### 圆角
- 页面卡片：`12px`
- 小卡片/按钮：`8px`
- 装饰元素：`2px` - `6px`

#### 阴影
- 页面卡片：`0 2px 8px rgba(0, 0, 0, 0.07)`
- 页面头部：`0 2px 12px rgba(0, 0, 0, 0.03)`
- 悬浮效果：`0 4px 12px rgba(0, 0, 0, 0.15)`

### 字体规范

#### 字号
- 页面标题：`20px` (移动端 `18px`)
- 卡片标题：`16px` - `18px`
- 正文：`14px`
- 辅助文字：`12px` - `13px`

#### 字重
- 标题：`600` (Semi-bold)
- 强调文字：`500` (Medium)
- 正文：`400` (Regular)

## 组件样式规范

### 页面头部 (.page-header)
```css
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 16px 20px;
  background-color: var(--el-bg-color);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.03);
}
```

### 标题装饰 (.title-accent)
```css
.title-accent {
  width: 4px;
  height: 36px;
  background: var(--system-accent-gradient);
  border-radius: 2px;
  margin-right: 12px;
}
```

### 内容卡片 (.content-card)
```css
.content-card {
  flex: 1;
  background-color: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.07);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
```

### 统计数据 (.stat-item)
```css
.stat-item {
  text-align: center;
  flex-shrink: 0;
  padding: 0 12px;
}

.stat-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
```

### 搜索操作面板 (.search-actions-panel)
```css
.search-actions-panel {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  padding: 20px 24px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background-color: var(--el-bg-color);
  gap: 16px;
}
```

## 响应式设计

### 断点
- 桌面端：`> 768px`
- 平板端：`768px - 480px`
- 移动端：`< 480px`

### 移动端适配
```css
@media (max-width: 768px) {
  .page-view {
    padding: 0;
    gap: 0;
    background-color: var(--el-bg-color-page);
  }

  .page-header {
    border-radius: 0;
    padding: 16px;
  }

  .title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .header-stats {
    display: none;
  }

  .content-card {
    border-radius: 0;
    box-shadow: none;
  }
}
```

## 状态样式

### 成功状态
```css
.highlight {
  color: var(--el-color-success);
}
```

### 警告状态
```css
.highlight-warning {
  color: var(--el-color-warning);
}
```

### 加载状态
```css
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}
```

## 动画效果

### 淡入淡出
```css
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
```

### 滑动效果
```css
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(20px);
  opacity: 0;
}
```

## 使用指南

### 1. 引入通用样式
在页面组件中引入通用样式文件：

```vue
<style scoped>
@import '../styles/common.css';

/* 页面特定样式 */
.custom-style {
  /* 自定义样式 */
}
</style>
```

### 2. 使用标准类名
使用预定义的 CSS 类名：

```vue
<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>页面标题</h2>
          <div class="page-description">页面描述</div>
        </div>
      </div>
    </div>
    
    <div class="content-card">
      <!-- 内容 -->
    </div>
  </div>
</template>
```

### 3. 自定义样式
当需要自定义样式时，遵循以下原则：

- 使用 CSS 变量而非硬编码颜色
- 保持与系统风格的一致性
- 优先使用已有的样式类

```css
/* 推荐 */
.custom-button {
  background-color: var(--el-color-primary);
  color: var(--el-bg-color);
  border-radius: 8px;
}

/* 不推荐 */
.custom-button {
  background-color: #409EFF;
  color: #ffffff;
  border-radius: 8px;
}
```

## 最佳实践

### 1. 保持一致性
- 使用统一的间距和圆角
- 遵循既定的配色方案
- 保持字体大小和字重的一致性

### 2. 性能优化
- 避免过度嵌套的 CSS 选择器
- 使用 CSS 变量提高可维护性
- 合理使用 CSS 动画

### 3. 可维护性
- 使用语义化的类名
- 适当添加注释
- 模块化样式文件

### 4. 可访问性
- 确保足够的颜色对比度
- 提供清晰的视觉层次
- 支持键盘导航

## 常见问题

### Q: 如何自定义主题色？
A: 修改 CSS 变量中的主色调值：
```css
:root {
  --el-color-primary: #your-color;
}
```

### Q: 移动端样式不生效？
A: 检查是否正确使用了响应式断点和媒体查询。

### Q: 如何添加新的通用样式？
A: 在 `styles/common.css` 文件中添加，并确保遵循现有的命名规范。

## 更新日志

- **v1.0.0** (2026-01-08): 初始版本，建立基础样式规范
- 统一了页面布局结构
- 定义了配色方案和字体规范
- 添加了响应式设计支持
- 创建了通用样式文件

---

**维护者：** 开发团队  
**最后更新：** 2026-01-08
