import { useCallback, useEffect, useMemo, useState } from "react";
import {
  MapPin, User, Briefcase, Heart, Languages, Plus, Trash2,
} from "lucide-react";
import { useDispatch } from "react-redux";
import { Employee } from "../mockData";
import { useAdminSync } from "../../admin/useAdminSync";
import {
  EditableSectionCard,
  ProfileInfoField,
  EmptyStateCard,
} from "../employee-details";
import {
  EmployeePersonalDetailsApi,
  employeeToPersonalDetailsPayload,
  getMyPersonalDetails,
  patchMyPersonalDetails,
  personalDetailsToEmployee,
  postMyPersonalDetails,
} from "../../../api/employeePersonalDetails";
import {
  EmployeeEmploymentDetailsApi,
  employmentDetailsToEmployee,
  getMyEmploymentDetails,
} from "../../../api/employeeEmploymentDetails";
import {
  AddressChoiceApi,
  AddressDetailsResponse,
  EmployeeProfileAddress,
  addressDetailsToEmployeePatch,
  employeeAddressToSubmitRow,
  getAddressCityChoices,
  getAddressCountryChoices,
  getAddressStateChoices,
  getMyAddressDetails,
  patchMyAddressDetails,
  postMyAddressDetails,
} from "../../../api/employeeAddressDetails";
import {
  EmployeeLanguageRow,
  LanguageMasterOption,
  LanguageProficiencyMasterOption,
  employeeLanguageRowsToPayload,
  getLanguageChoices,
  getLanguageProficiencyChoices,
  getMyLanguageDetails,
  languageDetailsToEmployeeRows,
  patchMyLanguageDetails,
  postMyLanguageDetails,
} from "../../../api/employeeLanguageDetails";
import {
  employeeMedicalDetailsToPayload,
  getMyMedicalDetails,
  hasMedicalDetails,
  medicalDetailsToEmployeePatch,
  patchMyMedicalDetails,
  postMyMedicalDetails,
} from "../../../api/employeeMedicalDetails";
import { useMasterList } from "../../../modules/masters/hooks";
import type { MasterRecord } from "../../../modules/masters/types";
import { addNotification } from "../../../../store/slices/notificationSlice";
import { updateAdminEmployee } from "../../../../store/slices/adminSlice";
import type { AppDispatch } from "../../../../store";

interface Props {
  employee: Employee;
}

type LangRow = EmployeeLanguageRow;

const YES_NO_OPTIONS = [
  { value: "Yes", label: "Yes" },
  { value: "No", label: "No" },
];

function masterLabel(record: MasterRecord) {
  return String(record.label ?? record.name ?? record.title ?? record.code ?? record.id);
}

function masterOptions(records: MasterRecord[]) {
  return records.map((record) => {
    const label = masterLabel(record);
    return { value: label, label };
  });
}

function toNumericId(value: string | number | null | undefined) {
  if (typeof value === "number") return value;
  if (typeof value === "string" && /^\d+$/.test(value)) return Number(value);
  return undefined;
}

function resolveMasterId(
  label: string,
  records: MasterRecord[],
  currentId: number | null | undefined
) {
  if (!label) return null;
  const selected = records.find((record) => masterLabel(record) === label);
  return toNumericId(selected?.id) ?? currentId ?? undefined;
}

