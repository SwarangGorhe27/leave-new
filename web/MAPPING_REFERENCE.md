# Form to Details Modal - Complete Mapping Reference

## Visual Data Flow

```
┌─────────────────────────────────────────┐
│  ADD NEW OFFBOARDING FORM (8 Steps)     │
│                                         │
│  ✓ Step 1: Employee Information        │
│  ✓ Step 2: Resignation Details         │
│  ✓ Step 3: Approval Workflow          │
│  ✓ Step 4: Notice Period              │
│  ✓ Step 5: Clearance Checklist        │
│  ✓ Step 6: Financial Settlement       │
│  ✓ Step 7: Exit Interview             │
│  ✓ Step 8: Documents                  │
└──────────────────────┬──────────────────┘
                       │
                    [SAVE]
                       │
                       ↓
        ┌──────────────────────────────┐
        │ Structured OffboardingData   │
        │ (TypeScript interface)       │
        │                              │
        │ - Employee info              │
        │ - Resignation details        │
        │ - Approval workflow          │
        │ - Notice period              │
        │ - Clearance checklist        │
        │ - Financial settlement       │
        │ - Exit interview             │
        │ - Documents                  │
        │ - Metadata & timestamps      │
        └──────────────────────┬───────┘
                               │
                               ↓
                    localStorage Persistence
                 (offboarding-data-{id})
                               │
                               ↓
        ┌────────────────────────────────┐
        │ OFFBOARDING DETAILS MODAL      │
        │ (7 Dynamic Tabs)               │
        │                                │
        │ ✓ Overview                     │
        │ ✓ Resignation/Approval         │
        │ ✓ Clearance                    │
        │ ✓ Finance                      │
        │ ✓ Exit Interview               │
        │ ✓ Documents                    │
        │ ✓ Activity Logs                │
        └────────────────────────────────┘
```

## Step-by-Step Mapping Detail

### STEP 3: APPROVAL WORKFLOW → RESIGNATION/APPROVAL TAB

```
FORM INPUT                          DETAILS DISPLAY
──────────────────────────────────────────────────────────
Select: Reporting Manager Approval  │ Status Badge: "Approved" ✓
  └─ "Approved" / "Pending" / etc   │   With date & remarks

Add Remarks: [manager feedback]     │ Remarks displayed in box
  └─ Text input                     │   With gray background

Select: HR Approval                 │ Status Badge: "Approved" ✓
  └─ "Approved" / "Pending" / etc   │   With date & remarks

Add Remarks: [HR feedback]          │ Remarks displayed in box
  └─ Text input                     │   

Select: IT Clearance Approval       │ Status Badge: "Approved" ✓
  └─ "Approved" / "Pending" / etc   │   With date & remarks

Add Remarks: [IT feedback]          │ Remarks displayed in box
  └─ Text input                     │   

Textarea: Final Approval Remarks    │ Highlighted box showing
  └─ Optional final notes           │   final remarks (if filled)
```

### STEP 4: NOTICE PERIOD → OVERVIEW/NOTICE SECTION

```
FORM INPUT                          DETAILS DISPLAY (Overview Tab)
────────────────────────────────────────────────────────────────
Select: Notice Start Date           │ Card 1: "Notice Period Status"
  └─ e.g., "2024-05-01"           │   ├─ Start Date: 2024-05-01
                                   │   ├─ End Date: 2024-06-01
Select: Notice End Date             │   ├─ Days Remaining: 8 days
  └─ e.g., "2024-06-01"           │   └─ Buyout Required: No
                                   │
Auto-calc: Notice Days             │ Progress Bar:
  └─ Math: (end - start) days      │   Calculated from dates
                                   │
Checkbox: Buyout Required          │ Days Remaining Badge:
  └─ True/False                    │   Color: Amber if remaining
                                   │   Text: "X days" or "Completed"
Checkbox: Early Release Approved   │
  └─ True/False                    │ Buyout Flag:
                                   │   Badge: "Yes" or "No"
```

### STEP 5: CLEARANCE CHECKLIST → CLEARANCE TAB + PROGRESS

```
FORM INPUT                          DETAILS DISPLAY
────────────────────────────────────────────────────────────
Checkbox: Laptop Returned           │ Clearance Tab:
  └─ ☑ Checked                      │   ├─ ☑ Laptop Returned
                                   │   ├─ ☐ ID Card Returned
Checkbox: ID Card Returned          │   ├─ ☑ Knowledge Transfer Done
  └─ ☐ Unchecked                    │   ├─ ☑ Email Access Disabled
                                   │   └─ ☐ Assets Cleared
Checkbox: Knowledge Transfer Done   │
  └─ ☑ Checked                      │ Overview Tab:
                                   │   Progress Bar: 60%
Checkbox: Email Access Disabled     │   (3 out of 5 completed)
  └─ ☑ Checked                      │
                                   │ Each Item Shows:
Checkbox: Assets Cleared            │   - Checkbox icon (checked/empty)
  └─ ☐ Unchecked                    │   - Item name
                                   │   - Status badge (Completed/Pending)
Text: Clearance Remarks             │   - Date completed (if available)
  └─ Optional notes                 │
                                   │ Clearance Remarks:
Auto-calc: Clearance Progress       │   Separate section with remarks
  └─ Math: (3/5) × 100 = 60%       │
```

