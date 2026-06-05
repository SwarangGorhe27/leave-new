import React, { useState } from 'react';
import { Upload, ChevronRight, ChevronLeft, X, AlertCircle, CheckCircle } from 'lucide-react';
import { Button, Modal, toast } from '@components/ui';
import { MASTER_FIELDS } from './admin/constants';
import type { MappingField, ValidationError } from '@types/admin';

interface BulkUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (data: any) => void;
}

interface StepState {
  step: 1 | 2 | 3;
  file: File | null;
  mappings: MappingField[];
  validationErrors: ValidationError[];
  isValidating: boolean;
}

export function BulkUploadModal({ isOpen, onClose, onSuccess }: BulkUploadModalProps) {
  const [state, setState] = useState<StepState>({
    step: 1,
    file: null,
    mappings: [],
    validationErrors: [],
    isValidating: false,
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (!['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'text/csv'].includes(file.type)) {
        toast.error('Please upload an Excel (.xlsx) or CSV (.csv) file');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }
      setState((prev) => ({ ...prev, file }));
    }
  };

  const proceedToStep2 = () => {
    if (!state.file) {
      toast.error('Please select a file');
      return;
    }

    // Generate sample mappings from first row of file
    const excelHeaders = ['Column1', 'Column2', 'Column3', 'Column4', 'Column5'];
    const mappings: MappingField[] = excelHeaders.map((header, idx) => ({
      id: `mapping-${idx}`,
      excelField: header,
      mappedTo: '',
      previewData: `Sample value ${idx + 1}`,
    }));

    setState((prev) => ({
      ...prev,
      step: 2,
      mappings,
    }));
  };

  const proceedToStep3 = () => {
    const requiredMappings = state.mappings.filter((m) => !m.mappedTo);
    if (requiredMappings.length > 0) {
      toast.error('Please map all required fields');
      return;
    }

    // Simulate validation
    setState((prev) => ({
      ...prev,
      step: 3,
      isValidating: true,
    }));

    setTimeout(() => {
      const errors: ValidationError[] = [
        {
          row: 5,
          field: 'email',
          message: 'Invalid email format',
          value: 'invalid-email@',
        },
        {
          row: 12,
          field: 'employee_number',
          message: 'Duplicate employee number',
          value: 'EMP-0001',
        },
      ];

      setState((prev) => ({
        ...prev,
        isValidating: false,
        validationErrors: errors,
      }));
    }, 1500);
  };

  const handleMappingChange = (index: number, field: Partial<MappingField>) => {
    setState((prev) => ({
      ...prev,
      mappings: prev.mappings.map((m, i) =>
        i === index ? { ...m, ...field } : m
      ),
    }));
  };

  const handlePrevious = () => {
    setState((prev) => ({
      ...prev,
      step: (prev.step - 1) as 1 | 2 | 3,
    }));
  };

  const handleSubmit = () => {
    toast.success('Bulk upload submitted successfully!');
    onSuccess?.({
      file: state.file,
      mappings: state.mappings,
    });
    handleClose();
  };

  const handleClose = () => {
    setState({
      step: 1,
      file: null,
      mappings: [],
      validationErrors: [],
      isValidating: false,
    });
    onClose();
  };

  if (!isOpen) return null;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Bulk Upload Employees">
      <div className="space-y-6">
        {/* Stepper */}
        <div className="flex items-center justify-between px-6 pt-6">
          {[1, 2, 3].map((step, idx) => (
            <div key={step} className="flex items-center flex-1">
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-full font-bold text-sm transition-all ${
                  step <= state.step
                    ? 'bg-brand-500 text-white'
                    : 'bg-surface-200 text-text-tertiary dark:bg-white/10'
                }`}
              >
                {step}
              </div>
              {idx < 2 && (
                <div
                  className={`flex-1 h-1 mx-2 rounded-full transition-all ${
                    step < state.step
                      ? 'bg-brand-500'
                      : 'bg-surface-200 dark:bg-white/10'
                  }`}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step labels */}
        <div className="px-6 flex justify-between text-xs font-medium text-text-secondary">
          <span>Upload File</span>
          <span>Map Fields</span>
          <span>Validate</span>
        </div>

        {/* Content */}
        <div className="px-6 pb-6 space-y-4">
          {state.step === 1 && (
            <>
              {/* File Upload */}
              <div>
                <label className="block text-sm font-semibold text-text-primary mb-2">
                  Upload Employee Data (Excel or CSV)
                </label>
                <div className="border-2 border-dashed border-surface-300 dark:border-white/10 rounded-lg p-8 text-center hover:border-brand-500 transition-colors cursor-pointer">
                  <input
                    type="file"
                    accept=".xlsx,.csv,.xls"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="bulk-file-input"
                  />
                  <label htmlFor="bulk-file-input" className="cursor-pointer block">
                    <Upload className="h-10 w-10 text-text-tertiary mx-auto mb-3" />
                    <p className="text-sm font-semibold text-text-primary mb-1">
                      {state.file ? state.file.name : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-xs text-text-tertiary">
                      Supported formats: XLSX, CSV (Max 10MB)
                    </p>
                  </label>
                </div>
              </div>

              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
                <p className="text-xs text-blue-900 dark:text-blue-300">
                  <strong>💡 Tip:</strong> Make sure your Excel file has headers in the first row.
                </p>
              </div>
            </>
          )}

          {state.step === 2 && (
            <>
              <div className="bg-surface-50 dark:bg-white/3 border border-surface-200 dark:border-white/10 rounded-lg p-4 text-sm">
                <p className="font-medium text-text-primary mb-2">Map Excel Columns to Employee Fields</p>
                <p className="text-text-tertiary text-xs">
                  Select the corresponding master field for each column in your Excel file.
                </p>
              </div>

              <div className="space-y-3 max-h-80 overflow-y-auto">
                {state.mappings.map((mapping, idx) => (
                  <div key={mapping.id} className="border border-surface-200 dark:border-white/10 rounded-lg p-3 space-y-2">
                    <div className="grid grid-cols-3 gap-2 items-center text-xs">
                      <div>
                        <div className="font-semibold text-text-primary">Excel: {mapping.excelField}</div>
                      </div>
                      <div className="text-center text-text-tertiary">→</div>
                      <div>
                        <label className="block text-xs font-semibold text-text-secondary mb-1">
                          Map to Field
                        </label>
                        <select
                          value={mapping.mappedTo}
                          onChange={(e) => handleMappingChange(idx, { mappedTo: e.target.value })}
                          className="w-full px-2 py-1 rounded border border-surface-300 dark:border-white/20 bg-surface-0 dark:bg-white/5 text-text-primary text-xs outline-none focus:ring-1 focus:ring-brand-500"
                        >
                          <option value="">-- Select Field --</option>
                          {MASTER_FIELDS.map((field) => (
                            <option key={field.id} value={field.id}>
                              {field.fieldName} {field.required ? '*' : ''}
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>
                    <div className="text-xs text-text-tertiary bg-surface-100 dark:bg-white/3 px-2 py-1 rounded">
                      Preview: {mapping.previewData}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {state.step === 3 && (
            <>
              {state.isValidating ? (
                <div className="text-center py-8 space-y-3">
                  <div className="inline-block animate-spin">
                    <div className="h-12 w-12 border-4 border-brand-500/20 border-t-brand-500 rounded-full" />
                  </div>
                  <p className="text-sm font-medium text-text-primary">Validating employee data...</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {state.validationErrors.length === 0 ? (
                    <div className="bg-green-50 dark:bg-green-900/20 border border-green-300 dark:border-green-800 rounded-lg p-4">
                      <div className="flex items-center gap-3">
                        <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0" />
                        <div>
                          <p className="font-semibold text-green-900 dark:text-green-300">
                            All Records Valid!
                          </p>
                          <p className="text-sm text-green-800 dark:text-green-400">
                            Ready to import employees.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <div className="bg-red-50 dark:bg-red-900/20 border border-red-300 dark:border-red-800 rounded-lg p-3">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                          <p className="font-semibold text-red-900 dark:text-red-300">
                            {state.validationErrors.length} Error{state.validationErrors.length !== 1 ? 's' : ''}
                          </p>
                        </div>
                      </div>

                      <div className="bg-surface-50 dark:bg-white/3 border border-surface-200 dark:border-white/10 rounded-lg p-3 space-y-2 max-h-48 overflow-y-auto">
                        {state.validationErrors.map((error, idx) => (
                          <div key={idx} className="text-xs border-l-2 border-red-500 pl-3 py-1">
                            <p className="font-medium text-text-primary">
                              Row {error.row} - {error.field}
                            </p>
                            <p className="text-red-600 dark:text-red-400">{error.message}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div className="bg-surface-50 dark:bg-white/3 border border-surface-200 dark:border-white/10 rounded-lg p-3 space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Total Records:</span>
                      <span className="font-semibold text-text-primary">250</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Valid Records:</span>
                      <span className="font-semibold text-green-600 dark:text-green-400">
                        {250 - state.validationErrors.length}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-text-secondary">Invalid Records:</span>
                      <span className="font-semibold text-red-600 dark:text-red-400">
                        {state.validationErrors.length}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer Actions */}
        <div className="px-6 pb-6 flex gap-3 justify-end border-t border-surface-200 dark:border-white/10 pt-6">
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          {state.step > 1 && (
            <Button variant="secondary" iconLeft={<ChevronLeft className="h-4 w-4" />} onClick={handlePrevious}>
              Previous
            </Button>
          )}
          {state.step < 3 && (
            <Button
              variant="primary"
              iconRight={<ChevronRight className="h-4 w-4" />}
              onClick={state.step === 1 ? proceedToStep2 : proceedToStep3}
            >
              {state.step === 1 ? 'Next' : 'Validate'}
            </Button>
          )}
          {state.step === 3 && !state.isValidating && (
            <Button
              variant="primary"
              iconLeft={<CheckCircle className="h-4 w-4" />}
              onClick={handleSubmit}
              disabled={state.validationErrors.length > 0}
            >
              Submit Upload
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
