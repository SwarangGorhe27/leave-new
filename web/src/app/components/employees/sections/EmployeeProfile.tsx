import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import {
  MapPin,
  Mail,
  Phone,
  User,
  Briefcase,
  Heart,
  Languages,
  Monitor,
  Users,
  ShieldCheck,
  Edit2,
} from "lucide-react";
import { useDispatch } from "react-redux";
import {
  Employee,
} from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableSectionCard,
  ProfileInfoField,
  UploadField,
  EmptyStateCard,
  ConfirmationDialog,
} from "../employee-details";
import { useMasterOptions } from "./useMasterOptions";
import {
  EmployeeLanguageRow,
  LanguageMasterOption,
  LanguageProficiencyMasterOption,
  employeeLanguageRowsToPayload,
  getEmployeeLanguageDetails,
  getLanguageChoices,
  getLanguageProficiencyChoices,
  languageDetailsToEmployeeRows,
  patchEmployeeLanguageDetails,
} from "../../../api/employeeLanguageDetails";
import {
  employeeMedicalDetailsToPayload,
  getEmployeeMedicalDetails,
  medicalDetailsToEmployeePatch,
  patchEmployeeMedicalDetails,
} from "../../../api/employeeMedicalDetails";
import { addNotification } from "../../../../store/slices/notificationSlice";
import { updateAdminEmployee } from "../../../../store/slices/adminSlice";
import type { AppDispatch } from "../../../../store";

interface Props {
  employee: Employee;
  isFinalSubmitted?: boolean;
}

type LangRow = EmployeeLanguageRow;

const YES_NO_OPTIONS = [
  { value: "Yes", label: "Yes" },
  { value: "No", label: "No" },
];

