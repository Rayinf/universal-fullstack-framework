/**
 * 表单交互修复工具
 * 解决Element Plus表单标签点击导致下拉框意外展开的问题
 */

/**
 * 修复表单项标签点击行为
 * 防止点击标签时触发表单控件的焦点事件
 */
export function fixFormLabelClick() {
  // 等待DOM加载完成
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyFormFixes)
  } else {
    applyFormFixes()
  }
}

/**
 * 应用表单修复
 */
function applyFormFixes() {
  // 使用事件委托处理所有表单标签点击
  document.addEventListener('click', handleFormLabelClick, true)
  
  // 监听DOM变化，为动态添加的表单项应用修复
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const element = node as Element
            // 为新添加的表单项应用修复
            applyFixToFormItems(element)
          }
        })
      }
    })
  })
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  })
  
  // 为现有表单项应用修复
  applyFixToFormItems(document.body)
}

/**
 * 处理表单标签点击事件
 */
function handleFormLabelClick(event: Event) {
  const target = event.target as Element
  
  // 检查是否点击了表单标签
  if (target.classList.contains('el-form-item__label') || 
      target.closest('.el-form-item__label')) {
    
    // 阻止事件传播和默认行为
    event.preventDefault()
    event.stopPropagation()
    event.stopImmediatePropagation()
    
    return false
  }
  
  // 检查是否点击了表单项的空白区域（但不是控件区域）
  const formItem = target.closest('.el-form-item')
  if (formItem) {
    const formContent = formItem.querySelector('.el-form-item__content')
    if (formContent && target === formContent) {
      // 如果点击的是表单内容区域的空白部分，阻止事件
      event.preventDefault()
      event.stopPropagation()
      return false
    }
    
    // 检查是否点击了表单项的其他空白区域（不包括控件）
    if (target === formItem && !target.closest('.el-form-item__content')) {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
  }
}

/**
 * 为表单项应用修复
 */
function applyFixToFormItems(container: Element) {
  const formItems = container.querySelectorAll('.el-form-item')
  
  formItems.forEach((formItem) => {
    const label = formItem.querySelector('.el-form-item__label')
    const content = formItem.querySelector('.el-form-item__content')
    
    if (label) {
      // 移除标签的for属性，防止自动关联
      label.removeAttribute('for')
      
      // 添加CSS类标记已处理
      label.classList.add('form-label-fixed')
    }
    
    if (content) {
      // 为内容区域添加标记
      content.classList.add('form-content-fixed')
    }
  })
}

/**
 * 修复特定选择器组件的点击行为
 * 注意：这个函数现在主要用于调试，实际的点击控制主要通过CSS实现
 */
export function fixSelectClickBehavior() {
  // 移除过度的JavaScript控制，让Element Plus自然处理点击事件
  // 只在必要时进行干预
  console.log('选择器点击行为修复已启用')
}

/**
 * 初始化所有表单修复
 */
export function initFormFixes() {
  fixFormLabelClick()
  fixSelectClickBehavior()
}
