import { Fragment, useEffect, useMemo } from "react";
import { useQueries } from "@tanstack/react-query";
import { useForm, Controller, useWatch } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "../../../components/ui/button";
import { Checkbox } from "../../../components/ui/checkbox";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../../../components/ui/select";
import { Switch } from "../../../components/ui/switch";
import { Textarea } from "../../../components/ui/textarea";
import { getMasterList } from "../../../modules/masters/api";
import type { MasterConfig, MasterFieldConfig, MasterRecord } from "../../../modules/masters/types";

type FormValues = Record<string, unknown>;

function schemaForFields(fields: MasterFieldConfig[]) {
  const shape: Record<string, z.ZodTypeAny> = {};
  for (const field of fields) {
    if (field.readOnly) continue;
    if (field.type === "boolean") {
      shape[field.key] = z.boolean().optional();
      continue;
    }
    if (field.type === "multiselect") {
      shape[field.key] = z.array(z.string()).optional();
      continue;
    }
    if (field.type === "number") {
      let base = z.coerce.number();
      if (field.min !== undefined) base = base.min(field.min);
      if (field.max !== undefined) base = base.max(field.max);
      shape[field.key] = z.preprocess(
        (value) => (value === "" || value === null ? undefined : value),
        field.required ? base : base.optional(),
      );
      continue;
    }
    const str = z.string().trim();
    shape[field.key] = field.required
      ? z.preprocess((value) => value ?? "", str.min(1, `${field.label} is required`))
      : z.preprocess((value) => (value === null ? undefined : value), str.optional());
  }
  return z.object(shape);
}

function getLabel(rec: MasterRecord) {
  return String(rec.label ?? rec.name ?? rec.code ?? rec.id);
}

function isFieldDisabled(field: MasterFieldConfig, values: FormValues) {
  if (!field.disabledWhen) return false;
  const current = values[field.disabledWhen.field];
  if (field.disabledWhen.equals !== undefined) return current === field.disabledWhen.equals;
  if (field.disabledWhen.notEquals !== undefined) return current !== field.disabledWhen.notEquals;
  return false;
}

function buildDefaultValues(
  fields: MasterFieldConfig[],
  configDefaults: Record<string, unknown> | undefined,
  initialData: MasterRecord | null | undefined,
  mode: "create" | "edit",
) {
  const out: FormValues = { ...configDefaults };
  for (const field of fields) {
    if (field.readOnly && mode !== "edit") continue;
    const fromRecord = initialData?.[field.key];
    if (fromRecord !== undefined && fromRecord !== null) {
      if (field.type === "multiselect") {
        out[field.key] = Array.isArray(fromRecord) ? fromRecord.map(String) : [];
      } else if (field.type === "boolean") {
        out[field.key] = Boolean(fromRecord);
      } else {
        out[field.key] = String(fromRecord);
      }
      continue;
    }
    if (out[field.key] !== undefined) continue;
    if (field.type === "boolean") {
      out[field.key] = field.defaultValue ?? field.key === "is_active";
    } else if (field.type === "multiselect") {
      out[field.key] = field.defaultValue ?? [];
    } else if (field.type === "number") {
      out[field.key] = field.defaultValue ?? "";
    } else {
      out[field.key] = field.defaultValue ?? "";
    }
  }
  return out;
}

