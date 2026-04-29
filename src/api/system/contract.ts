import request from '@/utils/request'
import type {
  ContractDashboardData,
  ContractPageData,
  ContractPageParams,
  ContractPaymentSummary,
  ContractRecord,
  ContractSaveDto,
} from '@/types/system/contract'

export const pageContractApi = (params: ContractPageParams) =>
  request.get<ContractPageData>('/local/contracts/page', params)

export const getContractDetailApi = (id: string) =>
  request.get<ContractRecord>(`/local/contracts/${id}`)

export const createContractApi = (data: ContractSaveDto) =>
  request.post<unknown>('/local/contracts', data)

export const createContractFromQuotationApi = (quotationId: string, data?: Record<string, any>) =>
  request.post<{ id: string; contractNo: string }>(
    `/local/contracts/from-quotation/${quotationId}`,
    data || {},
  )

export const updateContractApi = (id: string, data: ContractSaveDto) =>
  request.put<unknown>(`/local/contracts/${id}`, data)

export const deleteContractApi = (id: string) => request.delete<unknown>(`/local/contracts/${id}`)

export const terminateContractApi = (id: string, remark?: string) =>
  request.post<unknown>(`/local/contracts/${id}/terminate`, null, {
    params: { remark: remark || '' },
  })

export const getContractPaymentSummaryApi = (contractId?: string) =>
  request.get<ContractPaymentSummary[]>('/local/contracts/payment-summary', {
    contractId: contractId || undefined,
  })

export const checkExpiringContractsApi = (days = 30) =>
  request.get<{ expiringCount: number; newWarnings: number; days: number }>(
    '/local/contracts/check-expiring',
    { days },
  )

export const getContractDashboardApi = () =>
  request.get<ContractDashboardData>('/local/contract/dashboard')

export type { ContractRecord, ContractSaveDto, ContractPaymentSummary, ContractDashboardData }
