import { zodResolver } from '@hookform/resolvers/zod';
import { Save } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { FormField } from '@components/forms/FormField';
import { FormSection } from '@components/forms/FormSection';
import { MasterSelect } from '@components/forms/MasterSelect';
import { Badge, Button, Input, Textarea } from '@components/ui';
import { toast } from '@components/ui/Toast';
import type { Employee, EmployeeProfileSection } from '@/types/employee';

const employeeSchema = z.object({
  firstName: z.string().min(2).max(50),
  email: z.string().email(),
  phone: z.string().min(10).max(16),
  address: z.string().min(5),
  emergencyContact: z.string().min(2)
});

type EmployeeFormValues = z.infer<typeof employeeSchema>;

interface EmployeeProfileTabProps {
  employee: Employee;
  sections: EmployeeProfileSection[];
  title: string;
}

export function EmployeeProfileTab({ employee, sections, title }: EmployeeProfileTabProps) {
  const [editing, setEditing] = useState(false);
  const form = useForm<EmployeeFormValues>({
    resolver: zodResolver(employeeSchema),
    defaultValues: {
      firstName: employee.name.split(' ')[0] ?? '',
      email: employee.email,
      phone: '+91 98765 43210',
      address: employee.location,
      emergencyContact: 'Karan Mehta'
    }
  });

  const submit = form.handleSubmit(async (values) => {
    await toast.promise(Promise.resolve(values), {
      loading: `Saving ${title.toLowerCase()} updates`,
      success: `${title} updated`,
      error: `Failed to update ${title.toLowerCase()}`
    });
    setEditing(false);
  });

  return (
    <div className="space-y-4">
      {sections.map((section) => (
        <FormSection
          key={section.id}
          title={section.title}
          subtitle={editing ? 'Edit mode is active for this section.' : 'Read-only employee information with inline editing support.'}
          actions={
            editing ? (
              <div className="flex gap-2">
                <Button size="xs" variant="secondary" onClick={() => setEditing(false)}>Cancel</Button>
                <Button size="xs" iconLeft={<Save className="h-3.5 w-3.5" />} onClick={submit}>Save</Button>
              </div>
            ) : (
              <Button variant="ghost" size="xs" onClick={() => setEditing(true)}>Edit</Button>
            )
          }
        >
          {editing ? (
            <form className="grid gap-4 md:grid-cols-2" onSubmit={submit}>
              <FormField label="First name" required>
                <Input label="First name" {...form.register('firstName')} error={form.formState.errors.firstName?.message} />
              </FormField>
              <FormField label="Email" required>
                <Input label="Email" {...form.register('email')} error={form.formState.errors.email?.message} />
              </FormField>
              <FormField label="Phone" required>
                <Input label="Phone" {...form.register('phone')} error={form.formState.errors.phone?.message} />
              </FormField>
              <FormField label="Emergency contact" required>
                <Input label="Emergency contact" {...form.register('emergencyContact')} error={form.formState.errors.emergencyContact?.message} />
              </FormField>
              <div className="md:col-span-2">
                <FormField label="Address" required>
                  <Textarea label="Address" value={form.watch('address')} onChange={(event) => form.setValue('address', event.target.value)} error={form.formState.errors.address?.message} maxLength={180} />
                </FormField>
              </div>
              <MasterSelect label="Master data" value={employee.department} onValueChange={() => undefined} options={[{ label: employee.department, value: employee.department }, { label: employee.location, value: employee.location }]} helperText="Demonstrates master-driven dropdowns for official mappings." />
            </form>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {section.fields.map((field) => (
                <div key={field.label} className="rounded-2xl border border-surface-300/60 bg-surface-50/80 px-4 py-3 dark:border-white/10 dark:bg-white/[0.03]">
                  <p className="text-xs uppercase tracking-[0.12em] text-surface-500 dark:text-white/35">{field.label}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <p className="text-sm font-medium text-surface-800 dark:text-white/80">{field.value}</p>
                    <Badge variant="ghost" size="sm">{field.icon}</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </FormSection>
      ))}
    </div>
  );
}
