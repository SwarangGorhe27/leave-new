import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

function extract<T>(res: unknown): T[] {
  const d = res as Record<string, unknown>;
  return (d?.data as Record<string, unknown>)?.results as T[]
    ?? (d?.data as Record<string, unknown>)?.data as T[]
    ?? d?.data as T[]
    ?? d?.results as T[]
    ?? (Array.isArray(d) ? d : []) as T[];
}

function extractOne<T>(res: unknown): T {
  const d = res as Record<string, unknown>;
  return ((d?.data as Record<string, unknown>)?.data ?? d?.data ?? d) as T;
}

export interface FormDefinition {
  id: string;
  title: string;
  description: string;
  status: 'DRAFT' | 'PUBLISHED' | 'CLOSED';
  submission_count: number;
  published_at: string | null;
  closes_at: string | null;
  created_at: string;
  fields: FormField[];
}

export interface FormField {
  id: string;
  label: string;
  field_type: 'TEXT' | 'NUMBER' | 'EMAIL' | 'DATE' | 'SELECT' | 'CHECKBOX' | 'TEXTAREA' | 'FILE';
  is_required: boolean;
  placeholder: string;
  help_text: string;
  options: string[];
  sort_order: number;
}

export interface FormSubmission {
  id: string;
  form: string;
  employee: string;
  employee_code: string;
  data: Record<string, unknown>;
  submitted_at: string;
  is_anonymous: boolean;
}

export function useForms() {
  return useQuery({
    queryKey: ['forms'],
    queryFn: async () => {
      const res = await api.get('/forms/forms/');
      return extract<FormDefinition>(res);
    },
    staleTime: 60_000,
  });
}

export function useFormSubmissions(formId?: string) {
  return useQuery({
    queryKey: ['forms', formId, 'submissions'],
    queryFn: async () => {
      const res = await api.get(`/forms/forms/${formId}/submissions/`);
      return extract<FormSubmission>(res);
    },
    enabled: !!formId,
  });
}

export function useCreateForm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (data: { title: string; description?: string }) => {
      const res = await api.post('/forms/forms/', data);
      return extractOne<FormDefinition>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  });
}

export function usePublishForm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/forms/forms/${id}/publish/`);
      return extractOne<FormDefinition>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  });
}

export function useCloseForm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post(`/forms/forms/${id}/close/`);
      return extractOne<FormDefinition>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  });
}

export function useDeleteForm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/forms/forms/${id}/`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  });
}

export function useSubmitForm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({ formId, data }: { formId: string; data: Record<string, unknown> }) => {
      const res = await api.post('/forms/submissions/', { form: formId, data });
      return extractOne<FormSubmission>(res);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['forms'] }),
  });
}
