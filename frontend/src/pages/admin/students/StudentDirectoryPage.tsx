import { useQuery } from '@tanstack/react-query'
import { type ColumnDef } from '@tanstack/react-table'
import { Plus, Upload, Download, Eye, Pencil, Trash2 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { DataTable } from '@/components/tables/DataTable'
import { PageHeader } from '@/components/common/PageHeader'
import { Button } from '@/components/ui/button'
import { StatusBadge } from '@/components/ui/badge'
import { UserAvatar } from '@/components/ui/avatar'
import { usePagination } from '@/hooks/usePagination'
import { useDebounce } from '@/hooks/useDebounce'
import { get } from '@/lib/api'
import { formatDate } from '@/lib/utils'
import type { StudentProfile } from '@/types/models'
import type { PaginatedResponse } from '@/types/models'
import { API } from '@/lib/constants'
import { toast } from 'sonner'

export default function StudentDirectoryPage() {
  const { page, pageSize, search, setPage, setSearch, setPageSize } = usePagination()
  const debouncedSearch = useDebounce(search)

  const { data, isLoading } = useQuery<PaginatedResponse<StudentProfile>>({
    queryKey: ['students', page, pageSize, debouncedSearch],
    queryFn: () => get<PaginatedResponse<StudentProfile>>(API.STUDENTS.BASE, {
      page, page_size: pageSize, search: debouncedSearch,
    }),
    staleTime: 2 * 60 * 1000,
  })

  const columns: ColumnDef<StudentProfile>[] = [
    {
      id: 'student',
      header: 'Student',
      cell: ({ row: { original: s } }) => (
        <div className="flex items-center gap-3">
          <UserAvatar name={s.full_name} src={s.avatar_url} size="sm" />
          <div>
            <p className="font-medium text-foreground">{s.full_name}</p>
            <p className="text-xs text-muted-foreground">#{s.admission_number}</p>
          </div>
        </div>
      ),
    },
    {
      accessorKey: 'class_name',
      header: 'Class',
      cell: ({ getValue }) => (
        <span className="text-sm text-foreground">{getValue<string>() ?? '—'}</span>
      ),
    },
    {
      accessorKey: 'section_name',
      header: 'Section',
      cell: ({ getValue }) => (
        <span className="font-medium text-primary">{getValue<string>() ?? '—'}</span>
      ),
    },
    {
      accessorKey: 'roll_number',
      header: 'Roll No.',
      cell: ({ getValue }) => (
        <span className="font-mono text-sm">{getValue<string>() ?? '—'}</span>
      ),
    },
    {
      accessorKey: 'gender',
      header: 'Gender',
      cell: ({ getValue }) => (
        <span className="text-sm text-muted-foreground capitalize">{getValue<string>() ?? '—'}</span>
      ),
    },
    {
      accessorKey: 'date_of_admission',
      header: 'Admitted',
      cell: ({ getValue }) => (
        <span className="text-sm text-muted-foreground">
          {getValue<string>() ? formatDate(getValue<string>()) : '—'}
        </span>
      ),
    },
    {
      accessorKey: 'is_active',
      header: 'Status',
      cell: ({ getValue }) => (
        <StatusBadge status={getValue<boolean>() ? 'ACTIVE' : 'INACTIVE'} />
      ),
    },
    {
      id: 'actions',
      header: '',
      cell: ({ row: { original: s } }) => (
        <div className="flex items-center gap-1">
          <Link to={`/admin/students/${s.id}`}>
            <Button variant="ghost" size="icon-sm" aria-label="View student">
              <Eye className="size-3.5" />
            </Button>
          </Link>
          <Link to={`/admin/students/${s.id}/edit`}>
            <Button variant="ghost" size="icon-sm" aria-label="Edit student">
              <Pencil className="size-3.5" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="icon-sm"
            className="text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
            aria-label="Delete student"
            onClick={() => toast.error('Delete coming soon')}
          >
            <Trash2 className="size-3.5" />
          </Button>
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Student Directory"
        description={`${data?.total ?? 0} students enrolled`}
        breadcrumbs={[{ label: 'Admin' }, { label: 'Students' }]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link to="/admin/students/bulk-import">
                <Upload className="size-4" />
                Bulk Import
              </Link>
            </Button>
            <Button variant="outline" size="sm" onClick={() => toast.info('Export coming soon')}>
              <Download className="size-4" />
              Export
            </Button>
            <Button size="sm" asChild>
              <Link to="/admin/students/new">
                <Plus className="size-4" />
                Enroll Student
              </Link>
            </Button>
          </div>
        }
      />

      <DataTable
        data={data?.items ?? []}
        columns={columns}
        isLoading={isLoading}
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search by name, admission no..."
        page={page}
        pageSize={pageSize}
        total={data?.total ?? 0}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
        emptyTitle="No students found"
        emptyDescription="Try adjusting your search or enroll a new student."
      />
    </div>
  )
}
