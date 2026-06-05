import { useQuery } from '@tanstack/react-query';
import api from '@api/client';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

export interface MasterRef {
  id: string;
  name: string;
  code: string;
}

export interface ContactInfo {
  id: string;
  personal_email: string;
  work_email: string;
  personal_mobile: string;
  work_mobile: string;
  home_phone: string;
  emergency_contact_name: string;
  emergency_contact_number: string;
  emergency_contact_relation_detail?: MasterRef;
}

export interface AddressInfo {
  id: string;
  address_type: 'CURRENT' | 'PERMANENT' | 'TEMPORARY';
  address_line1: string;
  address_line2: string;
  landmark: string;
  city: string | null;
  state: string | null;
  country: string | null;
  pincode: string;
}

export interface AssetInfo {
  id: string;
  asset_name: string;
  asset_code: string;
  asset_type: string;
  assigned_date: string | null;
  return_date: string | null;
  condition: string;
  remarks: string;
}

export interface InsuranceInfo {
  policy_number: string;
  provider: string;
  start_date: string | null;
  end_date: string | null;
  coverage_amount: string;
  nominee_name: string;
}

export interface EmploymentInfo {
  id: string;
  department_detail?: MasterRef;
  designation_detail?: MasterRef;
  employment_type_detail?: MasterRef;
  employee_category_detail?: MasterRef;
  company_location_detail?: MasterRef;
  date_of_joining: string;
  date_of_confirmation: string | null;
  probation_end_date: string | null;
  notice_period_days: number;
  shift?: string;
  date_of_exit: string | null;
}

export interface FamilyMemberInfo {
  id: string;
  name: string;
  relation_detail?: MasterRef;
  date_of_birth: string | null;
  gender: string | null;
  blood_group_detail?: MasterRef;
  is_dependent: boolean;
  is_emergency_contact: boolean;
  phone: string;
  occupation: string;
}

export interface EducationInfo {
  id: string;
  qualification_detail?: MasterRef;
  qualification_type_detail?: MasterRef;
  university_detail?: MasterRef;
  institution_name: string;
  specialization: string;
  year_of_passing: number | null;
  percentage_or_cgpa: string;
  grade: string;
}

export interface BankInfo {
  id: string;
  bank_detail?: MasterRef;
  branch_detail?: MasterRef;
  branch_name: string;
  account_number: string;
  ifsc_code: string;
  account_holder_name: string;
  account_type: string;
  is_primary: boolean;
}

export interface LanguageInfo {
  id: string;
  language_detail?: MasterRef;
  can_read: boolean;
  can_write: boolean;
  can_speak: boolean;
  proficiency_level: string;
}

export interface LifecycleEvent {
  id: string;
  event_type: string;
  event_date: string;
  effective_date: string;
  remarks: string;
  previous_value: string;
  new_value: string;
}

export interface NomineeInfo {
  id: string;
  name: string;
  relation_detail?: MasterRef;
  percentage: string;
  phone: string;
}

export interface ReportingInfo {
  id: string;
  reporting_manager_name: string;
  functional_manager_name: string;
  hr_partner_name: string;
  is_current: boolean;
}

export interface SystemAccessInfo {
  id: string;
  biometric_id: string;
  access_card_number: string;
  can_login: boolean;
  can_use_mobile_app: boolean;
  can_use_web_checkin: boolean;
}

export interface MyProfileData {
  id: string;
  employee_code: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;
  date_of_birth: string;
  profile_photo: string | null;
  gender_detail?: MasterRef;
  blood_group_detail?: MasterRef;
  marital_status_detail?: MasterRef;
  spouse_name: string | null;
  nationality_detail?: MasterRef;
  religion_detail?: MasterRef;
  caste_detail?: MasterRef;
  caste_category_detail?: MasterRef;
  residential_status_detail?: MasterRef;
  place_of_birth: string | null;
  father_name: string | null;
  is_physically_challenged: boolean;
  is_international_employee: boolean;
  identification_mark: string | null;
  status_detail?: MasterRef;
  pan_number: string;
  aadhaar_number: string;
  passport_number: string;
  uan_number: string;
  contact?: ContactInfo;
  addresses: AddressInfo[];
  employment?: EmploymentInfo;
  system_access?: SystemAccessInfo;
  lifecycle_events: LifecycleEvent[];
  current_reporting?: ReportingInfo;
  family_members: FamilyMemberInfo[];
  nominees: NomineeInfo[];
  education: EducationInfo[];
  languages: LanguageInfo[];
  bank_details: BankInfo[];
  assets: AssetInfo[];
  insurance?: InsuranceInfo;
}

