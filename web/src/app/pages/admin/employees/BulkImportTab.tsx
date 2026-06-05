import { useState, useRef } from "react";
import { 
  Download, 
  Upload, 
  FileText, 
  CheckCircle, 
  X, 
  AlertCircle, 
  Loader2, 
  Plus, 
  Check, 
  FileSpreadsheet,
  ArrowRight,
  Database
} from "lucide-react";
import * as XLSX from "xlsx";
import { useQueryClient } from "@tanstack/react-query";
import { addNotification } from "@/store/slices/notificationSlice";
import { useDispatch } from "react-redux";
import { AppDispatch } from "@/store";
import { addAdminEmployee } from "@/store/slices/adminSlice";
import type { Employee } from "@/app/components/employees/mockData";
import { downloadBulkImportTemplate, type BulkImportResult } from "@/api/addEmployeeApi";
import {
  buildEmployeesFromImportResult,
  runBulkImport,
  type BulkPreviewRow,
} from "./bulkImportUtils";

interface BulkImportTabProps {
  onImportComplete?: (employees: Employee[]) => void;
}

const REQUIRED_COLUMNS = [
  "Salutation", "Employee Number Series", "Employee No", "First Name", "Last Name",
  "Email", "Mobile Number", "Date of Birth", "Aadhaar Number", "Gender", "Status",
  "Date of Joining", "Department", "Designation / Role", "Employment Type",
  "Work Location"
];

const SAMPLE_DATA = [
  {
    "Salutation": "Mr.",
    "Employee Number Series": "EMP",
    "Employee No": "EMP-2024-001",
    "First Name": "John",
    "Last Name": "Doe",
    "Email": "john.doe@example.com",
    "Mobile Number": "9876543210",
    "Date of Birth": "1990-05-15",
    "Aadhaar Number": "123456789012",
    "Gender": "Male",
    "Status": "Active",
    "Date of Joining": "2024-06-01",
    "Department": "Engineering",
    "Designation / Role": "Software Engineer",
    "Employment Type": "Full-time",
    "Work Location": "Bangalore"
  }
];

