import { useMemo } from 'react';
import { DataTable } from '@components/ui';
import type { ColumnDef } from '@components/ui';
import type { EmployeeListItem } from '@hooks/useEmployees';

interface EmployeeTableProps {
  data: EmployeeListItem[];
  isLoading?: boolean;
}

export function EmployeeTable({ data, isLoading }: EmployeeTableProps) {
  const columns = useMemo<ColumnDef<EmployeeListItem>[]>(
    () => [
      {
        id: 'full_name',
        header: 'Employee',
        accessor: 'full_name',
        sortable: true,
        width: 280,
        sticky: true,
        render: (row: EmployeeListItem) => (
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-brand-100 text-sm font-bold text-brand-700 dark:bg-brand-500/20 dark:text-brand-300">
              {row.first_name[0]}{row.last_name[0]}
            </div>
            <div>
              <p className="font-bold text-text-primary">{row.full_name}</p>
              <p className="text-xs text-text-tertiary">{row.work_email}</p>
            </div>
          </div>
        ),
      },
      { 
        id: 'employee_code', 
        header: 'ID', 
        accessor: 'employee_code', 
        sortable: true, 
        width: 140,
        render: (row) => <span className="font-mono text-xs font-medium text-text-secondary">{row.employee_code}</span>
      },
      { 
        id: 'designation', 
        header: 'Designation', 
        accessor: 'designation', 
        sortable: true, 
        width: 200,
        render: (row) => <span className="text-sm text-text-secondary">{row.designation}</span>
      },
      { 
        id: 'department', 
        header: 'Department', 
        accessor: 'department', 
        sortable: true, 
        width: 180,
        render: (row) => <span className="text-sm text-text-secondary">{row.department}</span>
      },
      {
        id: 'status',
        header: 'Status',
        accessor: (row) => row.status_detail?.name ?? '—',
        sortable: true,
        width: 140,
        render: (row: EmployeeListItem) => {
          const color = row.status_detail?.color_code || '#999';
          return (
            <div className="flex items-center gap-2">
              <div 
                className="h-2 w-2 rounded-full shadow-[0_0_8px_rgba(0,0,0,0.1)]" 
                style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}40` }} 
              />
              <span className="text-xs font-semibold text-text-secondary">{row.status_detail?.name ?? '—'}</span>
            </div>
          );
        },
      },
    ],
    [],
  );

  return (
    <DataTable
      id="employee-directory-table"
      data={data}
      columns={columns}
      isLoading={isLoading}
      getRowId={(row) => row.id}
    />
  );
}
