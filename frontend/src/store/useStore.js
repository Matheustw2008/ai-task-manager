import { create } from "zustand";

const useStore = create((set) => ({
  user: null,
  token: sessionStorage.getItem("token") || null,
  tasks: [],
  pdfs: [],

  setAuth: (user, token) => {
    sessionStorage.setItem("token", token);
    set({ user, token });
  },

  logout: () => {
    sessionStorage.removeItem("token");
    set({ user: null, token: null, tasks: [], pdfs: [] });
  },

  setTasks: (tasks) => set({ tasks }),
  addTask: (task) => set((s) => ({ tasks: [...s.tasks, task] })),
  updateTask: (updated) =>
    set((s) => ({
      tasks: s.tasks.map((t) => (t.id === updated.id ? updated : t)),
    })),
  removeTask: (id) =>
    set((s) => ({ tasks: s.tasks.filter((t) => t.id !== id) })),

  setPdfs: (pdfs) => set({ pdfs }),
  addPdf: (pdf) => set((s) => ({ pdfs: [...s.pdfs, pdf] })),
  removePdf: (id) =>
    set((s) => ({ pdfs: s.pdfs.filter((p) => p.id !== id) })),
}));

export default useStore;