import { useState, useCallback } from 'react'
import { DEFAULT_PAGE_SIZE } from '@/lib/constants'

export interface PaginationState {
  page: number
  pageSize: number
  search: string
  sortBy: string
  sortDir: 'asc' | 'desc'
}

export function usePagination(defaults?: Partial<PaginationState>) {
  const [state, setState] = useState<PaginationState>({
    page: 1,
    pageSize: defaults?.pageSize ?? DEFAULT_PAGE_SIZE,
    search: defaults?.search ?? '',
    sortBy: defaults?.sortBy ?? 'created_at',
    sortDir: defaults?.sortDir ?? 'desc',
  })

  const setPage = useCallback((page: number) => setState((s) => ({ ...s, page })), [])
  const setSearch = useCallback((search: string) => setState((s) => ({ ...s, search, page: 1 })), [])
  const setSort = useCallback((sortBy: string) => {
    setState((s) => ({
      ...s,
      sortBy,
      sortDir: s.sortBy === sortBy && s.sortDir === 'asc' ? 'desc' : 'asc',
      page: 1,
    }))
  }, [])
  const setPageSize = useCallback((pageSize: number) => setState((s) => ({ ...s, pageSize, page: 1 })), [])

  return { ...state, setPage, setSearch, setSort, setPageSize }
}