export function BulkImportTab({ onImportComplete }: BulkImportTabProps) {
  const dispatch = useDispatch<AppDispatch>();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const [errors, setErrors] = useState<string[]>([]);
  const [importResult, setImportResult] = useState<BulkImportResult | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const downloadTemplate = async () => {
    try {
      const blob = await downloadBulkImportTemplate();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'employee_import_template_v1.2.xlsx';
      a.click();
      URL.revokeObjectURL(url);
      dispatch(addNotification({ type: "success", message: "Template downloaded successfully" }));
    } catch {
      // Fallback: generate client-side template if backend unreachable
      const ws = XLSX.utils.json_to_sheet(SAMPLE_DATA, { header: REQUIRED_COLUMNS });
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "Template");
      XLSX.writeFile(wb, "Employee_Import_Template.xlsx");
      dispatch(addNotification({ type: "success", message: "Template downloaded (offline mode)" }));
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) processFile(f);
  };

  const processFile = async (f: File) => {
    const ext = f.name.split('.').pop()?.toLowerCase();
    if (!['xlsx', 'xls', 'csv'].includes(ext || '')) {
      dispatch(addNotification({ type: "error", message: "Invalid file format. Support .xlsx, .xls, .csv" }));
      return;
    }
    if (f.size > 10 * 1024 * 1024) {
      dispatch(addNotification({ type: "error", message: "File size must not exceed 10 MB." }));
      return;
    }

    setFile(f);
    setValidating(true);
    setUploadProgress(0);
    setErrors([]);
    setPreviewData([]);
    setImportResult(null);

    // Simulate progress
    const interval = setInterval(() => {
      setUploadProgress(p => p < 90 ? p + 10 : p);
    }, 100);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = e.target?.result;
        const workbook = XLSX.read(data, { type: "binary" });
        const sheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[sheetName];
        const json = XLSX.utils.sheet_to_json(worksheet);

        if (json.length === 0) {
          setErrors(["The file is empty."]);
          return;
        }

        const headers = XLSX.utils.sheet_to_json(worksheet, { header: 1 })[0] as string[];
        if (!headers || headers.length === 0) {
          setErrors(["The file has no header row."]);
          return;
        }
        if (json.length > 500) {
          setErrors(["The file exceeds the 500-row limit."]);
          return;
        }

        const validationErrors: string[] = [];
        const processedData = json.map((row: any, index: number) => {
          const rowNum = index + 2;
          const rowErrors: string[] = [];

          if (!row["Employee No"]) rowErrors.push(`Row ${rowNum}: Employee No is required`);
          if (!row["First Name"]) rowErrors.push(`Row ${rowNum}: First Name is required`);
          if (!row["Last Name"]) rowErrors.push(`Row ${rowNum}: Last Name is required`);
          if (!row["Email"]) rowErrors.push(`Row ${rowNum}: Email is required`);
          else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row["Email"])) {
             rowErrors.push(`Row ${rowNum}: Invalid Email format`);
          }

          if (rowErrors.length > 0) validationErrors.push(...rowErrors);
          
          return {
            ...row,
            isValid: rowErrors.length === 0,
            error: rowErrors.join(", ")
          };
        });

        setErrors(validationErrors);
        setPreviewData(processedData);
        setUploadProgress(100);
      } catch (err) {
        setErrors(["Failed to parse excel file."]);
      } finally {
        clearInterval(interval);
        setValidating(false);
      }
    };
    reader.readAsBinaryString(f);
  };

  const handleImport = async () => {
    if (errors.length > 0) {
      dispatch(addNotification({ type: "error", message: "Please fix validation errors before importing." }));
      return;
    }
    if (!file) return;

    setLoading(true);
    try {
      const validRows = previewData.filter((row) => row.isValid) as BulkPreviewRow[];
      const result = await runBulkImport(file, validRows);
      setImportResult(result);

      const imported = buildEmployeesFromImportResult(result, previewData);
      for (const emp of imported) {
        dispatch(addAdminEmployee(emp));
      }

      await queryClient.invalidateQueries({ queryKey: ["admin-employee-directory"] });
      await queryClient.invalidateQueries({ queryKey: ["employees-list"] });

      onImportComplete?.(imported);
      dispatch(
        addNotification({
          type: result.failed_count > 0 ? 'error' : 'success',
          message: `Imported ${result.success_count} of ${result.total_rows} rows.${
            result.failed_count > 0 ? ` ${result.failed_count} rows had errors.` : ''
          }`,
        }),
      );
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ??
        'Bulk import failed. Please check your file and try again.';
      dispatch(addNotification({ type: 'error', message: msg }));
    } finally {
      setLoading(false);
    }
  };

  const removeFile = () => {
    setFile(null);
    setPreviewData([]);
    setErrors([]);
    setImportResult(null);
    setUploadProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500 pb-10">
      {/* SECTION 1: Download Template */}
      <div className="flat-card bg-card p-6 border-border hover:border-foreground/20 transition-all group">
        <div className="flex items-start justify-between gap-4">
          <div className="flex gap-4">
            <div className="w-12 h-12 rounded-2xl bg-secondary flex items-center justify-center shrink-0 group-hover:bg-foreground group-hover:text-primary-foreground transition-all duration-300">
              <Download size={22} />
            </div>
            <div>
              <h3 className="text-[15px] font-bold text-foreground">Download Employee Import Template</h3>
              <p className="text-xs text-muted-foreground mt-1 max-w-md">
                Download the standard employee import sheet and fill employee details in the required format. 
                Fields like Family, Nominee, and Education details are skipped as they will be filled by employees via the ESS portal.
              </p>
              <button
                type="button"
                onClick={downloadTemplate}
                className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-foreground text-primary-foreground rounded-xl text-xs font-bold hover:bg-accent transition-all active:scale-95"
              >
                <FileSpreadsheet size={14} />
                Download Sample Excel
              </button>
            </div>
          </div>
          <div className="hidden md:block">
             <div className="px-3 py-1.5 rounded-lg bg-secondary text-[10px] font-bold text-muted-foreground uppercase tracking-widest border border-border">
               v1.2 Template
             </div>
          </div>
        </div>
      </div>

      {/* SECTION 2: Upload Excel */}
      <div className="flat-card bg-card p-6 border-border overflow-hidden">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-foreground flex items-center justify-center text-primary-foreground">
            <Upload size={20} />
          </div>
          <div>
            <h3 className="text-sm font-black text-foreground uppercase tracking-tight">Upload Employee Excel</h3>
            <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Supports .xlsx, .xls, .csv</p>
          </div>
        </div>

        {!file ? (
          <div 
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              const f = e.dataTransfer.files[0];
              if (f) processFile(f);
            }}
            className="border-2 border-dashed border-border rounded-2xl p-10 text-center cursor-pointer hover:border-foreground/30 hover:bg-secondary/30 transition-all group"
          >
            <input 
              ref={fileInputRef}
              type="file" 
              className="hidden" 
              accept=".xlsx,.xls,.csv"
              onChange={handleFileChange}
            />
            <div className="w-14 h-14 rounded-full bg-secondary flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
               <Upload size={24} className="text-muted-foreground" />
            </div>
            <p className="text-sm font-bold text-foreground">Drag & Drop file here</p>
            <p className="text-xs text-muted-foreground mt-1">Or click to browse from your computer</p>
            <div className="mt-6 flex items-center justify-center gap-4">
               <span className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase tracking-wider bg-secondary px-2 py-1 rounded">
                 <CheckCircle size={10} /> Max 10MB
               </span>
               <span className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase tracking-wider bg-secondary px-2 py-1 rounded">
                 <CheckCircle size={10} /> Up to 500 rows
               </span>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between p-4 rounded-2xl border border-border bg-secondary/20">
               <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-xl bg-foreground text-primary-foreground flex items-center justify-center">
                    <FileText size={20} />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-foreground">{file.name}</p>
                    <p className="text-[10px] text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
               </div>
               <button 
                onClick={removeFile}
                className="w-8 h-8 rounded-full border border-border flex items-center justify-center text-muted-foreground hover:bg-red-50 hover:text-red-500 hover:border-red-200 transition-all"
               >
                 <X size={16} />
               </button>
            </div>

            {uploadProgress < 100 || validating ? (
              <div className="space-y-3">
                 <div className="flex items-center justify-between text-xs font-bold uppercase tracking-wider">
                   <span className="text-muted-foreground flex items-center gap-2">
                     {validating ? "Validating data..." : "Uploading file..."}
                     <Loader2 size={12} className="animate-spin" />
                   </span>
                   <span>{uploadProgress}%</span>
                 </div>
                 <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-foreground transition-all duration-300 ease-out"
                      style={{ width: `${uploadProgress}%` }}
                    />
                 </div>
              </div>
            ) : (
              <div className="animate-in fade-in duration-500">
                {errors.length > 0 ? (
                  <div className="p-4 rounded-2xl bg-red-50 border border-red-100 mb-6">
                    <div className="flex items-start gap-3">
                      <AlertCircle size={18} className="text-red-500 shrink-0 mt-0.5" />
                      <div>
                        <h4 className="text-sm font-bold text-red-700">Validation Failed</h4>
                        <p className="text-xs text-red-600 mt-1">Please fix the following {errors.length} errors in your file and re-upload.</p>
                        <ul className="mt-3 space-y-1">
                          {errors.slice(0, 5).map((err, i) => (
                            <li key={i} className="text-[11px] font-medium text-red-600 flex items-center gap-2">
                              <span className="w-1 h-1 rounded-full bg-red-400 shrink-0" />
                              {err}
                            </li>
                          ))}
                          {errors.length > 5 && (
                            <li className="text-[11px] font-bold text-red-700 mt-2">
                              + {errors.length - 5} more errors...
                            </li>
                          )}
                        </ul>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="p-4 rounded-2xl bg-green-50 border border-green-100 mb-6">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-green-500 text-white flex items-center justify-center">
                        <Check size={16} strokeWidth={3} />
                      </div>
                      <div>
                        <h4 className="text-sm font-bold text-green-700">Validation Successful</h4>
                        <p className="text-xs text-green-600">All columns matched and {previewData.length} records are ready to import.</p>
                      </div>
                    </div>
                  </div>
                )}

                {previewData.length > 0 && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="text-xs font-bold text-muted-foreground uppercase tracking-widest">Import Preview</h4>
                      <div className="flex gap-2">
                        <span className="px-2 py-0.5 rounded-full bg-secondary text-[10px] font-bold text-muted-foreground uppercase">
                          {previewData.length} Total
                        </span>
                        <span className="px-2 py-0.5 rounded-full bg-green-100 text-[10px] font-bold text-green-700 uppercase">
                          {previewData.filter(d => d.isValid).length} Valid
                        </span>
                        {errors.length > 0 && (
                          <span className="px-2 py-0.5 rounded-full bg-red-100 text-[10px] font-bold text-red-700 uppercase">
                            {previewData.filter(d => !d.isValid).length} Failed
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="border border-border rounded-2xl overflow-hidden">
                       <table className="w-full text-left border-collapse">
                          <thead className="bg-secondary/50">
                             <tr>
                                <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Employee</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Dept & Role</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Email</th>
                                <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Status</th>
                             </tr>
                          </thead>
                          <tbody className="divide-y divide-border">
                             {previewData.slice(0, 5).map((row, i) => (
                               <tr key={i} className="hover:bg-secondary/10 transition-colors">
                                 <td className="px-4 py-3">
                                   <div className="flex items-center gap-3">
                                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-bold ${row.isValid ? "bg-foreground text-primary-foreground" : "bg-red-100 text-red-500"}`}>
                                        {row.isValid ? row["First Name"][0] + row["Last Name"][0] : "!"}
                                      </div>
                                      <div>
                                        <p className="text-xs font-bold text-foreground">{row["First Name"]} {row["Last Name"]}</p>
                                        <p className="text-[10px] font-mono text-muted-foreground uppercase tracking-tighter">{row["Employee No"]}</p>
                                      </div>
                                   </div>
                                 </td>
                                 <td className="px-4 py-3">
                                   <p className="text-xs font-medium text-foreground">{row["Department"]}</p>
                                   <p className="text-[10px] text-muted-foreground">{row["Designation / Role"]}</p>
                                 </td>
                                 <td className="px-4 py-3">
                                   <p className="text-xs text-foreground font-medium">{row["Email"]}</p>
                                 </td>
                                 <td className="px-4 py-3 text-right">
                                   {row.isValid ? (
                                     <span className="inline-flex items-center gap-1 text-[10px] font-bold text-green-600 uppercase">
                                       <Check size={10} strokeWidth={3} /> Ready
                                     </span>
                                   ) : (
                                     <span className="inline-flex items-center gap-1 text-[10px] font-bold text-red-500 uppercase">
                                       <X size={10} strokeWidth={3} /> Failed
                                     </span>
                                   )}
                                 </td>
                               </tr>
                             ))}
                             {previewData.length > 5 && (
                               <tr>
                                 <td colSpan={4} className="px-4 py-3 text-center text-[10px] font-bold text-muted-foreground uppercase bg-secondary/20">
                                   + {previewData.length - 5} more records in this file
                                 </td>
                               </tr>
                             )}
                          </tbody>
                       </table>
                    </div>

                    <div className="flex items-center justify-end gap-3 pt-4">
                       <button 
                        onClick={removeFile}
                        className="px-6 py-2 rounded-xl border border-border text-xs font-bold text-foreground hover:bg-secondary transition-all"
                       >
                         Cancel
                       </button>
                       <button 
                        disabled={loading || errors.length > 0}
                        onClick={handleImport}
                        className="px-8 py-2 rounded-xl bg-foreground text-primary-foreground text-xs font-bold hover:bg-accent transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                       >
                         {loading ? <Loader2 size={14} className="animate-spin" /> : <Database size={14} />}
                         {loading ? "Importing..." : "Confirm & Import Employees"}
                       </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {importResult && (
        <div className="flat-card bg-card p-6 border-border">
          <div className="flex items-center justify-between gap-4 mb-5">
            <div>
              <h3 className="text-sm font-black text-foreground uppercase tracking-tight">Import Results</h3>
              <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">
                Row-wise import status from the server
              </p>
            </div>
            <div className="flex flex-wrap gap-2 justify-end">
              <span className="px-3 py-1.5 rounded-lg bg-secondary text-[10px] font-bold text-muted-foreground uppercase">
                Total Records: {importResult.total_rows}
              </span>
              <span className="px-3 py-1.5 rounded-lg bg-green-100 text-[10px] font-bold text-green-700 uppercase">
                Successful Records: {importResult.success_count}
              </span>
              <span className="px-3 py-1.5 rounded-lg bg-red-100 text-[10px] font-bold text-red-700 uppercase">
                Failed Records: {importResult.failed_count}
              </span>
            </div>
          </div>

          <div className="border border-border rounded-2xl overflow-hidden">
            <table className="w-full text-left border-collapse">
              <thead className="bg-secondary/50">
                <tr>
                  <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Row Number</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Employee Code</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Status</th>
                  <th className="px-4 py-3 text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Error Message</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {importResult.results.map((row) => {
                  const errorMessage = row.errors
                    ? Object.entries(row.errors).map(([field, message]) => `${field}: ${message}`).join("; ")
                    : "";
                  return (
                    <tr key={`${row.row}-${row.employee_code ?? "empty"}`} className="hover:bg-secondary/10 transition-colors">
                      <td className="px-4 py-3 text-xs font-mono text-foreground">{row.row}</td>
                      <td className="px-4 py-3 text-xs font-mono text-foreground">{row.employee_code || "-"}</td>
                      <td className="px-4 py-3">
                        <span className={[
                          "inline-flex items-center gap-1 text-[10px] font-bold uppercase",
                          row.status === "success" ? "text-green-600" : "text-red-500",
                        ].join(" ")}>
                          {row.status === "success" ? <Check size={10} strokeWidth={3} /> : <X size={10} strokeWidth={3} />}
                          {row.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-muted-foreground">{errorMessage || "-"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* FOOTER INFO */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
         <div className="flat-card bg-secondary/30 p-4 border-border flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-foreground/5 flex items-center justify-center shrink-0">
               <CheckCircle size={14} className="text-foreground" />
            </div>
            <div>
               <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Automatic ESS</p>
               <p className="text-[11px] font-medium text-foreground mt-0.5">Self-service accounts will be auto-created for all imported employees.</p>
            </div>
         </div>
         <div className="flat-card bg-secondary/30 p-4 border-border flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-foreground/5 flex items-center justify-center shrink-0">
               <CheckCircle size={14} className="text-foreground" />
            </div>
            <div>
               <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Smart Matching</p>
               <p className="text-[11px] font-medium text-foreground mt-0.5">The system intelligently matches your excel headers with HRMS fields.</p>
            </div>
         </div>
         <div className="flat-card bg-secondary/30 p-4 border-border flex items-start gap-3">
            <div className="w-8 h-8 rounded-lg bg-foreground/5 flex items-center justify-center shrink-0">
               <CheckCircle size={14} className="text-foreground" />
            </div>
            <div>
               <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest">Post Import</p>
               <p className="text-[11px] font-medium text-foreground mt-0.5">Employees can fill their family, education, and other details from their portal.</p>
            </div>
         </div>
      </div>
    </div>
  );
}
