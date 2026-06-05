/**
 * Employee Basic Information Form - Modern Enterprise HRMS
 * Complete form rebuild with React Hook Form + Zod + Tailwind + Shadcn UI
 */

import { useState, useEffect, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router';
import { motion } from 'framer-motion';
import {
  ChevronRight, ArrowLeft, Save, FileText, Briefcase, Clock,
  Calendar, User, Shield, Upload, X, AlertCircle,
  Building2, Loader2,
  HelpCircle, Trash2, LayoutDashboard, FileCheck, GraduationCap, Mail, Phone, Plus
} from 'lucide-react';
import { toast } from 'sonner';
import { EmployeeFormProvider } from './employee-details/EmployeeFormContext';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Checkbox } from '@/app/components/ui/checkbox';
import { Textarea } from '@/app/components/ui/textarea';
import { Badge } from '@/app/components/ui/badge';
import { MasterSelect } from '@/app/components/ui/MasterSelect';
import { FormSection } from '@/app/components/ui/FormSection';
import { SearchableSelect } from '@/app/components/ui/SearchableSelect';
import { fetchManagers, type Manager } from '@/api/managersClient';


// ═══════════════════════════════════════════════════════════
// VALIDATION SCHEMA
// ═══════════════════════════════════════════════════════════

const validateAadhaar = (value: string) => /^\d{12}$/.test(value.replace(/\s/g, ''));
const validatePAN = (value: string) => /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(value);
const validatePhone = (value: string) => {
  const cleanValue = value.replace(/\D/g, '');
  return cleanValue.length >= 10 && cleanValue.length <= 15;
};

const formSchema = z.object({
  // BASIC INFORMATION
  salutation: z.string().min(1, 'Required'),
  employeeNumberSeries: z.string().min(1, 'Required'),
  employeeId: z.string().min(1, 'Required'),
  firstName: z.string().min(2, 'At least 2 characters'),
  middleName: z.string().optional(),
  lastName: z.string().min(2, 'At least 2 characters'),
  dateOfBirth: z.string().min(1, 'Required'),
  gender: z.string().min(1, 'Required'),
  maritalStatus: z.string().min(1, 'Required'),
  aadhaarNumber: z.string().refine(validateAadhaar, 'Must be 12 digits'),
  panNumber: z.string().refine(validatePAN, 'Invalid PAN format'),
  bloodGroup: z.string().min(1, 'Required'),
  nationality: z.string().min(1, 'Required'),
  personalEmail: z.string().email('Invalid email'),
  personalMobileNumber: z.string().refine(validatePhone, 'Invalid phone number'),
  emergencyContactName: z.string().min(2, 'At least 2 characters'),
  emergencyContactNumber: z.string().refine(validatePhone, 'Invalid phone number'),
  currentAddress: z.string().min(5, 'At least 5 characters'),
  permanentAddress: z.string().optional(),
  sameAsCurrent: z.boolean(),
  fathersName: z.string().optional(),
  mothersName: z.string().optional(),
  spouseName: z.string().optional(),
  religion: z.string().optional(),
  languagesKnown: z.array(z.string()).optional(),

  // JOB DETAILS
  reportingManagerId: z.string().min(1, 'Required'),
  referredById: z.string().optional(),
  employeeStatus: z.string().min(1, 'Required'),
  dateOfJoining: z.string().min(1, 'Required'),
  workLocationId: z.string().min(1, 'Required'),
  employeeCategory: z.string().min(1, 'Required'),
  employeeType: z.string().optional(),
  probationPeriod: z.coerce.number().optional(),
  probationPeriodUnit: z.enum(['days', 'months']),
  confirmationDate: z.string().optional(),
  officialEmail: z.string().email('Invalid email'),
  officialMobileNumber: z.string().refine(validatePhone, 'Invalid phone number'),
  departmentId: z.string().optional(),
  designationId: z.string().optional(),
  branchId: z.string().optional(),

  // ATTENDANCE SETTINGS
  attendanceSchemeId: z.string().min(1, 'Required'),
  shiftAssignmentId: z.string().optional(),
  attendanceTrackingType: z.enum(['biometrics', 'mobile_gps', 'web_login', 'hybrid']),
  deviceId: z.string().optional(),

  // PAYROLL & STATUTORY
  // uanNumber: z.string().optional(),
  // esicNumber: z.string().optional(),
  // disabilityStatus: z.boolean(),
  // costCenterId: z.string().optional(),
  // gradeId: z.string().optional(),

  // MISC
  allowEmployeeToFillInfo: z.boolean(),
  passportNumber: z.string().optional(),
  passportExpiryDate: z.string().optional(),
  employeeTags: z.array(z.string()).optional(),
  hrNotes: z.string().max(1000, 'Max 1000 characters').optional(),
  internalNotes: z.string().max(1000, 'Max 1000 characters').optional(),

  // EDUCATION
  educationDetails: z.array(z.object({
    educationLevel: z.string(),
    qualification: z.string(),
    specialization: z.string(),
    institutionName: z.string(),
    boardUniversity: z.string(),
    startDate: z.string(),
    endDate: z.string(),
    grade: z.string(),
    modeOfStudy: z.string(),
    country: z.string(),
    certificateUrl: z.string().optional(),
  })).optional(),

  // BACKGROUND CHECK
  backgroundCheck: z.object({
    verificationStatus: z.string().optional(),
    completedOn: z.string().optional(),
    agencyName: z.string().optional(),
    remarks: z.string().optional(),
    reportUrl: z.string().optional(),
    verifiedBy: z.string().optional(),
    referenceNumber: z.string().optional(),
  }).optional(),
}).refine(
  (data) => {
    if (!data.dateOfBirth || !data.dateOfJoining) return true;
    return new Date(data.dateOfJoining) >= new Date(data.dateOfBirth);
  },
  { message: 'DOJ cannot be before DOB', path: ['dateOfJoining'] }
).refine(
  (data) => !data.sameAsCurrent || (data.permanentAddress === data.currentAddress || !data.permanentAddress),
  { message: 'Required if different from current', path: ['permanentAddress'] }
);

