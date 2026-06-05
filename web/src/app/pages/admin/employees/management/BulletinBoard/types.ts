export type BulletinStatus = "Open" | "Closed";

export interface Bulletin {
  id: string;
  category: string;
  title: string;
  content: string;
  postedDate: string;
  startDate: string;
  expiryDate: string;
  rank: number;
  isHidden: boolean;
  attachments: BulletinAttachment[];
  employeeFilters: string[];
  status: BulletinStatus;
}

export interface BulletinAttachment {
  id: string;
  name: string;
  size: number;
  type: string;
  url: string;
}

export interface BulletinCategoryMaster {
  id: string;
  label: string;
}

export interface EmployeeFilterMaster {
  id: string;
  label: string;
}
