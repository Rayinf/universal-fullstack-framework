import request from '@/utils/request'
import type {
  ProjectPageData,
  ProjectPageParams,
  ProjectRecord,
  ProjectSaveDto,
} from '@/types/system/project'

export const pageProjectApi = (params: ProjectPageParams) =>
  request.get<ProjectPageData>('/local/projects/page', params)

export const createProjectApi = (data: ProjectSaveDto) => request.post<unknown>('/local/projects', data)

export const updateProjectApi = (id: string, data: ProjectSaveDto) =>
  request.put<unknown>(`/local/projects/${id}`, data)

export const deleteProjectApi = (id: string) => request.delete<unknown>(`/local/projects/${id}`)

export type { ProjectRecord, ProjectSaveDto }
