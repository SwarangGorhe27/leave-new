import { useMemo, useState } from "react";
import { useQueries } from "@tanstack/react-query";
import { Edit3, Plus, Search, Shield, ToggleLeft, ToggleRight, Trash2 } from "lucide-react";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../../../components/ui/dialog";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Switch } from "../../../components/ui/switch";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../../../components/ui/table";
import { Textarea } from "../../../components/ui/textarea";
import { getMasterList } from "../../../modules/masters/api";
import { useMasterCreate, useMasterDelete, useMasterList, useMasterToggleActive, useMasterUpdate } from "../../../modules/masters/hooks";
import { formatDateTime, getCellValue, normalizeTableColumns, sortRecords } from "../../../modules/masters/tableUtils";
import type { MasterConfig, MasterFieldConfig, MasterListQuery, MasterRecord, MasterTableColumnConfig } from "../../../modules/masters/types";
import { MasterForm } from "./MasterForm";

function displayLabel(rec: MasterRecord) {
  return String(rec.label ?? rec.name ?? rec.title ?? rec.code ?? rec.id ?? "");
}

function renderCell(record: MasterRecord, column: MasterTableColumnConfig) {
  if (column.render === "status" || column.key === "is_active") {
    return (
      <Badge variant={record.is_active ? "secondary" : "outline"}>
        {record.is_active ? "Active" : "Inactive"}
      </Badge>
    );
  }
  if (column.render === "datetime") {
    return formatDateTime(record[column.key]);
  }
  if (column.render === "boolean") {
    return record[column.key] ? "Yes" : "No";
  }
  return getCellValue(record, column);
}

function supportsMultiCreate(config: MasterConfig) {
  return config.category === "employee" || config.categoryKey === "employee";
}

