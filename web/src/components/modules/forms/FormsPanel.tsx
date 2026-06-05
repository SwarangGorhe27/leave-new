import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, Eye, CheckCircle2, FileText, Users, BarChart2, ChevronRight, Send, X } from 'lucide-react';
import { cn } from '@utils/utils';
import {
  useForms, useCreateForm, usePublishForm, useCloseForm, useDeleteForm,
  useFormSubmissions, useSubmitForm,
  type FormDefinition, type FormField,
} from '@hooks/useForms';
import { useUIStore } from '@store/uiStore';

// ─── Status badge ────────────────────────────────────────────────────

const STATUS_STYLES: Record<string, string> = {
  DRAFT: 'bg-surface-100 text-surface-600 dark:bg-white/10 dark:text-white/50',
  PUBLISHED: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  CLOSED: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
};

// ─── Form submission renderer ─────────────────────────────────────────

function FormRenderer({ form, onClose }: { form: FormDefinition; onClose: () => void }) {
  const submit = useSubmitForm();
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const [submitted, setSubmitted] = useState(false);

  const sorted = [...form.fields].sort((a, b) => a.sort_order - b.sort_order);

  function handleSubmit() {
    submit.mutate(
      { formId: form.id, data: answers },
      { onSuccess: () => setSubmitted(true) },
    );
  }

  if (submitted) {
    return (
      <div className="flex flex-col items-center gap-4 py-12 text-center">
        <CheckCircle2 className="h-12 w-12 text-emerald-500" />
        <h3 className="text-lg font-semibold text-surface-900 dark:text-white">Response submitted!</h3>
        <p className="text-sm text-surface-500 dark:text-white/40">Thank you for completing "{form.title}".</p>
        <button onClick={onClose} className="mt-2 rounded-xl border border-surface-200 px-4 py-2 text-sm dark:border-white/10">
          Close
        </button>
      </div>
    );
  }

  const inputCls = 'w-full rounded-xl border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  return (
    <div className="space-y-5 p-1">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-base font-semibold text-surface-900 dark:text-white">{form.title}</h3>
          {form.description && <p className="mt-0.5 text-sm text-surface-500 dark:text-white/40">{form.description}</p>}
        </div>
        <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg text-surface-400 hover:bg-surface-100 dark:hover:bg-white/10">
          <X className="h-4 w-4" />
        </button>
      </div>

      {sorted.length === 0 ? (
        <p className="text-sm text-surface-400 dark:text-white/30">This form has no fields configured.</p>
      ) : (
        <div className="space-y-4">
          {sorted.map((field: FormField) => (
            <div key={field.id} className="space-y-1.5">
              <label className="text-sm font-medium text-surface-800 dark:text-white/80">
                {field.label}{field.is_required && <span className="ml-1 text-red-500">*</span>}
              </label>
              {field.help_text && <p className="text-xs text-surface-400 dark:text-white/30">{field.help_text}</p>}

              {(field.field_type === 'TEXT' || field.field_type === 'EMAIL' || field.field_type === 'NUMBER') && (
                <input
                  type={field.field_type === 'EMAIL' ? 'email' : field.field_type === 'NUMBER' ? 'number' : 'text'}
                  placeholder={field.placeholder}
                  value={String(answers[field.id] ?? '')}
                  onChange={(e) => setAnswers((a) => ({ ...a, [field.id]: e.target.value }))}
                  className={inputCls}
                />
              )}
              {field.field_type === 'DATE' && (
                <input
                  type="date"
                  value={String(answers[field.id] ?? '')}
                  onChange={(e) => setAnswers((a) => ({ ...a, [field.id]: e.target.value }))}
                  className={inputCls}
                />
              )}
              {field.field_type === 'TEXTAREA' && (
                <textarea
                  placeholder={field.placeholder}
                  rows={3}
                  value={String(answers[field.id] ?? '')}
                  onChange={(e) => setAnswers((a) => ({ ...a, [field.id]: e.target.value }))}
                  className={cn(inputCls, 'resize-none')}
                />
              )}
              {field.field_type === 'SELECT' && (
                <select
                  value={String(answers[field.id] ?? '')}
                  onChange={(e) => setAnswers((a) => ({ ...a, [field.id]: e.target.value }))}
                  className={inputCls}
                >
                  <option value="">Select an option</option>
                  {field.options.map((opt) => <option key={opt} value={opt}>{opt}</option>)}
                </select>
              )}
              {field.field_type === 'CHECKBOX' && (
                <label className="flex items-center gap-2 text-sm text-surface-700 dark:text-white/60">
                  <input
                    type="checkbox"
                    checked={Boolean(answers[field.id])}
                    onChange={(e) => setAnswers((a) => ({ ...a, [field.id]: e.target.checked }))}
                    className="h-4 w-4 rounded"
                  />
                  {field.placeholder || field.label}
                </label>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="flex justify-end pt-2">
        <button
          onClick={handleSubmit}
          disabled={submit.isPending}
          className="flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          <Send className="h-4 w-4" />
          {submit.isPending ? 'Submitting…' : 'Submit Response'}
        </button>
      </div>
    </div>
  );
}

// ─── Submissions view ─────────────────────────────────────────────────

function SubmissionsView({ form, onBack }: { form: FormDefinition; onBack: () => void }) {
  const { data: submissions = [], isLoading } = useFormSubmissions(form.id);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button onClick={onBack} className="flex items-center gap-1 text-sm text-surface-500 hover:text-brand-600 dark:text-white/40 dark:hover:text-brand-400">
          ← Back
        </button>
        <h3 className="text-sm font-semibold text-surface-900 dark:text-white">{form.title} — Submissions ({form.submission_count})</h3>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1, 2, 3].map((i) => <div key={i} className="h-14 animate-pulse rounded-xl bg-surface-100 dark:bg-white/10" />)}</div>
      ) : submissions.length === 0 ? (
        <div className="flex flex-col items-center py-16 text-center">
          <FileText className="h-10 w-10 text-surface-300 dark:text-white/20" />
          <p className="mt-3 text-sm text-surface-500 dark:text-white/40">No submissions yet.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {submissions.map((sub) => (
            <div key={sub.id} className="rounded-xl border border-surface-200/70 bg-surface-0 px-4 py-3 dark:border-white/10 dark:bg-white/5">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-surface-800 dark:text-white/80">
                  {sub.is_anonymous ? 'Anonymous' : (sub.employee_code || sub.employee)}
                </span>
                <span className="text-xs text-surface-400 dark:text-white/30">
                  {new Date(sub.submitted_at).toLocaleString('en-IN')}
                </span>
              </div>
              <details className="mt-1">
                <summary className="cursor-pointer text-xs text-brand-600 dark:text-brand-400">View response</summary>
                <pre className="mt-2 overflow-auto rounded-lg bg-surface-50 p-2 text-xs text-surface-700 dark:bg-white/5 dark:text-white/60">
                  {JSON.stringify(sub.data, null, 2)}
                </pre>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Main Forms Panel ─────────────────────────────────────────────────

export function FormsPanel() {
  const portal = useUIStore((s) => s.portal);
  const activeModule = useUIStore((s) => s.activeModule);
  const rawView = useUIStore((s) => s.moduleViews[activeModule] ?? 'employee');
  const isAdmin = portal === 'hrms' && rawView === 'admin';

  const { data: forms = [], isLoading } = useForms();
  const createForm = useCreateForm();
  const publishForm = usePublishForm();
  const closeForm = useCloseForm();
  const deleteForm = useDeleteForm();

  const [showCreate, setShowCreate] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [selectedForm, setSelectedForm] = useState<FormDefinition | null>(null);
  const [viewSubs, setViewSubs] = useState<FormDefinition | null>(null);

  function handleCreate() {
    if (!newTitle.trim()) return;
    createForm.mutate(
      { title: newTitle.trim(), description: newDesc.trim() || undefined },
      { onSuccess: () => { setShowCreate(false); setNewTitle(''); setNewDesc(''); } },
    );
  }

  // If filling a form (employee view)
  if (selectedForm) {
    return <FormRenderer form={selectedForm} onClose={() => setSelectedForm(null)} />;
  }
  if (viewSubs) {
    return <SubmissionsView form={viewSubs} onBack={() => setViewSubs(null)} />;
  }

  const inputCls = 'w-full rounded-xl border border-surface-200 bg-surface-0 px-3 py-2 text-sm text-surface-900 placeholder-surface-400 focus:border-brand-400 focus:outline-none dark:border-white/10 dark:bg-white/5 dark:text-white dark:placeholder-white/30';

  // Filter for employee: only PUBLISHED forms
  const visibleForms = isAdmin ? forms : forms.filter((f) => f.status === 'PUBLISHED');

  return (
    <div className="space-y-4 p-1">
      {/* Admin toolbar */}
      {isAdmin && (
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-surface-900 dark:text-white">
            All Forms <span className="ml-1 text-surface-400 dark:text-white/30">({forms.length})</span>
          </h3>
          <button
            onClick={() => setShowCreate(!showCreate)}
            className="flex items-center gap-1.5 rounded-xl bg-brand-600 px-3 py-2 text-xs font-medium text-white hover:bg-brand-700"
          >
            <Plus className="h-3.5 w-3.5" /> New Form
          </button>
        </div>
      )}

      {/* Create form */}
      <AnimatePresence>
        {showCreate && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden rounded-2xl border border-brand-200 bg-brand-50/30 p-4 dark:border-brand-800/40 dark:bg-brand-900/10"
          >
            <h4 className="mb-3 text-sm font-semibold text-surface-900 dark:text-white">Create New Form</h4>
            <div className="space-y-3">
              <input type="text" placeholder="Form title *" value={newTitle} onChange={(e) => setNewTitle(e.target.value)} className={inputCls} />
              <textarea placeholder="Description (optional)" value={newDesc} onChange={(e) => setNewDesc(e.target.value)} rows={2} className={cn(inputCls, 'resize-none')} />
              <div className="flex justify-end gap-2">
                <button onClick={() => setShowCreate(false)} className="rounded-xl border border-surface-200 px-4 py-2 text-sm text-surface-600 dark:border-white/10 dark:text-white/50">Cancel</button>
                <button onClick={handleCreate} disabled={!newTitle.trim() || createForm.isPending} className="rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50">
                  {createForm.isPending ? 'Creating…' : 'Create'}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Forms list */}
      {isLoading ? (
        <div className="space-y-3">{[1, 2, 3].map((i) => <div key={i} className="h-20 animate-pulse rounded-xl bg-surface-100 dark:bg-white/10" />)}</div>
      ) : visibleForms.length === 0 ? (
        <div className="flex flex-col items-center py-16 text-center">
          <FileText className="h-10 w-10 text-surface-300 dark:text-white/20" />
          <p className="mt-3 text-sm font-medium text-surface-700 dark:text-white/60">
            {isAdmin ? 'No forms yet' : 'No forms available'}
          </p>
          <p className="mt-1 text-xs text-surface-400 dark:text-white/30">
            {isAdmin ? 'Create your first form using the button above.' : 'No published forms assigned to you yet.'}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {visibleForms.map((form) => (
            <div key={form.id} className="rounded-2xl border border-surface-200/70 bg-surface-0 p-4 shadow-xs dark:border-white/10 dark:bg-white/5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-medium text-surface-900 dark:text-white truncate">{form.title}</p>
                    <span className={cn('shrink-0 rounded-full px-2 py-0.5 text-xs font-medium', STATUS_STYLES[form.status])}>
                      {form.status}
                    </span>
                  </div>
                  {form.description && (
                    <p className="mt-0.5 text-xs text-surface-500 dark:text-white/40 truncate">{form.description}</p>
                  )}
                  <div className="mt-2 flex items-center gap-4 text-xs text-surface-400 dark:text-white/30">
                    <span className="flex items-center gap-1"><FileText className="h-3 w-3" /> {form.fields?.length ?? 0} fields</span>
                    <span className="flex items-center gap-1"><Users className="h-3 w-3" /> {form.submission_count} responses</span>
                    {form.created_at && <span>{new Date(form.created_at).toLocaleDateString('en-IN')}</span>}
                  </div>
                </div>

                <div className="flex shrink-0 flex-col items-end gap-1.5">
                  {/* Employee: fill form */}
                  {!isAdmin && form.status === 'PUBLISHED' && (
                    <button
                      onClick={() => setSelectedForm(form)}
                      className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-brand-700"
                    >
                      Fill Form <ChevronRight className="h-3 w-3" />
                    </button>
                  )}

                  {/* Admin: actions */}
                  {isAdmin && (
                    <div className="flex gap-1.5">
                      <button
                        onClick={() => setViewSubs(form)}
                        className="flex items-center gap-1 rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs text-surface-700 hover:border-brand-400 hover:text-brand-600 dark:border-white/10 dark:text-white/60"
                      >
                        <BarChart2 className="h-3 w-3" /> Submissions
                      </button>
                      {form.status === 'DRAFT' && (
                        <button
                          onClick={() => publishForm.mutate(form.id)}
                          className="flex items-center gap-1 rounded-lg bg-emerald-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-emerald-700"
                        >
                          <Eye className="h-3 w-3" /> Publish
                        </button>
                      )}
                      {form.status === 'PUBLISHED' && (
                        <button
                          onClick={() => closeForm.mutate(form.id)}
                          className="flex items-center gap-1 rounded-lg bg-amber-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-amber-700"
                        >
                          Close
                        </button>
                      )}
                      {form.status === 'DRAFT' && (
                        <button
                          onClick={() => deleteForm.mutate(form.id)}
                          className="rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs text-red-600 hover:bg-red-50 dark:border-white/10 dark:hover:bg-red-900/20"
                        >
                          Delete
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
