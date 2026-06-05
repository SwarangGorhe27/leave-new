import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useDispatch } from "react-redux";
import { BankAccount, Employee } from "../mockData";
import { CreditCard, Shield, Building2, Plus, Trash2 } from "lucide-react";
import { useAdminSync } from "../../admin/useAdminSync";
import { useAuth } from "../../../context/AuthContext";
import { addNotification } from "../../../../store/slices/notificationSlice";
import type { AppDispatch } from "../../../../store";
import {
  cacheEmployeeInRedux,
  persistEmployeeProfile,
} from "../../../services/employeeProfilePersistence";
import {
  hasValidationErrors,
  validateBankStatutoryClient,
  type BankRowFieldErrors,
  type BankStatutoryFieldErrors,
} from "../../../utils/bankStatutoryValidation";
import { useInvalidateEmployeeProfile } from "../../../../hooks/useEmployeeModuleProfile";
import { EditableSectionCard } from "../employee-details/EditableSectionCard";
import { useMasterOptions } from "./useMasterOptions";
import { lookupBankByIfsc } from "../../../../api/employeeModuleApi";
import {
  isValidUuid,
  normalizeTaxRegimeId,
} from "../../../utils/employeeApiMappers";
import { deleteAdminBankAccount } from "../../../../api/employeeModuleApi";

interface Props {
  employee: Employee;
  disableEdit?: boolean;
  /** Show Add / Edit for bank details (enabled on admin, employee, and manager) */
  showAddButton?: boolean;
}

const emptyBank = (employeeId: string, index: number, isPrimary: boolean): BankAccount => ({
  id: `bank-${employeeId}-${index}-${Date.now()}`,
  accountNumber: "",
  bankName: "",
  ifscCode: "",
  accountType: "Savings",
  isPrimary,
  accountHolderName: "",
});

function normalizeBankAccountsFromEmployee(employee: Employee): BankAccount[] {
  const rows = employee.bankAccounts ?? [];
  if (rows.length) {
    return rows.map((row, index) => ({
      ...row,
      id: row.id || `bank-${employee.id}-${index}`,
    }));
  }
  if (employee.accountNumber || employee.ifscCode || employee.bankName) {
    return [
      {
        ...emptyBank(employee.id, 0, true),
        accountNumber: employee.accountNumber ?? "",
        bankName: employee.bankName ?? "",
        ifscCode: employee.ifscCode ?? "",
        isPrimary: true,
      },
    ];
  }
  return [];
}

function hasAnyBankRecord(employee: Employee): boolean {
  return normalizeBankAccountsFromEmployee(employee).some(
    (r) =>
      Boolean(r.accountNumber?.trim()) ||
      Boolean(r.ifscCode?.trim()) ||
      Boolean(r.bankName?.trim()) ||
      Boolean(r.accountNumberMasked),
  );
}

function bankRowHasInput(row: BankAccount): boolean {
  return Boolean(
    row.accountNumber?.trim() ||
      row.ifscCode?.trim() ||
      row.bankId ||
      row.bankName?.trim() ||
      row.accountNumberMasked,
  );
}

function bankInputRowIndex(rows: BankAccount[], displayIndex: number): number | null {
  if (!bankRowHasInput(rows[displayIndex])) return null;
  let n = 0;
  for (let i = 0; i < displayIndex; i += 1) {
    if (bankRowHasInput(rows[i])) n += 1;
  }
  return n;
}

function isMaskedIdentifier(value: string): boolean {
  return /X{2,}/i.test(value) || /\*{2,}/.test(value);
}

/** Clear masked API values so edit fields are plain text inputs, not dropdowns. */
function clearMaskedForEdit(value: string | undefined): string {
  if (!value || isMaskedIdentifier(value)) return "";
  return value;
}