### STEP 6: FINANCIAL SETTLEMENT → FINANCE TAB

```
FORM INPUT                          DETAILS DISPLAY
────────────────────────────────────────────────────────────
Number: Leave Encashment           │ Card 1: "Leave Encashment"
  └─ e.g., 50000                   │   Amount: ₹50,000
                                   │
Number: Deductions                 │ Card 2: "Deductions"
  └─ e.g., 5000                    │   Amount: ₹5,000
                                   │
Auto-calc: Final Settlement        │ Highlighted Box:
  └─ 50000 - 5000 = 45000         │   "Final Settlement Amount"
                                   │   ₹45,000 (large, primary color)
Select: Payment Status             │
  └─ "Pending" / "Processed" / etc  │ Payment Status Card:
                                   │   Badge: "Pending" (amber)
(Optional) Payment Date            │
(Optional) Payment Method          │ Additional Cards:
                                   │   - Payment Date (if filled)
                                   │   - Payment Method (if filled)
```

### STEP 7: EXIT INTERVIEW → EXIT INTERVIEW TAB

```
FORM INPUT                          DETAILS DISPLAY
────────────────────────────────────────────────────────────
Date: Exit Interview Date          │ Card 1: "Exit Interview Details"
  └─ e.g., "2024-06-20"           │   Interview Date: 20 Jun 2024
                                   │
Select: Reason for Leaving         │ Card 2: "Reason for Leaving"
  └─ e.g., "Better Opportunity"   │   Better Opportunity
                                   │
Textarea: Employee Feedback        │ Card 3: "Would Rejoin Company"
  └─ Detailed feedback text        │   Badge: "Yes" ✓ (or "No")
                                   │
Checkbox: Would Rejoin Company     │ Separate Section:
  └─ True / False                  │   "Employee Feedback"
                                   │   [Full feedback text]
```

### STEP 8: DOCUMENTS → DOCUMENTS TAB

```
FORM INPUT                          DETAILS DISPLAY
────────────────────────────────────────────────────────────
File Upload: Resignation Letter    │ List Item: Resignation Letter
  └─ File: resignation.pdf         │   Status: ✓ Uploaded Successfully
  └─ Size: 250 KB                  │   File: resignation.pdf
  └─ Time: 14 May 2024, 2:30 PM   │   Size: 250 KB
                                   │   Date: 14 May 2024, 2:30 PM
File Upload: Clearance Form        │   Buttons: [View] [Download]
  └─ File: clearance.pdf           │
  └─ Size: 180 KB                  │ List Item: Clearance Form
  └─ Time: 14 May 2024, 2:31 PM   │   Status: ✓ Uploaded Successfully
                                   │   File: clearance.pdf
File Upload: Relieving Letter      │   Size: 180 KB
File Upload: Experience Letter     │   Date: 14 May 2024, 2:31 PM
File Upload: Settlement Copy       │   Buttons: [View] [Download]
                                   │
                                   │ ... (3 more files)
```

## Dynamic Calculations Reference

### Calculation 1: Notice Days
```
Formula: (End Date - Start Date) / (1000 × 60 × 60 × 24)
Example: (2024-06-01 - 2024-05-01) = 31 days
Display: Shown in "Notice Period Status" card
Updated: On every form save
```

### Calculation 2: Clearance Progress
```
Formula: (Completed Items / Total Items) × 100
Items:   Laptop, ID Card, Knowledge Transfer, Email, Assets
Example: 3 checked out of 5 = 60%
Display: Progress bar in Overview tab
         Percentage in Clearance tab
Updated: Real-time as checkboxes change
```

### Calculation 3: Final Settlement Amount
```
Formula: Leave Encashment - Deductions
Example: ₹50,000 - ₹5,000 = ₹45,000
Display: Large highlighted number in Finance tab
Updated: On form save
Format:  Currency with ₹ symbol, comma-separated
```

### Calculation 4: Status Determination
```
Status: Based on completedSteps array
Values: Draft → In Progress → Completed → Archived
Display: Status badge in profile panel
Updated: Calculated at save time
```

## Data Structure (TypeScript)

