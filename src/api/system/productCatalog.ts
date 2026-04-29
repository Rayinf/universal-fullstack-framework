import request from '@/utils/request'
import type {
  ProductCatalogPageData,
  ProductCatalogPageParams,
  ProductCatalogRecord,
  ProductCatalogSaveDto,
} from '@/types/system/productCatalog'

export const pageProductCatalogApi = (params: ProductCatalogPageParams) =>
  request.get<ProductCatalogPageData>('/local/product-catalog/page', params)

export const listProductCatalogApi = () =>
  request.get<ProductCatalogRecord[]>('/local/product-catalog/list')

export const createProductCatalogApi = (data: ProductCatalogSaveDto) =>
  request.post<unknown>('/local/product-catalog', data)

export const updateProductCatalogApi = (id: string, data: ProductCatalogSaveDto) =>
  request.put<unknown>(`/local/product-catalog/${id}`, data)

export const deleteProductCatalogApi = (id: string) =>
  request.delete<unknown>(`/local/product-catalog/${id}`)

export type { ProductCatalogRecord, ProductCatalogSaveDto }