export function EssEmployeeProfile({ employee }: Props) {
  const { handleAdminSave } = useAdminSync();
  const dispatch = useDispatch<AppDispatch>();
  const masterQuery = useMemo(() => ({ is_active: "true" as const, page: 1 }), []);

  const genderRecords = useMasterList("Gender", masterQuery).data?.results ?? [];
  const maritalStatusRecords = useMasterList("MaritalStatus", masterQuery).data?.results ?? [];
  const bloodGroupRecords = useMasterList("BloodGroup", masterQuery).data?.results ?? [];
  const nationalityRecords = useMasterList("Nationality", masterQuery).data?.results ?? [];
  const religionRecords = useMasterList("Religion", masterQuery).data?.results ?? [];
  const casteRecords = useMasterList("Caste", masterQuery).data?.results ?? [];
  const casteCategoryRecords = useMasterList("CasteCategory", masterQuery).data?.results ?? [];
  const relationRecords = useMasterList("Relation", masterQuery).data?.results ?? [];

  const [personalEdit, setPersonalEdit] = useState(false);
  const [personal, setPersonal] = useState(employee);
  const [personalDetails, setPersonalDetails] = useState<EmployeePersonalDetailsApi | null>(null);
  const [personalLoading, setPersonalLoading] = useState(false);
  const [personalSaving, setPersonalSaving] = useState(false);
  const [personalError, setPersonalError] = useState<string | null>(null);

  const [addressEdit, setAddressEdit] = useState(false);
  const [addr, setAddr] = useState<{
    current?: EmployeeProfileAddress;
    permanent?: EmployeeProfileAddress;
    same: boolean;
  }>({
    current: employee.currentAddress as EmployeeProfileAddress | undefined,
    permanent: employee.permanentAddress as EmployeeProfileAddress | undefined,
    same: employee.currentAddress?.isSameAsPermanent ?? false,
  });
  const [addressDetails, setAddressDetails] = useState<AddressDetailsResponse | null>(null);
  const [addressChoices, setAddressChoices] = useState<{
    countries: AddressChoiceApi[];
    states: AddressChoiceApi[];
    cities: AddressChoiceApi[];
  }>({ countries: [], states: [], cities: [] });
  const [addressLoading, setAddressLoading] = useState(false);
  const [addressSaving, setAddressSaving] = useState(false);
  const [addressError, setAddressError] = useState<string | null>(null);

  const [work, setWork] = useState(employee);
  const [workDetails, setWorkDetails] = useState<EmployeeEmploymentDetailsApi | null>(null);
  const [workLoading, setWorkLoading] = useState(false);
  const [workError, setWorkError] = useState<string | null>(null);

  const [langEdit, setLangEdit] = useState(false);
  const [languages, setLanguages] = useState<LangRow[]>(employee.languages || []);
  const [savedLanguages, setSavedLanguages] = useState<LangRow[]>(employee.languages || []);
  const [languageDetailsLoaded, setLanguageDetailsLoaded] = useState(false);
  const [hasExistingLanguageDetails, setHasExistingLanguageDetails] = useState(false);
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
  const [hasExistingMedicalDetails, setHasExistingMedicalDetails] = useState(false);
  const [medicalLoading, setMedicalLoading] = useState(false);
  const [medicalSaving, setMedicalSaving] = useState(false);
  const [medicalError, setMedicalError] = useState<string | null>(null);

  const languageSelectOptions = useMemo(
    () => languageChoices.map((choice) => ({ value: choice.label, label: choice.label })),
    [languageChoices]
  );

  const languageProficiencySelectOptions = useMemo(
    () => languageProficiencyChoices.map((choice) => ({ value: choice.label, label: choice.label })),
    [languageProficiencyChoices]
  );

  const employeeWithApiPersonalDetails = useMemo(
    () => (personalDetails ? personalDetailsToEmployee(employee, personalDetails) : employee),
    [employee, personalDetails]
  );

  const employeeWithApiAddressDetails = useMemo(
    () => (addressDetails ? { ...employee, ...addressDetailsToEmployeePatch(employee, addressDetails) } : employee),
    [employee, addressDetails]
  );

  const employeeWithApiWorkDetails = useMemo(
    () => (workDetails ? employmentDetailsToEmployee(employee, workDetails) : employee),
    [employee, workDetails]
  );

  useEffect(() => {
    setPersonal(employeeWithApiPersonalDetails);
    setAddr({
      current: employeeWithApiAddressDetails.currentAddress as EmployeeProfileAddress | undefined,
      permanent: employeeWithApiAddressDetails.permanentAddress as EmployeeProfileAddress | undefined,
      same: employeeWithApiAddressDetails.currentAddress?.isSameAsPermanent ?? false,
    });
    setWork(employeeWithApiWorkDetails);
    if (!languageDetailsLoaded) {
      setLanguages(employee.languages || []);
      setSavedLanguages(employee.languages || []);
    }
    if (!medicalDetailsLoaded) {
      const nextEmergency = { ec: employee.emergencyContact, med: employee.medicalInfo };
      setEmergency(nextEmergency);
      setSavedEmergency(nextEmergency);
    }
  }, [employee, employeeWithApiPersonalDetails, employeeWithApiAddressDetails, employeeWithApiWorkDetails, languageDetailsLoaded, medicalDetailsLoaded]);

  useEffect(() => {
    let cancelled = false;

    async function loadPersonalDetails() {
      setPersonalLoading(true);
      setPersonalError(null);
      try {
        const details = await getMyPersonalDetails();
        if (cancelled || !details) return;
        setPersonalDetails(details);
        const nextEmployee = personalDetailsToEmployee(employee, details);
        setPersonal(nextEmployee);
        dispatch(updateAdminEmployee(nextEmployee));
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : "Could not load personal details.";
        setPersonalError(message);
        dispatch(addNotification({ type: "error", message }));
      } finally {
        if (!cancelled) setPersonalLoading(false);
      }
    }

    loadPersonalDetails();

    return () => {
      cancelled = true;
    };
  }, [dispatch, employee.id]);

  useEffect(() => {
    let cancelled = false;

    async function loadMedicalDetails() {
      setMedicalLoading(true);
      setMedicalError(null);
      try {
        const details = await getMyMedicalDetails();
        if (cancelled) return;

        const medicalPatch = medicalDetailsToEmployeePatch(details);
        const nextEmergency = {
          ec: medicalPatch.emergencyContact,
          med: medicalPatch.medicalInfo,
        };
        setMedicalDetailsLoaded(true);
        setHasExistingMedicalDetails(hasMedicalDetails(details));
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

  useEffect(() => {
    let cancelled = false;

    async function loadAddressDetails() {
      setAddressLoading(true);
      setAddressError(null);
      try {
        const [details, countries, states, cities] = await Promise.all([
          getMyAddressDetails(),
          getAddressCountryChoices(),
          getAddressStateChoices(),
          getAddressCityChoices(),
        ]);
        if (cancelled) return;

        setAddressDetails(details);
        setAddressChoices({ countries, states, cities });
        const addressPatch = addressDetailsToEmployeePatch(employee, details);
        setAddr({
          current: addressPatch.currentAddress as EmployeeProfileAddress | undefined,
          permanent: addressPatch.permanentAddress as EmployeeProfileAddress | undefined,
          same: addressPatch.currentAddress?.isSameAsPermanent ?? false,
        });
        dispatch(updateAdminEmployee({ ...employee, ...addressPatch }));
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : "Could not load address details.";
        setAddressError(message);
        dispatch(addNotification({ type: "error", message }));
      } finally {
        if (!cancelled) setAddressLoading(false);
      }
    }

    loadAddressDetails();

    return () => {
      cancelled = true;
    };
  }, [dispatch, employee.id]);

  useEffect(() => {
    let cancelled = false;

    async function loadEmploymentDetails() {
      setWorkLoading(true);
      setWorkError(null);
      try {
        const details = await getMyEmploymentDetails();
        if (cancelled || !details) return;

        setWorkDetails(details);
        const nextEmployee = employmentDetailsToEmployee(employee, details);
        setWork(nextEmployee);
      } catch (error) {
        if (cancelled) return;
        const message = error instanceof Error ? error.message : "Could not load work details.";
        setWorkError(message);
        dispatch(addNotification({ type: "error", message }));
      } finally {
        if (!cancelled) setWorkLoading(false);
      }
    }

    loadEmploymentDetails();

    return () => {
      cancelled = true;
    };
  }, [dispatch, employee.id]);

  useEffect(() => {
    let cancelled = false;

    async function loadLanguageDetails() {
      setLanguageLoading(true);
      setLanguageError(null);
      try {
        const [details, languageMaster, proficiencyMaster] = await Promise.all([
          getMyLanguageDetails(),
          getLanguageChoices(),
          getLanguageProficiencyChoices(),
        ]);
        if (cancelled) return;

        const nextLanguages = languageDetailsToEmployeeRows(details);
        setLanguageDetailsLoaded(true);
        setHasExistingLanguageDetails(details.length > 0);
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

  const mergeEmployee = useCallback(
    (patch: Partial<Employee>) => ({ ...employee, ...patch }),
    [employee]
  );

  const isEditable = (id: string) => employee.editableSections?.includes(id);

  const savePersonalDetails = async () => {
    if (!personal.firstName?.trim() || !personal.lastName?.trim()) {
      dispatch(addNotification({ type: "warning", message: "First name and last name are required." }));
      return;
    }

    setPersonalSaving(true);
    setPersonalError(null);
    try {
      const payload = {
        ...employeeToPersonalDetailsPayload(personal, personalDetails ?? undefined),
        gender_id: resolveMasterId(personal.gender, genderRecords, personalDetails?.gender_id),
        marital_status_id: resolveMasterId(
          personal.maritalStatus,
          maritalStatusRecords,
          personalDetails?.marital_status_id
        ),
        blood_group_id: resolveMasterId(personal.bloodGroup, bloodGroupRecords, personalDetails?.blood_group_id),
        nationality_id: resolveMasterId(personal.nationality, nationalityRecords, personalDetails?.nationality_id),
        religion_id: resolveMasterId(personal.religion || "", religionRecords, personalDetails?.religion_id),
        caste_id: resolveMasterId(personal.caste || "", casteRecords, personalDetails?.caste_id),
        caste_category_id: resolveMasterId(
          personal.casteCategory || "",
          casteCategoryRecords,
          personalDetails?.caste_category_id
        ),
      };

      const submitPersonalDetails = personalDetails ? patchMyPersonalDetails : postMyPersonalDetails;
      await submitPersonalDetails(payload);
      setPersonalEdit(false);
      dispatch(
        addNotification({
          type: "success",
          message: "Personal details submitted for admin approval.",
        })
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not submit personal details.";
      setPersonalError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setPersonalSaving(false);
    }
  };

  const saveAddressDetails = async () => {
    const currentAddress = {
      ...(addr.current || {}),
      isSameAsPermanent: addr.same,
    } as EmployeeProfileAddress;
    const permanentAddress = addr.same && addr.permanent
      ? addr.permanent
      : (addr.permanent as EmployeeProfileAddress | undefined);

    setAddressSaving(true);
    setAddressError(null);
    try {
      const payload = {
        current_address: employeeAddressToSubmitRow(
          currentAddress,
          "CURRENT",
          addressChoices,
          addr.same
        ),
        permanent_address: employeeAddressToSubmitRow(
          permanentAddress,
          "PERMANENT",
          addressChoices,
          false
        ),
      };

      const submitAddressDetails = addressDetails ? patchMyAddressDetails : postMyAddressDetails;
      await submitAddressDetails(payload);
      setAddressEdit(false);
      dispatch(
        addNotification({
          type: "success",
          message: "Address details submitted for admin approval.",
        })
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not submit address details.";
      setAddressError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setAddressSaving(false);
    }
  };

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
      const submitLanguageDetails = hasExistingLanguageDetails ? patchMyLanguageDetails : postMyLanguageDetails;
      await submitLanguageDetails(payload);
      setLangEdit(false);
      setHasExistingLanguageDetails(true);
      setSavedLanguages(languages);
      dispatch(updateAdminEmployee({ ...employee, languages }));
      dispatch(
        addNotification({
          type: "success",
          message: "Language details submitted for admin approval.",
        })
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not submit language details.";
      setLanguageError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setLanguageSaving(false);
    }
  };

  const addLanguageRow = () => {
    setLanguages((rows) => [
      ...rows,
      {
        language: "",
        proficiency: languageProficiencyChoices[0]?.label || "",
        canRead: true,
        canWrite: true,
        canSpeak: true,
        languageId: null,
        proficiencyLevelId: languageProficiencyChoices[0]?.id ?? null,
        readProficiencyId: languageProficiencyChoices[0]?.id ?? null,
        writeProficiencyId: languageProficiencyChoices[0]?.id ?? null,
        speakProficiencyId: languageProficiencyChoices[0]?.id ?? null,
        isMotherTongue: false,
      },
    ]);
    setLangEdit(true);
  };

  const saveMedicalDetails = async () => {
    setMedicalSaving(true);
    setMedicalError(null);
    try {
      const payload = employeeMedicalDetailsToPayload(emergency);
      const submitMedicalDetails = hasExistingMedicalDetails ? patchMyMedicalDetails : postMyMedicalDetails;
      await submitMedicalDetails(payload);
      setEmEdit(false);
      setHasExistingMedicalDetails(true);
      setSavedEmergency(emergency);
      dispatch(updateAdminEmployee({ ...employee, emergencyContact: emergency.ec, medicalInfo: emergency.med }));
      dispatch(
        addNotification({
          type: "success",
          message: "Emergency and medical information submitted for admin approval.",
        })
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Could not submit emergency and medical information.";
      setMedicalError(message);
      dispatch(addNotification({ type: "error", message }));
    } finally {
      setMedicalSaving(false);
    }
  };

  return (
    <div className="space-y-6 pb-20">
      {/* Personal Information */}
      <EditableSectionCard
        title="Personal Information"
        icon={User}
        sectionId="profile-personal"
        canEmployeeEdit={isEditable("profile-personal")}
        hideAdminControls
        requestStatus={employee.editRequestStatus}
        isEditing={personalEdit}
        onEdit={() => setPersonalEdit(true)}
        onCancel={() => { setPersonal(employeeWithApiPersonalDetails); setPersonalEdit(false); }}
        onSave={savePersonalDetails}
      >
        {personalLoading ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Loading saved personal details...
          </div>
        ) : null}
        {personalError ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700">
            {personalError}
          </div>
        ) : null}
        {personalSaving ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Submitting personal details...
          </div>
        ) : null}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField label="First Name" value={personal.firstName || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, firstName: v }))} />
          <ProfileInfoField label="Middle Name" value={personal.middleName || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, middleName: v }))} />
          <ProfileInfoField label="Last Name" value={personal.lastName || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, lastName: v }))} />
          <ProfileInfoField label="Father's Name" value={personal.fathersName || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, fathersName: v }))} />
          <ProfileInfoField label="Spouse's Name" value={personal.spouseName || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, spouseName: v }))} />
          <ProfileInfoField label="Date of Birth" value={personal.dateOfBirth} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, dateOfBirth: v }))} type="date" />
          <ProfileInfoField label="Actual DOB" value={personal.actualDob || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, actualDob: v }))} type="date" />
          <ProfileInfoField label="Place of Birth" value={personal.placeOfBirth || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, placeOfBirth: v }))} />
          <ProfileInfoField label="Gender" value={personal.gender} editing={personalEdit} options={masterOptions(genderRecords)} placeholder="Select Gender" onChange={(v) => setPersonal((p) => ({ ...p, gender: v }))} />
          <ProfileInfoField label="Marital Status" value={personal.maritalStatus} editing={personalEdit} options={masterOptions(maritalStatusRecords)} placeholder="Select Marital Status" onChange={(v) => setPersonal((p) => ({ ...p, maritalStatus: v }))} />
          <ProfileInfoField label="Blood Group" value={personal.bloodGroup} editing={personalEdit} options={masterOptions(bloodGroupRecords)} placeholder="Select Blood Group" onChange={(v) => setPersonal((p) => ({ ...p, bloodGroup: v }))} />
          <ProfileInfoField label="Nationality" value={personal.nationality} editing={personalEdit} options={masterOptions(nationalityRecords)} placeholder="Select Nationality" onChange={(v) => setPersonal((p) => ({ ...p, nationality: v }))} />
          <ProfileInfoField label="Religion" value={personal.religion || ""} editing={personalEdit} options={masterOptions(religionRecords)} placeholder="Select Religion" onChange={(v) => setPersonal((p) => ({ ...p, religion: v }))} />
          <ProfileInfoField label="Caste" value={personal.caste || ""} editing={personalEdit} options={masterOptions(casteRecords)} placeholder="Select Caste" onChange={(v) => setPersonal((p) => ({ ...p, caste: v }))} />
          <ProfileInfoField label="Caste Category" value={personal.casteCategory || ""} editing={personalEdit} options={masterOptions(casteCategoryRecords)} placeholder="Select Caste Category" onChange={(v) => setPersonal((p) => ({ ...p, casteCategory: v }))} />
          <ProfileInfoField label="Identification Mark" value={personal.identificationMark || ""} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, identificationMark: v }))} />
          <ProfileInfoField label="Physically Challenged" value={personal.isPhysicallyChallenged ? "Yes" : "No"} editing={personalEdit} options={YES_NO_OPTIONS} placeholder="Select Physically Challenged" onChange={(v) => setPersonal((p) => ({ ...p, isPhysicallyChallenged: v === "Yes" }))} />
          <ProfileInfoField label="International Employee" value={personal.isInternationalEmployee ? "Yes" : "No"} editing={personalEdit} options={YES_NO_OPTIONS} placeholder="Select International Employee" onChange={(v) => setPersonal((p) => ({ ...p, isInternationalEmployee: v === "Yes" }))} />
          <ProfileInfoField label="Joining Date" value={personal.joiningDate} editing={personalEdit} onChange={(v) => setPersonal((p) => ({ ...p, joiningDate: v }))} type="date" />
        </div>
      </EditableSectionCard>

      {/* Address Details */}
      <EditableSectionCard
        title="Address Details"
        icon={MapPin}
        sectionId="profile-address"
        canEmployeeEdit={isEditable("profile-address")}
        hideAdminControls
        requestStatus={employee.editRequestStatus}
        isEditing={addressEdit}
        onEdit={() => setAddressEdit(true)}
        onCancel={() => {
          setAddr({
            current: employeeWithApiAddressDetails.currentAddress as EmployeeProfileAddress | undefined,
            permanent: employeeWithApiAddressDetails.permanentAddress as EmployeeProfileAddress | undefined,
            same: employeeWithApiAddressDetails.currentAddress?.isSameAsPermanent ?? false,
          });
          setAddressEdit(false);
        }}
        onSave={saveAddressDetails}
      >
        {addressLoading ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Loading saved address details...
          </div>
        ) : null}
        {addressError ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700">
            {addressError}
          </div>
        ) : null}
        {addressSaving ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Submitting address details...
          </div>
        ) : null}
        <div className="space-y-8">
          <div>
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-3">Current Address</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {(["addressLine1", "addressLine2", "landmark","country", "state","city","pincode", "startDate", "toDate"] as const).map((key) => (
                <ProfileInfoField
                  key={key}
                  label={key === "addressLine1" ? "Address Line 1" : key === "addressLine2" ? "Address Line 2" : key === "startDate" ? "StartDate" : key === "toDate" ? "ToDate" : key.charAt(0).toUpperCase() + key.slice(1)}
                  value={(addr.current?.[key] as string) || ""}
                  editing={addressEdit}
                  type={key.includes("Date") ? "date" : "text"}
                  options={
                    key === "country"
                      ? addressChoices.countries.map((choice) => ({ value: choice.label, label: choice.label }))
                      : key === "state"
                        ? addressChoices.states.map((choice) => ({ value: choice.label, label: choice.label }))
                        : key === "city"
                          ? addressChoices.cities.map((choice) => ({ value: choice.label, label: choice.label }))
                          : undefined
                  }
                  onChange={(v) =>
                    setAddr((a) => ({
                      ...a,
                      current: { ...(a.current || {}), [key]: v } as EmployeeProfileAddress,
                    }))
                  }
                />
              ))}
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
                        current: nextSame && a.permanent
                          ? { ...a.current, ...a.permanent, apiId: a.current?.apiId, isSameAsPermanent: true }
                          : { ...(a.current || {}), isSameAsPermanent: false } as EmployeeProfileAddress,
                      };
                    })
                  }
                />
                Same as permanent address
              </label>
            </div>
          </div>
          <div className="pt-6 border-t border-border">
            <h4 className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-3">Permanent Address</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {(["addressLine1", "addressLine2", "landmark", "city", "state", "country", "pincode", "startDate", "toDate"] as const).map((key) => (
                <ProfileInfoField
                  key={`p-${key}`}
                  label={key === "addressLine1" ? "Address Line 1" : key === "addressLine2" ? "Address Line 2" : key === "startDate" ? "StartDate" : key === "toDate" ? "ToDate" : key.charAt(0).toUpperCase() + key.slice(1)}
                  value={(addr.permanent?.[key] as string) || ""}
                  editing={addressEdit && !addr.same}
                  type={key.includes("Date") ? "date" : "text"}
                  options={
                    key === "country"
                      ? addressChoices.countries.map((choice) => ({ value: choice.label, label: choice.label }))
                      : key === "state"
                        ? addressChoices.states.map((choice) => ({ value: choice.label, label: choice.label }))
                        : key === "city"
                          ? addressChoices.cities.map((choice) => ({ value: choice.label, label: choice.label }))
                          : undefined
                  }
                  onChange={(v) =>
                    setAddr((a) => ({
                      ...a,
                      permanent: { ...(a.permanent || {}), [key]: v } as EmployeeProfileAddress,
                    }))
                  }
                />
              ))}
            </div>
          </div>
        </div>
      </EditableSectionCard>

      {/* Work Details */}
      <EditableSectionCard
        title="Work Details"
        icon={Briefcase}
        hideAdminControls
        requestStatus={employee.editRequestStatus}
        isEditing={false}
        onCancel={() => setWork(employeeWithApiWorkDetails)}
        onSave={() => undefined}
      >
        {workLoading ? (
          <div className="mb-4 rounded-lg border border-border bg-secondary/30 px-3 py-2 text-xs font-semibold text-muted-foreground">
            Loading saved work details...
          </div>
        ) : null}
        {workError ? (
          <div className="mb-4 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-700">
            {workError}
          </div>
        ) : null}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField label="Employee ID" value={work.employeeId} editing={false} />
          <ProfileInfoField label="Employee Category" value={work.employeeCategory || ""} editing={false} />
          <ProfileInfoField label="Department" value={work.department} editing={false} />
          <ProfileInfoField label="Team" value={work.team} editing={false} />
          <ProfileInfoField label="Designation" value={work.designation} editing={false} />
          <ProfileInfoField label="Shift" value={work.shift || ""} editing={false} />
          <ProfileInfoField label="Work Location" value={work.location} editing={false} />
          <ProfileInfoField label="Employee Type" value={work.employeeType || ""} editing={false} />
          <ProfileInfoField label="Confirmation Date" value={work.confirmationDate || ""} editing={false} />
          <ProfileInfoField label="Employment Status" value={work.employmentStatus || ""} editing={false} />
          <ProfileInfoField label="Probation Period" value={work.probationPeriod || ""} editing={false} />
          <ProfileInfoField label="Notice Period" value={work.noticePeriod || ""} editing={false} />
          <ProfileInfoField label="Reporting To" value={work.reportingTo || ""} editing={false} />
          <ProfileInfoField label="Functional Manager" value={work.functionalManager || ""} editing={false} />
          <ProfileInfoField label="HR Partner" value={work.hrPartner || ""} editing={false} />
        </div>
      </EditableSectionCard>

      {/* Language Details */}
      <EditableSectionCard
        title="Language Details"
        icon={Languages}
        sectionId="profile-languages"
        canEmployeeEdit={isEditable("profile-languages")}
        hideAdminControls
        requestStatus={employee.editRequestStatus}
        isEditing={langEdit}
        onAdd={addLanguageRow}
        addLabel="Add Language"
        onEdit={() => setLangEdit(true)}
        editDisabled={!savedLanguages.length}
        onCancel={() => { setLanguages(savedLanguages); setLangEdit(false); }}
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
            Submitting language details...
          </div>
        ) : null}
        {!languages.length && !langEdit ? (
          <EmptyStateCard
            icon={Languages}
            title="No languages recorded"
            description="Use Add Language to add your first language, or Edit after records exist."
          />
        ) : (
          <div className="space-y-4">
            {languages.map((row, idx) => (
              <div key={idx} className="rounded-xl border border-border bg-background p-4 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <ProfileInfoField label="Language Name" value={row.language} editing={langEdit} options={languageSelectOptions} onChange={(v) => setLanguages((rows) => rows.map((r, i) => (i === idx ? { ...r, language: v } : r)))} />
                  <div className="space-y-1.5">
                    <span className="block text-[11px] font-semibold text-muted-foreground tracking-wide">Proficiency Level</span>
                    {langEdit ? (
                      <select value={row.proficiency} onChange={(e) => setLanguages((rows) => rows.map((r, i) => (i === idx ? { ...r, proficiency: e.target.value } : r)))} className="w-full rounded-lg border border-border bg-secondary/40 px-3 py-2 text-sm font-medium">
                        <option value="">Select Proficiency</option>
                        {languageProficiencySelectOptions.map((p) => <option key={p.value} value={p.value}>{p.label}</option>)}
                      </select>
                    ) : (
                      <div className="rounded-lg border border-border bg-secondary/30 px-3 py-2 text-sm font-semibold">{row.proficiency || "—"}</div>
                    )}
                  </div>
                </div>
                <div className="flex flex-wrap gap-6">
                  {(["canRead", "canWrite", "canSpeak"] as const).map((key) => (
                    <label key={key} className="flex items-center gap-2 text-sm font-medium cursor-pointer">
                      <input type="checkbox" checked={row[key]} disabled={!langEdit} onChange={() => setLanguages((rows) => rows.map((r, i) => (i === idx ? { ...r, [key]: !r[key] } : r)))} />
                      {key.replace("can", "")}
                    </label>
                  ))}
                  {langEdit ? (
                    <button
                      type="button"
                      onClick={() => setLanguages((rows) => rows.filter((_, i) => i !== idx))}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 px-2.5 py-1 text-xs font-bold text-rose-600 hover:bg-rose-50"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                      Remove
                    </button>
                  ) : null}
                </div>
              </div>
            ))}
            {langEdit ? (
              <button
                type="button"
                onClick={addLanguageRow}
                className="inline-flex items-center gap-1.5 rounded-lg border border-dashed border-border px-3 py-2 text-xs font-bold text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
              >
                <Plus className="h-3.5 w-3.5" />
                Add another language
              </button>
            ) : null}
          </div>
        )}
      </EditableSectionCard>

      {/* Emergency & Medical */}
      <EditableSectionCard
        title="Emergency & Medical Information"
        icon={Heart}
        sectionId="profile-medical"
        canEmployeeEdit={isEditable("profile-medical")}
        hideAdminControls
        requestStatus={employee.editRequestStatus}
        isEditing={emEdit}
        onEdit={() => setEmEdit(true)}
        onCancel={() => { setEmergency(savedEmergency); setEmEdit(false); }}
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
            Submitting emergency and medical information...
          </div>
        ) : null}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <ProfileInfoField
            label="Emergency Contact Name"
            value={emergency.ec?.name || ""}
            editing={emEdit}
            onChange={(v) =>
              setEmergency((e) => ({
                ...e,
                ec: {
                  name: v,
                  relationship: e.ec?.relationship || "",
                  phone: e.ec?.phone || "",
                  alternatePhone: e.ec?.alternatePhone,
                },
              }))
            }
          />
          <ProfileInfoField
            label="Emergency Contact #"
            value={emergency.ec?.phone || ""}
            editing={emEdit}
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
            value={emergency.ec?.relationship || emergency.med?.relationship || ""}
            editing={emEdit}
            options={masterOptions(relationRecords)}
            onChange={(v) =>
              setEmergency((e) => ({
                ...e,
                ec: { name: e.ec?.name || "", phone: e.ec?.phone || "", relationship: v },
                med: { ...e.med, relationship: v },
              }))
            }
          />

          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3 text-sm font-semibold text-foreground">
              <input
                type="checkbox"
                checked={Boolean(emergency.med?.hasDisease)}
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
              Has Any Disease?
            </label>
            {emergency.med?.hasDisease ? (
              <ProfileInfoField
                label="Disease Details"
                value={emergency.med?.diseaseDetails || ""}
                editing={emEdit}
                type="textarea"
                placeholder="Enter disease name, description, medication, since when, etc."
                onChange={(v) => setEmergency((e) => ({ ...e, med: { ...e.med, diseaseDetails: v } }))}
              />
            ) : null}
          </div>

          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3 text-sm font-semibold text-foreground">
              <input
                type="checkbox"
                checked={Boolean(emergency.med?.hasSurgery)}
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
              Any Surgery or Operation Done?
            </label>
            {emergency.med?.hasSurgery ? (
              <ProfileInfoField
                label="Surgery / Operation Details"
                value={emergency.med?.surgeryDetails || ""}
                editing={emEdit}
                type="textarea"
                placeholder="Enter surgery name, hospital, date, recovery status, etc."
                onChange={(v) => setEmergency((e) => ({ ...e, med: { ...e.med, surgeryDetails: v } }))}
              />
            ) : null}
          </div>

          <div className="sm:col-span-2 lg:col-span-3">
            <label className="flex items-center gap-3 mb-3 text-sm font-semibold text-foreground">
              <input
                type="checkbox"
                checked={Boolean(emergency.med?.hasAllergies)}
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
              Any Allergies?
            </label>
            {emergency.med?.hasAllergies ? (
              <ProfileInfoField
                label="Allergy Details"
                value={emergency.med?.allergyDetails || ""}
                editing={emEdit}
                type="textarea"
                placeholder="Enter allergy type and description."
                onChange={(v) =>
                  setEmergency((e) => ({
                    ...e,
                    med: { ...e.med, allergyDetails: v, allergies: v },
                  }))
                }
              />
            ) : null}
          </div>
        </div>
      </EditableSectionCard>
    </div>
  );
}
