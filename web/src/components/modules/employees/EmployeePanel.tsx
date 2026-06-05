import { UserPlus, FileLock2, Download, Upload, ArrowRight } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Button, toast } from '@components/ui';
import { AddEmployeeForm } from './AddEmployeeForm';
import { EmployeeCard } from './EmployeeCard';
import { EmployeeTable } from './EmployeeTable';
import { FilterBar } from './FilterBar';
import { QuickAddModal } from './QuickAddModal';
import { BulkUploadModal } from './BulkUploadModal';
import { useEmployeeList } from '@hooks/useEmployees';
import type { EmployeeListItem } from '@hooks/useEmployees';
import { motion, AnimatePresence } from 'framer-motion';
import { AdminSectionMenu, GenerateLetterPage } from './admin';

/* ================================================================== */
/*  Admin: Employee Directory (Enhanced)                              */
/* ================================================================== */

interface FilterState {
  search: string;
  category: string;
  employmentStatus: string;
  employeeFilter: string;
  department: string;
  designation: string;
  team: string;
  dateStart: string;
  dateEnd: string;
}

function EmployeeDirectory() {
  const [showQuickAdd, setShowQuickAdd] = useState(false);
  const [showBulkUpload, setShowBulkUpload] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'card'>('list');
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    category: '',
    employmentStatus: '',
    employeeFilter: '',
    department: '',
    designation: '',
    team: '',
    dateStart: '',
    dateEnd: '',
  });

  const { data: apiEmployees = [], isLoading } = useEmployeeList();

  const filteredEmployees = useMemo(() => {
    return apiEmployees.filter(emp => {
      const matchesSearch = !filters.search || 
        emp.full_name.toLowerCase().includes(filters.search.toLowerCase()) ||
        emp.employee_code.toLowerCase().includes(filters.search.toLowerCase()) ||
        emp.work_email.toLowerCase().includes(filters.search.toLowerCase());
      
      const matchesDept = !filters.department || emp.department === filters.department;
      const matchesDesig = !filters.designation || emp.designation === filters.designation;
      
      // Basic date range filtering
      let matchesDate = true;
      if (emp.date_of_joining) {
        const joinDate = new Date(emp.date_of_joining).getTime();
        if (filters.dateStart) {
          matchesDate = matchesDate && joinDate >= new Date(filters.dateStart).getTime();
        }
        if (filters.dateEnd) {
          matchesDate = matchesDate && joinDate <= new Date(filters.dateEnd).getTime();
        }
      }

      return matchesSearch && matchesDept && matchesDesig && matchesDate;
    });
  }, [apiEmployees, filters]);

  const handleExport = () => {
    toast.success('Exporting filtered employee data...');
  };

  const handleQuickAddSuccess = (employee: any) => {
    toast.success(`Employee ${employee.employeeName} added successfully!`);
    setShowQuickAdd(false);
  };

  const handleBulkUploadSuccess = (data: any) => {
    toast.success('Bulk upload completed successfully!');
    setShowBulkUpload(false);
  };

  if (showAddForm) {
    return <AddEmployeeForm onClose={() => setShowAddForm(false)} onSuccess={() => { }} />;
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header section */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-text-primary">
            Employee Directory
          </h2>
          <p className="text-xs text-text-tertiary">
            Manage your organization's workforce and identity details.
          </p>
        </div>

        <div className="flex items-center gap-3 flex-wrap">
          <Button 
            variant="secondary" 
            size="sm" 
            iconLeft={<Download className="h-4 w-4" />}
            onClick={handleExport}
          >
            Export
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            iconLeft={<UserPlus className="h-4 w-4" />}
            onClick={() => setShowQuickAdd(true)}
          >
            Quick Add
          </Button>
          <Button 
            variant="secondary" 
            size="sm" 
            iconLeft={<Upload className="h-4 w-4" />}
            onClick={() => setShowBulkUpload(true)}
          >
            Bulk Upload
          </Button>
          <Button 
            variant="primary" 
            size="sm" 
            iconLeft={<UserPlus className="h-4 w-4" />}
            onClick={() => setShowAddForm(true)}
          >
            Add Employee
          </Button>
        </div>
      </div>

      {/* Control Bar (Filters + View Toggle) */}
      <FilterBar 
        filters={filters} 
        onFilterChange={setFilters} 
        viewMode={viewMode} 
        onViewModeChange={setViewMode} 
      />

      {/* Main Content */}
      <div className="min-h-[400px]">
        {isLoading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-48 animate-pulse rounded-2xl bg-surface-200 dark:bg-white/5" />
            ))}
          </div>
        ) : filteredEmployees.length > 0 ? (
          <AnimatePresence mode="wait">
            {viewMode === 'list' ? (
              <motion.div
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <EmployeeTable data={filteredEmployees} />
              </motion.div>
            ) : (
              <motion.div
                key="grid"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3"
              >
                {filteredEmployees.map((emp) => (
                  <EmployeeCard key={emp.id} employee={emp} />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-3xl border-2 border-dashed border-surface-200 py-20 text-center dark:border-white/5">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-50 dark:bg-white/5">
              <FileLock2 className="h-8 w-8 text-text-tertiary" />
            </div>
            <p className="mt-4 font-bold text-text-primary">No matching employees</p>
            <p className="mt-1 text-sm text-text-tertiary">Try adjusting your filters or search terms.</p>
            <Button 
              variant="ghost" 
              size="sm" 
              className="mt-4"
              onClick={() => setFilters({
                search: '',
                category: '',
                employmentStatus: '',
                employeeFilter: '',
                department: '',
                designation: '',
                team: '',
                dateStart: '',
                dateEnd: '',
              })}
            >
              Clear all filters
            </Button>
          </div>
        )}
      </div>

      {/* Modals */}
      <QuickAddModal 
        isOpen={showQuickAdd} 
        onClose={() => setShowQuickAdd(false)}
        onSuccess={handleQuickAddSuccess}
      />
      <BulkUploadModal 
        isOpen={showBulkUpload} 
        onClose={() => setShowBulkUpload(false)}
        onSuccess={handleBulkUploadSuccess}
      />
    </div>
  );
}

/* ================================================================== */
/*  Admin Section View                                                */
/* ================================================================== */

function AdminSection() {
  const [selectedAdminPage, setSelectedAdminPage] = useState<string>('generate-letter');

  const renderAdminPage = () => {
    switch (selectedAdminPage) {
      case 'generate-letter':
      default:
        return <GenerateLetterPage />;
    }
  };

  return (
    <div className="flex gap-6 p-6">
      {/* Sidebar Menu */}
      <div className="w-64 flex-shrink-0">
        <div className="sticky top-6 rounded-lg border border-surface-200 dark:border-white/8 bg-surface-0 dark:bg-white/3 p-4">
          <AdminSectionMenu 
            selectedItem={selectedAdminPage}
            onSelectItem={(itemId, route) => setSelectedAdminPage(itemId)}
          />
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 min-h-[600px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={selectedAdminPage}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {renderAdminPage()}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ================================================================== */
/*  Main: Employee Panel with Dual Views                              */
/* ================================================================== */

export function EmployeePanel() {
  const [activeView, setActiveView] = useState<'information' | 'admin'>('information');

  return (
    <div className="space-y-0">
      {/* Tab Navigation */}
      <div className="flex gap-1 border-b border-surface-200 dark:border-white/10 px-6 pt-6">
        {[
          { id: 'information', label: 'Information' },
          { id: 'admin', label: 'Admin' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveView(tab.id as 'information' | 'admin')}
            className={`px-4 py-3 text-sm font-medium border-b-2 transition-all ${
              activeView === tab.id
                ? 'border-brand-500 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        {activeView === 'information' ? (
          <motion.div
            key="information"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <EmployeeDirectory />
          </motion.div>
        ) : (
          <motion.div
            key="admin"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <AdminSection />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
