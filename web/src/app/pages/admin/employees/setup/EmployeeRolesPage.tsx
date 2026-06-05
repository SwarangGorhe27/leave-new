import React, { useState, useMemo } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/store/index";
import { 
  addRole, deleteRole, saveMapping, 
  Role, EmployeeRoleMapping 
} from "@/store/slices/roleFilterSlice";
import { 
  UserCog, Plus, Shield, ShieldCheck, ChevronRight, 
  Search, Settings, Network, Edit, Trash2, Check, UserCheck, X 
} from "lucide-react";
import { Button } from "@/app/components/ui/button";
import { employees } from "../../../../components/employees/mockData";
import { toast } from "sonner";

export function EmployeeRolesPage() {
  const dispatch = useDispatch();
  
  // States from Redux
  const roles = useSelector((state: RootState) => state.roleFilter.roles);
  const mappings = useSelector((state: RootState) => state.roleFilter.mappings);

  // Filter criteria for Employee list
  const [empTypeFilter, setEmpTypeFilter] = useState<'All' | 'Current' | 'Resigned'>('Current');
  const [empSearch, setEmpSearch] = useState("");
  
  // Selection states
  const [selectedEmpId, setSelectedEmpId] = useState<string | null>(null);
  const [selectedRoles, setSelectedRoles] = useState<string[]>([]);

  // Create Role popup state
  const [isCreateRoleOpen, setIsCreateRoleOpen] = useState(false);
  const [newRoleName, setNewRoleName] = useState("");
  const [newRoleAccess, setNewRoleAccess] = useState("Self Service");

  // Get active selection details
  const selectedEmployee = useMemo(() => {
    return employees.find(e => e.id === selectedEmpId) || null;
  }, [selectedEmpId]);

  // Load selected employee mappings on change
  const handleSelectEmployee = (empId: string) => {
    setSelectedEmpId(empId);
    const existing = mappings.find(m => m.employeeId === empId);
    setSelectedRoles(existing ? existing.assignedRoles : ["General User"]);
  };

  // Filter employee list dynamically
  const filteredEmployees = useMemo(() => {
    return employees.filter(emp => {
      // Search matches
      const matchesSearch = emp.name.toLowerCase().includes(empSearch.toLowerCase()) || 
                            emp.employeeId.toLowerCase().includes(empSearch.toLowerCase());
      
      // Resigned vs current mock check
      const isResigned = emp.status === "Terminated" || emp.status === "Suspended";
      const matchesType = 
        empTypeFilter === 'All' ? true :
        empTypeFilter === 'Current' ? !isResigned : isResigned;

      return matchesSearch && matchesType;
    });
  }, [empSearch, empTypeFilter]);

  // Handle Save Role mapping
  const handleSaveMapping = () => {
    if (!selectedEmpId) return;
    dispatch(saveMapping({
      employeeId: selectedEmpId,
      assignedRoles: selectedRoles
    }));
    toast.success(`Role assignment saved for ${selectedEmployee?.name}`);
  };

  const handleCreateRole = () => {
    if (!newRoleName.trim()) {
      toast.error("Role Name is required");
      return;
    }
    dispatch(addRole({
      id: `role-${Date.now()}`,
      name: newRoleName.trim(),
      access: newRoleAccess,
      status: "Moderate",
      users: 0
    }));
    toast.success(`Role "${newRoleName}" created successfully`);
    setNewRoleName("");
    setIsCreateRoleOpen(false);
  };

  const handleDeleteRole = (id: string, name: string) => {
    if (window.confirm(`Are you sure you want to delete role "${name}"?`)) {
      dispatch(deleteRole(id));
      toast.success(`Role "${name}" deleted`);
    }
  };

  const toggleRoleSelection = (roleName: string) => {
    setSelectedRoles(prev => 
      prev.includes(roleName) ? prev.filter(r => r !== roleName) : [...prev, roleName]
    );
  };

  return (
    <div className="p-8 space-y-8 animate-in fade-in duration-300">
      
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-card/40 border border-border/50 p-6 rounded-[24px]">
        {/* <div className="space-y-1">
          <h2 className="text-xl font-black text-foreground uppercase tracking-tight flex items-center gap-2">
            <UserCog className="w-5 h-5 text-rose-500" />
            Employee Roles & Mapping
          </h2>
          <p className="text-xs text-muted-foreground font-semibold">Define administrative roles and map permissions to your workforce segments dynamically.</p>
        </div> */}
        <Button 
          onClick={() => setIsCreateRoleOpen(true)}
          className="h-10 px-5 rounded-xl !bg-violet-600 !text-white text-[10px] font-black uppercase tracking-widest gap-2 !hover:bg-violet-700 !hover:text-white"
        >
          <Plus size={14} strokeWidth={3} /> Create Custom Role
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left: Role Definitions List */}
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-card border border-border rounded-[24px] overflow-hidden shadow-sm">
            <div className="px-6 py-4 border-b border-border/60 bg-secondary/10">
              <h3 className="text-xs font-black uppercase tracking-wider text-foreground">Available Roles</h3>
            </div>
            
            <div className="divide-y divide-border/60">
              {roles.map(role => (
                <div key={role.id} className="p-4 flex items-center justify-between hover:bg-secondary/15 transition-all">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-500 flex items-center justify-center">
                      <Shield size={16} />
                    </div>
                    <div>
                      <h4 className="text-xs font-black text-foreground uppercase tracking-tight">{role.name}</h4>
                      <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest">{role.users} Active Users</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[9px] font-black uppercase tracking-widest text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                      {role.access}
                    </span>
                    <button 
                      onClick={() => handleDeleteRole(role.id, role.name)}
                      className="w-7 h-7 rounded-lg border border-border text-muted-foreground hover:text-red-500 hover:bg-red-50 transition-all flex items-center justify-center"
                      title="Delete Role"
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center/Right: Employee Selection and Assigned Roles */}
        <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-12 gap-6">
          
          {/* Employee list selection */}
          <div className="md:col-span-7 bg-card border border-border rounded-[24px] p-6 space-y-4 shadow-sm flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-xs font-black uppercase tracking-widest text-foreground">Employee Selection</h3>
                
                {/* Employee Type filter */}
                <select
                  value={empTypeFilter}
                  onChange={(e) => setEmpTypeFilter(e.target.value as any)}
                  className="text-[9px] font-black uppercase py-1 px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  <option value="All">All Employees</option>
                  <option value="Current">Current</option>
                  <option value="Resigned">Resigned</option>
                </select>
              </div>

              {/* Search Bar */}
              <div className="relative">
                <Search size={13} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input 
                  type="text" 
                  value={empSearch}
                  onChange={(e) => setEmpSearch(e.target.value)}
                  placeholder="Search Employee Number, Name..."
                  className="w-full pl-9 pr-4 py-2 text-xs font-semibold bg-card border border-border rounded-xl focus:border-foreground/30 outline-none"
                />
              </div>

              {/* Employee table/list */}
              <div className="border border-border/80 rounded-2xl overflow-y-auto max-h-[300px] divide-y divide-border/60">
                {filteredEmployees.map(emp => {
                  const isSelected = selectedEmpId === emp.id;
                  const empRoles = mappings.find(m => m.employeeId === emp.id)?.assignedRoles || ["General User"];
                  
                  return (
                    <div
                      key={emp.id}
                      onClick={() => handleSelectEmployee(emp.id)}
                      className={`flex items-center justify-between p-3 cursor-pointer hover:bg-secondary/15 transition-all ${
                        isSelected ? "bg-primary/5 border-l-4 border-l-rose-500" : ""
                      }`}
                    >
                      <div>
                        <span className="text-xs font-bold text-foreground block">{emp.name}</span>
                        <span className="text-[9px] text-muted-foreground font-bold uppercase tracking-widest mt-0.5">
                          {emp.employeeId} · {emp.department}
                        </span>
                      </div>
                      <div className="text-right">
                        <span className="text-[8px] bg-secondary px-2 py-0.5 rounded text-muted-foreground font-bold uppercase block truncate max-w-[120px]">
                          {empRoles.join(", ")}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Role mapping selection details */}
          <div className="md:col-span-5 bg-card border border-border rounded-[24px] p-6 shadow-sm flex flex-col justify-between">
            {selectedEmployee ? (
              <div className="space-y-6 flex flex-col justify-between h-full">
                
                <div className="space-y-4">
                  <div className="border-b border-border pb-3">
                    <p className="text-[8px] font-black text-muted-foreground uppercase tracking-widest">Map Permissions</p>
                    <h3 className="text-sm font-black text-foreground uppercase tracking-tight mt-0.5">{selectedEmployee.name}</h3>
                    <p className="text-[10px] text-muted-foreground font-semibold">{selectedEmployee.employeeId} · {selectedEmployee.department}</p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-muted-foreground uppercase tracking-widest">Assigned Roles</label>
                    
                    {/* Multiselect checkboxes for roles */}
                    <div className="border border-border rounded-2xl p-4 space-y-3 bg-secondary/5">
                      {roles.map(r => {
                        const isChecked = selectedRoles.includes(r.name);
                        return (
                          <label key={r.id} className="flex items-center gap-3 cursor-pointer select-none">
                            <input 
                              type="checkbox"
                              checked={isChecked}
                              onChange={() => toggleRoleSelection(r.name)}
                              className="rounded border-border focus:ring-0 w-3.5 h-3.5"
                            />
                            <div className="text-xs font-bold text-foreground">{r.name}</div>
                          </label>
                        );
                      })}
                    </div>
                  </div>
                </div>

                <div className="pt-6 border-t border-border">
                  <Button 
                    onClick={handleSaveMapping}
                    className="w-full h-10 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest"
                  >
                    Save Mapping
                  </Button>
                </div>

              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-16 text-center text-muted-foreground">
                <UserCheck className="w-8 h-8 opacity-25 mb-2" />
                <p className="text-xs font-bold">No employee selected</p>
                <p className="text-[10px] text-muted-foreground max-w-[150px] mx-auto mt-1">Select an employee from the list to map roles.</p>
              </div>
            )}
          </div>

        </div>

      </div>

      {/* CREATE ROLE POPUP */}
      {isCreateRoleOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="bg-card w-full max-w-sm rounded-[24px] border border-border shadow-2xl overflow-hidden p-6 text-foreground space-y-4">
            
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h4 className="text-xs font-black uppercase tracking-tight">Create Custom Role</h4>
              <button onClick={() => setIsCreateRoleOpen(false)} className="w-7 h-7 rounded-full border border-border flex items-center justify-center hover:bg-secondary">
                <X size={13} />
              </button>
            </div>

            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Role Name *</label>
                <input 
                  type="text" 
                  value={newRoleName}
                  onChange={(e) => setNewRoleName(e.target.value)}
                  placeholder="e.g. Talent Acquisition"
                  className="flat-input h-9 w-full text-xs px-2 border border-border bg-card rounded-lg"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[9px] font-black text-muted-foreground uppercase">Access Level</label>
                <select
                  value={newRoleAccess}
                  onChange={(e) => setNewRoleAccess(e.target.value)}
                  className="flat-input h-9 w-full text-xs px-2 border border-border bg-card rounded-lg outline-none cursor-pointer"
                >
                  <option value="Full Access">Full Access</option>
                  <option value="View & Edit">View & Edit</option>
                  <option value="Self Service">Self Service</option>
                  <option value="System Settings">System Settings</option>
                </select>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3">
              <Button variant="outline" onClick={() => setIsCreateRoleOpen(false)} className="h-9 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest">
                Cancel
              </Button>
              <Button onClick={handleCreateRole} className="h-9 px-4 rounded-xl bg-foreground text-primary-foreground text-[10px] font-black uppercase tracking-widest hover:opacity-90">
                Save Role
              </Button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
