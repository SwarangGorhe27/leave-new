import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Key, RefreshCw } from "lucide-react";
import { useDispatch } from "react-redux";
import { AccessCardEntry, Employee } from "../mockData";
import { EditableSectionCard, ProfileInfoField, EmptyStateCard } from "../employee-details";
import {
  accessCardsToEmployeeEntries,
  createEmployeeAccessCard,
  deleteEmployeeAccessCard,
  extractAccessCardApiError,
  getEmployeeAccessCards,
  isPersistedAccessCardId,
  todayIsoDate,
  updateEmployeeAccessCard,
} from "../../../api/employeeAccessCards";
import { AppDispatch } from "../../../../store";
import { updateAdminEmployee } from "../../../../store/slices/adminSlice";
import { addNotification } from "../../../../store/slices/notificationSlice";

interface Props {
  employee: Employee;
  showActions?: boolean;
}

function emptyCard(employee: Employee): AccessCardEntry {
  return {
    id: `acc-${Date.now()}`,
    employeeId: employee.employeeId,
    cardNumber: "",
  };
}

function validateCards(cards: AccessCardEntry[]): Record<number, string> {
  const errors: Record<number, string> = {};
  cards.forEach((c, idx) => {
    if (!c.cardNumber.trim()) errors[idx] = "Card number is required";
  });
  return errors;
}

export function AccessCardDetails({ employee, showActions = true }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [serverCards, setServerCards] = useState<AccessCardEntry[]>([]);
  const [cards, setCards] = useState<AccessCardEntry[]>([]);
  const [errors, setErrors] = useState<Record<number, string>>({});
  const isEditingRef = useRef(isEditing);

  useEffect(() => {
    isEditingRef.current = isEditing;
  }, [isEditing]);

  const baseline = useMemo(() => serverCards, [serverCards]);
  const employeeId = employee.id;
  const employeeCode = employee.employeeId;

  const loadAccessCards = useCallback(async () => {
    if (!employeeId) return;
    setIsLoading(true);
    setLoadError(null);
    try {
      const rows = await getEmployeeAccessCards(employeeId);
      const mapped = accessCardsToEmployeeEntries(rows, employeeCode);
      setServerCards(mapped);
      if (!isEditingRef.current) {
        setCards(mapped);
      }
    } catch (error) {
      const message = extractAccessCardApiError(error, "Could not load access card details.");
      setLoadError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setIsLoading(false);
    }
  }, [dispatch, employeeCode, employeeId]);

  useEffect(() => {
    void loadAccessCards();
  }, [loadAccessCards]);

  const startEdit = () => {
    setCards(baseline.length ? [...baseline] : [emptyCard(employee)]);
    setErrors({});
    setIsEditing(true);
  };

  const handleSave = async () => {
    const nextErrors = validateCards(cards);
    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors);
      return;
    }

    if (!employeeId) {
      dispatch(addNotification({ type: "error", message: "Employee ID is missing." }));
      return;
    }

    setIsSaving(true);
    try {
      const baselineById = new Map(
        baseline.filter((c) => isPersistedAccessCardId(c.id)).map((c) => [c.id, c]),
      );
      const nextById = new Map(
        cards.filter((c) => isPersistedAccessCardId(c.id)).map((c) => [c.id, c]),
      );

      for (const [id] of baselineById) {
        if (!nextById.has(id)) {
          await deleteEmployeeAccessCard(employeeId, id);
        }
      }

      for (const card of cards) {
        const cardNumber = card.cardNumber.trim();
        if (isPersistedAccessCardId(card.id)) {
          const previous = baselineById.get(card.id);
          if (previous && previous.cardNumber.trim() !== cardNumber) {
            await updateEmployeeAccessCard(employeeId, card.id, {
              access_card_number: cardNumber,
            });
          }
        } else {
          await createEmployeeAccessCard(employeeId, {
            access_card_number: cardNumber,
            from_date: todayIsoDate(),
          });
        }
      }

      const rows = await getEmployeeAccessCards(employeeId);
      const mapped = accessCardsToEmployeeEntries(rows, employeeCode);
      setServerCards(mapped);
      setCards(mapped);
      dispatch(updateAdminEmployee({ ...employee, accessCards: mapped }));
      setErrors({});
      setIsEditing(false);
      dispatch(addNotification({ type: "success", message: "Access card details saved successfully." }));
    } catch (error) {
      dispatch(
        addNotification({
          type: "error",
          message: extractAccessCardApiError(error, "Failed to save access card details."),
        }),
      );
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setCards(baseline);
    setErrors({});
    setIsEditing(false);
  };

  const updateCard = (idx: number, patch: Partial<AccessCardEntry>) => {
    setCards((rows) => rows.map((r, i) => (i === idx ? { ...r, ...patch } : r)));
    if (errors[idx]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[idx];
        return next;
      });
    }
  };

  const displayCards = isEditing ? cards : baseline;

  return (
    <div className="space-y-5 pb-24">
      <div>
        <h2 className="text-lg font-bold text-foreground">Access Card Details</h2>
        <p className="text-sm text-muted-foreground mt-1">Building access cards for {employee.name}</p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 rounded-md border border-border bg-card px-4 py-3 text-sm text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          Loading access cards…
        </div>
      )}

      {loadError && !isLoading && (
        <div className="flex items-center justify-between gap-3 rounded-md border border-border bg-card px-4 py-3 text-sm">
          <p className="text-muted-foreground">{loadError}</p>
          <button
            type="button"
            onClick={() => void loadAccessCards()}
            className="rounded-md border border-border px-3 py-1.5 text-xs font-semibold hover:bg-secondary"
          >
            Retry
          </button>
        </div>
      )}

      <EditableSectionCard
        title="Access Cards"
        icon={Key}
        isEditing={isEditing}
        onCancel={handleCancel}
        onSave={() => void handleSave()}
        onEdit={showActions ? startEdit : undefined}
        editLabel={baseline.length ? "Edit" : "Add"}
      >
        {!displayCards.length && !isEditing ? (
          <EmptyStateCard
            icon={Key}
            title="No access cards"
            description="No access cards registered. Contact admin to add one."
          />
        ) : (
          <div className="space-y-4">
            {displayCards.map((row, i) => (
              <div key={row.id} className="rounded-2xl border border-border bg-secondary/10 p-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-3xl">
                  <ProfileInfoField
                    label="Employee ID"
                    value={employee.employeeId}
                    editing={isEditing}
                    readOnly
                  />
                  <ProfileInfoField
                    label="Card Number"
                    value={row.cardNumber}
                    editing={isEditing}
                    error={errors[i]}
                    onChange={(v) => updateCard(i, { cardNumber: v })}
                  />
                </div>
                {isEditing && displayCards.length > 1 ? (
                  <button
                    type="button"
                    className="mt-4 text-xs font-semibold text-destructive hover:underline"
                    onClick={() => setCards((rows) => rows.filter((_, j) => j !== i))}
                  >
                    Remove card
                  </button>
                ) : null}
              </div>
            ))}
          </div>
        )}
        {isSaving ? (
          <p className="mt-4 text-xs font-medium text-muted-foreground">Saving access card details…</p>
        ) : null}
      </EditableSectionCard>
    </div>
  );
}
