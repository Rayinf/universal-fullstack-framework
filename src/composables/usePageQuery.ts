import { reactive } from 'vue'

export interface StandardPagination {
  current: number
  size: number
  total: number
}

export interface UsePageQueryContext<TQuery extends object> {
  query: TQuery
  pagination: StandardPagination
}

interface UsePageQueryOptions<TQuery extends object> {
  initialQuery: TQuery
  initialPagination?: Partial<StandardPagination>
  load: (context: UsePageQueryContext<TQuery>) => void | Promise<void>
  resetQuery?: (query: TQuery) => void
}

const DEFAULT_PAGINATION: StandardPagination = {
  current: 1,
  size: 10,
  total: 0,
}

const resetReactiveObject = <TQuery extends object>(
  target: TQuery,
  source: TQuery,
) => {
  Object.keys(target as object).forEach((key) => {
    if (!(key in (source as object))) {
      delete (target as Record<string, unknown>)[key]
    }
  })
  Object.assign(target, source)
}

export const usePageQuery = <TQuery extends object>(
  options: UsePageQueryOptions<TQuery>,
) => {
  const query = reactive({ ...options.initialQuery }) as TQuery
  const pagination = reactive<StandardPagination>({
    ...DEFAULT_PAGINATION,
    ...options.initialPagination,
  })

  const loadData = () => Promise.resolve(options.load({ query, pagination }))

  const handleSearch = () => {
    pagination.current = 1
    return loadData()
  }

  const handleReset = () => {
    if (options.resetQuery) {
      options.resetQuery(query)
    } else {
      resetReactiveObject(query, options.initialQuery)
    }
    pagination.current = 1
    return loadData()
  }

  const handleSizeChange = (size: number) => {
    pagination.size = size
    pagination.current = 1
    return loadData()
  }

  const handleCurrentChange = (current: number) => {
    pagination.current = current
    return loadData()
  }

  return {
    query,
    pagination,
    loadData,
    handleSearch,
    handleReset,
    handleSizeChange,
    handleCurrentChange,
  }
}
