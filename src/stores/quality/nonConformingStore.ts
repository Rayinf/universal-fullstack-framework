import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import {
  getNonConformingPage,
  getNonConformingDetail,
  createNonConformingReport,
  updateNonConformingReport,
  voidNonConformingReport,
} from '@/api/quality/nonConforming'
import { updateReview } from '@/api/quality/review'
import type {
  NonConformingReport,
  NonConformingQueryDTO,
  ReviewSaveDTO,
} from '@/types/quality/nonConforming'
import { ElMessage } from 'element-plus'

export const useNonConformingStore = defineStore('nonConforming', () => {
  const loading = ref(false)
  const list = ref<NonConformingReport[]>([])
  const total = ref(0)
  const currentReport = ref<NonConformingReport | null>(null)

  // 分页查询
  const fetchList = async (params: NonConformingQueryDTO) => {
    loading.value = true
    try {
      const res: any = await getNonConformingPage(params)
      if (res.code === 0 || res.code === 200) {
        list.value = res.data.records
        total.value = res.data.total
      }
    } catch (error) {
      console.error('获取不合格品列表失败', error)
    } finally {
      loading.value = false
    }
  }

  // 获取详情
  const fetchDetail = async (id: string) => {
    loading.value = true
    try {
      const res: any = await getNonConformingDetail(id)
      if (res.code === 0 || res.code === 200) {
        currentReport.value = res.data
        return res.data
      }
    } catch (error) {
      console.error('获取不合格品详情失败', error)
    } finally {
      loading.value = false
    }
  }

  // 创建登记
  const createReport = async (data: Partial<NonConformingReport>) => {
    try {
      const res: any = await createNonConformingReport(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('登记成功')
        return true
      }
      return false
    } catch (error) {
      console.error('登记失败', error)
      return false
    }
  }

  // 更新登记 (含责任部门分析)
  const updateReport = async (data: Partial<NonConformingReport>) => {
    try {
      const res: any = await updateNonConformingReport(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('保存成功')
        // 刷新详情
        if (data.id) await fetchDetail(data.id)
        return true
      }
      return false
    } catch (error) {
      console.error('更新失败', error)
      return false
    }
  }

  // 提交评审意见
  const submitReview = async (data: ReviewSaveDTO) => {
    try {
      const res: any = await updateReview(data)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('评审意见已提交')
        if (data.reportId) await fetchDetail(data.reportId)
        return true
      }
      return false
    } catch (error) {
      console.error('提交评审失败', error)
      return false
    }
  }

  // 作废
  const voidReport = async (id: string) => {
    try {
      const res: any = await voidNonConformingReport(id)
      if (res.code === 0 || res.code === 200) {
        ElMessage.success('已作废')
        return true
      }
      return false
    } catch (error) {
      console.error('作废失败', error)
      return false
    }
  }

  return {
    loading,
    list,
    total,
    currentReport,
    fetchList,
    fetchDetail,
    createReport,
    updateReport,
    submitReview,
    voidReport,
  }
})
