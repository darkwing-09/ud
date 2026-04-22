import {
  useReactTable, getCoreRowModel, getSortedRowModel, flexRender,
  type ColumnDef, type SortingState,
} from '@tanstack/react-table'
import { useState } from 'react'
import { ChevronDown, ChevronUp, ChevronsUpDown, ChevronLeft, ChevronRight, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { EmptyState } from '@/components/common/EmptyState'
import { TableSkeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { PAGE_SIZE_OPTIONS } from '@/lib/constants'

interface DataTableProps<T> {
  data: T[]
  columns: ColumnDef<T, any>[]
  isLoading?: boolean
  searchValue?: string
  onSearchChange?: (v: string) => void
  searchPlaceholder?: string
  page?: number
  pageSize?: number
  total?: number
  onPageChange?: (p: number) => void
  onPageSizeChange?: (ps: number) => void
  actions?: React.ReactNode
  emptyTitle?: string
  emptyDescription?: string
  className?: string
}

function SortIcon({ direction }: { direction: 'asc' | 'desc' | false }) {
  if (!direction) return <ChevronsUpDown className="size-3.5 text-muted-foreground/50" />
  if (direction === 'asc') return <ChevronUp className="size-3.5 text-primary" />
  return <ChevronDown className="size-3.5 text-primary" />
}

export function DataTable<T>({
  data,
  columns,
  isLoading,
  searchValue,
  onSearchChange,
  searchPlaceholder = 'Search...',
  page = 1,
  pageSize = 20,
  total = 0,
  onPageChange,
  onPageSizeChange,
  actions,
  emptyTitle = 'No records found',
  emptyDescription,
  className,
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortingState>([])

  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    manualPagination: true,
    manualFiltering: true,
    rowCount: total,
  })

  const totalPages = Math.ceil(total / pageSize)

  if (isLoading) return <TableSkeleton rows={pageSize > 10 ? 10 : pageSize} cols={columns.length} />

  return (
    <div className={cn('data-table-wrapper', className)}>
      {/* Toolbar */}
      {(onSearchChange !== undefined || actions) && (
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b border-border">
          {onSearchChange !== undefined && (
            <Input
              placeholder={searchPlaceholder}
              value={searchValue}
              onChange={(e) => onSearchChange(e.target.value)}
              leftIcon={<Search />}
              className="max-w-xs"
            />
          )}
          <div className="flex items-center gap-2 ml-auto">
            {actions}
          </div>
        </div>
      )}

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            {table.getHeaderGroups().map((hg) => (
              <tr key={hg.id} className="border-b border-border bg-muted/30">
                {hg.headers.map((header) => (
                  <th
                    key={header.id}
                    className={cn(
                      'px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted-foreground whitespace-nowrap',
                      header.column.getCanSort() && 'cursor-pointer select-none hover:text-foreground transition-colors'
                    )}
                    onClick={header.column.getToggleSortingHandler()}
                    aria-sort={
                      header.column.getIsSorted() === 'asc' ? 'ascending'
                        : header.column.getIsSorted() === 'desc' ? 'descending'
                        : 'none'
                    }
                  >
                    <div className="flex items-center gap-1.5">
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getCanSort() && (
                        <SortIcon direction={header.column.getIsSorted()} />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody className="divide-y divide-border">
            {table.getRowModel().rows.length === 0 ? (
              <tr>
                <td colSpan={columns.length}>
                  <EmptyState
                    title={emptyTitle}
                    description={emptyDescription}
                    className="py-12"
                  />
                </td>
              </tr>
            ) : (
              table.getRowModel().rows.map((row, i) => (
                <tr
                  key={row.id}
                  className={cn(
                    'hover:bg-muted/30 transition-colors duration-100',
                    i % 2 === 0 ? 'bg-transparent' : 'bg-muted/10'
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3 text-sm text-foreground">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {(onPageChange || onPageSizeChange) && (
        <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-t border-border">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span>Show</span>
            <select
              value={pageSize}
              onChange={(e) => onPageSizeChange?.(Number(e.target.value))}
              className="h-7 rounded-md border border-border bg-input px-2 text-foreground text-xs outline-none focus:ring-2 focus:ring-ring"
            >
              {PAGE_SIZE_OPTIONS.map((ps) => (
                <option key={ps} value={ps}>{ps}</option>
              ))}
            </select>
            <span>of {total} records</span>
          </div>

          <div className="flex items-center gap-1">
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => onPageChange?.(page - 1)}
              disabled={page <= 1}
              aria-label="Previous page"
            >
              <ChevronLeft className="size-3.5" />
            </Button>
            <div className="flex items-center gap-0.5">
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                const p = i + 1
                return (
                  <button
                    key={p}
                    onClick={() => onPageChange?.(p)}
                    className={cn(
                      'h-7 min-w-7 px-2 rounded-md text-xs font-medium transition-colors',
                      p === page
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                    )}
                  >
                    {p}
                  </button>
                )
              })}
              {totalPages > 7 && <span className="px-1 text-xs text-muted-foreground">…{totalPages}</span>}
            </div>
            <Button
              variant="outline"
              size="icon-sm"
              onClick={() => onPageChange?.(page + 1)}
              disabled={page >= totalPages}
              aria-label="Next page"
            >
              <ChevronRight className="size-3.5" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