function statutoryFromEmployee(employee: Employee, forEdit = false): Employee {
  const pan = employee.panNumber ?? "";
  const aadhaar = employee.aadhaarNumber ?? "";
  return {
    ...employee,
    panNumber: forEdit ? clearMaskedForEdit(pan) : pan,
    aadhaarNumber: forEdit ? clearMaskedForEdit(aadhaar) : aadhaar,
    uanNumber: forEdit ? clearMaskedForEdit(employee.uanNumber) : (employee.uanNumber ?? ""),
    pfNumber: forEdit ? clearMaskedForEdit(employee.pfNumber) : (employee.pfNumber ?? ""),
    esiNumber: forEdit ? clearMaskedForEdit(employee.esiNumber) : (employee.esiNumber ?? ""),
    linNumber: forEdit ? clearMaskedForEdit(employee.linNumber) : (employee.linNumber ?? ""),
    taxRegime: employee.taxRegime ?? "",
    taxRegimeId: normalizeTaxRegimeId(employee.taxRegimeId),
    isPfCovered: Boolean(employee.isPfCovered),
    isEsiCovered: Boolean(employee.isEsiCovered),
    isLwfCovered: Boolean(employee.isLwfCovered),
    isEarlierMemberOfPensionOnHigherWages: Boolean(
      employee.isEarlierMemberOfPensionOnHigherWages,
    ),
  };
}

/** Project uses `danger` palette — not shadcn `destructive`. */
const fieldErrorBorderClass = "border-danger-500 focus:ring-danger-500/25";
const fieldErrorTextClass = "text-xs font-semibold text-danger-600 mt-1";

function BankGridField({
  label,
  value,
  mono,
  isEditing,
  children,
  error,
}: {
  label: string;
  value: string;
  mono?: boolean;
  isEditing: boolean;
  children?: ReactNode;
  error?: string;
}) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground mb-1">{label}</p>
      {isEditing && children ? (
        <>
          {children}
          {error ? <p className={fieldErrorTextClass}>{error}</p> : null}
        </>
      ) : (
        <p className={`text-sm font-semibold text-foreground ${mono ? "font-mono" : ""}`}>
          {value || "—"}
        </p>
      )}
    </div>
  );
}

function StatutoryField({
  label,
  value,
  mono,
  isEditing,
  onChange,
  options,
  placeholder,
  error,
}: {
  label: string;
  value: string;
  mono?: boolean;
  isEditing: boolean;
  onChange?: (v: string) => void;
  options?: Array<{ value: string; label: string }>;
  placeholder?: string;
  error?: string;
}) {
  const useSelect = Boolean(options?.length);
  const invalidClass = error ? fieldErrorBorderClass : "";

  return (
    <div className="flex justify-between items-start py-3 border-b border-border last:border-0 gap-4">
      <span className="text-sm text-muted-foreground font-medium shrink-0 pt-1">{label}</span>
      <div className="flex flex-col items-end min-w-[12rem]">
      {isEditing && useSelect ? (
        <select
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          className={`text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 min-w-[12rem] focus:outline-none focus:ring-2 focus:ring-primary/30 ${invalidClass}`}
        >
          <option value="">Select {label}</option>
          {(options ?? []).map((o) => (
            <option key={o.value} value={o.value}>
              {o.label}
            </option>
          ))}
        </select>
      ) : isEditing ? (
        <input
          type="text"
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          placeholder={placeholder}
          className={`text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1 min-w-[12rem] focus:outline-none focus:ring-2 focus:ring-primary/30 ${mono ? "font-mono" : ""} ${invalidClass}`}
        />
      ) : (
        <span className={`text-sm font-semibold text-foreground text-right ${mono ? "font-mono" : ""}`}>
          {value || "—"}
        </span>
      )}
      {error && isEditing ? (
        <p className={`${fieldErrorTextClass} text-right`}>{error}</p>
      ) : null}
      </div>
    </div>
  );
}

