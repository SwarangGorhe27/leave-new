import React, { useState } from 'react';
import { X, Check } from 'lucide-react';
import { Button, Modal, toast } from '@components/ui';
import type { QuickAddEmployee } from '@types/admin';

interface QuickAddModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (employee: QuickAddEmployee) => void;
}

export function QuickAddModal({ isOpen, onClose, onSuccess }: QuickAddModalProps) {
  const [formData, setFormData] = useState<QuickAddEmployee>({
    employeeName: '',
    employeeNumber: '',
    dateOfJoining: '',
    location: '',
    emailId: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error for this field
    if (errors[name]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.employeeName.trim()) newErrors.employeeName = 'Employee name is required';
    if (!formData.employeeNumber.trim()) newErrors.employeeNumber = 'Employee number is required';
    if (!formData.dateOfJoining) newErrors.dateOfJoining = 'Joining date is required';
    if (!formData.location.trim()) newErrors.location = 'Location is required';
    if (!formData.emailId.trim()) newErrors.emailId = 'Email ID is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.emailId))
      newErrors.emailId = 'Invalid email format';

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsSubmitting(true);
    // Simulate API call
    setTimeout(() => {
      setIsSubmitting(false);
      toast.success(`Employee ${formData.employeeName} added successfully!`);
      onSuccess?.(formData);
      resetForm();
      onClose();
    }, 1000);
  };

  const resetForm = () => {
    setFormData({
      employeeName: '',
      employeeNumber: '',
      dateOfJoining: '',
      location: '',
      emailId: '',
    });
    setErrors({});
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Quick Add Employee">
      <form onSubmit={handleSubmit} className="space-y-4 px-6 py-4">
        {/* Employee Name */}
        <div>
          <label className="block text-sm font-semibold text-text-primary mb-2">
            Employee Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="employeeName"
            value={formData.employeeName}
            onChange={handleChange}
            placeholder="Enter employee name"
            className={`w-full px-3 py-2 rounded-lg border bg-surface-0 dark:bg-white/3 text-text-primary placeholder-text-tertiary outline-none transition-all ${
              errors.employeeName
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-surface-200 dark:border-white/10 focus:ring-brand-500/20 focus:border-brand-500'
            } focus:ring-2`}
          />
          {errors.employeeName && <p className="text-xs text-red-500 mt-1">{errors.employeeName}</p>}
        </div>

        {/* Employee Number */}
        <div>
          <label className="block text-sm font-semibold text-text-primary mb-2">
            Employee Number <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            name="employeeNumber"
            value={formData.employeeNumber}
            onChange={handleChange}
            placeholder="e.g., EMP-0001"
            className={`w-full px-3 py-2 rounded-lg border bg-surface-0 dark:bg-white/3 text-text-primary placeholder-text-tertiary outline-none transition-all ${
              errors.employeeNumber
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-surface-200 dark:border-white/10 focus:ring-brand-500/20 focus:border-brand-500'
            } focus:ring-2`}
          />
          {errors.employeeNumber && <p className="text-xs text-red-500 mt-1">{errors.employeeNumber}</p>}
        </div>

        {/* Date of Joining */}
        <div>
          <label className="block text-sm font-semibold text-text-primary mb-2">
            Date of Joining <span className="text-red-500">*</span>
          </label>
          <input
            type="date"
            name="dateOfJoining"
            value={formData.dateOfJoining}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg border bg-surface-0 dark:bg-white/3 text-text-primary outline-none transition-all ${
              errors.dateOfJoining
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-surface-200 dark:border-white/10 focus:ring-brand-500/20 focus:border-brand-500'
            } focus:ring-2`}
          />
          {errors.dateOfJoining && (
            <p className="text-xs text-red-500 mt-1">{errors.dateOfJoining}</p>
          )}
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-semibold text-text-primary mb-2">
            Location <span className="text-red-500">*</span>
          </label>
          <select
            name="location"
            value={formData.location}
            onChange={handleChange}
            className={`w-full px-3 py-2 rounded-lg border bg-surface-0 dark:bg-white/3 text-text-primary outline-none transition-all ${
              errors.location
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-surface-200 dark:border-white/10 focus:ring-brand-500/20 focus:border-brand-500'
            } focus:ring-2`}
          >
            <option value="">-- Select Location --</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Delhi">Delhi</option>
            <option value="Pune">Pune</option>
            <option value="Chennai">Chennai</option>
          </select>
          {errors.location && <p className="text-xs text-red-500 mt-1">{errors.location}</p>}
        </div>

        {/* Email ID */}
        <div>
          <label className="block text-sm font-semibold text-text-primary mb-2">
            Email ID <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            name="emailId"
            value={formData.emailId}
            onChange={handleChange}
            placeholder="employee@company.com"
            className={`w-full px-3 py-2 rounded-lg border bg-surface-0 dark:bg-white/3 text-text-primary placeholder-text-tertiary outline-none transition-all ${
              errors.emailId
                ? 'border-red-500 focus:ring-red-500/20'
                : 'border-surface-200 dark:border-white/10 focus:ring-brand-500/20 focus:border-brand-500'
            } focus:ring-2`}
          />
          {errors.emailId && <p className="text-xs text-red-500 mt-1">{errors.emailId}</p>}
        </div>

        {/* Footer Actions */}
        <div className="flex gap-3 justify-end pt-4 border-t border-surface-200 dark:border-white/10">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            iconLeft={<Check className="h-4 w-4" />}
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Adding...' : 'Add Employee'}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
