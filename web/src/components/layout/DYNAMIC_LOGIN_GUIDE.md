# Dynamic Login System - Complete Documentation

## Overview

This document describes the comprehensive dynamic login system for the HRMS platform. The system includes separate, customized login experiences for **Employees** and **Admins** with real-time data integration, personalized content, and extensive UI components.

---

## Table of Contents

1. [Employee Login Page](#employee-login-page)
2. [Admin Login Page](#admin-login-page)
3. [Shared Components](#shared-components)
4. [Data Integration](#data-integration)
5. [Customization Guide](#customization-guide)
6. [API Integration](#api-integration)

---

## Employee Login Page

### Overview
Located in: `DynamicEmployeeLoginLayout.tsx`
Page: `/src/pages/EmployeeLoginPage.tsx`

The employee login page is designed to provide a personalized, welcoming experience with real-time employee data.

### Dynamic Fields & Components

#### 1. **Personalized Welcome Section**
- **Greeting**: Time-based greeting (Good morning/afternoon/evening)
- **Employee Name**: Fetched from auth store
- **Tenure Information**: Years and months of employment
- **Motivational Message**: Context-aware based on role

```tsx
<h1>
  {getGreeting()}, {employeeData?.name.split(' ')[0]}
</h1>
```

#### 2. **Employee Profile Card** (Condensed)
Displays core employee information:

| Field | Data Source | Dynamic? | Notes |
|-------|------------|----------|-------|
| Name | authStore.user.name | ✓ | Fetched from auth store |
| Title | authStore.employees[idx].designation | ✓ | Employee designation |
| Department | authStore.employees[idx].department | ✓ | Department information |
| Location | authStore.employees[idx].location | ✓ | Work location |
| Manager | authStore.employees[idx].reportingChain[1] | ✓ | Direct manager |
| Tenure | authStore.employees[idx].tenure | ✓ | Calculated from joinDate |

#### 3. **Alert Banners**
Two primary alert types:

**Leave Balance Alert**
- Shows remaining leave days
- Dynamic color based on balance (>10: success, 5-10: warning, <5: danger)
- Message: "You have {balance} days remaining. Plan your leaves wisely."

**Attendance Alert**
- Shows present days this month
- Static type (info)
- Message: "You're marked present for {days} days this month."

```tsx
<AlertBanner
  title="Leave Balance Alert"
  description={`You have ${employeeData?.leaveBalance || 0} days remaining.`}
  type={leaveStatus.type}
/>
```

#### 4. **Stats Grid** (Four Cards)

**Card 1: Leave Balance**
- Label: "Leave Balance"
- Value: `${balance} days`
- Delta: Status message (Low balance/Plan ahead/Sufficient balance)
- Icon: Calendar
- Color: Dynamic based on balance

**Card 2: Days Present**
- Label: "Days Present"
- Value: Number of present days
- Delta: "+2 vs last month" (comparison)
- Icon: CheckCircle2
- Color: Success (green)

**Card 3: Tenure**
- Label: "Tenure"
- Value: `${years}y ${months}m`
- Delta: "Last increment pending"
- Icon: Zap
- Color: Warning (yellow)

**Card 4: Next Increment**
- Label: "Next Increment"
- Value: Date formatted (e.g., "Jul 01")
- Delta: `${daysAway} days away`
- Icon: BriefcaseBusiness
- Color: Brand (blue)

```tsx
<StatCard
  label="Leave Balance"
  value={`${employeeData?.leaveBalance || 0} days`}
  delta={leaveStatus.label}
  icon={Calendar}
  trend={leaveStatus.type === 'alert' ? 'negative' : 'positive'}
  color={leaveStatus.type}
/>
```

#### 5. **Recent Activity Section**
Displays 3 most recent activities:

| Field | Data Source | Example |
|-------|------------|---------|
| Activity Title | authStore.employees[idx].recentActivity | "Promoted to Senior Product Designer" |
| Date | Computed | "2 days ago", "1 week ago" |
| Type Badge | Activity index | First: achievement, others: update |
| Icon | Activity type | CheckCircle2 for achievement |

### Layout Structure

```
+-------------------------------------------+----------------------------+
|                                           |                            |
|  Employee Information Section             |   Login Form Section       |
|  - Header badge                           |   - Email input            |
|  - Personalized welcome                   |   - Password input         |
|  - Profile card                           |   - Employee role badge    |
|  - Alert banners                          |   - Sign-in button         |
|  - Stats grid (2x2)                       |   - Social login           |
|  - Recent activity                        |   - Footer                 |
|                                           |                            |
+-------------------------------------------+----------------------------+
```

### Color Scheme
- **Primary**: Blue (#3B82F6) - Brand color
- **Success**: Green (#10B981) - Positive stats
- **Warning**: Orange (#F59E0B) - Caution alerts
- **Danger**: Red (#EF4444) - Critical alerts
- **Background**: Slate colors with glassmorphism effects

---

## Admin Login Page

### Overview
Located in: `DynamicAdminLoginLayout.tsx`
Page: `/src/pages/AdminLoginPage.tsx`

The admin login page provides a command center view with team health metrics, pending actions, and administrative overview.

### Dynamic Fields & Components

#### 1. **Admin Welcome Section**
- **Greeting**: Time-based greeting
- **Admin Name**: "HR Administrator" or specific name
- **Motivational Message**: Focus on team health and operations

#### 2. **Admin Profile Card**
Displays administrative information:

| Field | Data Source | Dynamic? | Notes |
|-------|------------|----------|-------|
| Name | authStore.user.name | ✓ | Admin name |
| Title | authStore.user.title | ✓ | e.g., "HR Operations Head" |
| Admin Level | Hardcoded | ✓ | "Super Admin" or role-based |
| Team Size | Computed | ✓ | Total employee count |
| Department | authStore.user.company | ✓ | Company/HR Department |
| Access | Hardcoded | - | "Full System" |

#### 3. **Priority Alert Badges**

**High Priority Alerts**
- Leave Approvals Pending (12 items)
- Badge color: Red (#EF4444)
- Action: "Review"

**Medium Priority Alerts**
- Document Verifications (18 items)
- Badge color: Orange (#F59E0B)
- Action: "Process"

```tsx
<PriorityAlert
  title="Leave Approvals Pending"
  description="12 leave requests awaiting your approval"
  count={12}
  priority="high"
  icon={AlertCircle}
  action="Review"
/>
```

#### 4. **Admin Stats Grid** (Four Cards)

**Card 1: Total Employees**
- Value: 230
- Status: "3 new this month"
- Trend: up
- Icon: Users
- Color: Brand (blue)

**Card 2: Attendance Rate**
- Value: 94.2%
- Status: "↑ 1.2% vs month"
- Trend: up
- Icon: CheckCircle2
- Color: Success (green)

**Card 3: Pending Leaves**
- Value: 12
- Status: "Action needed"
- Trend: neutral
- Icon: Clock
- Color: Warning (orange)

**Card 4: Open Requisitions**
- Value: 5
- Status: "In hiring stage"
- Trend: down
- Icon: TrendingUp
- Color: Info (blue)

#### 5. **Team Health Metrics** Component

Displays:

| Metric | Display | Trend |
|--------|---------|-------|
| Attendance Rate | 94.2% | +1.2% vs month |
| Leave Approvals | 12 | Action needed |
| New Joiners | 3 | Onboarding in progress |

Includes:
- Progress bar for attendance rate
- Dynamic color coding
- Comparison vs previous period
- Actionable items count

```tsx
<TeamHealthMetrics>
  {/* Renders health visualization */}
</TeamHealthMetrics>
```

#### 6. **Quick Actions Component**

Four action buttons:

1. **Manage Employees**
   - Icon: Users
   - Count: "230 total"
   - Color: Brand (blue)

2. **Approve Documents**
   - Icon: CheckCircle2
   - Count: "18 pending"
   - Color: Success (green)

3. **Review Requests**
   - Icon: AlertCircle
   - Count: "7 alerts"
   - Color: Warning (orange)

4. **View Reports**
   - Icon: TrendingUp
   - Count: "Updated today"
   - Color: Purple

Each action:
- Clickable for navigation
- Shows relevant count
- Includes hover effects
- Icons indicate action type

### Layout Structure

```
+-----------------------------------------------+---------------------------+
|                                               |                           |
|  Admin Dashboard Overview                     |   Login Form              |
|  - Header badge (HR Admin)                    |   - Email input           |
|  - Welcome section                            |   - Password input        |
|  - Profile card (Admin info)                  |   - Admin role badge      |
|  - Priority alerts                            |   - Sign-in button        |
|  - Stats grid (2x2)                           |   - Social login          |
|  - Team health + Quick actions (2 cols)       |   - Security notice       |
|                                               |   - IT Support footer     |
|                                               |                           |
+-----------------------------------------------+---------------------------+
```

### Color Scheme
- **Primary**: Red (#EF4444) - Admin distinction
- **Secondary**: Orange (#FF9500) - Warnings
- **Success**: Green (#10B981) - Positive metrics
- **Info**: Blue (#3B82F6) - General info
- **Background**: Slate with indigo/red gradients

---

## Shared Components

### StatCard Component
```tsx
<StatCard
  label="Leave Balance"
  value="14 days"
  delta="+2 vs last month"
  icon={Calendar}
  trend="positive"
  color="success"
/>
```

**Props:**
- `label` (string): Card label
- `value` (string|number): Main value
- `delta` (string): Secondary information
- `icon` (ReactNode): Icon component
- `trend` (positive|negative|neutral): Trend type
- `color` (brand|success|warning|danger): Color scheme

### ActivityItem Component
```tsx
<ActivityItem
  title="Promoted to Senior Product Designer"
  date="2 days ago"
  icon={CheckCircle2}
  type="achievement"
  isLatest={true}
/>
```

**Props:**
- `title` (string): Activity title
- `description` (string): Optional description
- `date` (string): Relative or absolute date
- `icon` (ReactNode): Activity icon
- `type` (achievement|alert|update|default): Activity type
- `isLatest` (boolean): Highlight if most recent

### AlertBanner Component
```tsx
<AlertBanner
  title="Leave Balance Alert"
  description="You have 14 days remaining."
  type="warning"
  action={{ label: "View", onClick: () => {} }}
/>
```

**Props:**
- `title` (string): Alert title
- `description` (string): Optional description
- `type` (success|warning|alert|info): Alert severity
- `action` (object): Optional action button

---

## Data Integration

### Current Data Sources

All data is currently fetched from **useAuthStore** and hardcoded demo data:

```typescript
const user = useAuthStore((state) => state.user);
const employees = useAuthStore((state) => state.employees);
```

### Employee Data Structure

```typescript
interface Employee {
  id: string;
  code: string;
  name: string;
  email: string;
  designation: string;        // Title
  department: string;
  location: string;
  status: 'Active' | 'Inactive';
  joinedAt: string;            // YYYY-MM-DD
  nextIncrement: string;       // YYYY-MM-DD
  leaveBalance: number;
  presentDays: number;
  tenure: string;              // e.g., "4y 10m"
  reportingChain: Array<{
    name: string;
    title: string;
  }>;
  recentActivity: string[];
  stats: Array<{
    label: string;
    value: string | number;
    delta?: string;
  }>;
}
```

### Custom Hooks

Located in: `src/hooks/useLoginPageData.ts`

#### useAdminDashboardStats()
Returns admin-specific metrics:
```typescript
{
  totalEmployees: 230,
  presentToday: 215,
  onLeaveToday: 8,
  pendingApprovals: 12,
  newHiresThisMonth: 3,
  attendanceRate: 94.2,
  departmentCount: 12,
  avgTenure: '3.5 years'
}
```

#### useEmployeeDashboardStats()
Returns employee-specific data for login page.

#### useLoginPageAlerts()
Returns role-based alerts for the login page.

#### useTimeBasedGreeting()
Returns time-appropriate greeting.

---

## Customization Guide

### Adding New Employee Login Fields

1. **Update authStore.ts** (if new data needed):
```typescript
// Add to AuthUser interface
customField: string;
```

2. **Update DynamicEmployeeLoginLayout.tsx**:
```tsx
// In getEmployeeData() function
{
  // ... existing data
  customField: employee?.customField || 'default'
}
```

3. **Add UI component**:
```tsx
<div className="space-y-1">
  <p className="text-xs font-semibold text-slate-500">CUSTOM FIELD</p>
  <p className="text-sm font-semibold">{employeeData?.customField}</p>
</div>
```

### Adding New Admin Metrics

1. **Update DynamicAdminLoginLayout.tsx**:
```tsx
<AdminStatCard
  label="New Metric"
  value="123"
  status="Description"
  icon={IconComponent}
  trend="up"
  color="brand"
/>
```

2. **Update useAdminDashboardStats** hook:
```typescript
const mockStats: DashboardStats = {
  // ... existing
  newMetric: value
};
```

### Changing Colors

Update the `colorMap` objects in component files:
```typescript
const colorMap = {
  brand: 'bg-brand-50 text-brand-600 border-brand-200',
  success: 'bg-success-50 text-success-600 border-success-200',
  // Add custom colors here
  custom: 'bg-custom-50 text-custom-600 border-custom-200'
};
```

### Adding Real API Integration

Replace the mock data in hooks:

```typescript
// Before
const mockStats: DashboardStats = { /* mock */ };
setStats(mockStats);

// After
const response = await fetch('/api/admin/dashboard');
const data = await response.json();
setStats(data);
```

---

## API Integration

### Recommended Endpoints

**For Employee Login Data:**
```
GET /api/employee/profile
GET /api/employee/stats
GET /api/employee/recent-activity
GET /api/employee/leave-balance
```

**For Admin Login Data:**
```
GET /api/admin/dashboard/overview
GET /api/admin/dashboard/team-health
GET /api/admin/dashboard/pending-tasks
GET /api/admin/dashboard/metrics
```

### Expected Response Formats

**Employee Stats Response:**
```json
{
  "leaveBalance": 14,
  "presentDays": 19,
  "nextIncrement": "2026-07-01",
  "recentActivity": [
    "Promoted to Senior Product Designer",
    "Document set updated",
    "Manager changed"
  ]
}
```

**Admin Metrics Response:**
```json
{
  "totalEmployees": 230,
  "presentToday": 215,
  "onLeaveToday": 8,
  "pendingApprovals": 12,
  "attendanceRate": 94.2,
  "priorityAlerts": [
    {
      "title": "Leave Approvals Pending",
      "count": 12,
      "priority": "high"
    }
  ]
}
```

---

## Responsive Design

Both login pages are fully responsive:

- **Mobile**: Single column, centered layout
- **Tablet**: Adapted grid system
- **Desktop**: Two-column layout with sticky form

### Breakpoints Used
- `sm`: 640px
- `md`: 768px
- `lg`: 1024px
- `xl`: 1280px

---

## Accessibility Features

- ✓ Semantic HTML structure
- ✓ ARIA labels on icons
- ✓ Keyboard navigation support
- ✓ Focus indicators on form elements
- ✓ Color contrast ratios (WCAG AA compliant)
- ✓ Password visibility toggle
- ✓ Error state indicators

---

## Performance Optimizations

1. **Lazy Loading**: Components load data on mount
2. **Memoization**: Using `useMemo` for expensive calculations
3. **Conditional Rendering**: Data fetched based on user role
4. **Optimized Re-renders**: State updates only when necessary

---

## Troubleshooting

### Data Not Displaying

1. Check if `useAuthStore` is properly initialized
2. Verify employee data exists in store
3. Console log `employeeData` to debug

### Styling Issues

1. Ensure Tailwind CSS is compiled
2. Check dark mode configuration
3. Verify color tokens in `tailwind.config.ts`

### Performance Issues

1. Check Network tab for slow API calls
2. Profile React components for unnecessary re-renders
3. Optimize image sizes

---

## Future Enhancements

- [ ] Real-time data refresh (WebSocket)
- [ ] Personalized recommendations
- [ ] Advanced analytics on login
- [ ] Role-based feature toggles
- [ ] A/B testing framework
- [ ] Dark mode animations
- [ ] Accessibility audit
- [ ] Performance metrics tracking

---

## Support & Questions

For questions about customization or implementation:
1. Review the component source code
2. Check the hooks documentation
3. Refer to Tailwind CSS docs for styling
4. Consult React documentation for patterns

