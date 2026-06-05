import { FileDigit, Upload } from 'lucide-react';
import { Badge, Button } from '@components/ui';
import type { Employee } from '@/types/employee';

interface EmployeeDocumentsTabProps {
  employee: Employee;
}

export function EmployeeDocumentsTab({ employee }: EmployeeDocumentsTabProps) {
  return (
    <div className="space-y-5">
      <section className="surface-card border-dashed p-5">
        <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-surface-300/70 bg-surface-50 px-6 py-10 text-center dark:border-white/10 dark:bg-white/[0.03]">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-brand-50 text-brand-600 dark:bg-brand-500/10 dark:text-brand-200">
            <Upload className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-surface-900 dark:text-white">Drag files here or browse</h3>
            <p className="mt-1 text-sm text-surface-600 dark:text-white/55">Upload identity proofs, compliance documents, and signed policies.</p>
          </div>
          <Button variant="secondary">Browse files</Button>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {employee.documents.map((document) => (
          <article key={document.id} className="surface-card p-4">
            <div className="flex items-start justify-between gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-200">
                <FileDigit className="h-5 w-5" />
              </div>
              <Badge variant={document.status === 'Valid' ? 'success' : document.status === 'Expiring Soon' ? 'warning' : 'danger'}>
                {document.status}
              </Badge>
            </div>
            <h3 className="mt-5 text-sm font-semibold text-surface-900 dark:text-white">{document.name}</h3>
            <p className="mt-1 text-xs text-surface-500 dark:text-white/40">{document.type}</p>
            <div className="mt-5 flex items-center justify-between text-xs text-surface-600 dark:text-white/50">
              <span>Uploaded {document.uploadedAt}</span>
              {document.expiresAt ? <span>Expires {document.expiresAt}</span> : <span>Permanent</span>}
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