export function BankDetails({ employee, disableEdit = false, showAddButton = true }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const { user } = useAuth();
  const invalidateProfile = useInvalidateEmployeeProfile();
  const taxRegimeOptions = useMasterOptions("TaxRegime");
  const accountTypeOptions = useMasterOptions("AccountType");
  const paymentTypeOptions = useMasterOptions("PaymentType");
  const { handleToggleEditAccess } = useAdminSync();
  const portal =
    user?.role === "admin" ? "admin" : user?.role === "manager" ? "manager" : "employee";

  const [fieldErrors, setFieldErrors] = useState<BankStatutoryFieldErrors>({});
  const [bankRowErrors, setBankRowErrors] = useState<Record<number, BankRowFieldErrors>>({});

  const baselineBanks = useMemo(() => normalizeBankAccountsFromEmployee(employee), [employee]);
  const [banks, setBanks] = useState<BankAccount[]>(baselineBanks);
  const [statutory, setStatutory] = useState<Employee>(() => statutoryFromEmployee(employee));
  const [sectionEditing, setSectionEditing] = useState(false);
  const [ifscMessages, setIfscMessages] = useState<Record<number, string>>({});
  const [resolvingIfscIndex, setResolvingIfscIndex] = useState<number | null>(null);

  useEffect(() => {
    setBanks(baselineBanks);
    setStatutory(statutoryFromEmployee(employee));
    setSectionEditing(false);
    setIfscMessages({});
    setResolvingIfscIndex(null);
  }, [employee, baselineBanks]);

  const defaultAccountType = useMemo(() => {
    const savings = accountTypeOptions.find((o) => /savings/i.test(o.label));
    return savings ?? accountTypeOptions[0];
  }, [accountTypeOptions]);

  const applyDefaultAccountType = useCallback(
    (row: BankAccount): BankAccount => {
      if (row.accountTypeId) return row;
      if (!defaultAccountType) return row;
      return {
        ...row,
        accountTypeId: defaultAccountType.value,
        accountType: defaultAccountType.label,
      };
    },
    [defaultAccountType],
  );

  const updateBank = (index: number, patch: Partial<BankAccount>) => {
    setBanks((prev) => prev.map((row, i) => (i === index ? { ...row, ...patch } : row)));
  };

  const resolveIfsc = async (ifsc: string, index: number) => {
    const code = ifsc.trim().toUpperCase();
    if (code.length < 11) {
      setIfscMessages((prev) => {
        const next = { ...prev };
        delete next[index];
        return next;
      });
      return;
    }
    setResolvingIfscIndex(index);
    setIfscMessages((prev) => ({ ...prev, [index]: "" }));
    try {
      const match = await lookupBankByIfsc(code);
      if (match) {
        updateBank(index, {
          ifscCode: code,
          bankId: match.id,
          bankName: match.name,
          branchName: match.branch || banks[index]?.branchName,
        });
        setIfscMessages((prev) => {
          const next = { ...prev };
          delete next[index];
          return next;
        });
      } else {
        setIfscMessages((prev) => ({
          ...prev,
          [index]: "No bank found for this IFSC. Check the code or contact HR.",
        }));
      }
    } catch {
      setIfscMessages((prev) => ({
        ...prev,
        [index]: "Could not look up bank. Try again.",
      }));
    } finally {
      setResolvingIfscIndex(null);
    }
  };

  const addBankAccount = () => {
    setBanks((prev) => {
      const next = [
        ...prev,
        applyDefaultAccountType(
          emptyBank(employee.id, prev.length, prev.length === 0),
        ),
      ];
      if (next.length === 1) {
        next[0] = { ...next[0], isPrimary: true };
      }
      return next;
    });
    setSectionEditing(true);
  };

  const removeBankAccount = async (index: number) => {
    const row = banks[index];
    if (portal === "admin" && isValidUuid(row.id)) {
      try {
        const patch = await deleteAdminBankAccount(employee.id, row.id);
        const merged: Employee = { ...employee, ...patch, id: employee.id };
        cacheEmployeeInRedux(dispatch, merged);
        invalidateProfile(portal, employee.id, merged);
        setBanks((prev) => {
          const next = prev.filter((_, i) => i !== index);
          if (next.length && !next.some((r) => r.isPrimary)) {
            next[0] = { ...next[0], isPrimary: true };
          }
          return next;
        });
        dispatch(
          addNotification({
            type: "success",
            message: "Bank account removed successfully.",
          }),
        );
        return;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Could not remove bank account.";
        dispatch(addNotification({ type: "error", message }));
        return;
      }
    }

    setBanks((prev) => {
      const next = prev.filter((_, i) => i !== index);
      if (next.length && !next.some((r) => r.isPrimary)) {
        next[0] = { ...next[0], isPrimary: true };
      }
      return next;
    });
  };

  const setPrimaryBank = (index: number) => {
    setBanks((prev) =>
      prev.map((row, i) => ({
        ...row,
        isPrimary: i === index,
      })),
    );
  };

  const startEdit = () => {
    const initial =
      baselineBanks.length > 0
        ? baselineBanks.map((row) => applyDefaultAccountType({ ...row }))
        : [applyDefaultAccountType(emptyBank(employee.id, 0, true))];
    setBanks(initial);
    setStatutory(statutoryFromEmployee(employee, true));
    setSectionEditing(true);
    setIfscMessages({});
    setFieldErrors({});
    setBankRowErrors({});
  };

  const cancelEdit = () => {
    setBanks(baselineBanks);
    setStatutory(statutoryFromEmployee(employee));
    setSectionEditing(false);
    setIfscMessages({});
    setFieldErrors({});
    setBankRowErrors({});
  };

  const saveSection = async () => {
    const warn = (message: string) => {
      dispatch(addNotification({ type: "warning", message }));
    };

    const rowsWithInput = banks.filter(bankRowHasInput);
    for (let i = 0; i < rowsWithInput.length; i += 1) {
      const row = applyDefaultAccountType(rowsWithInput[i]);
      const label = rowsWithInput.length > 1 ? `Bank account ${i + 1}` : "Bank account";
      const ifsc = row.ifscCode?.trim().toUpperCase() ?? "";
      if (ifsc.length !== 11) {
        warn(`${label}: IFSC code must be 11 characters (e.g. HDFC0004673).`);
        return;
      }
      if (!row.bankId && !row.bankName?.trim()) {
        warn(`${label}: enter a valid IFSC to load the bank name from masters.`);
        return;
      }
      if (!row.accountTypeId && !row.accountType) {
        warn(`${label}: please select an account type.`);
        return;
      }
      if (!row.accountNumber?.trim() && !row.accountNumberMasked) {
        warn(`${label}: bank account number is required.`);
        return;
      }
    }

    let normalizedRows = rowsWithInput.map((row) =>
      applyDefaultAccountType({
        ...row,
        ifscCode: row.ifscCode?.trim().toUpperCase() || row.ifscCode,
        accountHolderName: row.accountHolderName || employee.name,
        paymentType:
          paymentTypeOptions.find((o) => o.value === row.paymentTypeId)?.label ??
          row.paymentType,
      }),
    );
    if (normalizedRows.length && !normalizedRows.some((row) => row.isPrimary)) {
      normalizedRows = normalizedRows.map((row, index) => ({
        ...row,
        isPrimary: index === 0,
      }));
    }

    const primary =
      normalizedRows.find((row) => row.isPrimary) ?? normalizedRows[0];
    const taxRegimeId = normalizeTaxRegimeId(statutory.taxRegimeId);
    const taxLabel =
      taxRegimeOptions.find((o) => o.value === taxRegimeId)?.label ?? statutory.taxRegime;
    const updated: Employee = {
      ...employee,
      ...statutory,
      taxRegime: taxLabel,
      taxRegimeId,
      bankAccounts: normalizedRows,
      bankName: primary?.bankName ?? "",
      accountNumber: primary?.accountNumber ?? "",
      ifscCode: primary?.ifscCode ?? "",
    };

    const clientValidation = validateBankStatutoryClient(updated, normalizedRows);
    if (hasValidationErrors(clientValidation.fieldErrors, clientValidation.bankRowErrors)) {
      setFieldErrors(clientValidation.fieldErrors);
      setBankRowErrors(clientValidation.bankRowErrors);
      warn("Please correct the highlighted fields.");
      return;
    }

    setFieldErrors({});
    setBankRowErrors({});
    const originalForSave: Employee = {
      ...employee,
      bankAccounts: baselineBanks,
    };
    const result = await persistEmployeeProfile(
      dispatch,
      portal,
      employee.id,
      originalForSave,
      updated,
      "Bank / PF / ESI Details",
    );
    if (!result.ok) {
      setFieldErrors(result.fieldErrors ?? {});
      setBankRowErrors(result.bankRowErrors ?? {});
      dispatch(addNotification({ type: "error", message: result.message }));
      return;
    }

    cacheEmployeeInRedux(dispatch, result.employee);
    invalidateProfile(portal, employee.id, result.employee);
    setStatutory(statutoryFromEmployee(result.employee));
    dispatch(
      addNotification({
        type: "success",
        message:
          portal === "admin"
            ? "Bank and statutory details saved successfully."
            : "Bank and statutory changes submitted for HR approval.",
      }),
    );
    setSectionEditing(false);
  };

  const isEditing = sectionEditing && !disableEdit;
  const displayBanks = sectionEditing ? banks : baselineBanks;
  const bankOnFile = hasAnyBankRecord(employee);
  const canAddOrEdit = showAddButton && !disableEdit;

  const accountTypeSelectOptions =
    accountTypeOptions.length > 0 ? accountTypeOptions : [];
  const paymentTypeSelectOptions =
    paymentTypeOptions.length > 0 ? paymentTypeOptions : [];

  const taxRegimeSelectValue = normalizeTaxRegimeId(statutory.taxRegimeId);
  const taxRegimeDisplay =
    taxRegimeOptions.find((o) => o.value === taxRegimeSelectValue)?.label ||
    statutory.taxRegime ||
    "—";

  const inputClass =
    "w-full text-sm font-semibold text-foreground bg-secondary/50 border border-border rounded-md px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary/30";
  const selectClass = `${inputClass} min-w-0`;

  return (
    <div className="space-y-6 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Bank / PF / ESI Details</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Financial and statutory details for {employee.name}
        </p>
      </div>

      <EditableSectionCard
        title="Bank / PF / ESI Details"
        icon={Building2}
        sectionId="bank-pf-esi-details"
        canEmployeeEdit={employee.editableSections?.includes("bank-pf-esi-details")}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "bank-pf-esi-details", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={sectionEditing}
        onEdit={canAddOrEdit ? startEdit : undefined}
        onSave={saveSection}
        onCancel={cancelEdit}
        editLabel={bankOnFile ? "Edit" : "Add"}
        editDisabled={!canAddOrEdit}
        allowEssDirectEdit={showAddButton}
        headerExtra={
          isEditing && showAddButton ? (
            <button
              type="button"
              onClick={addBankAccount}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-xs font-bold transition-colors hover:bg-secondary"
            >
              <Plus className="h-3.5 w-3.5" />
              Add Bank Account
            </button>
          ) : null
        }
      >
        <div className="space-y-8">
          <div className="space-y-4">
            {displayBanks.length === 0 ? (
              <div className="rounded-lg border border-dashed border-border bg-secondary/20 p-8 text-center">
                <p className="text-sm font-semibold text-muted-foreground">No bank accounts on file</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {canAddOrEdit
                    ? "Use Add or Add Bank Account to register bank details."
                    : "Bank details are not recorded yet."}
                </p>
              </div>
            ) : (
              displayBanks.map((bank, index) => {
                const inputIdx = bankInputRowIndex(displayBanks, index);
                const rowErr = inputIdx !== null ? bankRowErrors[inputIdx] : undefined;
                const holderName = bank.accountHolderName || employee.name;
                const rowAccountTypeOptions =
                  accountTypeSelectOptions.length > 0
                    ? accountTypeSelectOptions
                    : bank.accountType
                      ? [
                          {
                            value: bank.accountTypeId || bank.accountType,
                            label: bank.accountType,
                          },
                        ]
                      : [];
                const rowPaymentTypeOptions =
                  paymentTypeSelectOptions.length > 0
                    ? paymentTypeSelectOptions
                    : bank.paymentType
                      ? [
                          {
                            value: bank.paymentTypeId || bank.paymentType,
                            label: bank.paymentType,
                          },
                        ]
                      : [];
                const displayAccountNumber =
                  bank.accountNumber ||
                  (bank.accountNumberMasked ? "•••• (re-enter to change)" : "");

                return (
                  <div key={bank.id || `bank-row-${index}`} className="space-y-3">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
                        <CreditCard className="w-4 h-4 text-muted-foreground" />
                        Bank Account{displayBanks.length > 1 ? ` ${index + 1}` : ""}
                        {bank.isPrimary ? (
                          <span className="text-[10px] font-bold uppercase tracking-wider text-primary px-2 py-0.5 rounded border border-primary/30 bg-primary/5">
                            Primary
                          </span>
                        ) : null}
                      </h3>
                      {isEditing ? (
                        <div className="flex flex-wrap items-center gap-2">
                          {displayBanks.length > 1 ? (
                            <label className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground cursor-pointer">
                              <input
                                type="radio"
                                name="primary-bank"
                                checked={Boolean(bank.isPrimary)}
                                onChange={() => setPrimaryBank(index)}
                                className="h-3.5 w-3.5"
                              />
                              Primary
                            </label>
                          ) : null}
                          {displayBanks.length > 1 ? (
                            <button
                              type="button"
                              onClick={() => void removeBankAccount(index)}
                              className="inline-flex items-center gap-1 rounded-lg border border-rose-200 px-2.5 py-1 text-xs font-bold text-rose-600 hover:bg-rose-50"
                            >
                              <Trash2 className="h-3.5 w-3.5" />
                              Remove
                            </button>
                          ) : null}
                        </div>
                      ) : null}
                    </div>
                    <div className="rounded-lg border border-border bg-card p-6 space-y-6">
                      <BankGridField label="Account Holder" value={holderName} isEditing={isEditing}>
                        <input
                          type="text"
                          value={bank.accountHolderName || employee.name}
                          onChange={(e) =>
                            updateBank(index, { accountHolderName: e.target.value })
                          }
                          className={inputClass}
                        />
                      </BankGridField>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <BankGridField
                          label="IFSC"
                          value={bank.ifscCode}
                          mono
                          isEditing={isEditing}
                          error={rowErr?.ifscCode}
                        >
                          <input
                            type="text"
                            value={bank.ifscCode}
                            onChange={(e) =>
                              updateBank(index, {
                                ifscCode: e.target.value.toUpperCase(),
                                bankName: "",
                                bankId: "",
                              })
                            }
                            onBlur={(e) => resolveIfsc(e.target.value, index)}
                            className={`${inputClass} uppercase font-mono ${rowErr?.ifscCode ? fieldErrorBorderClass : ""}`}
                            placeholder="HDFC0004673"
                            maxLength={11}
                          />
                          {resolvingIfscIndex === index && (
                            <p className="text-xs mt-1 text-muted-foreground">Looking up bank…</p>
                          )}
                          {ifscMessages[index] ? (
                            <p className="text-xs mt-1 text-amber-600">{ifscMessages[index]}</p>
                          ) : null}
                        </BankGridField>

                        <BankGridField
                          label="Bank Name"
                          value={bank.bankName || (isEditing ? "Enter IFSC to load" : "")}
                          isEditing={isEditing}
                          error={rowErr?.bankName}
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <BankGridField
                          label="Bank Account Number"
                          value={displayAccountNumber}
                          mono
                          isEditing={isEditing}
                          error={rowErr?.accountNumber}
                        >
                          <input
                            type="text"
                            value={bank.accountNumber}
                            onChange={(e) =>
                              updateBank(index, {
                                accountNumber: e.target.value.replace(/\D/g, "").slice(0, 30),
                                accountNumberMasked: false,
                              })
                            }
                            inputMode="numeric"
                            pattern="[0-9]*"
                            className={`${inputClass} font-mono ${rowErr?.accountNumber ? fieldErrorBorderClass : ""}`}
                            placeholder={
                              bank.accountNumberMasked
                                ? "Re-enter full account number"
                                : "Account number"
                            }
                          />
                        </BankGridField>

                        <BankGridField label="Bank Branch" value={bank.branchName ?? ""} isEditing={isEditing}>
                          <input
                            type="text"
                            value={bank.branchName ?? ""}
                            onChange={(e) => updateBank(index, { branchName: e.target.value })}
                            className={inputClass}
                            placeholder="Branch name"
                          />
                        </BankGridField>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <BankGridField
                          label="Account Type"
                          value={bank.accountType}
                          isEditing={isEditing}
                          error={rowErr?.accountType}
                        >
                          <select
                            value={bank.accountTypeId || ""}
                            onChange={(e) => {
                              const opt = rowAccountTypeOptions.find(
                                (o) => o.value === e.target.value,
                              );
                              updateBank(index, {
                                accountTypeId: e.target.value,
                                accountType: opt?.label ?? "",
                              });
                            }}
                            className={`${selectClass} ${rowErr?.accountType ? fieldErrorBorderClass : ""}`}
                          >
                            <option value="">Select account type</option>
                            {rowAccountTypeOptions.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                        </BankGridField>

                        <BankGridField
                          label="Payment Type"
                          value={bank.paymentType ?? ""}
                          isEditing={isEditing}
                        >
                          <select
                            value={bank.paymentTypeId || ""}
                            onChange={(e) => {
                              const opt = rowPaymentTypeOptions.find(
                                (o) => o.value === e.target.value,
                              );
                              updateBank(index, {
                                paymentTypeId: e.target.value,
                                paymentType: opt?.label ?? "",
                              });
                            }}
                            className={selectClass}
                          >
                            <option value="">Select payment type</option>
                            {rowPaymentTypeOptions.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                        </BankGridField>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <div>
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2 mb-4">
              <Shield className="w-4 h-4 text-muted-foreground" />
              Statutory Documents
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8">
              <StatutoryField
                label="PAN Number"
                value={
                  isEditing
                    ? statutory.panNumber || ""
                    : employee.panNumber || statutory.panNumber || ""
                }
                mono
                isEditing={isEditing}
                error={fieldErrors.panNumber}
                placeholder={
                  isEditing && isMaskedIdentifier(employee.panNumber ?? "")
                    ? "Enter full PAN (e.g. ABCDE1234F)"
                    : undefined
                }
                onChange={(v) =>
                  setStatutory((p) => ({ ...p, panNumber: v.toUpperCase() }))
                }
              />
              <StatutoryField
                label="Aadhaar Number"
                value={
                  isEditing
                    ? statutory.aadhaarNumber || ""
                    : employee.aadhaarNumber || statutory.aadhaarNumber || ""
                }
                mono
                isEditing={isEditing}
                error={fieldErrors.aadhaarNumber}
                placeholder={
                  isEditing && isMaskedIdentifier(employee.aadhaarNumber ?? "")
                    ? "Enter full 12-digit Aadhaar"
                    : undefined
                }
                onChange={(v) =>
                  setStatutory((p) => ({
                    ...p,
                    aadhaarNumber: v.replace(/\D/g, "").slice(0, 12),
                  }))
                }
              />
              <StatutoryField
                label="Tax Regime"
                value={isEditing ? taxRegimeSelectValue : taxRegimeDisplay}
                isEditing={isEditing}
                error={fieldErrors.taxRegimeId}
                onChange={(v) => {
                  const regimeId = normalizeTaxRegimeId(v);
                  const label =
                    taxRegimeOptions.find((o) => o.value === regimeId)?.label ?? "";
                  setStatutory((p) => ({ ...p, taxRegimeId: regimeId, taxRegime: label }));
                }}
                options={taxRegimeOptions}
              />
            </div>

            <div className="mt-6 border-t border-border pt-4 space-y-4">
              <div className="flex flex-wrap items-center gap-4 py-2 border-b border-border">
                <label className="flex items-center gap-3 w-full sm:w-96 shrink-0 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={Boolean(statutory.isPfCovered)}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setStatutory((p) => ({ ...p, isPfCovered: e.target.checked }))
                    }
                    className="h-4 w-4 rounded border-border text-primary-600"
                  />
                  <span>
                    <span className="text-sm font-medium block">Is Employee Covered Under PF?</span>
                    <span className="text-xs text-muted-foreground">Provide PF number if applicable</span>
                  </span>
                </label>
                {statutory.isPfCovered && (
                  <div className="flex flex-wrap items-end gap-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        PF Number
                      </span>
                      <input
                        type="text"
                        value={statutory.pfNumber || ""}
                        disabled={!isEditing}
                        onChange={(e) => setStatutory((p) => ({ ...p, pfNumber: e.target.value }))}
                        placeholder="PF Number"
                        className={`text-sm font-mono font-semibold bg-secondary/50 border border-border rounded-md px-2.5 py-1.5 w-44 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-80 ${fieldErrors.pfNumber ? fieldErrorBorderClass : ""}`}
                      />
                      {fieldErrors.pfNumber ? (
                        <p className={fieldErrorTextClass}>{fieldErrors.pfNumber}</p>
                      ) : null}
                    </div>
                    <div className="flex flex-col gap-1">
                      <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                        UAN Number
                      </span>
                      <input
                        type="text"
                        value={statutory.uanNumber || ""}
                        disabled={!isEditing}
                        onChange={(e) => setStatutory((p) => ({ ...p, uanNumber: e.target.value }))}
                        placeholder="UAN Number"
                        className={`text-sm font-mono font-semibold bg-secondary/50 border border-border rounded-md px-2.5 py-1.5 w-44 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-80 ${fieldErrors.uanNumber ? fieldErrorBorderClass : ""}`}
                      />
                      {fieldErrors.uanNumber ? (
                        <p className={fieldErrorTextClass}>{fieldErrors.uanNumber}</p>
                      ) : null}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-4 py-2 border-b border-border">
                <label className="flex items-center gap-3 w-full sm:w-96 shrink-0 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={Boolean(statutory.isEsiCovered)}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setStatutory((p) => ({ ...p, isEsiCovered: e.target.checked }))
                    }
                    className="h-4 w-4 rounded border-border text-primary-600"
                  />
                  <span>
                    <span className="text-sm font-medium block">Is Employee Covered Under ESI?</span>
                    <span className="text-xs text-muted-foreground">Provide ESI number if applicable</span>
                  </span>
                </label>
                {statutory.isEsiCovered && (
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      ESI Number
                    </span>
                    <input
                      type="text"
                      value={statutory.esiNumber || ""}
                      disabled={!isEditing}
                      onChange={(e) => setStatutory((p) => ({ ...p, esiNumber: e.target.value }))}
                      placeholder="ESI Number"
                      className={`text-sm font-mono font-semibold bg-secondary/50 border border-border rounded-md px-2.5 py-1.5 w-56 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-80 ${fieldErrors.esiNumber ? fieldErrorBorderClass : ""}`}
                    />
                    {fieldErrors.esiNumber ? (
                      <p className={fieldErrorTextClass}>{fieldErrors.esiNumber}</p>
                    ) : null}
                  </div>
                )}
              </div>

              <div className="flex flex-wrap items-center gap-4 py-2 border-b border-border">
                <label className="flex items-center gap-3 w-full sm:w-96 shrink-0 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={Boolean(statutory.isLwfCovered)}
                    disabled={!isEditing}
                    onChange={(e) =>
                      setStatutory((p) => ({ ...p, isLwfCovered: e.target.checked }))
                    }
                    className="h-4 w-4 rounded border-border text-primary-600"
                  />
                  <span>
                    <span className="text-sm font-medium block">Is Employee Covered Under LWF?</span>
                    <span className="text-xs text-muted-foreground">Provide LIN number if applicable</span>
                  </span>
                </label>
                {statutory.isLwfCovered && (
                  <div className="flex flex-col gap-1">
                    <span className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground">
                      LIN Number
                    </span>
                    <input
                      type="text"
                      value={statutory.linNumber || ""}
                      disabled={!isEditing}
                      onChange={(e) => setStatutory((p) => ({ ...p, linNumber: e.target.value }))}
                      placeholder="LIN Number"
                      className={`text-sm font-mono font-semibold bg-secondary/50 border border-border rounded-md px-2.5 py-1.5 w-56 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-80 ${fieldErrors.linNumber ? fieldErrorBorderClass : ""}`}
                    />
                    {fieldErrors.linNumber ? (
                      <p className={fieldErrorTextClass}>{fieldErrors.linNumber}</p>
                    ) : null}
                  </div>
                )}
              </div>

              <label className="flex items-center gap-3 py-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={Boolean(statutory.isEarlierMemberOfPensionOnHigherWages)}
                  disabled={!isEditing}
                  onChange={(e) =>
                    setStatutory((p) => ({
                      ...p,
                      isEarlierMemberOfPensionOnHigherWages: e.target.checked,
                    }))
                  }
                  className="h-4 w-4 rounded border-border text-primary-600"
                />
                <span>
                  <span className="text-sm font-medium block">
                    Earlier Member of Pension on Higher Wages?
                  </span>
                  <span className="text-xs text-muted-foreground">Check if applicable</span>
                </span>
              </label>
            </div>
          </div>
        </div>
      </EditableSectionCard>
    </div>
  );
}
