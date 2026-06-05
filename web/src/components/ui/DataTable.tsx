import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { useVirtualizer } from '@tanstack/react-virtual';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown, ChevronLeft, ChevronRight, ChevronsUpDown, Download, Eye, MoreHorizontal, Pencil, Search, Trash2 } from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { cn } from '@utils/utils';
import { Button } from './Button';
import { EmptyState } from './EmptyState';
import { SkeletonTable } from './Skeleton';

export interface ColumnDef<T> {
  id: string;
  header: string;
  accessor?: keyof T | ((row: T) => string | number | boolean | null | undefined | Date);
  cell?: (row: T) => React.ReactNode;
  sortable?: boolean;
  width?: number;
  minWidth?: number;
  sticky?: boolean;
}

export interface FilterChip {
  id: string;
  label: string;
  value: string;
}

export interface BulkAction<T> {
  label: string;
  onClick: (rows: T[]) => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
}

interface SortState {
  id: string;
  direction: 'asc' | 'desc';
}

interface DataTableProps<T> {
  id: string;
  data: T[];
  columns: ColumnDef<T>[];
  loading?: boolean;
  manual?: boolean;
  totalCount?: number;
  page?: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
  onSearchChange?: (value: string) => void;
  emptyState?: React.ReactNode;
  getRowId: (row: T) => string;
  bulkActions?: BulkAction<T>[];
  activeFilters?: FilterChip[];
  onRemoveFilter?: (filterId: string) => void;
  onClearFilters?: () => void;
  onRowClick?: (row: T) => void;
  rowActions?: (row: T) => React.ReactNode;
  globalSearchPlaceholder?: string;
  exportFileName?: string;
}

const PAGE_SIZES = [10, 25, 50, 100];

function sortRows<T>(rows: T[], columns: ColumnDef<T>[], sorting: SortState[]) {
  const columnMap = new Map(columns.map((column) => [column.id, column]));
  return [...rows].sort((left, right) => {
    for (const sort of sorting) {
      const column = columnMap.get(sort.id);
      if (!column) {
        continue;
      }
      const leftValue = getCellValue(left, column);
      const rightValue = getCellValue(right, column);
      if (leftValue === rightValue) {
        continue;
      }
      const result = String(leftValue ?? '').localeCompare(String(rightValue ?? ''), undefined, { numeric: true, sensitivity: 'base' });
      return sort.direction === 'asc' ? result : -result;
    }
    return 0;
  });
}

function getCellValue<T>(row: T, column: ColumnDef<T>) {
  if (typeof column.accessor === 'function') {
    return column.accessor(row);
  }
  if (column.accessor) {
    return row[column.accessor];
  }
  return '';
}

