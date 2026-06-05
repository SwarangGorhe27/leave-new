export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
