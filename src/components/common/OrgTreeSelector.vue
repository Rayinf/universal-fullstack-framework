<template>
  <div class="org-tree-selector">
    <el-tree-select
      v-model="selectedValues"
      :data="treeData"
      :props="treeProps"
      :multiple="multiple"
      :show-checkbox="multiple"
      :check-strictly="checkStrictly"
      :render-after-expand="false"
      :placeholder="placeholder"
      :clearable="clearable"
      :collapse-tags="multiple"
      :collapse-tags-tooltip="multiple"
      :max-collapse-tags="3"
      :disabled="disabled"
      node-key="id"
      class="org-tree"
    >
      <template #default="{ data }">
        <span class="custom-tree-node">
          <el-icon><OfficeBuilding /></el-icon>
          <span class="node-label">{{ data.label }}</span>
        </span>
      </template>
    </el-tree-select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { OfficeBuilding } from '@element-plus/icons-vue'
import { getDeptTreeApi } from '@/api/system/dept'

interface OrgNode {
  id: string
  label: string
  type: 'dept'
  deptId?: string
  children?: OrgNode[]
}

const props = defineProps<{
  modelValue: string | string[]
  multiple?: boolean
  checkStrictly?: boolean
  placeholder?: string
  clearable?: boolean
  disabled?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string | string[]]
}>()

const treeProps = {
  label: 'label',
  children: 'children',
}

const treeData = ref<OrgNode[]>([])

const selectedValues = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// 递归处理原始树形数据，仅保留部门结构，不加载人员
const processTreeNodes = (nodes: any[], parentDeptId?: string): OrgNode[] => {
  if (!nodes || !Array.isArray(nodes)) return []

  const result: OrgNode[] = []

  nodes.forEach((node) => {
    // 1. 判断是否为部门 (根据 JSON：type 为 0 是部门)
    const isDept = String(node.type) === '0'

    if (isDept) {
      const currentDeptId = String(node.id || node.deptId)
      const children: OrgNode[] = []

      // 1.1 处理子部门 (children)
      if (node.children && node.children.length > 0) {
        children.push(...processTreeNodes(node.children, currentDeptId))
      }

      // 1.2 ⭐ 移除处理部门下的人员 (userList) 的逻辑

      // 添加部门节点
      result.push({
        id: `dept:${currentDeptId}:${parentDeptId || '0'}`,
        label: node.name || node.deptName || '未知部门',
        type: 'dept',
        deptId: currentDeptId,
        children: children.length > 0 ? children : undefined,
      })
    }
    // 2. ⭐ 移除根节点直接是人员 (isUser) 的处理逻辑
  })

  return result
}

// Helper to find full ID by deptId (e.g. 2011330996358168577) in the tree
const findFullIdByDeptId = (nodes: OrgNode[], deptId: string): string | null => {
  for (const node of nodes) {
    // node.id format: "dept:deptId:parentId"
    const parts = node.id.split(':')
    const currentDeptId = parts[1]

    if (currentDeptId === deptId) {
      return node.id
    }

    if (node.children) {
      const found = findFullIdByDeptId(node.children, deptId)
      if (found) return found
    }
  }
  return null
}

// 获取组织架构数据
const fetchOrgData = async () => {
  try {
    const res = await getDeptTreeApi()
    if ((res.code === 0 || res.code === 200) && res.data) {
      treeData.value = processTreeNodes(res.data)

      // Try to match if modelValue is a raw ID (no colon)
      // Only applicable when not multiple
      if (
        !props.multiple &&
        typeof props.modelValue === 'string' &&
        props.modelValue &&
        !props.modelValue.includes(':')
      ) {
        const fullId = findFullIdByDeptId(treeData.value, props.modelValue)
        if (fullId) {
          emit('update:modelValue', fullId)
        }
      }
    }
  } catch (error) {
    console.error('获取组织架构失败:', error)
  }
}

onMounted(() => {
  fetchOrgData()
})
</script>

<style scoped>
.org-tree-selector {
  width: 100%;
}

.org-tree {
  width: 100%;
}

.custom-tree-node {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
  padding-right: 8px;
}

.node-label {
  flex: 1;
}

.ml-2 {
  margin-left: 8px;
}

:deep(.el-tree-node__content) {
  height: 32px;
}
</style>