export function MasterForm({
  config,
  mode,
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
}: {
  config: MasterConfig;
  mode: "create" | "edit";
  initialData?: MasterRecord | null;
  onSubmit: (values: FormValues) => void;
  onCancel: () => void;
  isSubmitting?: boolean;
}) {
  const fields = useMemo(
    () => (config.formFields ?? []).filter((field) => !field.readOnly || mode === "edit"),
    [config.formFields, mode],
  );

  const schema = useMemo(
    () => config.validationSchema ?? schemaForFields(fields),
    [config.validationSchema, fields],
  );

  const defaults = useMemo(
    () => buildDefaultValues(config.formFields ?? [], config.defaultValues, initialData, mode),
    [config.formFields, config.defaultValues, initialData, mode],
  );

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: defaults,
  });

  const watchedValues = useWatch({ control: form.control }) as FormValues;

  useEffect(() => {
    if (!config.formBehaviors?.length) return;
    for (const rule of config.formBehaviors) {
      if (watchedValues?.[rule.when.field] !== rule.when.equals || !rule.set) continue;
      Object.entries(rule.set).forEach(([key, value]) => {
        if (form.getValues(key) !== value) {
          form.setValue(key, value, { shouldValidate: true });
        }
      });
    }
  }, [config.formBehaviors, form, watchedValues]);

  const relationFields = fields.filter((f) => f.relationMaster && f.type !== "multiselect");
  const multiselectRelationFields = fields.filter((f) => f.relationMaster && f.type === "multiselect");

  const relationQueries = useQueries({
    queries: [...relationFields, ...multiselectRelationFields].map((f) => ({
      queryKey: ["masters", "options", f.relationMaster],
      queryFn: () => getMasterList(String(f.relationMaster), { is_active: "true", page: 1 }),
    })),
  });

  const relationOptionsByKey = useMemo(() => {
    const allRelationFields = [...relationFields, ...multiselectRelationFields];
    const map: Record<string, MasterRecord[]> = {};
    allRelationFields.forEach((f, i) => {
      map[f.key] = relationQueries[i]?.data?.results ?? [];
    });
    return map;
  }, [relationFields, multiselectRelationFields, relationQueries]);

  const sections = useMemo(() => {
    const grouped = new Map<string, MasterFieldConfig[]>();
    for (const field of fields) {
      const section = field.section ?? "";
      if (!grouped.has(section)) grouped.set(section, []);
      grouped.get(section)!.push(field);
    }
    return Array.from(grouped.entries());
  }, [fields]);

  const renderField = (field: MasterFieldConfig) => {
    const err = form.formState.errors[field.key]?.message;
    const disabled = isFieldDisabled(field, watchedValues ?? {});

    return (
      <div key={field.key} className={field.type === "textarea" ? "sm:col-span-2 space-y-1.5" : "space-y-1.5"}>
        <Label className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {field.label}{field.required ? " *" : ""}
        </Label>

        {field.type === "boolean" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <div className="flex h-9 items-center justify-between rounded-lg border border-border px-3">
                <span className="text-sm text-foreground">{ctrl.value ? "Enabled" : "Disabled"}</span>
                <Switch checked={Boolean(ctrl.value)} onCheckedChange={ctrl.onChange} disabled={disabled} />
              </div>
            )}
          />
        ) : field.type === "textarea" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <Textarea
                value={String(ctrl.value ?? "")}
                onChange={ctrl.onChange}
                onBlur={ctrl.onBlur}
                name={ctrl.name}
                placeholder={field.placeholder}
                disabled={disabled}
              />
            )}
          />
        ) : field.type === "date" || field.type === "time" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <Input
                type={field.type}
                value={String(ctrl.value ?? "")}
                onChange={ctrl.onChange}
                onBlur={ctrl.onBlur}
                name={ctrl.name}
                disabled={disabled || field.readOnly}
              />
            )}
          />
        ) : field.type === "multiselect" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => {
              const selected = Array.isArray(ctrl.value) ? (ctrl.value as string[]) : [];
              const options =
                field.options ??
                relationOptionsByKey[field.key]?.map((r) => ({ value: String(r.id), label: getLabel(r) })) ??
                [];

              return (
                <div className={`space-y-2 rounded-lg border border-border p-3 ${disabled ? "opacity-50" : ""}`}>
                  {options.map((opt) => {
                    const checked = selected.includes(opt.value);
                    return (
                      <label key={opt.value} className="flex items-center gap-2 text-sm">
                        <Checkbox
                          checked={checked}
                          disabled={disabled}
                          onCheckedChange={(next) => {
                            const nextSelected = next
                              ? [...selected, opt.value]
                              : selected.filter((v) => v !== opt.value);
                            ctrl.onChange(nextSelected);
                          }}
                        />
                        <span>{opt.label}</span>
                      </label>
                    );
                  })}
                </div>
              );
            }}
          />
        ) : field.type === "select" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <Select value={String(ctrl.value ?? "")} onValueChange={ctrl.onChange} disabled={disabled || field.readOnly}>
                <SelectTrigger>
                  <SelectValue placeholder={`Select ${field.label}`} />
                </SelectTrigger>
                <SelectContent>
                  {(field.options ?? relationOptionsByKey[field.key]?.map((r) => ({ value: String(r.id), label: getLabel(r) })) ?? [])
                    .map((opt) => (
                      <SelectItem key={opt.value} value={opt.value}>
                        {opt.label}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            )}
          />
        ) : field.type === "color" ? (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <Input
                type="color"
                value={String(ctrl.value ?? "#000000")}
                onChange={ctrl.onChange}
                onBlur={ctrl.onBlur}
                name={ctrl.name}
                disabled={disabled || field.readOnly}
              />
            )}
          />
        ) : (
          <Controller
            control={form.control}
            name={field.key}
            render={({ field: ctrl }) => (
              <Input
                type={field.type === "number" ? "number" : "text"}
                value={String(ctrl.value ?? "")}
                onChange={ctrl.onChange}
                onBlur={ctrl.onBlur}
                name={ctrl.name}
                placeholder={field.placeholder}
                readOnly={field.readOnly}
                disabled={disabled}
              />
            )}
          />
        )}

        {err && <p className="text-xs text-destructive">{String(err)}</p>}
      </div>
    );
  };

  return (
    <form onSubmit={form.handleSubmit((vals) => onSubmit(vals))} className="space-y-4">
      {sections.map(([section, sectionFields]) => (
        <Fragment key={section || "default"}>
          {section ? (
            <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">{section}</p>
          ) : null}
          <div className="grid gap-3 sm:grid-cols-2">{sectionFields.map(renderField)}</div>
        </Fragment>
      ))}

      <div className="flex items-center justify-end gap-2 border-t border-border pt-3">
        <Button type="button" variant="outline" onClick={onCancel}>Cancel</Button>
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : mode === "create" ? "Create" : "Update"}
        </Button>
      </div>
    </form>
  );
}
