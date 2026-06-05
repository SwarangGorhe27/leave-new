export const maskSensitive = (key: string, value: string) => {
  const lower = key.toLowerCase();
  if (!value) return value;
  if (!["aadhaar", "pan", "accountnumber", "passport"].some((entry) => lower.includes(entry))) {
    return value;
  }
  if (value.length <= 4) return "*".repeat(value.length);
  return `${"*".repeat(Math.max(0, value.length - 4))}${value.slice(-4)}`;
};

const flattenObject = (obj: unknown, parentKey = ""): Record<string, string> => {
  if (obj === null || obj === undefined) return {};
  if (typeof obj !== "object") {
    return { [parentKey || "value"]: String(obj) };
  }
  if (Array.isArray(obj)) {
    return obj.reduce((acc, item, index) => {
      const next = flattenObject(item, `${parentKey}[${index}]`);
      return { ...acc, ...next };
    }, {} as Record<string, string>);
  }
  return Object.entries(obj as Record<string, unknown>).reduce((acc, [key, value]) => {
    const path = parentKey ? `${parentKey}.${key}` : key;
    const next = flattenObject(value, path);
    return { ...acc, ...next };
  }, {} as Record<string, string>);
};

export const buildDiffRows = (oldValue: unknown, newValue: unknown) => {
  const oldFlat = flattenObject(oldValue);
  const nextFlat = flattenObject(newValue);
  const keys = Array.from(new Set([...Object.keys(oldFlat), ...Object.keys(nextFlat)]));
  return keys
    .filter((key) => oldFlat[key] !== nextFlat[key])
    .map((key) => ({
      field: key,
      oldValue: oldFlat[key] ?? "",
      newValue: nextFlat[key] ?? "",
    }));
};

export const isEqualPayload = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

export const validateEmail = (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());

export const validatePan = (value: string) => /^[A-Z]{5}[0-9]{4}[A-Z]$/.test(value.replace(/\s+/g, "").toUpperCase());

export const validateAadhaar = (value: string) => /^[0-9]{12}$/.test(value.replace(/\s+/g, ""));

export const detectDuplicateValues = (values: string[]) => {
  const clean = values.map((value) => value.trim()).filter(Boolean);
  return new Set(clean).size !== clean.length;
};
