import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@api/client';

const DOCS_KEY = 'hrms-demo-documents';

interface DemoDocument {
  id: string;
  title: string;
  description: string;
  category: string;
  status: string;
  version: number;
  file_name: string;
  file_size: number;
  mime_type: string;
  file: string;
  created_at: string;
}

const DEMO_DOCUMENTS: DemoDocument[] = [
  { id: 'doc-1', title: 'Offer Letter', description: 'Original offer letter issued at joining', category: 'LETTER', status: 'ACTIVE', version: 1, file_name: 'Offer_Letter_Aditi_Mehra.pdf', file_size: 248000, mime_type: 'application/pdf', file: '#', created_at: '2024-01-10T10:00:00Z' },
  { id: 'doc-2', title: 'Appointment Letter', description: 'Formal appointment confirmation after probation', category: 'LETTER', status: 'ACTIVE', version: 1, file_name: 'Appointment_Letter_2024.pdf', file_size: 192000, mime_type: 'application/pdf', file: '#', created_at: '2024-07-16T11:30:00Z' },
  { id: 'doc-3', title: 'PAN Card', description: 'PAN card copy for KYC', category: 'CERTIFICATE', status: 'ACTIVE', version: 1, file_name: 'PAN_Card.pdf', file_size: 520000, mime_type: 'application/pdf', file: '#', created_at: '2024-01-12T09:00:00Z' },
  { id: 'doc-4', title: 'Aadhaar Card', description: 'Aadhaar for identity verification', category: 'CERTIFICATE', status: 'ACTIVE', version: 1, file_name: 'Aadhaar_Front_Back.pdf', file_size: 740000, mime_type: 'application/pdf', file: '#', created_at: '2024-01-12T09:30:00Z' },
  { id: 'doc-5', title: 'Employee Handbook', description: 'Company policies, code of conduct, and procedures', category: 'POLICY', status: 'ACTIVE', version: 3, file_name: 'Employee_Handbook_v3.pdf', file_size: 1850000, mime_type: 'application/pdf', file: '#', created_at: '2025-01-01T00:00:00Z' },
  { id: 'doc-6', title: 'Leave Policy 2026', description: 'Official leave policy for FY 2025-26', category: 'POLICY', status: 'ACTIVE', version: 2, file_name: 'Leave_Policy_FY2026.pdf', file_size: 430000, mime_type: 'application/pdf', file: '#', created_at: '2026-01-01T00:00:00Z' },
  { id: 'doc-7', title: 'NDA Agreement', description: 'Non-disclosure agreement signed at onboarding', category: 'COMPANY', status: 'ACTIVE', version: 1, file_name: 'NDA_Signed_2024.pdf', file_size: 310000, mime_type: 'application/pdf', file: '#', created_at: '2024-01-15T10:00:00Z' },
  { id: 'doc-8', title: 'Appraisal Letter FY2025', description: 'Annual increment and appraisal letter', category: 'LETTER', status: 'ACTIVE', version: 1, file_name: 'Appraisal_Letter_FY25.pdf', file_size: 185000, mime_type: 'application/pdf', file: '#', created_at: '2025-04-01T09:00:00Z' },
];

function readDemoDocs(): DemoDocument[] {
  const raw = localStorage.getItem(DOCS_KEY);
  if (raw) { try { return JSON.parse(raw) as DemoDocument[]; } catch { /* ignore */ } }
  localStorage.setItem(DOCS_KEY, JSON.stringify(DEMO_DOCUMENTS));
  return DEMO_DOCUMENTS;
}

function writeDemoDocs(docs: DemoDocument[]) {
  localStorage.setItem(DOCS_KEY, JSON.stringify(docs));
}

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

export function useMyDocuments() {
  return useQuery({
    queryKey: ['me', 'documents'],
    queryFn: async () => {
      try {
        const res = await api.get('/me/documents/');
        const rows = extract<Record<string, unknown>>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return readDemoDocs() as unknown as Record<string, unknown>[];
    },
  });
}

export function useUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) => {
      try {
        const res = await api.post('/me/upload-document/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return extractOne<Record<string, unknown>>(res);
      } catch {
        const file = formData.get('file') as File | null;
        const title = (formData.get('title') as string | null) ?? file?.name ?? 'Document';
        const doc: DemoDocument = {
          id: crypto.randomUUID(),
          title,
          description: '',
          category: (formData.get('category') as string) ?? 'OTHER',
          status: 'ACTIVE',
          version: 1,
          file_name: file?.name ?? title,
          file_size: file?.size ?? 0,
          mime_type: file?.type ?? 'application/octet-stream',
          file: '#',
          created_at: new Date().toISOString(),
        };
        writeDemoDocs([doc, ...readDemoDocs()]);
        return doc as unknown as Record<string, unknown>;
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['me', 'documents'] });
    },
  });
}

/* ------------------------------------------------------------------ */
/*  Admin hooks (HRMS portal)                                          */
/* ------------------------------------------------------------------ */

export function useAllDocuments() {
  return useQuery({
    queryKey: ['admin', 'documents'],
    queryFn: async () => {
      try {
        const res = await api.get('/documents/documents/');
        const rows = extract<Record<string, unknown>>(res);
        if (rows.length) return rows;
      } catch { /* fallback */ }
      return readDemoDocs() as unknown as Record<string, unknown>[];
    },
    staleTime: 60_000,
  });
}

export function useAdminUploadDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (formData: FormData) => {
      const res = await api.post('/documents/documents/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return extractOne<Record<string, unknown>>(res);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'documents'] });
      qc.invalidateQueries({ queryKey: ['me', 'documents'] });
    },
  });
}

export function useDeleteDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/documents/documents/${id}/`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'documents'] });
      qc.invalidateQueries({ queryKey: ['me', 'documents'] });
    },
  });
}

