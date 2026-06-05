import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { Edit2, Save, X } from "lucide-react";
import { AppDispatch } from "../../../store";
import { EmployeeProfile } from "../../modules/ess/types";
import { saveEssProfileWithAdminSync } from "../../../store/slices/employeeSlice";
import { addNotification } from "../../../store/slices/notificationSlice";
import { ProfileImageUploader } from "./ProfileImageUploader";
import { validateEmail } from "../../modules/ess/utils";

type Props = {
  employeeId: string;
  profile: EmployeeProfile;
};

function loosePhoneOk(v: string): boolean {
  const d = v.replace(/\D/g, "");
  if (!v.trim()) return true;
  return d.length >= 10 && d.length <= 15;
}

export function EssProfileHeaderCard({ employeeId, profile }: Props) {
  const dispatch = useDispatch<AppDispatch>();
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [banner, setBanner] = useState<string | null>(null);
  const [draft, setDraft] = useState({
    firstName: "",
    middleName: "",
    lastName: "",
    officialEmail: "",
    personalMobile: "",
    alternateMobileNumber: "",
    designation: "",
    employeeStatus: "",
    workLocation: "",
    profilePhotoDataUrl: "" as string | undefined,
  });

  useEffect(() => {
    if (editing) return;
    setDraft({
      firstName: profile.profile.firstName,
      middleName: profile.profile.middleName,
      lastName: profile.profile.lastName,
      officialEmail: profile.profile.officialEmail || profile.profile.personalEmail,
      personalMobile: profile.profile.personalMobile,
      alternateMobileNumber: profile.profile.alternateMobileNumber || "",
      designation: profile.employmentDetails.designation,
      employeeStatus: profile.employmentDetails.employeeStatus || "Active",
      workLocation: profile.employmentDetails.workLocation,
      profilePhotoDataUrl: profile.profilePhotoDataUrl,
    });
  }, [profile, editing]);

  const displayName = [draft.firstName, draft.middleName, draft.lastName].filter(Boolean).join(" ").trim();

  const startEdit = () => {
    setBanner(null);
    setEditing(true);
    setDraft({
      firstName: profile.profile.firstName,
      middleName: profile.profile.middleName,
      lastName: profile.profile.lastName,
      officialEmail: profile.profile.officialEmail || profile.profile.personalEmail,
      personalMobile: profile.profile.personalMobile,
      alternateMobileNumber: profile.profile.alternateMobileNumber || "",
      designation: profile.employmentDetails.designation,
      employeeStatus: profile.employmentDetails.employeeStatus || "Active",
      workLocation: profile.employmentDetails.workLocation,
      profilePhotoDataUrl: profile.profilePhotoDataUrl,
    });
  };

  const cancel = () => {
    setEditing(false);
    setBanner(null);
  };

  const save = async () => {
    setBanner(null);
    if (draft.officialEmail && !validateEmail(draft.officialEmail)) {
      setBanner("Official email format is invalid.");
      return;
    }
    if (!loosePhoneOk(draft.personalMobile)) {
      setBanner("Phone number should include 10–15 digits.");
      return;
    }
    if (!loosePhoneOk(draft.alternateMobileNumber)) {
      setBanner("Alternate mobile should include 10–15 digits.");
      return;
    }
    const next: EmployeeProfile = {
      ...profile,
      profile: {
        ...profile.profile,
        firstName: draft.firstName.trim(),
        middleName: draft.middleName.trim(),
        lastName: draft.lastName.trim(),
        officialEmail: draft.officialEmail.trim(),
        personalMobile: draft.personalMobile.trim(),
        alternateMobileNumber: draft.alternateMobileNumber.trim(),
        personalEmail: profile.profile.personalEmail,
        workMobile: profile.profile.workMobile,
        extensionNumber: profile.profile.extensionNumber,
        emergencyContactName: profile.profile.emergencyContactName,
        emergencyContactNumber: profile.profile.emergencyContactNumber,
      },
      employmentDetails: {
        ...profile.employmentDetails,
        designation: draft.designation.trim(),
        employeeStatus: draft.employeeStatus.trim(),
        workLocation: draft.workLocation.trim(),
      },
      profilePhotoDataUrl: draft.profilePhotoDataUrl,
    };
    setSaving(true);
    try {
      await dispatch(saveEssProfileWithAdminSync({ employeeId, profile: next })).unwrap();
      dispatch(addNotification({ type: "success", message: "Profile header saved and synced with HR." }));
      setEditing(false);
    } catch {
      setBanner("Could not save. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      {banner ? <p className="mb-3 text-sm text-destructive">{banner}</p> : null}
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start">
        <ProfileImageUploader
          value={draft.profilePhotoDataUrl}
          readOnly={profile.profileLocked === true}
          nameHint={displayName}
          onChange={(url) => {
            if (!editing) startEdit();
            setDraft((d) => ({ ...d, profilePhotoDataUrl: url }));
          }}
          onRemove={() => {
            if (!editing) startEdit();
            setDraft((d) => ({ ...d, profilePhotoDataUrl: "" }));
          }}
        />

        <div className="min-w-0 flex-1 space-y-3">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Employee</p>
              {editing ? (
                <div className="mt-1 flex flex-wrap gap-2">
                  <input
                    className="rounded-md border border-border bg-background px-2 py-1 text-sm font-semibold"
                    value={draft.firstName}
                    onChange={(e) => setDraft((d) => ({ ...d, firstName: e.target.value }))}
                    placeholder="First name"
                  />
                  <input
                    className="rounded-md border border-border bg-background px-2 py-1 text-sm font-semibold"
                    value={draft.middleName}
                    onChange={(e) => setDraft((d) => ({ ...d, middleName: e.target.value }))}
                    placeholder="Middle"
                  />
                  <input
                    className="rounded-md border border-border bg-background px-2 py-1 text-sm font-semibold"
                    value={draft.lastName}
                    onChange={(e) => setDraft((d) => ({ ...d, lastName: e.target.value }))}
                    placeholder="Last name"
                  />
                </div>
              ) : (
                <h1 className="text-xl font-bold tracking-tight text-foreground">{displayName || "—"}</h1>
              )}
              <div className="mt-2 flex flex-wrap gap-2 text-sm text-muted-foreground">
                {editing ? (
                  <>
                    <input
                      className="w-40 rounded-md border border-border bg-background px-2 py-1 text-xs"
                      value={draft.designation}
                      onChange={(e) => setDraft((d) => ({ ...d, designation: e.target.value }))}
                      placeholder="Designation"
                    />
                    <select
                      className="rounded-md border border-border bg-background px-2 py-1 text-xs"
                      value={draft.employeeStatus}
                      onChange={(e) => setDraft((d) => ({ ...d, employeeStatus: e.target.value }))}
                    >
                      <option value="Active">Active</option>
                      <option value="Inactive">Inactive</option>
                      <option value="On Leave">On Leave</option>
                    </select>
                  </>
                ) : (
                  <>
                    <span>{draft.designation || "—"}</span>
                    <span className="rounded-md border border-border px-2 py-0.5 text-xs font-semibold text-foreground">
                      {draft.employeeStatus || "—"}
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              {profile.profileLocked ? (
                <button
                  type="button"
                  onClick={() => {
                    try { window.dispatchEvent(new CustomEvent('ess:request_change', { detail: { sectionId: 'profile' } })); } catch {}
                  }}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-bold hover:bg-secondary"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                  Request Change
                </button>
              ) : editing ? (
                <>
                  <button
                    type="button"
                    disabled={saving}
                    onClick={save}
                    className="inline-flex items-center gap-1.5 rounded-lg bg-primary px-3 py-2 text-xs font-bold text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
                  >
                    <Save className="h-3.5 w-3.5" />
                    {saving ? "Saving…" : "Save"}
                  </button>
                  <button
                    type="button"
                    disabled={saving}
                    onClick={cancel}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-bold hover:bg-secondary disabled:opacity-50"
                  >
                    <X className="h-3.5 w-3.5" />
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  onClick={startEdit}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-border px-3 py-2 text-xs font-bold hover:bg-secondary"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                  Edit
                </button>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {(
              [
                ["officialEmail", "Email"],
                ["personalMobile", "Phone number"],
                ["alternateMobileNumber", "Alternate mobile"],
                ["workLocation", "Current location"],
              ] as const
            ).map(([key, label]) => (
              <div key={key} className="space-y-1">
                <p className="text-[11px] font-semibold uppercase text-muted-foreground">{label}</p>
                {editing ? (
                  <input
                    className="w-full rounded-md border border-border bg-background px-2 py-1.5 text-sm"
                    value={(draft as Record<string, string>)[key]}
                    onChange={(e) => setDraft((d) => ({ ...d, [key]: e.target.value }))}
                  />
                ) : (
                  <p className="text-sm font-medium text-foreground">{(draft as Record<string, string>)[key] || "—"}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
