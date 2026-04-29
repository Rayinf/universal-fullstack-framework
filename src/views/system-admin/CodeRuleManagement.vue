<template>
  <div class="page-view">
    <div class="page-header">
      <div class="title-container">
        <div class="title-accent"></div>
        <div class="title-row">
          <h2>编码规则配置</h2>
          <div class="page-description">管理系统中的业务编码生成规则，如工单号、产品编号等。</div>
        </div>
      </div>
    </div>

    <div class="content-card">
      <div class="table-container">
        <el-table
          :data="displayData"
          stripe
          highlight-current-row
          v-loading="loading"
          class="unified-table"
        >
          <el-table-column prop="typeName" label="业务类型" width="150" font-weight="bold" />
          <el-table-column label="规则名称" min-width="140">
            <template #default="{ row }">
              <span v-if="row.data">{{ row.data.ruleName }}</span>
              <span v-else class="text-placeholder">未配置</span>
            </template>
          </el-table-column>
          <el-table-column label="前缀" min-width="100">
            <template #default="{ row }">
              <span v-if="row.data">{{ row.data.prefix }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <template v-if="row.data">
                <el-tag :type="row.data.isEnable === 0 ? 'success' : 'danger'" effect="dark">
                  {{ row.data.isEnable === 0 ? '启用' : '禁用' }}
                </el-tag>
              </template>
              <template v-else>
                <el-tag type="info">未配置</el-tag>
              </template>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="150" show-overflow-tooltip>
            <template #default="{ row }">
              <span>{{ row.data?.remark || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="最后更新时间" width="180">
            <template #default="{ row }">
              <span>{{ row.data?.updateTime || row.data?.createTime || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" fixed="right" width="200" align="center">
            <template #default="{ row }">
              <template v-if="row.data">
                <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
                <el-button
                  link
                  :type="row.data.isEnable === 0 ? 'warning' : 'success'"
                  @click="handleToggleStatus(row.data)"
                >
                  {{ row.data.isEnable === 0 ? '禁用' : '启用' }}
                </el-button>
              </template>
              <template v-else>
                <el-button link type="primary" @click="handleCreate(row)">配置</el-button>
              </template>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>

    <!-- 编辑编码规则弹窗 -->
    <FormDialog
      v-model="dialogVisible"
      :title="dialogTitle"
      :form-data="formData"
      :rules="formRules"
      :loading="formLoading"
      width="500px"
      @submit="handleSubmit"
      @cancel="dialogVisible = false"
    >
      <template #default="{ formData }">
        <el-form-item label="业务类型">
          <el-input :value="currentTypeName" disabled />
        </el-form-item>
        <el-form-item label="规则名称" prop="ruleName">
          <el-input v-model="formData.ruleName" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="前缀" prop="prefix">
          <el-input v-model="formData.prefix" placeholder="请输入前缀" />
        </el-form-item>
        <el-form-item label="状态" prop="isEnable">
          <el-radio-group v-model="formData.isEnable">
            <el-radio :label="0">启用</el-radio>
            <el-radio :label="1">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="formData.remark" type="textarea" placeholder="请输入备注信息" />
        </el-form-item>
      </template>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import {
  getCodeRulePage,
  updateCodeRule,
  saveCodeRule,
  enableCodeRule,
  type CodeRuleVO,
  type CodeRuleUpdateDTO,
} from '@/api/system/codeRule'
import FormDialog from '@/components/system/FormDialog.vue'

// Fixed Rule Types
const RULE_TYPES = [
  { type: 1, name: '生产任务' },
  { type: 2, name: '工序工单' },
  { type: 3, name: '产品信息' },
]

interface DisplayRow {
  type: number
  typeName: string
  data?: CodeRuleVO
}

const loading = ref(false)
const existingRules = ref<CodeRuleVO[]>([])

const displayData = computed<DisplayRow[]>(() => {
  return RULE_TYPES.map((rt) => {
    const found = existingRules.value.find((r) => r.type === rt.type)
    return {
      type: rt.type,
      typeName: rt.name,
      data: found,
    }
  })
})

// Load Data
const loadData = async () => {
  loading.value = true
  try {
    // Fetch all rules (assuming < 100 total rules ever)
    const params = {
      current: 1,
      size: 100,
      sortColumn: 'create_time',
      sortType: 'desc',
    }
    const res = await getCodeRulePage(params)
    if (res && res.data) {
      existingRules.value = res.data.records || []
    }
  } catch (error) {
    console.error('加载编码规则失败:', error)
    ElNotification.error('加载编码规则失败')
  } finally {
    loading.value = false
  }
}

// Dialog
const dialogVisible = ref(false)
const dialogTitle = ref('配置编码规则')
const formLoading = ref(false)
const isEdit = ref(false)
const currentTypeName = ref('')

const formData = reactive<CodeRuleUpdateDTO>({
  id: undefined,
  type: 1,
  prefix: '',
  ruleName: '',
  remark: '',
  isEnable: 0,
})

const formRules = {
  ruleName: [{ required: true, message: '请输入规则名称', trigger: 'blur' }],
  prefix: [{ required: true, message: '请输入前缀', trigger: 'blur' }],
}

const handleCreate = (row: DisplayRow) => {
  isEdit.value = false
  dialogTitle.value = '配置编码规则'
  currentTypeName.value = row.typeName

  Object.assign(formData, {
    id: undefined,
    type: row.type,
    prefix: '',
    ruleName: '',
    remark: '',
    isEnable: 0,
  })
  dialogVisible.value = true
}

const handleEdit = (row: DisplayRow) => {
  if (!row.data) return
  isEdit.value = true
  dialogTitle.value = '编辑编码规则'
  currentTypeName.value = row.typeName

  Object.assign(formData, {
    id: row.data.id,
    type: row.data.type,
    prefix: row.data.prefix,
    ruleName: row.data.ruleName,
    remark: row.data.remark,
    isEnable: row.data.isEnable,
  })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  formLoading.value = true
  try {
    let res
    if (isEdit.value) {
      res = await updateCodeRule(formData)
    } else {
      res = await saveCodeRule(formData)
    }

    if (res.code === 0 || res.code === 200) {
      ElNotification.success(isEdit.value ? '编码规则更新成功' : '编码规则配置成功')
      dialogVisible.value = false
      loadData()
    } else {
      ElMessage.error(res.msg || (isEdit.value ? '更新失败' : '配置失败'))
    }
  } catch (error) {
    console.error('操作失败:', error)
  } finally {
    formLoading.value = false
  }
}

const handleToggleStatus = async (row: CodeRuleVO) => {
  const newStatus = row.isEnable === 0 ? 1 : 0
  const actionText = newStatus === 0 ? '启用' : '禁用'

  try {
    await ElMessageBox.confirm(`确认要${actionText}该规则吗？`, '提示', {
      type: 'warning',
    })

    const res = await enableCodeRule(row.id, newStatus)
    if (res.code === 0 || res.code === 200) {
      ElNotification.success(`已${actionText}`)
      loadData()
    } else {
      ElMessage.error(res.msg || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
@import '@/styles/common.css';

.table-container {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.unified-table {
  width: 100%;
  max-height: calc(100vh - 380px);
  overflow-y: auto;
}

.text-placeholder {
  color: #909399;
  font-style: italic;
  font-size: 12px;
}
</style>