type FormData = z.infer<typeof formSchema>;

// ═══════════════════════════════════════════════════════════
// OPTIONS DATA
// ═══════════════════════════════════════════════════════════

const TRACKING_OPTIONS = [
  { value: 'biometrics', label: 'Biometrics' },
  { value: 'mobile_gps', label: 'Mobile GPS' },
  { value: 'web_login', label: 'Web Login' },
  { value: 'hybrid', label: 'Hybrid' },
];

// ═══════════════════════════════════════════════════════════
// FORM UI COMPONENTS
// ═══════════════════════════════════════════════════════════

function SectionHeader({ title, icon: Icon, description }: { title: string; icon?: any; description?: string }) {
  return (
    <div className="flex flex-col gap-1 mb-6">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className="p-2 rounded-xl bg-primary/10 text-primary">
            <Icon size={18} strokeWidth={2.5} />
          </div>
        )}
        <h2 className="text-lg font-bold text-foreground tracking-tight">{title}</h2>
      </div>
      {description && <p className="text-sm text-muted-foreground ml-11">{description}</p>}
      <div className="h-px w-full bg-gradient-to-r from-border via-border/50 to-transparent mt-2" />
    </div>
  );
}

interface FormFieldProps {
  label: string;
  required?: boolean;
  error?: string;
  hint?: string;
  children: React.ReactNode;
  className?: string;
}

function FormField({ label, required, error, hint, children, className }: FormFieldProps) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      <Label className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest mb-0.5 ml-0.5">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <div className="relative group">
        {children}
        {error && (
          <div className="flex items-center gap-1.5 mt-1.5 text-[11px] text-red-500 font-bold animate-in slide-in-from-top-1 duration-200">
            <AlertCircle size={12} strokeWidth={3} />
            {error}
          </div>
        )}
        {!error && hint && <p className="text-[10px] text-muted-foreground/80 font-medium mt-1 ml-0.5">{hint}</p>}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// PHOTO UPLOAD COMPONENT
// ═══════════════════════════════════════════════════════════

interface PhotoUploadProps {
  onChange: (file: File | null) => void;
  preview?: string;
}

