import axios from "axios";

function resolveApiBase(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined;
  if (raw === undefined || raw.trim() === "") {
    // Relative URL — uses Vite dev-server proxy in development.
    return "";
  }
  return raw.replace(/\/$/, "");
}

const API_BASE = resolveApiBase();

const api = axios.create({
  baseURL: API_BASE ? `${API_BASE}/api` : "/api",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("hrms_access_token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Attach JWT token from localStorage on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('hrms_access_token');
  if (token) {
    config.headers = config.headers ?? {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
});

export default api;

export function unwrap<T>(response: { data: { data: T } | T }): T {
  if (
    typeof response.data === "object" &&
    response.data !== null &&
    "data" in response.data
  ) {
    return response.data.data as T;
  }

  return response.data as T;
}