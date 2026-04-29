export interface ProductCatalogRecord {
  id: string
  productCode: string
  productName: string
  specification: string
  unit: string
  referencePrice: number
  costPrice: number
  category: string
  status: number
  remark: string
  createTime: string
  updateTime: string
}

export interface ProductCatalogPageParams {
  current: number
  size: number
  keyword?: string
  status?: number
}

export interface ProductCatalogPageData {
  records: ProductCatalogRecord[]
  total: number
  size: number
  current: number
  pages: number
}

export interface ProductCatalogSaveDto {
  productCode: string
  productName: string
  specification: string
  unit: string
  referencePrice: number
  costPrice: number
  category: string
  status: number
  remark: string
}
