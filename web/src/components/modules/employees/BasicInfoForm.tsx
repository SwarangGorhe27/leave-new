import React, { useState } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  Calendar, 
  Droplets, 
  Heart, 
  Users, 
  IdCard,
  Save,
  RotateCcw
} from 'lucide-react';
import { Input, Select, Button, toast } from '@components/ui';
import { cn } from '@utils/utils';
import { motion } from 'framer-motion';

interface FormData {
  employeeId: string;
  fullName: string;
  email: string;
  mobile: string;
  alternateEmail: string;
  alternateMobile: string;
  dob: string;
  gender: string;
  maritalStatus: string;
  bloodGroup: string;
}

const INITIAL_DATA: FormData = {
  employeeId: '',
  fullName: '',
  email: '',
  mobile: '',
  alternateEmail: '',
  alternateMobile: '',
  dob: '',
  gender: '',
  maritalStatus: '',
  bloodGroup: '',
};

export function BasicInfoForm() {
  const [formData, setFormData] = useState<FormData>(INITIAL_DATA);
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validate = () => {
    const newErrors: Partial<Record<keyof FormData, string>> = {};
    
    if (!formData.employeeId) newErrors.employeeId = 'Employee ID is required';
    if (!formData.fullName) newErrors.fullName = 'Full Name is required';
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }
    
    if (!formData.mobile) {
      newErrors.mobile = 'Mobile number is required';
    } else if (!/^\+?[\d\s-]{10,15}$/.test(formData.mobile)) {
      newErrors.mobile = 'Invalid phone number';
    }

    if (formData.alternateEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.alternateEmail)) {
      newErrors.alternateEmail = 'Invalid email format';
    }

    if (formData.alternateMobile && !/^\+?[\d\s-]{10,15}$/.test(formData.alternateMobile)) {
      newErrors.alternateMobile = 'Invalid phone number';
    }

    if (!formData.dob) newErrors.dob = 'Date of Birth is required';
    if (!formData.gender) newErrors.gender = 'Gender is required';
    if (!formData.maritalStatus) newErrors.maritalStatus = 'Marital Status is required';
    if (!formData.bloodGroup) newErrors.bloodGroup = 'Blood Group is required';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    setIsSubmitting(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      toast.success('Basic information saved successfully');
      console.log('Submitted Data:', formData);
    } catch (error) {
      toast.error('Failed to save information');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFormData(INITIAL_DATA);
    setErrors({});
    toast.info('Form reset');
  };

  return (
    <div className="mx-auto max-w-4xl p-4">
      <motion.form 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        onSubmit={handleSubmit} 
        className="surface-card overflow-hidden"
      >
        {/* Header */}
        <div className="border-b border-surface-200 bg-surface-50/50 px-6 py-4 dark:border-white/5 dark:bg-white/[0.02]">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500/10 text-brand-500">
              <IdCard className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-text-primary">Basic Employee Information</h3>
              <p className="text-xs text-text-tertiary">Capture core identity and contact details of the employee.</p>
            </div>
          </div>
        </div>

        {/* Form Body */}
        <div className="space-y-8 px-6 py-6">
          {/* Identity Section */}
          <div>
            <h4 className="section-label mb-4">Identity & Name</h4>
            <div className="grid gap-6 md:grid-cols-2">
              <Input
                label="Employee ID"
                placeholder="e.g. EMP-101"
                required
                value={formData.employeeId}
                onChange={e => handleChange('employeeId', e.target.value)}
                error={errors.employeeId}
                leftIcon={<IdCard className="h-4 w-4" />}
              />
              <Input
                label="Full Name"
                placeholder="e.g. John Doe"
                required
                value={formData.fullName}
                onChange={e => handleChange('fullName', e.target.value)}
                error={errors.fullName}
                leftIcon={<User className="h-4 w-4" />}
              />
            </div>
          </div>

          {/* Contact Section */}
          <div>
            <h4 className="section-label mb-4">Contact Information</h4>
            <div className="grid gap-6 md:grid-cols-2">
              <Input
                label="Work Email"
                type="email"
                placeholder="john.doe@company.com"
                required
                value={formData.email}
                onChange={e => handleChange('email', e.target.value)}
                error={errors.email}
                leftIcon={<Mail className="h-4 w-4" />}
              />
              <Input
                label="Mobile Number"
                placeholder="+91 98765 43210"
                required
                value={formData.mobile}
                onChange={e => handleChange('mobile', e.target.value)}
                error={errors.mobile}
                leftIcon={<Phone className="h-4 w-4" />}
              />
              <Input
                label="Alternate Email"
                type="email"
                placeholder="personal.email@gmail.com"
                value={formData.alternateEmail}
                onChange={e => handleChange('alternateEmail', e.target.value)}
                error={errors.alternateEmail}
                leftIcon={<Mail className="h-4 w-4" />}
              />
              <Input
                label="Alternate Mobile"
                placeholder="+91 90000 12345"
                value={formData.alternateMobile}
                onChange={e => handleChange('alternateMobile', e.target.value)}
                error={errors.alternateMobile}
                leftIcon={<Phone className="h-4 w-4" />}
              />
            </div>
          </div>

          {/* Personal Section */}
          <div>
            <h4 className="section-label mb-4">Personal Details</h4>
            <div className="grid gap-6 md:grid-cols-2">
              <Input
                label="Date of Birth"
                type="date"
                required
                value={formData.dob}
                onChange={e => handleChange('dob', e.target.value)}
                error={errors.dob}
                leftIcon={<Calendar className="h-4 w-4" />}
              />
              <Select
                label="Gender"
                required
                value={formData.gender}
                onValueChange={val => handleChange('gender', val)}
                error={errors.gender}
                leftIcon={<Users className="h-4 w-4" />}
                options={[
                  { label: 'Male', value: 'male' },
                  { label: 'Female', value: 'female' },
                  { label: 'Other', value: 'other' },
                ]}
              />
              <Select
                label="Marital Status"
                required
                value={formData.maritalStatus}
                onValueChange={val => handleChange('maritalStatus', val)}
                error={errors.maritalStatus}
                leftIcon={<Heart className="h-4 w-4" />}
                options={[
                  { label: 'Single', value: 'single' },
                  { label: 'Married', value: 'married' },
                  { label: 'Divorced', value: 'divorced' },
                  { label: 'Widowed', value: 'widowed' },
                ]}
              />
              <Select
                label="Blood Group"
                required
                value={formData.bloodGroup}
                onValueChange={val => handleChange('bloodGroup', val)}
                error={errors.bloodGroup}
                leftIcon={<Droplets className="h-4 w-4" />}
                options={[
                  { label: 'A+', value: 'A+' },
                  { label: 'A-', value: 'A-' },
                  { label: 'B+', value: 'B+' },
                  { label: 'B-', value: 'B-' },
                  { label: 'AB+', value: 'AB+' },
                  { label: 'AB-', value: 'AB-' },
                  { label: 'O+', value: 'O+' },
                  { label: 'O-', value: 'O-' },
                ]}
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-3 border-t border-surface-200 bg-surface-50/50 px-6 py-4 dark:border-white/5 dark:bg-white/[0.02]">
          <Button
            type="button"
            variant="ghost"
            onClick={handleReset}
            disabled={isSubmitting}
            iconLeft={<RotateCcw className="h-4 w-4" />}
          >
            Reset
          </Button>
          <Button
            type="submit"
            isLoading={isSubmitting}
            iconLeft={<Save className="h-4 w-4" />}
          >
            Save Information
          </Button>
        </div>
      </motion.form>
    </div>
  );
}
