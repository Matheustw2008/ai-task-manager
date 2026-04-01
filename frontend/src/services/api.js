import axios from "axios";

const URL_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8001";

const api = axios.create({
  baseURL: URL_BASE,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      sessionStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post("/auth/register", {
    name: String(data.name).trim().slice(0, 100),
    email: String(data.email).trim().toLowerCase().slice(0, 255),
    password: String(data.password),
  }),
  login: (data) => api.post("/auth/login", {
    email: String(data.email).trim().toLowerCase().slice(0, 255),
    password: String(data.password),
  }),
};

export const tasksAPI = {
  list: () => api.get("/tasks/"),
  create: (data) => api.post("/tasks/", {
    title: String(data.title).trim().slice(0, 200),
    description: data.description ? String(data.description).trim().slice(0, 1000) : null,
    category: String(data.category).trim().slice(0, 50),
  }),
  update: (id, data) => api.put(`/tasks/${Number(id)}`, data),
  delete: (id) => api.delete(`/tasks/${Number(id)}`),
  prioritize: (ids) => api.post("/tasks/prioritize", { task_ids: ids.map(Number) }),
  summary: () => api.get("/tasks/summary"),
};

export const pdfAPI = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/pdf/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 60000,
    });
  },
  list: () => api.get("/pdf/"),
  summarize: (id) => api.post(`/pdf/${Number(id)}/summarize`),
  ask: (id, question) => api.post(`/pdf/${Number(id)}/ask`, {
    question: String(question).trim().slice(0, 500),
  }),
  delete: (id) => api.delete(`/pdf/${Number(id)}`),
};

export default api;