export function MasterTable({ config }: { config: MasterConfig }) {
  const [search, setSearch] = useState("");
  const [company, setCompany] = useState<string>("all");
  const [activeOnly, setActiveOnly] = useState(true);
  const [editorOpen, setEditorOpen] = useState(false);
  const [editing, setEditing] = useState<MasterRecord | null>(null);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const columns = useMemo(() => normalizeTableColumns(config.listColumns), [config.listColumns]);
  const multiCreate = supportsMultiCreate(config);

  const query = useMemo<MasterListQuery>(
    () => ({
      search: search.trim() || undefined,
      company: config.companyScoped && company !== "all" ? company : undefined,
      is_active: activeOnly ? "true" : undefined,
      page: 1,
    }),
    [search, config.companyScoped, company, activeOnly],
  );

  const listQ = useMasterList(config.apiName, query);
  const companyQ = useMasterList("Company", { is_active: "true", page: 1 }, config.companyScoped === true);
  const createMut = useMasterCreate(config.apiName, query);
  const updateMut = useMasterUpdate(config.apiName, query);
  const toggleMut = useMasterToggleActive(config.apiName, query);
  const deleteMut = useMasterDelete(config.apiName, query);

  const rows = useMemo(() => {
    const base = listQ.data?.results ?? [];
    if (!sortColumn) return base;
    const column = columns.find((c) => c.key === sortColumn);
    if (!column) return base;
    return sortRecords(base, column, sortDirection);
  }, [listQ.data?.results, sortColumn, sortDirection, columns]);

  const isBusy = createMut.isPending || updateMut.isPending;
  const extraColumns = (config.parentFieldKey ? 1 : 0) + (config.companyScoped ? 1 : 0);
  const colSpan = columns.length + 1 + extraColumns;

  const handleSort = (column: MasterTableColumnConfig) => {
    if (!column.sortable) return;
    if (sortColumn === column.key) {
      setSortDirection((prev) => (prev === "asc" ? "desc" : "asc"));
      return;
    }
    setSortColumn(column.key);
    setSortDirection("asc");
  };

  const buildPayload = (values: Record<string, unknown>) => {
    if (!("label" in values) && !("name" in values) && !("title" in values)) return values;
    const labelValue = String(values.label ?? values.name ?? values.title ?? "");
    return {
      ...values,
      label: String(values.label ?? labelValue),
      name: String(values.name ?? labelValue),
    };
  };

  const handleToggleActive = (record: MasterRecord) => {
    if (record.is_active && activeOnly) {
      setActiveOnly(false);
    }
    toggleMut.mutate({ id: record.id, is_active: !record.is_active });
  };

  const handleDelete = (record: MasterRecord) => {
    const label = String(record.label ?? record.name ?? record.code ?? "this record");
    if (!window.confirm(`Delete ${label}?`)) return;
    deleteMut.mutate(record.id);
  };

  return (
    <div className="space-y-4">
      <div className="flat-card bg-card p-4">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h2 className="text-base font-semibold text-foreground">{config.label}</h2>
            <p className="text-xs text-muted-foreground">
              Manage {config.label} master data.
            </p>
          </div>
          {!config.constant && (
            <Button
              className="gap-1.5"
              onClick={() => {
                setEditing(null);
                setEditorOpen(true);
              }}
            >
              <Plus className="h-4 w-4" />
              Add New
            </Button>
          )}
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <div className="relative min-w-[220px] flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground dark:text-muted-foreground" />
            <Input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-8"
              placeholder={config.searchPlaceholder ?? "Search by code or name"}
            />
          </div>

          {config.companyScoped && (
            <Select value={company} onValueChange={setCompany}>
              <SelectTrigger className="w-[220px]">
                <SelectValue placeholder="Filter company" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All companies</SelectItem>
                {(companyQ.data?.results ?? []).map((c) => (
                  <SelectItem key={String(c.id)} value={String(c.id)}>
                    {displayLabel(c) || c.code}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          <div className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm">
            <span>Active Only</span>
            <Switch checked={activeOnly} onCheckedChange={setActiveOnly} />
          </div>
        </div>
      </div>

      {config.constant && (
        <div className="rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1 font-semibold text-foreground">
            <Shield className="h-3.5 w-3.5" /> System Managed
          </span>{" "}
          This master is constant and cannot be created or edited from UI.
        </div>
      )}

      <div className="flat-card overflow-hidden bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((column) => (
                <TableHead
                  key={column.key}
                  className={column.sortable ? "cursor-pointer select-none" : undefined}
                  onClick={() => handleSort(column)}
                >
                  {column.label}
                  {sortColumn === column.key ? (sortDirection === "asc" ? " A-Z" : " Z-A") : null}
                </TableHead>
              ))}
              {config.parentFieldKey && <TableHead>{config.parentFieldKey.replaceAll("_", " ")}</TableHead>}
              {config.companyScoped && <TableHead>Company</TableHead>}
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {listQ.isLoading ? (
              <TableRow><TableCell colSpan={colSpan}>Loading...</TableCell></TableRow>
            ) : rows.length === 0 ? (
              <TableRow><TableCell colSpan={colSpan}>No records found.</TableCell></TableRow>
            ) : (
              rows.map((r) => (
                <TableRow key={String(r.id)}>
                  {columns.map((column) => (
                    <TableCell key={column.key} className={column.key === "code" ? "font-medium" : undefined}>
                      {renderCell(r, column)}
                    </TableCell>
                  ))}
                  {config.parentFieldKey && <TableCell>{String(r[config.parentFieldKey] ?? "-")}</TableCell>}
                  {config.companyScoped && <TableCell>{String(r.company_name ?? r.company ?? "-")}</TableCell>}
                  <TableCell>
                    <div className="flex justify-end gap-1.5">
                      {!config.constant && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8 gap-1.5"
                            onClick={() => {
                              setEditing(r);
                              setEditorOpen(true);
                            }}
                          >
                            <Edit3 className="h-3.5 w-3.5" />
                            Edit
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8 gap-1.5"
                            onClick={() => handleToggleActive(r)}
                          >
                            {r.is_active ? <ToggleLeft className="h-3.5 w-3.5" /> : <ToggleRight className="h-3.5 w-3.5" />}
                            {r.is_active ? "Deactivate" : "Activate"}
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="h-8 gap-1.5"
                            onClick={() => handleDelete(r)}
                            disabled={deleteMut.isPending}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                            Delete
                          </Button>
                        </>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      <Dialog open={editorOpen} onOpenChange={setEditorOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto overflow-x-hidden">
          <DialogHeader>
            <DialogTitle>{editing ? `Edit ${config.label}` : `Add ${config.label}`}</DialogTitle>
          </DialogHeader>
          {!editing && multiCreate ? (
            <MultipleMasterCreateForm
              config={config}
              isSubmitting={createMut.isPending}
              onCancel={() => setEditorOpen(false)}
              onSubmit={async (multiRows) => {
                for (const row of multiRows) {
                  await createMut.mutateAsync(buildPayload(row));
                }
                setEditorOpen(false);
              }}
            />
          ) : (
            <MasterForm
              config={config}
              mode={editing ? "edit" : "create"}
              initialData={editing}
              isSubmitting={isBusy}
              onCancel={() => setEditorOpen(false)}
              onSubmit={(values) => {
                const payload = buildPayload(values);
                if (editing) {
                  updateMut.mutate(
                    { id: editing.id, payload },
                    { onSuccess: () => setEditorOpen(false) },
                  );
                  return;
                }
                createMut.mutate(payload, { onSuccess: () => setEditorOpen(false) });
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}

type MultiCreateRow = Record<string, unknown>;

function buildDefaultRow(fields: MasterFieldConfig[], defaults: Record<string, unknown> | undefined): MultiCreateRow {
  const row: MultiCreateRow = { ...(defaults ?? {}) };
  for (const field of fields) {
    if (field.readOnly) continue;
    if (row[field.key] !== undefined) continue;
    if (field.type === "boolean") {
      row[field.key] = field.defaultValue ?? field.key === "is_active";
    } else if (field.type === "number") {
      row[field.key] = field.defaultValue ?? "";
    } else if (field.type === "multiselect") {
      row[field.key] = field.defaultValue ?? [];
    } else {
      row[field.key] = field.defaultValue ?? "";
    }
  }
  return row;
}

function MultipleMasterCreateForm({
  config,
  isSubmitting,
  onCancel,
  onSubmit,
}: {
  config: MasterConfig;
  isSubmitting?: boolean;
  onCancel: () => void;
  onSubmit: (rows: Record<string, unknown>[]) => Promise<void>;
}) {
  const fields = useMemo(
    () => (config.formFields ?? []).filter((field) => !field.readOnly),
    [config.formFields],
  );
  const defaultRow = useMemo(() => buildDefaultRow(fields, config.defaultValues), [fields, config.defaultValues]);
  const [rows, setRows] = useState<MultiCreateRow[]>([defaultRow]);
  const [error, setError] = useState("");

  const relationFields = fields.filter((field) => field.relationMaster);
  const relationQueries = useQueries({
    queries: relationFields.map((field) => ({
      queryKey: ["masters", "options", field.relationMaster],
      queryFn: () => getMasterList(String(field.relationMaster), { is_active: "true", page: 1 }),
    })),
  });

  const relationOptionsByKey = useMemo(() => {
    const map: Record<string, MasterRecord[]> = {};
    relationFields.forEach((field, index) => {
      map[field.key] = relationQueries[index]?.data?.results ?? [];
    });
    return map;
  }, [relationFields, relationQueries]);

  const updateRow = (index: number, patch: MultiCreateRow) => {
    setRows((current) => current.map((row, rowIndex) => (rowIndex === index ? { ...row, ...patch } : row)));
  };

  const validateRow = (row: MultiCreateRow) =>
    fields.every((field) => {
      if (!field.required) return true;
      const value = row[field.key];
      if (Array.isArray(value)) return value.length > 0;
      return value !== undefined && value !== null && String(value).trim() !== "";
    });

  const submitRows = async () => {
    const payloads = rows.map((row) => ({ ...row }));

    if (!payloads.length || !payloads.every(validateRow)) {
      setError("Please fill all required fields for every row.");
      return;
    }

    setError("");
    await onSubmit(payloads);
  };

  return (
    <div className="w-full min-w-0 space-y-4">
      <div className="space-y-2">
        {rows.map((row, index) => (
          <div key={index} className="space-y-3 rounded-lg border border-border p-3">
            <div className="grid min-w-0 gap-3 sm:grid-cols-2">
              {fields.map((field) => (
                <div key={field.key} className={field.type === "textarea" ? "space-y-1.5 sm:col-span-2" : "space-y-1.5"}>
                  <Label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                    {field.label}{field.required ? " *" : ""}
                  </Label>
                  {field.type === "boolean" ? (
                    <div className="flex h-10 w-full max-w-[190px] items-center justify-between rounded-lg border border-border px-3 text-sm">
                      <span>{row[field.key] ? "Active" : "Inactive"}</span>
                      <Switch
                        checked={Boolean(row[field.key])}
                        onCheckedChange={(checked) => updateRow(index, { [field.key]: checked })}
                      />
                    </div>
                  ) : field.type === "select" ? (
                    <Select
                      value={String(row[field.key] ?? "")}
                      onValueChange={(value) => updateRow(index, { [field.key]: value })}
                    >
                      <SelectTrigger className="h-10 min-w-0">
                        <SelectValue placeholder={`Select ${field.label}`} />
                      </SelectTrigger>
                      <SelectContent>
                        {(field.options ?? relationOptionsByKey[field.key]?.map((record) => ({
                          value: String(record.id),
                          label: displayLabel(record),
                        })) ?? []).map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  ) : field.type === "textarea" ? (
                    <Textarea
                      value={String(row[field.key] ?? "")}
                      onChange={(event) => updateRow(index, { [field.key]: event.target.value })}
                      placeholder={field.placeholder}
                    />
                  ) : field.type === "color" ? (
                    <Input
                      type="color"
                      value={String(row[field.key] ?? "#000000")}
                      onChange={(event) => updateRow(index, { [field.key]: event.target.value })}
                      className="h-10 min-w-0"
                    />
                  ) : (
                    <Input
                      type={field.type === "number" ? "number" : field.type === "date" || field.type === "time" ? field.type : "text"}
                      value={String(row[field.key] ?? "")}
                      onChange={(event) => updateRow(index, { [field.key]: event.target.value })}
                      placeholder={field.placeholder ?? field.label}
                      className="h-10 min-w-0"
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {error && <p className="text-xs text-destructive">{error}</p>}

      <div className="flex flex-wrap items-center justify-between gap-2 border-t border-border pt-3">
        <Button
          type="button"
          variant="outline"
          className="gap-1.5"
          onClick={() => setRows((current) => [...current, buildDefaultRow(fields, config.defaultValues)])}
        >
          <Plus className="h-4 w-4" />
          Add Row
        </Button>
        <div className="flex items-center gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="button" disabled={isSubmitting} onClick={submitRows}>
            {isSubmitting ? "Creating..." : rows.length > 1 ? "Create All" : "Create"}
          </Button>
        </div>
      </div>
    </div>
  );
}