```typescript
OffboardingData {
  // Basic Info
  offboardingId: string           // Unique ID
  employeeId: string              // Employee reference
  name: string                    // Employee name
  department: string              // Auto-filled
  designation: string             // Auto-filled
  
  // Step 3 → Resignation/Approval Tab
  approvalWorkflow: {
    reportingManagerApproval: "Pending" | "Approved" | "Rejected"
    reportingManagerApprovedAt?: string
    reportingManagerRemarks?: string
    hrApproval: "Pending" | "Approved" | "Rejected"
    hrApprovedAt?: string
    hrRemarks?: string
    itClearanceApproval: "Pending" | "Approved" | "Rejected"
    itApprovedAt?: string
    itRemarks?: string
    finalApprovalRemarks?: string
  }
  
  // Step 4 → Overview/Notice Section
  noticeDetails: {
    noticeStartDate: string
    noticeEndDate: string
    noticeDays: number              // AUTO-CALCULATED
    buyoutRequired: boolean
    buyoutAmount?: number
    earlyReleaseApproved: boolean
    earlyReleaseDate?: string
  }
  
  // Step 5 → Clearance Tab
  clearanceChecklist: {
    laptopReturned: boolean
    laptopReturnedDate?: string
    idCardReturned: boolean
    idCardReturnedDate?: string
    knowledgeTransferDone: boolean
    knowledgeTransferDate?: string
    emailAccessDisabled: boolean
    emailDisabledDate?: string
    assetsCleared: boolean
    assetsReturnedDate?: string
    clearanceRemarks?: string
    clearanceProgress: number      // AUTO-CALCULATED (0-100%)
  }
  
  // Step 6 → Finance Tab
  financialSettlement: {
    leaveEncashment: number
    deductions: number
    finalSettlementAmount: number  // AUTO-CALCULATED
    paymentStatus: "Pending" | "Processed" | "Completed"
    paymentDate?: string
    paymentMethod?: string
    bankDetails?: string
  }
  
  // Step 7 → Exit Interview Tab
  exitInterview: {
    exitInterviewDate: string
    exitReason: string
    employeeFeedback: string
    wouldRejoin: boolean
    interviewerName?: string
    interviewNotes?: string
  }
  
  // Step 8 → Documents Tab
  documents: {
    [docName: string]: {
      name: string
      fileName: string
      fileSize: number
      uploadedAt: string
      uploadStatus: "Uploaded Successfully" | "Uploading" | "Pending" | "Failed"
    }
  }
  
  // Metadata
  createdAt: string
  updatedAt: string
  createdBy?: string
  status: "Draft" | "In Progress" | "Completed" | "Archived"
  completedSteps: number[]        // Array of completed step IDs
}
```

## Empty States Handling

```
Location: Resignation/Approval Tab
Condition: No approval remarks entered
Display: "Pending Approvals" banner
Message: "Awaiting final approval remarks from HR department."

Location: Exit Interview Tab
Condition: exitInterviewDate is empty
Display: Full-screen empty state
Message: "Exit Interview Not Conducted - Please schedule it at your earliest convenience."

Location: Documents Tab
Condition: No documents uploaded
Display: Full-screen empty state
Message: "No Documents Uploaded - Please upload all required offboarding documents."

Location: Individual Items
Condition: Boolean field is false / amount is 0 / status is "Pending"
Display: "Pending" badge in amber
Message: Shows pending status
```

## Complete Workflow Tracker Steps

```
Step 1: Employee Selected
        Status: ✓ Completed (when employee selected in form)
        Date: Shows selection date

Step 2: Resignation Details
        Status: Completed if form submitted
        Date: resignation date from form

Step 3: Manager Approval
        Status: Completed if reportingManagerApproval = "Approved"
        Date: reportingManagerApprovedAt

Step 4: Notice Period
        Status: Completed if noticeStartDate & noticeEndDate filled
        Date: noticeDays countdown

Step 5: Clearance Process
        Status: Completed if any clearance item marked done
        Date: "In Progress" or date of completion

Step 6: Financial Settlement
        Status: Completed if leaveEncashment or deductions entered
        Date: paymentDate (if processed)

Step 7: Exit Interview
        Status: Completed if exitInterviewDate filled
        Date: exitInterviewDate from form

Step 8: Documents Uploaded
        Status: Completed if all required docs uploaded
        Date: Latest document uploadedAt date
```

## Summary

This mapping creates a complete flow where:
1. User enters data in 8 form steps
2. System structures it into TypeScript interface
3. Data saved to localStorage with unique ID
4. Details modal loads data and displays in 7 tabs
5. All tabs show corresponding form data dynamically
6. Calculations update automatically
7. Each employee sees only their own data
8. No static/placeholder data anywhere
9. Complete type safety with TypeScript
10. Ready for API integration