function exportRows<T>(rows: T[], columns: ColumnDef<T>[], type: 'csv' | 'xlsx', filename: string) {
  const activeColumns = columns.filter((column) => column.id !== 'select');
  const separator = type === 'csv' ? ',' : '\t';
  const content = [
    activeColumns.map((column) => column.header).join(separator),
    ...rows.map((row) =>
      activeColumns
        .map((column) => {
          const value = getCellValue(row, column);
          return `"${String(value ?? '').split('"').join('""')}"`;
        })
        .join(separator)
    )
  ].join('\n');
  const blob = new Blob([content], { type: type === 'csv' ? 'text/csv;charset=utf-8;' : 'application/vnd.ms-excel' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = `${filename}.${type}`;
  anchor.click();
  URL.revokeObjectURL(url);
}

export function DataTable<T>({
  id,
  data,
  columns,
  loading,
  manual,
  totalCount,
  page: controlledPage,
  pageSize: controlledPageSize,
  onPageChange,
  onPageSizeChange,
  onSearchChange,
  emptyState,
  getRowId,
  bulkActions = [],
  activeFilters = [],
  onRemoveFilter,
  onClearFilters,
  onRowClick,
  rowActions,
  globalSearchPlaceholder = 'Search records...',
  exportFileName = 'export'
}: DataTableProps<T>) {
  const [sorting, setSorting] = useState<SortState[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [pageState, setPageState] = useState(1);
  const [pageSizeState, setPageSizeState] = useState(10);
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>(() => Object.fromEntries(columns.map((column) => [column.id, column.width ?? 180])));
  const [visibleColumns, setVisibleColumns] = useState<Record<string, boolean>>(() => {
    const stored = localStorage.getItem(`table-visibility:${id}`);
    if (!stored) {
      return Object.fromEntries(columns.map((column) => [column.id, true]));
    }
    try {
      const parsed = JSON.parse(stored) as Record<string, boolean>;
      return { ...Object.fromEntries(columns.map((column) => [column.id, true])), ...parsed };
    } catch {
      return Object.fromEntries(columns.map((column) => [column.id, true]));
    }
  });
  const scrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(`table-visibility:${id}`, JSON.stringify(visibleColumns));
  }, [id, visibleColumns]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      onSearchChange?.(search);
    }, 300);
    return () => window.clearTimeout(timeout);
  }, [onSearchChange, search]);

  const page = controlledPage ?? pageState;
  const pageSize = controlledPageSize ?? pageSizeState;

  const visibleDefs = useMemo(() => columns.filter((column) => visibleColumns[column.id] !== false), [columns, visibleColumns]);

  const filteredRows = useMemo(() => {
    if (manual || !search.trim()) {
      return data;
    }
    const query = search.toLowerCase();
    return data.filter((row) =>
      visibleDefs.some((column) => {
        const value = getCellValue(row, column);
        return String(value ?? '').toLowerCase().includes(query);
      })
    );
  }, [data, manual, search, visibleDefs]);

  const sortedRows = useMemo(() => (manual ? filteredRows : sortRows(filteredRows, visibleDefs, sorting)), [filteredRows, manual, sorting, visibleDefs]);
  const total = totalCount ?? sortedRows.length;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const paginatedRows = useMemo(() => {
    if (manual) {
      return sortedRows;
    }
    const start = (page - 1) * pageSize;
    return sortedRows.slice(start, start + pageSize);
  }, [manual, page, pageSize, sortedRows]);

  const selectedRows = useMemo(() => paginatedRows.filter((row) => selectedIds.includes(getRowId(row))), [getRowId, paginatedRows, selectedIds]);
  const useVirtual = paginatedRows.length > 200;
  const rowVirtualizer = useVirtualizer({ count: paginatedRows.length, getScrollElement: () => scrollRef.current, estimateSize: () => 56, overscan: 8 });
  const virtualRows = useVirtual ? rowVirtualizer.getVirtualItems() : [];

  function toggleSort(columnId: string) {
    setSorting((current) => {
      const existing = current.find((item) => item.id === columnId);
      if (!existing) {
        return [...current, { id: columnId, direction: 'asc' }];
      }
      if (existing.direction === 'asc') {
        return current.map((item) => (item.id === columnId ? { ...item, direction: 'desc' } : item));
      }
      return current.filter((item) => item.id !== columnId);
    });
  }

  function resizeColumn(columnId: string, clientX: number) {
    const startWidth = columnWidths[columnId] ?? 180;
    const startX = clientX;
    function onMove(event: MouseEvent) {
      const nextWidth = Math.max(columns.find((column) => column.id === columnId)?.minWidth ?? 120, startWidth + event.clientX - startX);
      setColumnWidths((current) => ({ ...current, [columnId]: nextWidth }));
    }
    function onUp() {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }

  function setPage(nextPage: number) {
    const bounded = Math.max(1, Math.min(nextPage, totalPages));
    onPageChange ? onPageChange(bounded) : setPageState(bounded);
  }

  function setPageSize(nextPageSize: number) {
    onPageSizeChange ? onPageSizeChange(nextPageSize) : setPageSizeState(nextPageSize);
    setPage(1);
  }

  function toggleSelectAll() {
    if (selectedIds.length === paginatedRows.length && paginatedRows.length > 0) {
      setSelectedIds([]);
      return;
    }
    setSelectedIds(paginatedRows.map(getRowId));
  }

  function toggleSelect(idValue: string) {
    setSelectedIds((current) => (current.includes(idValue) ? current.filter((item) => item !== idValue) : [...current, idValue]));
  }

  const rowSet = selectedIds.length === paginatedRows.length && paginatedRows.length > 0;
  const rangeStart = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const rangeEnd = Math.min(page * pageSize, total);

  return (
    <div className="surface-card overflow-hidden">
      <div className="flex flex-col gap-4 border-b border-surface-300/70 px-5 py-4 dark:border-white/10">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative w-full max-w-sm">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-surface-500 dark:text-white/40" />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={globalSearchPlaceholder} className="input-base pl-10" />
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <Button variant="secondary" size="sm" iconLeft={<Eye className="h-4 w-4" />} iconRight={<ChevronDown className="h-4 w-4" />}>
                  Columns
                </Button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content sideOffset={8} align="end" className="z-50 min-w-[220px] rounded-xl border border-surface-300 bg-surface-0 p-1 shadow-lg dark:border-white/10 dark:bg-surface-100">
                  {columns.map((column) => (
                    <DropdownMenu.CheckboxItem key={column.id} checked={visibleColumns[column.id] !== false} onCheckedChange={(checked) => setVisibleColumns((current) => ({ ...current, [column.id]: Boolean(checked) }))} className="flex cursor-pointer items-center gap-2 rounded-lg px-3 py-2 text-sm text-surface-700 outline-none focus:bg-surface-100 dark:text-white/75 dark:focus:bg-white/5">
                      {column.header}
                    </DropdownMenu.CheckboxItem>
                  ))}
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <Button variant="secondary" size="sm" iconLeft={<Download className="h-4 w-4" />} iconRight={<ChevronDown className="h-4 w-4" />}>
                  Export
                </Button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content sideOffset={8} align="end" className="z-50 min-w-[180px] rounded-xl border border-surface-300 bg-surface-0 p-1 shadow-lg dark:border-white/10 dark:bg-surface-100">
                  <DropdownMenu.Item onSelect={() => exportRows(selectedRows.length > 0 ? selectedRows : sortedRows, visibleDefs, 'csv', exportFileName)} className="cursor-pointer rounded-lg px-3 py-2 text-sm text-surface-700 outline-none focus:bg-surface-100 dark:text-white/75 dark:focus:bg-white/5">Export CSV</DropdownMenu.Item>
                  <DropdownMenu.Item onSelect={() => exportRows(selectedRows.length > 0 ? selectedRows : sortedRows, visibleDefs, 'xlsx', exportFileName)} className="cursor-pointer rounded-lg px-3 py-2 text-sm text-surface-700 outline-none focus:bg-surface-100 dark:text-white/75 dark:focus:bg-white/5">Export XLSX</DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
          </div>
        </div>
        {activeFilters.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2">
            {activeFilters.map((filter) => (
              <span key={filter.id} className="inline-flex items-center gap-2 rounded-full bg-surface-100 px-3 py-1 text-xs text-surface-700 dark:bg-white/5 dark:text-white/60">
                <span className="font-medium">{filter.label}</span>
                <span>{filter.value}</span>
                {onRemoveFilter ? <button className="text-surface-500 dark:text-white/35" onClick={() => onRemoveFilter(filter.id)}>x</button> : null}
              </span>
            ))}
            {onClearFilters ? <Button variant="ghost" size="xs" onClick={onClearFilters}>Clear all</Button> : null}
          </div>
        ) : null}
      </div>

      <AnimatePresence>
        {selectedRows.length > 0 ? (
          <motion.div initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} className="flex items-center justify-between gap-3 border-b border-brand-200 bg-brand-50 px-5 py-3 dark:border-brand-500/20 dark:bg-brand-500/10">
            <p className="text-sm font-medium text-brand-800 dark:text-brand-100">{selectedRows.length} selected</p>
            <div className="flex flex-wrap items-center gap-2">
              {bulkActions.map((action) => (
                <Button key={action.label} size="sm" variant={action.variant ?? 'secondary'} onClick={() => action.onClick(selectedRows)}>
                  {action.label}
                </Button>
              ))}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {loading ? (
        <SkeletonTable rows={5} />
      ) : paginatedRows.length === 0 ? (
        emptyState ?? <EmptyState icon={Search} title="No matching records" description="Try adjusting the current filters or search query." />
      ) : (
        <div className="relative">
          <div ref={scrollRef} className="max-h-[520px] overflow-auto">
            <div className="min-w-full">
              <div className="sticky top-0 z-10 flex border-b border-surface-300/70 bg-surface-0/95 backdrop-blur-md dark:border-white/10 dark:bg-surface-100/95">
                <div className="sticky left-0 z-20 flex h-12 w-12 shrink-0 items-center justify-center border-r border-surface-300/70 bg-inherit dark:border-white/10">
                  <input type="checkbox" checked={rowSet} ref={(node) => {
                    if (node) {
                      node.indeterminate = selectedIds.length > 0 && selectedIds.length < paginatedRows.length;
                    }
                  }} onChange={toggleSelectAll} aria-label="Select all rows" />
                </div>
                {visibleDefs.map((column, index) => {
                  const sort = sorting.find((item) => item.id === column.id);
                  return (
                    <div key={column.id} style={{ width: columnWidths[column.id], minWidth: column.minWidth ?? 120 }} className={cn('group relative flex h-12 shrink-0 items-center gap-2 border-r border-surface-300/60 px-3 text-sm font-medium text-surface-700 dark:border-white/10 dark:text-white/65', column.sticky && 'sticky left-12 z-10 bg-inherit')}>
                      <button type="button" className="flex items-center gap-2" onClick={() => column.sortable ? toggleSort(column.id) : undefined}>
                        <span>{column.header}</span>
                        {column.sortable ? (
                          sort ? <span className="text-brand-500">{sort.direction === 'asc' ? '↑' : '↓'}</span> : <ChevronsUpDown className="h-3.5 w-3.5 text-surface-400 dark:text-white/30" />
                        ) : null}
                      </button>
                      {index < visibleDefs.length ? (
                        <button type="button" aria-label={`Resize ${column.header} column`} className="absolute right-0 top-0 h-full w-2 cursor-col-resize opacity-0 transition group-hover:opacity-100" onMouseDown={(event) => resizeColumn(column.id, event.clientX)} />
                      ) : null}
                    </div>
                  );
                })}
                <div className="sticky right-0 z-10 flex h-12 w-20 shrink-0 items-center justify-center bg-inherit text-sm font-medium text-surface-700 dark:text-white/65">Actions</div>
              </div>
              <div style={useVirtual ? { height: rowVirtualizer.getTotalSize(), position: 'relative' } : undefined}>
                {(useVirtual ? virtualRows.map((virtualRow) => ({ key: virtualRow.key, index: virtualRow.index, start: virtualRow.start })) : paginatedRows.map((_, index) => ({ key: index, index, start: index * 56 }))).map((virtualRow) => {
                  const row = paginatedRows[virtualRow.index];
                  const rowId = getRowId(row);
                  return (
                    <div
                      key={virtualRow.key}
                      style={useVirtual ? { position: 'absolute', top: 0, left: 0, width: '100%', transform: `translateY(${virtualRow.start}px)` } : undefined}
                      className={cn('group flex min-h-14 border-b border-surface-300/60 text-sm transition-colors hover:bg-surface-50 dark:border-white/5 dark:hover:bg-white/[0.03]', onRowClick && 'cursor-pointer')}
                      onClick={() => onRowClick?.(row)}
                    >
                      <div className="sticky left-0 z-[1] flex w-12 shrink-0 items-center justify-center border-r border-surface-300/60 bg-inherit dark:border-white/5">
                        <input type="checkbox" checked={selectedIds.includes(rowId)} onChange={() => toggleSelect(rowId)} onClick={(event) => event.stopPropagation()} aria-label={`Select row ${rowId}`} />
                      </div>
                      {visibleDefs.map((column) => (
                        <div key={column.id} style={{ width: columnWidths[column.id], minWidth: column.minWidth ?? 120 }} className={cn('flex shrink-0 items-center border-r border-surface-300/50 px-3 py-3 text-surface-700 dark:border-white/5 dark:text-white/75', column.sticky && 'sticky left-12 z-[1] bg-inherit')}>
                          {column.cell ? column.cell(row) : <span className="truncate">{String(getCellValue(row, column) ?? '-')}</span>}
                        </div>
                      ))}
                      <div className="sticky right-0 z-[1] flex w-20 shrink-0 items-center justify-center gap-1 bg-inherit opacity-0 transition-opacity group-hover:opacity-100">
                        {rowActions ? rowActions(row) : (
                          <>
                            <Button variant="ghost" size="xs" iconOnly aria-label="Edit row" onClick={(event) => event.stopPropagation()}>
                              <Pencil className="h-3.5 w-3.5" />
                            </Button>
                            <Button variant="ghost" size="xs" iconOnly aria-label="More options" onClick={(event) => event.stopPropagation()}>
                              <MoreHorizontal className="h-3.5 w-3.5" />
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="pointer-events-none absolute inset-y-0 right-0 w-8 bg-gradient-to-l from-surface-0 to-transparent dark:from-[var(--surface-100)]" />
        </div>
      )}

      <div className="flex flex-col gap-3 border-t border-surface-300/70 px-5 py-4 text-sm dark:border-white/10 lg:flex-row lg:items-center lg:justify-between">
        <p className="text-surface-600 dark:text-white/55">Showing {rangeStart}-{rangeEnd} of {total}</p>
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-surface-600 dark:text-white/55">
            <span>Rows</span>
            <select className="input-base h-9 w-[88px] py-0" value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
              {PAGE_SIZES.map((size) => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </label>
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" iconOnly onClick={() => setPage(page - 1)} disabled={page <= 1} aria-label="Previous page">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-surface-600 dark:text-white/55">Page</span>
            <input className="input-base h-9 w-16 py-0 text-center" value={page} onChange={(event) => setPage(Number(event.target.value) || 1)} aria-label="Page number" />
            <span className="text-surface-600 dark:text-white/55">of {totalPages}</span>
            <Button variant="secondary" size="sm" iconOnly onClick={() => setPage(page + 1)} disabled={page >= totalPages} aria-label="Next page">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
          {bulkActions.length > 0 ? <Button variant="ghost" size="sm" iconLeft={<Trash2 className="h-4 w-4" />} onClick={() => setSelectedIds([])}>Clear selection</Button> : null}
        </div>
      </div>
    </div>
  );
}
