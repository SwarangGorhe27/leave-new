CREATE TABLE profile_change_requests (
  id TEXT PRIMARY KEY,
  employee_id TEXT NOT NULL,
  section TEXT NOT NULL,
  section_label TEXT NOT NULL,
  changes JSONB NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('pending', 'approved', 'rejected')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  reviewed_by TEXT,
  reviewed_at TIMESTAMP,
  rejection_comment TEXT
);
