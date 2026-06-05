import { useState, useEffect, useCallback } from "react";
import { OffboardingData, OffboardingRecord } from "./types";

// Constants
const OFFBOARDING_STORAGE_KEY = "offboarding-data";
const OFFBOARDING_RECORDS_KEY = "offboarding-records";

function getOffboardingKey(id: string) {
  return `${OFFBOARDING_STORAGE_KEY}-${id}`;
}

export function useOffboardingDetails(offboardingId: string) {
  const [data, setData] = useState<OffboardingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data from localStorage (simulate API)
  useEffect(() => {
    setLoading(true);
    setError(null);
    try {
      const raw = localStorage.getItem(getOffboardingKey(offboardingId));
      if (raw) {
        setData(JSON.parse(raw));
      } else {
        setData(null);
      }
    } catch (e) {
      setError("Failed to load offboarding data");
      console.error(e);
    }
    setLoading(false);
  }, [offboardingId]);

  // Save complete data
  const save = useCallback((newData: OffboardingData) => {
    setData(newData);
    localStorage.setItem(getOffboardingKey(offboardingId), JSON.stringify(newData));
    // Also update in records list
    updateRecordsList(newData);
  }, [offboardingId]);

  // Allow partial update
  const update = useCallback((patch: Partial<OffboardingData>) => {
    setData((prev) => {
      if (!prev) return null;
      const updated = { ...prev, ...patch, updatedAt: new Date().toISOString() };
      localStorage.setItem(getOffboardingKey(offboardingId), JSON.stringify(updated));
      updateRecordsList(updated);
      return updated;
    });
  }, [offboardingId]);

  return { data, loading, error, save, update };
}

// Helper function to update records list
function updateRecordsList(offboardingData: OffboardingData) {
  try {
    const raw = localStorage.getItem(OFFBOARDING_RECORDS_KEY);
    const records: OffboardingRecord[] = raw ? JSON.parse(raw) : [];
    
    const existingIndex = records.findIndex(r => r.employeeId === offboardingData.employeeId);
    const recordData: OffboardingRecord = {
      id: offboardingData.offboardingId,
      employeeId: offboardingData.employeeId,
      name: offboardingData.name,
      initials: offboardingData.initials,
      avatarColor: offboardingData.avatarColor,
      department: offboardingData.department,
      designation: offboardingData.designation,
      reportingManager: offboardingData.reportingManager,
      resignationDate: offboardingData.resignationDate,
      lastWorkingDay: offboardingData.lastWorkingDay,
      noticeStatus: calculateNoticeStatus(offboardingData),
      exitStatus: calculateExitStatus(offboardingData),
      clearanceStatus: calculateClearanceStatus(offboardingData),
    };
    
    if (existingIndex >= 0) {
      records[existingIndex] = recordData;
    } else {
      records.push(recordData);
    }
    
    localStorage.setItem(OFFBOARDING_RECORDS_KEY, JSON.stringify(records));
  } catch (e) {
    console.error("Failed to update records list:", e);
  }
}

// Calculate notice status
function calculateNoticeStatus(data: OffboardingData): "In Notice" | "Completed" | "Waived" {
  const endDate = new Date(data.noticeDetails.noticeEndDate);
  const today = new Date();
  
  if (today > endDate) return "Completed";
  if (data.noticeDetails.earlyReleaseApproved) return "Waived";
  return "In Notice";
}

// Calculate exit status
function calculateExitStatus(data: OffboardingData): string {
  const completedSteps = data.completedSteps || [];
  
  if (completedSteps.length === 8) return "Completed";
  if (completedSteps.includes(7)) return "Clearance Pending";
  if (completedSteps.includes(4)) return "In Notice Period";
  if (completedSteps.includes(3)) return "Approved";
  return "Pending";
}

// Calculate clearance status
function calculateClearanceStatus(data: OffboardingData): "Pending" | "Partially Completed" | "Completed" {
  const checklist = data.clearanceChecklist;
  const items = [
    checklist.laptopReturned,
    checklist.idCardReturned,
    checklist.knowledgeTransferDone,
    checklist.emailAccessDisabled,
    checklist.assetsCleared
  ];
  
  const completed = items.filter(Boolean).length;
  const total = items.length;
  
  if (completed === 0) return "Pending";
  if (completed === total) return "Completed";
  return "Partially Completed";
}

// Hook to manage all offboarding records
export function useOffboardingRecords() {
  const [records, setRecords] = useState<OffboardingRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(OFFBOARDING_RECORDS_KEY);
      setRecords(raw ? JSON.parse(raw) : []);
    } catch (e) {
      console.error("Failed to load records:", e);
      setRecords([]);
    }
    setLoading(false);
  }, []);

  const addRecord = useCallback((record: OffboardingRecord) => {
    setRecords(prev => {
      // Upsert by employeeId if exists (replace draft record)
      const existingIndex = prev.findIndex(r => r.employeeId === record.employeeId);
      let updated;
      if (existingIndex >= 0) {
        updated = [...prev];
        updated[existingIndex] = record;
      } else {
        updated = [record, ...prev];
      }
      try { localStorage.setItem(OFFBOARDING_RECORDS_KEY, JSON.stringify(updated)); } catch(e) { console.warn(e); }
      return updated;
    });
  }, []);

  const updateRecord = useCallback((id: string, data: Partial<OffboardingRecord>) => {
    setRecords(prev => {
      const updated = prev.map(r => r.id === id ? { ...r, ...data } : r);
      localStorage.setItem(OFFBOARDING_RECORDS_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const deleteRecord = useCallback((id: string) => {
    setRecords(prev => {
      const updated = prev.filter(r => r.id !== id);
      localStorage.setItem(OFFBOARDING_RECORDS_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  return { records, loading, addRecord, updateRecord, deleteRecord };
}