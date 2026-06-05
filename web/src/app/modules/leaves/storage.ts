export function readStore<T>(key: string, seed: T[]): T[] {
  const raw = localStorage.getItem(key);
  if (raw) {
    try {
      return JSON.parse(raw) as T[];
    } catch {
      // fallthrough
    }
  }
  localStorage.setItem(key, JSON.stringify(seed));
  return seed;
}

export function writeStore<T>(key: string, data: T[]) {
  localStorage.setItem(key, JSON.stringify(data));
}

