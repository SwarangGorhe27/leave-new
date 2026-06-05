const IFSC_RE = /^[A-Z]{4}0[A-Z0-9]{6}$/;
const INDIAN_MOBILE_RE = /^(\+91[\s-]?)?[6-9]\d{9}$/;
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
/** Indian passport style: leading letter + 7 digits (optional trailing check digit) */
const PASSPORT_RE = /^[A-Za-z][1-9]\d{6}\d?$/;

export function validateIfsc(code: string): string | null {
  const c = code.replace(/\s/g, "").toUpperCase();
  if (!c) return "IFSC is required.";
  if (!IFSC_RE.test(c)) return "Enter a valid 11-character IFSC (e.g. HDFC0001234).";
  return null;
}

export function validateAccountNumber(num: string): string | null {
  const n = num.replace(/\s/g, "");
  if (!n) return "Account number is required.";
  if (n.length < 4) return "Account number looks too short.";
  return null;
}

export function validateEmail(email: string): string | null {
  if (!email.trim()) return "Email is required.";
  if (!EMAIL_RE.test(email.trim())) return "Enter a valid email address.";
  return null;
}

export function validateMobile(mobile: string): string | null {
  if (!mobile.trim()) return null;
  const compact = mobile.replace(/[\s-]/g, "");
  if (!INDIAN_MOBILE_RE.test(compact)) return "Enter a valid 10-digit mobile number.";
  return null;
}

export function validatePassport(num: string): string | null {
  if (!num.trim()) return null;
  const n = num.replace(/\s/g, "").toUpperCase();
  if (!PASSPORT_RE.test(n)) return "Passport number should be 1 letter followed by 7 digits.";
  return null;
}

export function parseYear(y: string): number | null {
  const n = parseInt(y.trim(), 10);
  if (Number.isNaN(n) || n < 1950 || n > 2100) return null;
  return n;
}

export function validateEducationYear(y: string): string | null {
  if (!y.trim()) return "Year of passing is required.";
  if (parseYear(y) === null) return "Enter a valid year (1950–2100).";
  return null;
}

export function validatePercentageCgpa(val: string): string | null {
  if (!val.trim()) return null;
  const n = parseFloat(val.replace(/%/g, ""));
  if (Number.isNaN(n)) return "Enter a valid number for percentage or CGPA.";
  if (n < 0 || n > 100) return "Value should be between 0 and 100.";
  return null;
}

export function validateDateOrder(start: string, end: string): string | null {
  if (!start || !end) return null;
  const a = new Date(start).getTime();
  const b = new Date(end).getTime();
  if (Number.isNaN(a) || Number.isNaN(b)) return "Enter valid dates.";
  if (b < a) return "End date must be on or after start date.";
  return null;
}