/* ------------------------------------------------------------------ */
/*  Demo fallback data                                                 */
/* ------------------------------------------------------------------ */

const DEMO_PROFILE: MyProfileData = {
  id: 'emp-1',
  employee_code: 'EMP-0001',
  first_name: 'Aditi',
  middle_name: '',
  last_name: 'Mehra',
  full_name: 'Aditi Mehra',
  date_of_birth: '1994-09-08',
  profile_photo: null,
  gender_detail: { id: 'g1', name: 'Female', code: 'F' },
  blood_group_detail: { id: 'bg1', name: 'B+', code: 'B_POS' },
  marital_status_detail: { id: 'ms1', name: 'Single', code: 'SINGLE' },
  spouse_name: null,
  nationality_detail: { id: 'nat1', name: 'Indian', code: 'IN' },
  religion_detail: { id: 'rel1', name: 'Hindu', code: 'HINDU' },
  caste_detail: { id: 'cast1', name: 'Open', code: 'OPEN' },
  caste_category_detail: { id: 'cc1', name: 'General', code: 'GEN' },
  residential_status_detail: { id: 'rs1', name: 'Resident Indian', code: 'RI' },
  place_of_birth: 'Mumbai, Maharashtra',
  father_name: 'Suresh Mehra',
  is_physically_challenged: false,
  is_international_employee: false,
  identification_mark: 'Mole on left cheek',
  status_detail: { id: 'stat1', name: 'Active', code: 'ACTIVE' },
  pan_number: 'BXQPM1234A',
  aadhaar_number: '234512349876',
  passport_number: 'N1234567',
  uan_number: '100456789012',
  contact: {
    id: 'cont-1',
    personal_email: 'aditi.mehra@personal.com',
    work_email: 'aditi.mehra@ampcus.example',
    personal_mobile: '9876543210',
    work_mobile: '9123456789',
    home_phone: '02025123456',
    emergency_contact_name: 'Suresh Mehra',
    emergency_contact_number: '9011223344',
    emergency_contact_relation_detail: { id: 'rel-e1', name: 'Father', code: 'FATHER' },
  },
  addresses: [
    {
      id: 'addr-1',
      address_type: 'CURRENT',
      address_line1: '304, Aashirwad Apartments, Koregaon Park',
      address_line2: '',
      landmark: 'Near Osho Ashram',
      city: 'Pune',
      state: 'Maharashtra',
      country: 'India',
      pincode: '411001',
    },
    {
      id: 'addr-2',
      address_type: 'PERMANENT',
      address_line1: '12, Rajpath Society, Viman Nagar',
      address_line2: '',
      landmark: 'Near Airport',
      city: 'Pune',
      state: 'Maharashtra',
      country: 'India',
      pincode: '411014',
    },
  ],
  employment: {
    id: 'emp-info-1',
    department_detail: { id: 'dept-1', name: 'Human Resources', code: 'HR' },
    designation_detail: { id: 'desig-1', name: 'HR Manager', code: 'HRM' },
    employment_type_detail: { id: 'etype-1', name: 'Permanent', code: 'PERM' },
    employee_category_detail: { id: 'cat-1', name: 'Staff', code: 'STAFF' },
    company_location_detail: { id: 'loc-1', name: 'Pune Office', code: 'PUN-01' },
    date_of_joining: '2024-01-15',
    date_of_confirmation: '2024-07-15',
    probation_end_date: '2024-07-14',
    notice_period_days: 60,
    shift: '9-6',
    date_of_exit: null,
  },
  system_access: {
    id: 'sa-1',
    biometric_id: 'BIO-0042',
    access_card_number: 'ACC-1129',
    can_login: true,
    can_use_mobile_app: true,
    can_use_web_checkin: true,
  },
  lifecycle_events: [],
  current_reporting: {
    id: 'rpt-1',
    reporting_manager_name: 'Sakshi Deshpande',
    functional_manager_name: 'Vijay Kulkarni',
    hr_partner_name: 'Priya Nair',
    is_current: true,
  },
  family_members: [
    {
      id: 'fm-1',
      name: 'Suresh Mehra',
      relation_detail: { id: 'rel-1', name: 'Father', code: 'FATHER' },
      date_of_birth: '1965-04-10',
      gender: 'Male',
      blood_group_detail: { id: 'bg2', name: 'O+', code: 'O_POS' },
      is_dependent: true,
      is_emergency_contact: true,
      phone: '9011223344',
      occupation: 'Retired',
    },
    {
      id: 'fm-2',
      name: 'Sunita Mehra',
      relation_detail: { id: 'rel-2', name: 'Mother', code: 'MOTHER' },
      date_of_birth: '1968-11-22',
      gender: 'Female',
      blood_group_detail: { id: 'bg3', name: 'A+', code: 'A_POS' },
      is_dependent: true,
      is_emergency_contact: false,
      phone: '9022334455',
      occupation: 'Homemaker',
    },
  ],
  nominees: [
    {
      id: 'nom-1',
      name: 'Suresh Mehra',
      relation_detail: { id: 'rel-1', name: 'Father', code: 'FATHER' },
      percentage: '60',
      phone: '9011223344',
    },
    {
      id: 'nom-2',
      name: 'Sunita Mehra',
      relation_detail: { id: 'rel-2', name: 'Mother', code: 'MOTHER' },
      percentage: '40',
      phone: '9022334455',
    },
  ],
  education: [
    {
      id: 'edu-1',
      qualification_detail: { id: 'q1', name: 'Bachelor of Management Studies', code: 'BMS' },
      qualification_type_detail: { id: 'qt1', name: 'Graduation', code: 'GRAD' },
      university_detail: { id: 'uni1', name: 'Savitribai Phule Pune University', code: 'SPPU' },
      institution_name: 'BVIMSR, Pune',
      specialization: 'Human Resource Management',
      year_of_passing: 2016,
      percentage_or_cgpa: '72.4%',
      grade: 'A',
    },
    {
      id: 'edu-2',
      qualification_detail: { id: 'q2', name: 'Master of Business Administration', code: 'MBA' },
      qualification_type_detail: { id: 'qt2', name: 'Post Graduation', code: 'PG' },
      university_detail: { id: 'uni2', name: 'Symbiosis International University', code: 'SIU' },
      institution_name: 'SIBM, Pune',
      specialization: 'Human Resources & Organizational Behaviour',
      year_of_passing: 2018,
      percentage_or_cgpa: '8.4 CGPA',
      grade: 'A+',
    },
  ],
  languages: [
    {
      id: 'lang-1',
      language_detail: { id: 'l1', name: 'Hindi', code: 'HI' },
      can_read: true,
      can_write: true,
      can_speak: true,
      proficiency_level: 'NATIVE',
    },
    {
      id: 'lang-2',
      language_detail: { id: 'l2', name: 'English', code: 'EN' },
      can_read: true,
      can_write: true,
      can_speak: true,
      proficiency_level: 'ADVANCED',
    },
    {
      id: 'lang-3',
      language_detail: { id: 'l3', name: 'Marathi', code: 'MR' },
      can_read: true,
      can_write: false,
      can_speak: true,
      proficiency_level: 'INTERMEDIATE',
    },
  ],
  bank_details: [
    {
      id: 'bank-1',
      bank_detail: { id: 'b1', name: 'HDFC Bank', code: 'HDFC' },
      branch_detail: { id: 'br1', name: 'Koregaon Park Branch', code: 'HDFC-KP-PUNE' },
      branch_name: 'Koregaon Park Branch',
      account_number: '50100123456789',
      ifsc_code: 'HDFC0001234',
      account_holder_name: 'Aditi Mehra',
      account_type: 'SAVINGS',
      is_primary: true,
    },
  ],
  assets: [
    {
      id: 'asset-1',
      asset_name: 'MacBook Pro 14"',
      asset_code: 'MBP-1482',
      asset_type: 'Laptop',
      assigned_date: '2024-01-20',
      return_date: null,
      condition: 'Good',
      remarks: 'Charger included',
    },
    {
      id: 'asset-2',
      asset_name: 'Dell 27" Monitor',
      asset_code: 'MON-0214',
      asset_type: 'Monitor',
      assigned_date: '2024-01-20',
      return_date: null,
      condition: 'Good',
      remarks: '',
    },
  ],
};

/* ------------------------------------------------------------------ */
/*  Hook                                                               */
/* ------------------------------------------------------------------ */

async function fetchMyProfile(): Promise<MyProfileData> {
  try {
    const response = await api.get('/me/');
    const data = response.data?.data ?? response.data;
    if (data && data.id) return data as MyProfileData;
  } catch {
    // fallback to demo data
  }
  return DEMO_PROFILE;
}

export function useMyProfile() {
  return useQuery({
    queryKey: ['my-profile'],
    queryFn: fetchMyProfile,
    staleTime: 5 * 60_000,
  });
}