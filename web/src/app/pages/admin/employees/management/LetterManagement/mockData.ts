import { LetterTemplate, LetterBatch } from "./types";

export const MOCK_TEMPLATES: LetterTemplate[] = [
  {
    id: "tmpl-1",
    name: "Standard Offer Letter v1",
    type: "Offer Letter",
    content: `
      <div style="font-family: sans-serif; line-height: 1.6;">
        <h1 style="text-align: center; color: #000;">OFFER LETTER</h1>
        <p>Date: {{current_date}}</p>
        <p>To,<br/><strong>{{employee_name}}</strong><br/>{{address}}</p>
        <p>Dear <strong>{{employee_name}}</strong>,</p>
        <p>We are pleased to offer you the position of <strong>{{designation}}</strong> in our <strong>{{department}}</strong> department. Your date of joining will be <strong>{{joining_date}}</strong>.</p>
        <p>Your annual salary will be <strong>{{salary}}</strong>. Please find the detailed salary breakup attached.</p>
        <p>We look forward to having you on board.</p>
        <br/><br/>
        <p>Sincerely,<br/><strong>Human Resources</strong></p>
      </div>
    `
  },
  {
    id: "tmpl-2",
    name: "Annual Increment Letter 2026",
    type: "Increment Letter",
    content: `
      <div style="font-family: sans-serif; line-height: 1.6;">
        <h1 style="text-align: center; color: #000;">SALARY INCREMENT LETTER</h1>
        <p>Date: {{current_date}}</p>
        <p>Dear <strong>{{employee_name}}</strong>,</p>
        <p>Congratulations! Based on your performance appraisal, your salary has been revised to <strong>{{new_salary}}</strong> effective from <strong>{{effective_date}}</strong>.</p>
        <p>Keep up the great work!</p>
        <br/><br/>
        <p>Best Regards,<br/><strong>Management Team</strong></p>
      </div>
    `
  }
];

export const MOCK_HISTORY: LetterBatch[] = [
  {
    id: "batch-101",
    letterType: "Offer Letter",
    templateId: "tmpl-1",
    templateName: "Standard Offer Letter v1",
    approvalWorkflow: "HR Manager",
    subject: "Offer Letter - James Anderson",
    remarks: "Standard offer for senior role",
    effectiveDate: "2026-06-01",
    publishDate: "2026-05-12",
    attachmentUrls: [],
    selectedEmployeeIds: ["EMP-1001"],
    status: "Published",
    createdBy: "Sarah Chen",
    createdAt: "2026-05-10T10:00:00Z",
    publishedAt: "2026-05-12T14:00:00Z"
  },
  {
    id: "batch-102",
    letterType: "Increment Letter",
    templateId: "tmpl-2",
    templateName: "Annual Increment Letter 2026",
    approvalWorkflow: "No Approval Required",
    subject: "Annual Increment 2026",
    remarks: "Bulk release for Tech team",
    effectiveDate: "2026-04-01",
    publishDate: "2026-04-15",
    attachmentUrls: [],
    selectedEmployeeIds: ["EMP-1002", "EMP-1003", "EMP-1004"],
    status: "Published",
    createdBy: "Sarah Chen",
    createdAt: "2026-04-10T09:30:00Z",
    publishedAt: "2026-04-15T11:20:00Z"
  }
];
