// Main dashboard component
export { AdminDashboard } from './AdminDashboard';

// Sub-components
export { ActionCenter, type ActionItem } from './ActionCenter';
export { AttendanceSnapshot } from './AttendanceSnapshot';
export { ImportantToday, type ImportantItem } from './ImportantToday';
export { LeaveSnapshot } from './LeaveSnapshot';
export { StatCard, StatCardSkeleton } from './StatCard';
export { WorkforceDistribution, type DepartmentData } from './WorkforceDistribution';

// Dashboard kit (reusable primitives)
export { DashboardCard, DashboardCardSkeleton } from './kit/DashboardCard';
export { ActionList, type ActionItem as ActionListItem } from './kit/ActionList';
export { SectionContainer } from './kit/SectionContainer';
export { InsightBlock } from './kit/InsightBlock';
export { EmptyState } from './kit/EmptyState';
export { SkeletonBlock, SkeletonList } from './kit/SkeletonLoader';