function formatDate(dateStr?: string) {
  if (!dateStr) return "";
  try {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export function EmployeeProfile({ employee, isFinalSubmitted = false }: Props) {
  const { handleAdminSave, handleToggleEditAccess } = useAdminSync();
  const dispatch = useDispatch<AppDispatch>();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleEditPhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 3 * 1024 * 1024) {
      alert("Image must be 3 MB or smaller.");
      return;
    }

    const reader = new FileReader();
    reader.onload = async () => {
      const dataUrl = reader.result as string;
      const nextEmployee = {
        ...employee,
        avatar: dataUrl,
      };
      await handleAdminSave("Profile Photo", employee, nextEmployee);
    };
    reader.readAsDataURL(file);
  };
  const genderOptions = useMasterOptions("Gender");
  const maritalStatusOptions = useMasterOptions("MaritalStatus");
  const bloodGroupOptions = useMasterOptions("BloodGroup");
  const nationalityOptions = useMasterOptions("Nationality");
  const religionOptions = useMasterOptions("Religion");
  const casteOptions = useMasterOptions("Caste");
  const casteCategoryOptions = useMasterOptions("CasteCategory");
  const countryOptions = useMasterOptions("Country");
  const stateOptions = useMasterOptions("State");
  const cityOptions = useMasterOptions("City");
  const employeeCategoryOptions = useMasterOptions("EmployeeCategory");
  const departmentOptions = useMasterOptions("Department");
  const designationOptions = useMasterOptions("Designation");
  const shiftOptions = useMasterOptions("ShiftGroup");
  const workLocationOptions = useMasterOptions("OfficeLocation");
  const employeeTypeOptions = useMasterOptions("EmployeeType");
  const employeeStatusOptions = useMasterOptions("EmployeeStatus");
  const languageOptions = useMasterOptions("Language");
  const proficiencyOptions = useMasterOptions("ProficiencyLevel");
  const relationOptions = useMasterOptions("Relation");

  const [personalEdit, setPersonalEdit] = useState(false);
  const [personal, setPersonal] = useState(employee);

  const [addressEdit, setAddressEdit] = useState(false);
  const [addr, setAddr] = useState({
    current: employee.currentAddress,
    permanent: employee.permanentAddress,
    same: employee.currentAddress?.isSameAsPermanent ?? false,
  });

  const [workEdit, setWorkEdit] = useState(false);
  const [work, setWork] = useState(employee);

  const [langEdit, setLangEdit] = useState(false);
  const [languages, setLanguages] = useState<LangRow[]>(employee.languages || []);
  const [savedLanguages, setSavedLanguages] = useState<LangRow[]>(employee.languages || []);
  const [languageChoices, setLanguageChoices] = useState<LanguageMasterOption[]>([]);
  const [languageProficiencyChoices, setLanguageProficiencyChoices] = useState<LanguageProficiencyMasterOption[]>([]);
  const [languageLoading, setLanguageLoading] = useState(false);
  const [languageSaving, setLanguageSaving] = useState(false);
  const [languageError, setLanguageError] = useState<string | null>(null);

  const [emEdit, setEmEdit] = useState(false);
  const [emergency, setEmergency] = useState({
    ec: employee.emergencyContact,
    med: employee.medicalInfo,
  });
  const [savedEmergency, setSavedEmergency] = useState({
    ec: employee.emergencyContact,
    med: employee.medicalInfo,
  });
  const [medicalDetailsLoaded, setMedicalDetailsLoaded] = useState(false);
  const [medicalLoading, setMedicalLoading] = useState(false);
  const [medicalSaving, setMedicalSaving] = useState(false);
  const [medicalError, setMedicalError] = useState<string | null>(null);

  useEffect(() => {
    setPersonal(employee);
    setAddr({
      current: employee.currentAddress,
      permanent: employee.permanentAddress,
      same: employee.currentAddress?.isSameAsPermanent ?? false,
    });
    setWork(employee);
    setLanguages(employee.languages || []);
    setSavedLanguages(employee.languages || []);
    if (!medicalDetailsLoaded) {
      const nextEmergency = { ec: employee.emergencyContact, med: employee.medicalInfo };
      setEmergency(nextEmergency);
      setSavedEmergency(nextEmergency);
    }
  }, [employee, medicalDetailsLoaded]);

  useEffect(() => {
    let cancelled = false;

    async function loadLanguageDetails() {
      if (!employee.id) return;
      setLanguageLoading(true);
      setLanguageError(null);
      try {
        const [details, languageMaster, proficiencyMaster] = await Promise.all([
          getEmployeeLanguageDetails(employee.id),
          getLanguageChoices(),
          getLanguageProficiencyChoices(),
        ]);
        if (cancelled) return;

        const nextLanguages = languageDetailsToEmployeeRows(details);
        setLanguageChoices(languageMaster);
        setLanguageProficiencyChoices(proficiencyMaster);
        setLanguages(nextLanguages);
        setSavedLanguages(nextLanguages);
        dispatch(updateAdminEmployee({ ...employee, languages: nextLanguages }));
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : "Could not load language details.";
        setLanguageError(message);
        dispatch(addNotification({ type: "error", message }));
      } finally {
        if (!cancelled) setLanguageLoading(false);
      }
    }

    loadLanguageDetails();

    return () => {
      cancelled = true;
    };
  }, [dispatch, employee.id]);

  useEffect(() => {
    let cancelled = false;

    async function loadMedicalDetails() {
      if (!employee.id) return;
      setMedicalLoading(true);
      setMedicalError(null);
      try {
        const details = await getEmployeeMedicalDetails(employee.id);
        if (cancelled) return;

        const medicalPatch = medicalDetailsToEmployeePatch(details);
        const nextEmergency = {
          ec: medicalPatch.emergencyContact,
          med: medicalPatch.medicalInfo,
        };
        setMedicalDetailsLoaded(true);
        setEmergency(nextEmergency);
        setSavedEmergency(nextEmergency);
        dispatch(updateAdminEmployee({ ...employee, ...medicalPatch }));
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : "Could not load emergency and medical information.";
        setMedicalError(message);
        dispatch(addNotification({ type: "error", message }));
      } finally {
        if (!cancelled) setMedicalLoading(false);
      }
    }

    loadMedicalDetails();

    return () => {
      cancelled = true;
    };
  }, [dispatch, employee.id]);

  const mergeEmployee = useCallback(
    (patch: Partial<Employee>) => ({ ...employee, ...patch }),
    [employee]
  );

  const statusStyle: Record<string, string> = {
    Active: "bg-emerald-500 text-white",
    "On Leave": "bg-amber-500 text-white",
    Inactive: "bg-rose-500 text-white",
  };

  const isEditable = (id: string) => employee.editableSections?.includes(id);

  const languageSelectOptions = useMemo(
    () =>
      languageChoices.length
        ? languageChoices.map((choice) => ({ value: choice.label, label: choice.label }))
        : languageOptions,
    [languageChoices, languageOptions]
  );

  const proficiencySelectOptions = useMemo(
    () =>
      languageProficiencyChoices.length
        ? languageProficiencyChoices.map((choice) => ({ value: choice.label, label: choice.label }))
        : [],
    [languageProficiencyChoices]
  );

  const saveLanguageDetails = async () => {
    if (!languageProficiencyChoices.length) {
      const message = "No active language proficiency masters found. Add active records in Language Proficiency master first.";
      setLanguageError(message);
      dispatch(addNotification({ type: "error", message }));
      return;
    }
    if (languages.some((row) => !row.proficiency)) {
      const message = "Select a proficiency level for each language row.";
      setLanguageError(message);
      dispatch(addNotification({ type: "warning", message }));
      return;
    }

    setLanguageSaving(true);
    setLanguageError(null);
    try {
      const payload = employeeLanguageRowsToPayload(languages, {
        languages: languageChoices,
        proficiencies: languageProficiencyChoices,
      });
      const saved = await patchEmployeeLanguageDetails(employee.id, payload);
      const nextLanguages = languageDetailsToEmployeeRows(saved);
      setLanguages(nextLanguages);
      setSavedLanguages(nextLanguages);
      setLangEdit(false);
      dispatch(updateAdminEmployee({ ...employee, languages: nextLanguages }));
      dispatch(addNotification({ type: "success", message: "Language details updated." }));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not save language details.";
      setLanguageError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setLanguageSaving(false);
    }
  };

  const saveMedicalDetails = async () => {
    setMedicalSaving(true);
    setMedicalError(null);
    try {
      const saved = await patchEmployeeMedicalDetails(
        employee.id,
        employeeMedicalDetailsToPayload(emergency)
      );
      const medicalPatch = medicalDetailsToEmployeePatch(saved);
      const nextEmergency = {
        ec: medicalPatch.emergencyContact,
        med: medicalPatch.medicalInfo,
      };
      setEmergency(nextEmergency);
      setSavedEmergency(nextEmergency);
      setEmEdit(false);
      dispatch(updateAdminEmployee({ ...employee, ...medicalPatch }));
      dispatch(addNotification({ type: "success", message: "Emergency and medical information updated." }));
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not save emergency and medical information.";
      setMedicalError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setMedicalSaving(false);
    }
  };

  return (
    <div className="space-y-6 pb-20">
      <div className="flat-card bg-card text-card-foreground p-8 relative overflow-hidden border border-border">
        <div className="absolute right-0 top-0 w-1/3 h-full bg-gradient-to-l from-primary/10 to-transparent pointer-events-none" />
        <div className="flex flex-col md:flex-row items-center md:items-start gap-8 relative z-10">
          <div className="relative group">
            {employee.avatar ? (
              <img
                src={employee.avatar}
                alt={employee.name}
                className="w-24 h-24 rounded-2xl object-cover border-4 border-background shadow-elevated"
              />
            ) : (
              <div
                className="w-24 h-24 rounded-2xl flex items-center justify-center border-4 border-background text-white text-3xl font-black shadow-elevated"
                style={{ backgroundColor: employee.avatarColor }}
              >
                {employee.initials}
              </div>
            )}
            <button
              type="button"
              onClick={handleEditPhotoClick}
              disabled={isFinalSubmitted}
              className={`absolute -bottom-2 -right-2 p-2 rounded-lg shadow-lg transition-colors ${isFinalSubmitted ? 'bg-surface-100 text-muted-foreground cursor-not-allowed' : 'bg-primary text-white hover:bg-primary/95'}`}
              title="Upload or change photo"
            >
              <Edit2 size={14} />
            </button>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept="image/jpeg,image/png,image/webp"
              className="hidden"
            />
          </div>
          <div className="flex-1 text-center md:text-left space-y-4">
            <div>
              <h2 className="text-3xl font-black tracking-tight">{personal.name}</h2>
              <p className="text-muted-foreground text-base font-bold mt-1 tracking-wide">{employee.designation}</p>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 mt-3">
                <span
                  className={`text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full ${
                    statusStyle[employee.status] ?? "bg-secondary text-muted-foreground"
                  }`}
                >
                  {employee.status}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-10 pt-8 border-t border-border relative z-10">
          {[
            { icon: Mail, value: employee.email, label: "Email Address" },
            { icon: Phone, value: employee.phone, label: "Phone Number" },
            { icon: Phone, value: employee.alternateMobile, label: "Alternate Mobile" },
            { icon: MapPin, value: employee.location, label: "Current Location" },
          ].map((contact) => (
            <div
              key={contact.label}
              className="flex items-center gap-4 bg-secondary p-4 rounded-2xl border border-border"
            >
              <div className="w-10 h-10 rounded-xl bg-background flex items-center justify-center border border-border">
                <contact.icon className="w-4 h-4 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[9px] font-black text-muted-foreground uppercase tracking-widest">{contact.label}</p>
                <p className="text-sm font-bold truncate">{contact.value || "—"}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <EditableSectionCard
        title="Personal Information"
        icon={User}
        sectionId="profile-personal"
        canEmployeeEdit={isEditable("profile-personal")}
        profileLocked={employee.profileLocked || isFinalSubmitted}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "profile-personal", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={personalEdit}
        onEdit={() => setPersonalEdit(true)}
        onCancel={() => {
          setPersonal(employee);
          setPersonalEdit(false);
        }}
        onSave={async () => {
          const ok = await handleAdminSave("Personal Information", employee, personal);
          if (ok) setPersonalEdit(false);
        }}
      >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField
            label="First Name"
            value={personal.firstName || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, firstName: v }))}
          />
          <ProfileInfoField
            label="Middle Name"
            value={personal.middleName || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, middleName: v }))}
          />
          <ProfileInfoField
            label="Last Name"
            value={personal.lastName || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, lastName: v }))}
          />
          <ProfileInfoField
            label="Father's Name"
            value={personal.fathersName || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, fathersName: v }))}
          />
          <ProfileInfoField
            label="Spouse's Name"
            value={personal.spouseName || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, spouseName: v }))}
          />
          <ProfileInfoField
            label="Date of Birth"
            value={personal.dateOfBirth}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, dateOfBirth: v }))}
            type="date"
          />
          <ProfileInfoField
            label="Actual DOB"
            value={personal.actualDob || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, actualDob: v }))}
            type="date"
          />
          <ProfileInfoField
            label="Place of Birth"
            value={personal.placeOfBirth || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, placeOfBirth: v }))}
          />
          <ProfileInfoField
            label="Gender"
            value={personal.gender}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Gender"
            onChange={(v) => setPersonal((p) => ({ ...p, gender: v }))}
            options={genderOptions}
          />
          <ProfileInfoField
            label="Marital Status"
            value={personal.maritalStatus}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Marital Status"
            onChange={(v) => setPersonal((p) => ({ ...p, maritalStatus: v }))}
            options={maritalStatusOptions}
          />
          <ProfileInfoField
            label="Blood Group"
            value={personal.bloodGroup}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Blood Group"
            onChange={(v) => setPersonal((p) => ({ ...p, bloodGroup: v }))}
            options={bloodGroupOptions}
          />
          <ProfileInfoField
            label="Nationality"
            value={personal.nationality}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Nationality"
            onChange={(v) => setPersonal((p) => ({ ...p, nationality: v }))}
            options={nationalityOptions}
          />
          <ProfileInfoField
            label="Religion"
            value={personal.religion || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Religion"
            onChange={(v) => setPersonal((p) => ({ ...p, religion: v }))}
            options={religionOptions}
          />
          <ProfileInfoField
            label="Caste"
            value={personal.caste || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Caste"
            onChange={(v) => setPersonal((p) => ({ ...p, caste: v }))}
            options={casteOptions}
          />
          <ProfileInfoField
            label="Caste Category"
            value={personal.casteCategory || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            placeholder="Select Caste Category"
            onChange={(v) => setPersonal((p) => ({ ...p, casteCategory: v }))}
            options={casteCategoryOptions}
          />
          <ProfileInfoField
            label="Identification Mark"
            value={personal.identificationMark || ""}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, identificationMark: v }))}
          />
          <ProfileInfoField
            label="Physically Challenged"
            value={personal.isPhysicallyChallenged ? "Yes" : "No"}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            type="select"
            options={YES_NO_OPTIONS}
            placeholder="Select Physically Challenged"
            onChange={(v) =>
              setPersonal((p) => ({ ...p, isPhysicallyChallenged: v === "Yes" }))
            }
          />
          <ProfileInfoField
            label="International Employee"
            value={personal.isInternationalEmployee ? "Yes" : "No"}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            type="select"
            options={YES_NO_OPTIONS}
            placeholder="Select International Employee"
            onChange={(v) =>
              setPersonal((p) => ({ ...p, isInternationalEmployee: v === "Yes" }))
            }
          />
          <ProfileInfoField
            label="Joining Date"
            value={personal.joiningDate}
            editing={personalEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setPersonal((p) => ({ ...p, joiningDate: v }))}
            type="date"
          />
        </div>
      </EditableSectionCard>

      <EditableSectionCard
        title="Address Details"
        icon={MapPin}
        sectionId="profile-address"
        canEmployeeEdit={isEditable("profile-address")}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "profile-address", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={addressEdit}
        onEdit={() => setAddressEdit(true)}
        onCancel={() => {
          setAddr({
            current: employee.currentAddress,
            permanent: employee.permanentAddress,
            same: employee.currentAddress?.isSameAsPermanent ?? false,
          });
          setAddressEdit(false);
        }}
        onSave={async () => {
          const currentAddress = {
            ...(addr.current || {}),
            isSameAsPermanent: addr.same,
          } as Employee["currentAddress"];
          const permanentAddress = addr.same ? { ...currentAddress, isSameAsPermanent: undefined } : addr.permanent;
          const next = mergeEmployee({
            currentAddress,
            permanentAddress: permanentAddress as Employee["permanentAddress"],
          });
          const ok = await handleAdminSave("Address Details", employee, next);
          if (ok) setAddressEdit(false);
        }}
      >
        <div className="space-y-8">
          <div>
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-3">
              Current Address
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {(
                [
                  ["addressLine1", "Address Line 1"],
                  ["addressLine2", "Address Line 2"],
                  ["landmark", "Landmark"],
                  ["city", "City"],
                  ["state", "State"],
                  ["country", "Country"],
                  ["pincode", "Pincode"],
                  ["startDate", "Start Date"],
                  ["toDate", "To Date"],
                ] as const
              ).map(([key, label]) => {
                const options =
                  key === "city"
                    ? cityOptions
                    : key === "state"
                      ? stateOptions
                      : key === "country"
                        ? countryOptions
                        : undefined;

                return (
                  <ProfileInfoField
                    key={key}
                    label={label}
                    value={(addr.current?.[key] as string) || ""}
                    editing={addressEdit}
                    readOnly={isFinalSubmitted}
                    type={key.includes("Date") ? "date" : "text"}
                    options={options}
                    onChange={(v) =>
                      setAddr((a) => ({
                        ...a,
                        current: { ...(a.current || {}), [key]: v } as Employee["currentAddress"],
                      }))
                    }
                  />
                );
              })}
              <label className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                <input
                  type="checkbox"
                  checked={addr.same}
                  disabled={!addressEdit}
                  onChange={() =>
                    setAddr((a) => {
                      const nextSame = !a.same;
                      return {
                        ...a,
                        same: nextSame,
                        permanent: nextSame && a.current ? { ...a.current } : a.permanent,
                      };
                    })
                  }
                />
                Same as permanent address
              </label>
            </div>
          </div>
          <div className="pt-6 border-t border-border">
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-3">
              Permanent Address
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {(
                [
                  ["addressLine1", "Address Line 1"],
                  ["addressLine2", "Address Line 2"],
                  ["landmark", "Landmark"],
                  ["city", "City"],
                  ["state", "State"],
                  ["country", "Country"],
                  ["pincode", "Pincode"],
                  ["startDate", "Start Date"],
                  ["toDate", "To Date"],
                ] as const
              ).map(([key, label]) => {
                const options =
                  key === "city"
                    ? cityOptions
                    : key === "state"
                      ? stateOptions
                      : key === "country"
                        ? countryOptions
                        : undefined;

                return (
                  <ProfileInfoField
                    key={`p-${key}`}
                    label={label}
                    value={(addr.permanent?.[key] as string) || ""}
                    editing={addressEdit && !addr.same}
                    readOnly={isFinalSubmitted}
                    type={key.includes("Date") ? "date" : "text"}
                    options={options}
                    onChange={(v) =>
                      setAddr((a) => ({
                        ...a,
                        permanent: { ...(a.permanent || {}), [key]: v } as Employee["permanentAddress"],
                      }))
                    }
                  />
                );
              })}
            </div>
          </div>
        </div>
      </EditableSectionCard>

      <EditableSectionCard
        title="Work Details"
        icon={Briefcase}
        sectionId="profile-work"
        canEmployeeEdit={isEditable("profile-work")}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "profile-work", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={workEdit}
        onEdit={() => setWorkEdit(true)}
        onCancel={() => {
          setWork(employee);
          setWorkEdit(false);
        }}
        onSave={async () => {
          const ok = await handleAdminSave("Work Details", employee, work);
          if (ok) setWorkEdit(false);
        }}
        headerExtra={null}
        >
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField label="Employee ID" value={employee.employeeId} editing={false} />
          <ProfileInfoField
            label="Employee Category"
            value={work.employeeCategory || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, employeeCategory: v }))}
            options={employeeCategoryOptions}
          />
          <ProfileInfoField
            label="Department"
            value={work.department}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, department: v }))}
            options={departmentOptions}
          />
          <ProfileInfoField
            label="Team"
            value={work.team}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, team: v }))}
          />
          <ProfileInfoField
            label="Designation"
            value={work.designation}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, designation: v }))}
            options={designationOptions}
          />
          <ProfileInfoField
            label="Shift"
            value={work.shift || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, shift: v }))}
            options={shiftOptions}
          />
          <ProfileInfoField
            label="Work Location"
            value={work.location}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, location: v }))}
            options={workLocationOptions}
          />
          <ProfileInfoField
            label="Employee Type"
            value={work.employeeType || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, employeeType: v }))}
            options={employeeTypeOptions}
          />
          <ProfileInfoField
            label="Confirmation Date"
            value={work.confirmationDate || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, confirmationDate: v }))}
            type="date"
          />
          <ProfileInfoField
            label="Employment Status"
            value={work.employmentStatus || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, employmentStatus: v }))}
            options={employeeStatusOptions}
          />
          <ProfileInfoField
            label="Probation Period"
            value={work.probationPeriod || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, probationPeriod: v }))}
          />
          <ProfileInfoField
            label="Notice Period"
            value={work.noticePeriod || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, noticePeriod: v }))}
          />
          <ProfileInfoField
            label="Notice Period (Days)"
            value={work.noticePeriodDays || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, noticePeriodDays: v }))}
          />
          <ProfileInfoField
            label="Referred By"
            value={work.referredBy || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, referredBy: v }))}
          />
          <ProfileInfoField
            label="Reporting To"
            value={work.reportingTo || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, reportingTo: v }))}
          />
          <ProfileInfoField
            label="Functional Manager"
            value={work.functionalManager || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, functionalManager: v }))}
          />
          <ProfileInfoField
            label="HR Partner"
            value={work.hrPartner || ""}
            editing={workEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setWork((w) => ({ ...w, hrPartner: v }))}
          />
        </div>
      </EditableSectionCard>

      <EditableSectionCard
        title="Language Details"
        icon={Languages}
        sectionId="profile-languages"
        canEmployeeEdit={isEditable("profile-languages")}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "profile-languages", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={langEdit}
        onEdit={() => setLangEdit(true)}
        onCancel={() => {
          setLanguages(savedLanguages);
          setLangEdit(false);
        }}
        onSave={saveLanguageDetails}
      >
        {languageLoading ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Loading saved language details...
          </div>
        ) : null}
        {languageError ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700">
            {languageError}
          </div>
        ) : null}
        {languageSaving ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Saving language details...
          </div>
        ) : null}
        {!languages.length ? (
          <EmptyStateCard
            icon={Languages}
            title="No languages recorded"
            description="Contact support or employee to record language proficiency."
          />
        ) : (
          <div className="space-y-4">
            {languages.map((row, idx) => (
              <div key={idx} className="rounded-xl border border-border bg-background p-4 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <ProfileInfoField
                    label="Language Name"
                    value={row.language}
                    editing={langEdit}
                    readOnly={isFinalSubmitted}
                    onChange={(v) =>
                      setLanguages((rows) => rows.map((r, i) => (i === idx ? { ...r, language: v } : r)))
                    }
                    options={languageSelectOptions}
                  />
                  <div className="space-y-1.5">
                    <span className="block text-[11px] font-semibold text-muted-foreground tracking-wide">
                      Proficiency Level
                    </span>
                    {langEdit ? (
                      <select
                        value={row.proficiency}
                        disabled={isFinalSubmitted || !langEdit}
                        onChange={(e) =>
                          setLanguages((rows) =>
                            rows.map((r, i) => (i === idx ? { ...r, proficiency: e.target.value } : r))
                          )
                        }
                        className="w-full rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-medium"
                      >
                        <option value="">Select Proficiency</option>
                        {proficiencySelectOptions.map((p) => (
                          <option key={p.value} value={p.value}>
                            {p.label}
                          </option>
                        ))}
                      </select>
                    ) : (
                      <div className="rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-semibold">
                        {row.proficiency || "—"}
                      </div>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap gap-6">
                  {(
                    [
                      ["canRead", "Read"],
                      ["canWrite", "Write"],
                      ["canSpeak", "Speak"],
                    ] as const
                  ).map(([key, label]) => (
                    <label key={key} className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                      <input
                        type="checkbox"
                        checked={row[key]}
                        disabled={isFinalSubmitted || !langEdit}
                        onChange={() =>
                          setLanguages((rows) =>
                            rows.map((r, i) => (i === idx ? { ...r, [key]: !r[key] } : r))
                          )
                        }
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </EditableSectionCard>

      <EditableSectionCard
        title="Emergency & Medical Information"
        icon={Heart}
        sectionId="profile-medical"
        canEmployeeEdit={isEditable("profile-medical")}
        onToggleEmployeeEdit={(v) => handleToggleEditAccess(employee, "profile-medical", v)}
        requestStatus={employee.editRequestStatus}
        isEditing={emEdit}
        onEdit={() => setEmEdit(true)}
        onCancel={() => {
          setEmergency(savedEmergency);
          setEmEdit(false);
        }}
        headerExtra={null}
        onSave={saveMedicalDetails}
      >
        {medicalLoading ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Loading saved emergency and medical information...
          </div>
        ) : null}
        {medicalError ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700">
            {medicalError}
          </div>
        ) : null}
        {medicalSaving ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Saving emergency and medical information...
          </div>
        ) : null}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField
            label="Emergency Contact Name"
            value={emergency.ec?.name || ""}
            editing={emEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) => setEmergency((e) => ({ ...e, ec: { ...e.ec, name: v, relationship: e.ec?.relationship || "", phone: e.ec?.phone || "" } }))}
          />
          <ProfileInfoField
            label="Emergency Contact #"
            value={emergency.ec?.phone || ""}
            editing={emEdit}
            readOnly={isFinalSubmitted}
            onChange={(v) =>
              setEmergency((e) => ({
                ...e,
                ec: {
                  name: e.ec?.name || "",
                  relationship: e.ec?.relationship || "",
                  phone: v,
                  alternatePhone: e.ec?.alternatePhone,
                },
              }))
            }
          />
          <ProfileInfoField
            label="Relationship"
            value={emergency.ec?.relationship || ""}
            editing={emEdit}
            readOnly={isFinalSubmitted}
            options={relationOptions}
            onChange={(v) =>
              setEmergency((e) => ({
                ...e,
                ec: { name: e.ec?.name || "", phone: e.ec?.phone || "", relationship: v },
              }))
            }
          />

          {/* Disease Details Checkbox & Textarea */}
          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3">
              <input
                type="checkbox"
                checked={!!emergency.med?.hasDisease}
                disabled={!emEdit}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setEmergency((prev) => ({
                    ...prev,
                    med: {
                      ...prev.med,
                      hasDisease: checked,
                      ...(checked ? {} : { diseaseDetails: "" }),
                    },
                  }));
                }}
              />
              <span className="text-sm font-semibold text-foreground">Has Any Disease?</span>
            </label>
            {emergency.med?.hasDisease ? (
              <ProfileInfoField
                label="Disease Details"
                value={emergency.med?.diseaseDetails || ""}
                editing={emEdit && !!emergency.med?.hasDisease}
                readOnly={isFinalSubmitted}
                type="textarea"
                placeholder="Enter disease name, description, medication, since when, etc."
                onChange={(v) => setEmergency((e) => ({ ...e, med: { ...e.med, diseaseDetails: v } }))}
              />
            ) : null}
          </div>

          {/* Surgery Details Checkbox & Textarea */}
          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3">
              <input
                type="checkbox"
                checked={!!emergency.med?.hasSurgery}
                disabled={!emEdit}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setEmergency((prev) => ({
                    ...prev,
                    med: {
                      ...prev.med,
                      hasSurgery: checked,
                      ...(checked ? {} : { surgeryDetails: "" }),
                    },
                  }));
                }}
              />
              <span className="text-sm font-semibold text-foreground">Any Surgery or Operation Done?</span>
            </label>
            {emergency.med?.hasSurgery ? (
              <ProfileInfoField
                label="Surgery / Operation Details"
                value={emergency.med?.surgeryDetails || ""}
                editing={emEdit && !!emergency.med?.hasSurgery}
                readOnly={isFinalSubmitted}
                type="textarea"
                placeholder="Enter surgery name, hospital, date, recovery status, etc."
                onChange={(v) => setEmergency((e) => ({ ...e, med: { ...e.med, surgeryDetails: v } }))}
              />
            ) : null}
          </div>

          {/* Allergy Details Checkbox & Textarea */}
          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3">
              <input
                type="checkbox"
                checked={!!emergency.med?.hasAllergies}
                disabled={!emEdit}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setEmergency((prev) => ({
                    ...prev,
                    med: {
                      ...prev.med,
                      hasAllergies: checked,
                      ...(checked ? {} : { allergyDetails: "" }),
                    },
                  }));
                }}
              />
              <span className="text-sm font-semibold text-foreground">Any Allergies?</span>
            </label>
            {emergency.med?.hasAllergies ? (
              <ProfileInfoField
                label="Allergy Details"
                value={emergency.med?.allergyDetails || ""}
                editing={emEdit && !!emergency.med?.hasAllergies}
                readOnly={isFinalSubmitted}
                type="textarea"
                placeholder="Enter allergy type and description."
                onChange={(v) => setEmergency((e) => ({ ...e, med: { ...e.med, allergyDetails: v } }))}
              />
            ) : null}
          </div>
        </div>
      </EditableSectionCard>


    </div>
  );
}
