import request from '@/utils/request'
import type { ReviewSaveDTO, ReviewRecord } from '@/types/quality/nonConforming'

enum Api {
  UpdateReview = '/manage/api/unqualifiedProductReview/updateReview',
  GetReview = '/manage/api/unqualifiedProductReview/', // + id
}

// 组织评审 (提交/更新评审意见)
export const updateReview = (data: ReviewSaveDTO) => {
  return request.post(Api.UpdateReview, data)
}

// 通过ID查询不合格品评审信息详情
export const getReviewDetail = (id: string) => {
  return request.get<ReviewRecord>(`${Api.GetReview}${id}`)
}