function PhotoUpload({ onChange, preview }: PhotoUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [localPreview, setLocalPreview] = useState<string>(preview || '');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      processFile(file);
    }
  };

  const processFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setLocalPreview(result);
      onChange(file);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="flex flex-col gap-3">
      {localPreview ? (
        <div className="relative w-20 h-20 rounded-lg overflow-hidden border border-border bg-secondary">
          <img src={localPreview} alt="Profile" className="w-full h-full object-cover" />
          <button
            type="button"
            onClick={() => {
              setLocalPreview('');
              onChange(null);
              if (fileInputRef.current) fileInputRef.current.value = '';
            }}
            className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-1 shadow-md hover:bg-red-600 transition"
          >
            <X size={12} />
          </button>
        </div>
      ) : (
        <div
          onDragOver={() => setIsDragging(true)}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
            isDragging
              ? 'border-primary bg-primary/5'
              : 'border-border hover:border-muted-foreground/50 hover:bg-secondary/30'
          }`}
        >
          <div className="flex flex-col items-center gap-2">
            <Upload size={20} className="text-muted-foreground" />
            <p className="text-xs font-medium">Drag & drop or click to upload</p>
            <p className="text-[10px] text-muted-foreground">JPG, PNG (Max 5MB)</p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file && file.size <= 5242880) processFile(file);
            }}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </div>
      )}
    </div>
  );
}

// ═══════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════

export default function AddEmployeeBasicForm() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDrafting, setIsDrafting] = useState(false);
  const [finalConfirmChecked, setFinalConfirmChecked] = useState(false);
  const [finalSubmitted, setFinalSubmitted] = useState(false);
  const [managers, setManagers] = useState<Manager[]>([]);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema as any),
    defaultValues: {
      salutation: '',
      employeeNumberSeries: '',
      employeeId: '',
      firstName: '',
      middleName: '',
      lastName: '',
      dateOfBirth: '',
      gender: '',
      maritalStatus: '',
      aadhaarNumber: '',
      panNumber: '',
      bloodGroup: '',
      nationality: '',
      personalEmail: '',
      personalMobileNumber: '',
      emergencyContactName: '',
      emergencyContactNumber: '',
      currentAddress: '',
      sameAsCurrent: true,
      employeeStatus: '',
      employeeCategory: '',
      employeeType: '',
      attendanceSchemeId: '',
      attendanceTrackingType: 'biometrics',
      allowEmployeeToFillInfo: false,
      probationPeriod: 0,
      probationPeriodUnit: 'months',
      educationDetails: [],
      backgroundCheck: {
        verificationStatus: '',
      }
    }
  });

  const { watch, setValue, formState: { errors } } = form;
  const sameAsCurrent = watch('sameAsCurrent');

  const onSubmit = async (data: FormData) => {
    setFinalSubmitted(true);
    setIsSubmitting(true);
    try {
      console.log('Form Submitted:', data);
      toast.success('Employee registration initiated successfully!');
      setTimeout(() => navigate('/admin/letters-policies/generate-letter'), 2000);
    } catch (error) {
      toast.error('Failed to submit form. Please check all fields.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDraftSave = () => {
    setIsDrafting(true);
    setTimeout(() => {
      setIsDrafting(false);
      toast.success('Draft saved successfully!');
    }, 1000);
  };

  const handleCancel = () => navigate('/admin/letters-policies/generate-letter');

  const [activeSection, setActiveSection] = useState('basic-info');

  const navItems = [
    { id: 'basic-info', label: 'Basic Information', icon: User },
    { id: 'job-details', label: 'Job Details', icon: Briefcase },
    { id: 'attendance-settings', label: 'Attendance Settings', icon: Clock },
    // { id: 'payroll-info', label: 'Payroll Information', icon: CreditCard },
    { id: 'leave-config', label: 'Leave Configuration', icon: Calendar },
    { id: 'documents', label: 'Documents', icon: Upload },
    { id: 'education-details', label: 'Education Details', icon: GraduationCap },
    { id: 'background-check', label: 'Background Check', icon: Shield },
    { id: 'account-access', label: 'Account Access', icon: LayoutDashboard },
  ];
  console.log("🔥 AddEmployeeBasicForm RENDEREDggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg");

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveSection(entry.target.id);
          }
        });
      },
      { threshold: 0.5, rootMargin: '-100px 0px -20% 0px' }
    );

    navItems.forEach((item) => {
      const el = document.getElementById(item.id);
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [navItems]);

  // Fetch managers for the reporting manager dropdown
  useEffect(() => {
    console.log("useEffect triggered");
  const loadManagers = async () => {
    try {
      const managersData = await fetchManagers();

      console.log("Managers API response:", managersData);

      setManagers(managersData);
    } catch (error) {
      console.error("Failed to load managers:", error);
      toast.error("Failed to load managers");
    }
  };

  loadManagers();
}, []);

  const scrollToSection = (id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <EmployeeFormProvider value={{ finalSubmitted }}>
    <div className="min-h-screen bg-[#F8FAFC] dark:bg-[#0B0F19] pb-32">
      {/* Top Header */}
      <div className="sticky top-0 z-50 bg-white/90 dark:bg-gray-950/90 backdrop-blur-2xl border-b border-border/40 shadow-[0_1px_3px_rgba(0,0,0,0.02)] transition-all duration-300">
        <div className="max-w-[1600px] mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              type="button"
              onClick={handleCancel}
              className="w-10 h-10 flex items-center justify-center rounded-xl bg-white dark:bg-gray-900 border border-border/50 hover:border-primary/50 hover:bg-primary/5 transition-all group"
            >
              <ArrowLeft size={18} className="text-muted-foreground group-hover:text-primary transition-colors" />
            </button>
            <div>
              <h1 className="text-xl font-black text-foreground tracking-tight">Add New Employee</h1>
              <div className="flex items-center gap-2 mt-0.5">
                <Badge variant="outline" className="bg-primary/5 text-primary border-primary/20 font-bold px-2 py-0 h-5 text-[10px] uppercase">Master Config Enabled</Badge>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleDraftSave}
              disabled={isDrafting}
              className="h-10 px-5 rounded-xl font-bold text-xs uppercase tracking-wider border-border/50 hover:bg-secondary"
            >
              {isDrafting ? <Loader2 size={14} className="animate-spin mr-2" /> : <Save size={14} className="mr-2" />}
              Save Draft
            </Button>
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 text-sm text-muted-foreground">
                <input type="checkbox" className="w-4 h-4" checked={finalConfirmChecked} onChange={(e) => setFinalConfirmChecked(e.target.checked)} disabled={finalSubmitted} />
                <span>I understand I cannot directly edit after final submission.</span>
              </label>

              <Button 
                type="submit" 
                disabled={isSubmitting || !finalConfirmChecked || finalSubmitted}
                form="add-employee-form"
                onClick={() => {
                  if (finalConfirmChecked && !finalSubmitted) setFinalSubmitted(true);
                }}
                className="h-10 px-6 rounded-xl font-black text-xs uppercase tracking-widest bg-primary text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? <Loader2 size={16} className="animate-spin mr-2" /> : <ChevronRight size={16} className="mr-2" />}
                {finalSubmitted ? 'Submitted' : 'Final Submit'}
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1600px] mx-auto px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* LEFT SIDEBAR - STICKY */}
          <aside className="lg:col-span-3 sticky top-28 space-y-2 hidden lg:block">
            <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-[2rem] border border-border/40 p-4 shadow-sm">
              <p className="px-4 py-2 text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground mb-2">Form Sections</p>
              <nav className="space-y-1">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeSection === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => scrollToSection(item.id)}
                      className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-all duration-300 group ${
                        isActive 
                          ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20 font-black' 
                          : 'hover:bg-primary/5 text-muted-foreground hover:text-primary font-bold'
                      }`}
                    >
                      <Icon size={18} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'animate-in zoom-in-50 duration-500' : 'group-hover:scale-110 transition-transform'} />
                      <span className="text-xs uppercase tracking-wider">{item.label}</span>
                      {isActive && <motion.div layoutId="active-indicator" className="ml-auto w-1.5 h-1.5 rounded-full bg-white" />}
                    </button>
                  );
                })}
              </nav>
            </div>

            <div className="p-6 bg-gradient-to-br from-primary/10 to-indigo-500/10 rounded-[2rem] border border-primary/20">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center text-white shadow-lg">
                  <HelpCircle size={20} />
                </div>
                <p className="text-xs font-black uppercase tracking-widest text-primary">Need Help?</p>
              </div>
              <p className="text-[11px] text-muted-foreground font-medium leading-relaxed">
                If you are missing a master value, contact your system administrator to add it to the Masters Management console.
              </p>
            </div>
          </aside>

          {/* MAIN FORM CONTENT */}
          <form id="add-employee-form" onSubmit={form.handleSubmit(onSubmit as any)} className="lg:col-span-9 space-y-12">
            
            {/* 1. BASIC INFORMATION */}
            <FormSection id="basic-info">
              <SectionHeader 
                title="Basic Information " 
                icon={User} 
                description="Primary identity and personal contact details of the employee"
              />

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-4">
                <div className="sm:col-span-2 grid grid-cols-1 sm:grid-cols-4 gap-6 items-start">
                  <FormField label="Salutation" required error={errors.salutation?.message}>
                    <MasterSelect 
                      masterName="Salutation" 
                      value={watch('salutation')} 
                      onChange={(v) => setValue('salutation', v)} 
                    />
                  </FormField>
                  <div className="sm:col-span-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <FormField label="First Name nnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn" required error={errors.firstName?.message}>
                      <Input placeholder="E.g. John" {...form.register('firstName')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                    </FormField>
                    <FormField label="Middle Name">
                      <Input placeholder="Optional"  {...form.register('middleName')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                    </FormField>
                    <FormField label="Last Name" required error={errors.lastName?.message}>
                      <Input placeholder="E.g. Doe" {...form.register('lastName')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                    </FormField>
                  </div>
                </div>

                <FormField label="Employee Number Series" required error={errors.employeeNumberSeries?.message}>
                  <MasterSelect 
                    masterName="EmployeeNumberSeries" 
                    value={watch('employeeNumberSeries')} 
                    onChange={(v) => setValue('employeeNumberSeries', v)} 
                  />
                </FormField>

                <FormField label="Employee ID" required hint="Admin editable only" error={errors.employeeId?.message}>
                  <Input
                    {...form.register('employeeId')}
                    rightIcon={<Shield size={14} />}
                    className="h-11 bg-slate-50/50 dark:bg-gray-800/50 border-border/50 focus:border-primary/50 rounded-xl text-sm font-bold tracking-tight transition-all"
                  />
                </FormField>

                <div className="sm:col-span-2 py-4">
                  <FormField label="Profile Photo" hint="Drag and drop your photo here">
                    <div className="flex items-center gap-6 p-4 rounded-[1.5rem] bg-slate-50 dark:bg-slate-900/50 border-2 border-dashed border-slate-200 dark:border-slate-800 group hover:border-primary/50 transition-all duration-300">
                      <PhotoUpload onChange={() => {}} preview={undefined} />
                      <div className="flex-1">
                        <p className="text-xs text-muted-foreground leading-relaxed">
                          Upload a professional headshot. <br /> 
                          <span className="font-bold text-foreground">PNG, JPG up to 5MB.</span>
                        </p>
                      </div>
                    </div>
                  </FormField>
                </div>

                <FormField label="Date of Birth" required error={errors.dateOfBirth?.message}>
                  <Input
                    type="date"
                    {...form.register('dateOfBirth')}
                    rightIcon={<Calendar size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>

                <FormField label="Gender" required error={errors.gender?.message}>
                  <MasterSelect 
                    masterName="Gender" 
                    value={watch('gender')} 
                    onChange={(v) => setValue('gender', v)} 
                  />
                </FormField>

                <FormField label="Marital Status" required error={errors.maritalStatus?.message}>
                  <MasterSelect 
                    masterName="MaritalStatus" 
                    value={watch('maritalStatus')} 
                    onChange={(v) => setValue('maritalStatus', v)} 
                  />
                </FormField>

                <FormField label="Blood Group" required error={errors.bloodGroup?.message}>
                  <MasterSelect 
                    masterName="BloodGroup" 
                    value={watch('bloodGroup')} 
                    onChange={(v) => setValue('bloodGroup', v)} 
                  />
                </FormField>

                <FormField label="Nationality" required error={errors.nationality?.message}>
                  <MasterSelect 
                    masterName="Nationality" 
                    value={watch('nationality')} 
                    onChange={(v) => setValue('nationality', v)} 
                  />
                </FormField>

                <FormField label="Religion">
                  <MasterSelect 
                    masterName="Religion" 
                    value={watch('religion') || ''} 
                    onChange={(v) => setValue('religion', v)} 
                  />
                </FormField>

                <FormField label="Personal Email" required error={errors.personalEmail?.message}>
                  <Input
                    type="email"
                    placeholder="personal@email.com"
                    {...form.register('personalEmail')}
                    leftIcon={<Mail size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>

                <FormField label="Personal Mobile" required error={errors.personalMobileNumber?.message}>
                  <Input
                    placeholder="+91 00000 00000"
                    {...form.register('personalMobileNumber')}
                    leftIcon={<Phone size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>

                <div className="sm:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4 p-5 bg-blue-50/50 dark:bg-blue-900/10 rounded-2xl border border-blue-100 dark:border-blue-800">
                  <FormField label="Emergency Contact Name" required error={errors.emergencyContactName?.message}>
                      <Input placeholder="Full Name" {...form.register('emergencyContactName')} leftIcon={<User size={14} />} className="h-10 bg-white dark:bg-gray-800 rounded-lg text-sm border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                  </FormField>
                  <FormField label="Emergency Number" required error={errors.emergencyContactNumber?.message}>
                      <Input placeholder="+91..." {...form.register('emergencyContactNumber')} leftIcon={<Phone size={14} />} className="h-10 bg-white dark:bg-gray-800 rounded-lg text-sm border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                  </FormField>
                </div>

                <FormField label="Current Address" required className="sm:col-span-2" error={errors.currentAddress?.message}>
                  <Textarea {...form.register('currentAddress')} className="bg-white dark:bg-gray-800 rounded-xl min-h-[100px] text-sm p-4 resize-none border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                </FormField>

                <div className="sm:col-span-2 flex items-center gap-3 ml-1">
                  <Checkbox 
                    id="same-address"
                    checked={sameAsCurrent}
                    onCheckedChange={(v) => setValue('sameAsCurrent', !!v)}
                    className="w-5 h-5 rounded-md border-2 border-primary/20 data-[state=checked]:bg-primary data-[state=checked]:border-primary transition-all"
                  />
                  <label htmlFor="same-address" className="text-sm font-bold text-foreground cursor-pointer select-none">
                    Permanent address is same as current address
                  </label>
                </div>

                {!sameAsCurrent && (
                  <FormField label="Permanent Address" className="sm:col-span-2" error={errors.permanentAddress?.message}>
                    <Textarea {...form.register('permanentAddress')} className="bg-white dark:bg-gray-800 rounded-xl min-h-[100px] text-sm p-4 resize-none border-border/40 focus:ring-4 focus:ring-primary/10 transition-all animate-in fade-in zoom-in-95 duration-300" />
                  </FormField>
                )}

                <div className="sm:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-6 pt-4">
                  <FormField label="Father's Name">
                    <Input {...form.register('fathersName')} leftIcon={<User size={14} />} className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm border-border/40" />
                  </FormField>
                  <FormField label="Mother's Name">
                    <Input {...form.register('mothersName')} leftIcon={<User size={14} />} className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm border-border/40" />
                  </FormField>
                  <FormField label="Spouse Name">
                    <Input {...form.register('spouseName')} leftIcon={<User size={14} />} className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm border-border/40" />
                  </FormField>
                </div>
              </div>
            </FormSection>

            {/* 2. JOB DETAILS */}
            <FormSection id="job-details">
              <SectionHeader title="Job Details" icon={Briefcase} description="Employment specifics, organizational structure and location" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <FormField label="Department" error={errors.departmentId?.message}>
                  <MasterSelect masterName="Department" value={watch('departmentId') || ''} onChange={(v) => setValue('departmentId', v)} />
                </FormField>
                <FormField label="Designation" error={errors.designationId?.message}>
                  <MasterSelect masterName="Designation" value={watch('designationId') || ''} onChange={(v) => setValue('designationId', v)} />
                </FormField>
                <FormField label="Branch" error={errors.branchId?.message}>
                  <MasterSelect masterName="Branch" value={watch('branchId') || ''} onChange={(v) => setValue('branchId', v)} />
                </FormField>
                <FormField label="Work Location" required error={errors.workLocationId?.message}>
                  <MasterSelect masterName="OfficeLocation" value={watch('workLocationId')} onChange={(v) => setValue('workLocationId', v)} />
                </FormField>
                <FormField label="Employee Status" required>
                  <MasterSelect masterName="EmployeeStatus" value={watch('employeeStatus')} onChange={(v) => setValue('employeeStatus', v)} />
                </FormField>
                <FormField label="Employee Category" required>
                  <MasterSelect masterName="EmployeeCategory" value={watch('employeeCategory')} onChange={(v) => setValue('employeeCategory', v)} />
                </FormField>
                <FormField label="Employee Type">
                  <MasterSelect masterName="EmployeeType" value={watch('employeeType') || ''} onChange={(v) => setValue('employeeType', v)} />
                </FormField>
                <FormField label="Reporting Manager" required error={errors.reportingManagerId?.message}>
                  <SearchableSelect
                    value={watch('reportingManagerId')}
                    onChange={(v) => setValue('reportingManagerId', v)}
                    options={managers.map(m => ({ value: m.id, label: `${m.name}${m.designation ? ` - ${m.designation}` : ''}` }))}
                  />
                </FormField>
                <FormField label="Referred By">
                  <SearchableSelect
                    value={watch('referredById') || ''}
                    onChange={(v) => setValue('referredById', v)}
                    options={managers.map(m => ({ value: m.id, label: `${m.name}${m.designation ? ` - ${m.designation}` : ''}` }))}
                  />
                </FormField>
                <FormField label="Date of Joining" required error={errors.dateOfJoining?.message}>
                  <Input
                    type="date"
                    {...form.register('dateOfJoining')}
                    rightIcon={<Calendar size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-medium border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>
                <div className="flex items-end gap-3">
                  <FormField label="Probation Period" className="flex-1">
                    <Input type="number" {...form.register('probationPeriod')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-bold border-border/40 focus:ring-4 focus:ring-primary/10 transition-all" />
                  </FormField>
                  <div className="w-24 pb-0.5">
                    <SearchableSelect
                      value={watch('probationPeriodUnit')}
                      onChange={(v) => setValue('probationPeriodUnit', v as any)}
                      options={[{ value: 'days', label: 'Days' }, { value: 'months', label: 'Months' }]}
                      searchable={false}
                    />
                  </div>
                </div>
                <FormField label="Official Email" required error={errors.officialEmail?.message}>
                  <Input
                    type="email"
                    placeholder="official@company.com"
                    {...form.register('officialEmail')}
                    leftIcon={<Building2 size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-bold border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>
                <FormField label="Official Mobile" required error={errors.officialMobileNumber?.message}>
                  <Input
                    placeholder="+91 00000 00000"
                    {...form.register('officialMobileNumber')}
                    leftIcon={<Phone size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-bold border-border/40 focus:ring-4 focus:ring-primary/10 transition-all"
                  />
                </FormField>
              </div>
            </FormSection>

            {/* 3. ATTENDANCE SETTINGS */}
            <FormSection id="attendance-settings">
              <SectionHeader title="Attendance Settings" icon={Clock} description="Configure attendance scheme, shift and tracking methods" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <FormField label="Attendance Scheme" required error={errors.attendanceSchemeId?.message}>
                  <MasterSelect masterName="AttendanceScheme" value={watch('attendanceSchemeId')} onChange={(v) => setValue('attendanceSchemeId', v)} />
                </FormField>
                <FormField label="Shift Assignment">
                  <MasterSelect masterName="Shift" value={watch('shiftAssignmentId') || ''} onChange={(v) => setValue('shiftAssignmentId', v)} />
                </FormField>
                <FormField label="Attendance Tracking">
                  <SearchableSelect
                    value={watch('attendanceTrackingType')}
                    onChange={(v) => setValue('attendanceTrackingType', v as any)}
                    options={TRACKING_OPTIONS}
                  />
                </FormField>
                <FormField label="Device / Biometric ID">
                  <Input {...form.register('deviceId')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-mono border-border/40" />
                </FormField>
              </div>
            </FormSection>

            {/* 4. PAYROLL INFORMATION
            <FormSection id="payroll-info">
              <SectionHeader title="Payroll & Statutory" icon={CreditCard} description="Taxation, statutory compliance and salary structure" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <FormField label="UAN Number">
                  <Input placeholder="12 Digits" {...form.register('uanNumber')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-mono border-border/40" />
                </FormField>
                <FormField label="ESIC Number">
                  <Input placeholder="17 Digits" {...form.register('esicNumber')} className="h-11 bg-white dark:bg-gray-800 rounded-xl px-4 text-sm font-mono border-border/40" />
                </FormField>
                <FormField label="Cost Center">
                  <MasterSelect masterName="CostCenter" value={watch('costCenterId') || ''} onChange={(v) => setValue('costCenterId', v)} />
                </FormField>
                <FormField label="Employee Grade">
                  <MasterSelect masterName="Grade" value={watch('gradeId') || ''} onChange={(v) => setValue('gradeId', v)} />
                </FormField>
                <div className="sm:col-span-2 py-2 flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900 border border-border/40 rounded-2xl">
                  <div className="flex flex-col">
                    <span className="text-xs font-bold text-foreground uppercase tracking-widest">Disability Status</span>
                    <span className="text-[10px] text-muted-foreground font-medium">Does the employee have any physical disability?</span>
                  </div>
                  <Checkbox 
                    checked={watch('disabilityStatus')} 
                    onCheckedChange={(v) => setValue('disabilityStatus', !!v)}
                    className="w-6 h-6 rounded-lg"
                  />
                </div>
              </div>
            </FormSection> */}

            {/* 5. LEAVE CONFIGURATION */}
            <FormSection id="leave-config">
              <SectionHeader title="Leave Configuration" icon={Calendar} description="Assign leave policies and balances" />
              <div className="p-12 text-center border-2 border-dashed border-border rounded-[2rem] bg-slate-50/50">
                <LayoutDashboard className="w-12 h-12 text-muted-foreground/20 mx-auto mb-4" />
                <p className="text-sm font-bold text-muted-foreground">Leave policy assignment will be available after basic registration.</p>
                <p className="text-xs text-muted-foreground/60 mt-1">You can configure this in the Employee Profile under 'Leave' tab.</p>
              </div>
            </FormSection>

            {/* 6. DOCUMENTS */}
            <FormSection id="documents">
              <SectionHeader title="Documents" icon={Upload} description="Upload identification and employment documents" />
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                <FormField label="Aadhaar Number" required error={errors.aadhaarNumber?.message}>
                  <Input
                    placeholder="0000 0000 0000"
                    {...form.register('aadhaarNumber')}
                    leftIcon={<Shield size={16} />}
                    className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-mono tracking-widest border-border/40 transition-all"
                  />
                </FormField>
                <FormField label="PAN Number" required error={errors.panNumber?.message}>
                  <Input placeholder="ABCDE1234F" {...form.register('panNumber')} leftIcon={<FileText size={14} />} className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-mono tracking-widest uppercase border-border/40 transition-all" />
                </FormField>
                <FormField label="Passport Number">
                  <Input {...form.register('passportNumber')} leftIcon={<FileText size={14} />} className="h-11 bg-white dark:bg-gray-800 rounded-xl text-sm font-mono border-border/40" />
                </FormField>
              </div>
              <div className="mt-8 p-12 text-center border-2 border-dashed border-border rounded-[2rem] bg-slate-50/50">
                <FileCheck className="w-12 h-12 text-muted-foreground/20 mx-auto mb-4" />
                <p className="text-sm font-bold text-muted-foreground">Document upload repository will be available after saving profile.</p>
                <Button variant="outline" className="mt-4 rounded-xl border-primary/20 text-primary hover:bg-primary/5 font-black text-[10px] tracking-widest uppercase">
                  Prepare Document Checklist
                </Button>
              </div>
            </FormSection>

            {/* 7. EDUCATION DETAILS */}
            <FormSection id="education-details">
              <SectionHeader title="Education Details" icon={GraduationCap} description="Academic qualifications and certifications" />
              
              <div className="space-y-6">
                {(watch('educationDetails') || []).map((edu, index) => (
                  <div key={index} className="p-6 rounded-[2rem] border border-border bg-slate-50/50 dark:bg-slate-900/30 relative group/edu">
                    <button 
                      type="button"
                      onClick={() => {
                        const current = watch('educationDetails') || [];
                        setValue('educationDetails', current.filter((_, i) => i !== index));
                      }}
                      className="absolute right-4 top-4 p-2 text-rose-500 hover:bg-rose-500 hover:text-white rounded-xl transition-all opacity-0 group-hover/edu:opacity-100"
                    >
                      <Trash2 size={16} />
                    </button>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <FormField label="Level">
                        <MasterSelect masterName="EducationLevel" value={edu.educationLevel} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].educationLevel = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <FormField label="Qualification / Degree">
                        <MasterSelect masterName="Qualification" value={edu.qualification} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].qualification = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <FormField label="Field of Study">
                        <MasterSelect masterName="EducationSpecialization" value={edu.specialization} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].specialization = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <FormField label="Institution Name">
                        <Input value={edu.institutionName} onChange={(e) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].institutionName = e.target.value;
                          setValue('educationDetails', current);
                        }} className="h-11 rounded-xl" />
                      </FormField>
                      <FormField label="Board / University">
                        <MasterSelect masterName="Board" value={edu.boardUniversity} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].boardUniversity = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <FormField label="Study Mode">
                        <MasterSelect masterName="StudyMode" value={edu.modeOfStudy} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].modeOfStudy = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <FormField label="Country">
                        <MasterSelect masterName="Country" value={edu.country} onChange={(v) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].country = v;
                          setValue('educationDetails', current);
                        }} />
                      </FormField>
                      <div className="grid grid-cols-2 gap-3">
                        <FormField label="Start Date">
                          <Input type="date" value={edu.startDate} onChange={(e) => {
                            const current = [...(watch('educationDetails') || [])];
                            current[index].startDate = e.target.value;
                            setValue('educationDetails', current);
                          }} className="h-11 rounded-xl text-xs" />
                        </FormField>
                        <FormField label="End Date">
                          <Input type="date" value={edu.endDate} onChange={(e) => {
                            const current = [...(watch('educationDetails') || [])];
                            current[index].endDate = e.target.value;
                            setValue('educationDetails', current);
                          }} className="h-11 rounded-xl text-xs" />
                        </FormField>
                      </div>
                      <FormField label="Grade / CGPA">
                        <Input value={edu.grade} onChange={(e) => {
                          const current = [...(watch('educationDetails') || [])];
                          current[index].grade = e.target.value;
                          setValue('educationDetails', current);
                        }} className="h-11 rounded-xl" />
                      </FormField>
                    </div>
                  </div>
                ))}

                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => {
                    const current = watch('educationDetails') || [];
                    setValue('educationDetails', [...current, {
                      educationLevel: '',
                      qualification: '',
                      specialization: '',
                      institutionName: '',
                      boardUniversity: '',
                      startDate: '',
                      endDate: '',
                      grade: '',
                      modeOfStudy: '',
                      country: ''
                    }]);
                  }}
                  className="w-full h-14 border-dashed border-2 hover:border-primary hover:bg-primary/5 rounded-[1.5rem] flex items-center justify-center gap-2 text-xs font-black text-muted-foreground hover:text-primary transition-all"
                >
                  <Plus size={16} />
                  ADD EDUCATION RECORD
                </Button>
              </div>
            </FormSection>

            {/* 8. BACKGROUND CHECK */}
            <FormSection id="background-check">
              <SectionHeader title="Background Check" icon={Shield} description="Verification status and agency details" />
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                <FormField label="Verification Status">
                  <MasterSelect 
                    masterName="VerificationStatus" 
                    value={watch('backgroundCheck.verificationStatus') || ''} 
                    onChange={(v) => setValue('backgroundCheck.verificationStatus', v as any)}
                  />
                </FormField>
                <FormField label="Agency Name">
                  <Input {...form.register('backgroundCheck.agencyName')} className="h-11 rounded-xl" placeholder="E.g. AuthBridge" />
                </FormField>
                <FormField label="Verified By">
                  <Input {...form.register('backgroundCheck.verifiedBy')} className="h-11 rounded-xl" placeholder="Auditor Name" />
                </FormField>
                <FormField label="Reference Number">
                  <Input {...form.register('backgroundCheck.referenceNumber')} className="h-11 rounded-xl" placeholder="Case ID" />
                </FormField>
                <FormField label="Remarks" className="sm:col-span-2">
                  <Textarea {...form.register('backgroundCheck.remarks')} className="rounded-xl min-h-[80px] resize-none" placeholder="Verification notes..." />
                </FormField>
              </div>
            </FormSection>

            {/* 9. ACCOUNT ACCESS */}
            <FormSection id="account-access">
              <SectionHeader title="Account Access & Behavior" icon={LayoutDashboard} description="Configure system roles, tags and internal notes" />
              <div className="space-y-8">
                <div className="p-6 bg-emerald-50/50 dark:bg-emerald-900/10 rounded-2xl border border-emerald-100 dark:border-emerald-800/50 flex items-center gap-4">
                  <Checkbox 
                    id="allow-fill-final"
                    checked={watch('allowEmployeeToFillInfo')}
                    onCheckedChange={(v) => setValue('allowEmployeeToFillInfo', !!v)}
                    className="w-6 h-6 rounded-lg border-2 border-emerald-400/30 data-[state=checked]:bg-emerald-500 data-[state=checked]:border-emerald-500"
                  />
                  <div className="flex flex-col">
                    <label htmlFor="allow-fill-final" className="text-sm font-bold text-emerald-800 dark:text-emerald-300">
                      Allow employee to self-onboard
                    </label>
                    <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">This will send an invite email to the employee to complete their profile.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <FormField label="Employee Tags">
                    <div className="flex flex-wrap gap-2 p-3 bg-white dark:bg-gray-800 border border-border/40 rounded-xl min-h-[44px]">
                      {watch('employeeTags')?.map(tag => (
                        <Badge key={tag} className="bg-slate-800 text-white gap-1 px-2 py-0.5 text-[10px] uppercase font-black tracking-widest rounded-lg">
                          {tag}
                          <X size={10} className="cursor-pointer" onClick={() => {
                            const current = watch('employeeTags') || [];
                            setValue('employeeTags', current.filter(t => t !== tag));
                          }} />
                        </Badge>
                      ))}
                      <input 
                        className="bg-transparent border-none outline-none text-xs font-bold placeholder:text-muted-foreground/50 flex-1 min-w-[100px]" 
                        placeholder="Add tag..."
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            const val = e.currentTarget.value.trim();
                            if (val) {
                              const current = watch('employeeTags') || [];
                              if (!current.includes(val)) setValue('employeeTags', [...current, val]);
                              e.currentTarget.value = '';
                            }
                          }
                        }}
                      />
                    </div>
                  </FormField>
                  <FormField label="System Role">
                    <MasterSelect masterName="SystemRole" value="" onChange={() => {}} placeholder="Assign Role..." />
                  </FormField>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <FormField label="HR Notes">
                    <Textarea {...form.register('hrNotes')} className="bg-white dark:bg-gray-800 rounded-xl min-h-[100px] text-sm p-4 resize-none border-border/40" placeholder="Confidential notes..." />
                  </FormField>
                  <FormField label="Admin Notes">
                    <Textarea {...form.register('internalNotes')} className="bg-slate-50 dark:bg-slate-900 rounded-xl min-h-[100px] text-sm p-4 resize-none border-border/40" placeholder="System reference..." />
                  </FormField>
                </div>
              </div>
            </FormSection>
          </form>
        </div>
      </div>
    </div>
    </EmployeeFormProvider>
  );
}
