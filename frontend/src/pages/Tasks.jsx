import { useState, useEffect } from "react";
import { tasksAPI } from "../services/api";
import useStore from "../store/useStore";

const CATEGORIES = ["geral", "trabalho", "estudos", "pessoal", "saude"];

const CATEGORY_COLORS = {
  geral: "bg-gray-700 text-gray-200",
  trabalho: "bg-blue-900 text-blue-200",
  estudos: "bg-violet-900 text-violet-200",
  pessoal: "bg-pink-900 text-pink-200",
  saude: "bg-green-900 text-green-200",
};

export default function Tasks() {
  const { tasks, setTasks, addTask, updateTask, removeTask } = useStore();
  const [form, setForm] = useState({ title: "", description: "", category: "geral" });
  const [aiLoading, setAiLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [filter, setFilter] = useState("all");
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    tasksAPI.list().then((r) => setTasks(r.data));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (creating || !form.title.trim()) return;
    setCreating(true);
    try {
      const res = await tasksAPI.create(form);
      addTask(res.data);
      setForm({ title: "", description: "", category: "geral" });
    } catch {
    } finally {
      setCreating(false);
    }
  };

  const handleToggle = async (task) => {
    try {
      const res = await tasksAPI.update(task.id, { is_completed: !task.is_completed });
      updateTask(res.data);
    } catch {}
  };

  const handleDelete = async (id) => {
    try {
      await tasksAPI.delete(id);
      removeTask(id);
    } catch {}
  };

  const handlePrioritize = async () => {
    setAiLoading(true);
    try {
      const ids = tasks.filter((t) => !t.is_completed).map((t) => t.id);
      if (ids.length === 0) return;
      const res = await tasksAPI.prioritize(ids);
      const prioritized = res.data;
      const completed = tasks.filter((t) => t.is_completed);
      setTasks([...prioritized, ...completed]);
    } catch {
    } finally {
      setAiLoading(false);
    }
  };

  const handleSummary = async () => {
    setAiLoading(true);
    setSummary("");
    try {
      const res = await tasksAPI.summary();
      setSummary(res.data.summary);
    } catch {
    } finally {
      setAiLoading(false);
    }
  };

  const filtered = tasks.filter((t) => {
    if (filter === "pending") return !t.is_completed;
    if (filter === "done") return t.is_completed;
    return true;
  });

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Minhas Tarefas</h1>
          <p className="text-gray-400 text-sm mt-1">{tasks.length} tarefas no total</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handlePrioritize}
            disabled={aiLoading || tasks.filter((t) => !t.is_completed).length === 0}
            className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-4 py-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {aiLoading ? "Processando..." : "Priorizar com IA"}
          </button>
          <button
            onClick={handleSummary}
            disabled={aiLoading || tasks.length === 0}
            className="bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white text-sm px-4 py-2 rounded-lg transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Resumo do dia
          </button>
        </div>
      </div>

      {summary && (
        <div className="bg-violet-900/20 border border-violet-700/40 rounded-xl p-4 mb-5">
          <p className="text-violet-300 text-xs font-medium mb-2">Resumo gerado pela IA</p>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-line">{summary}</p>
          <button
            onClick={() => setSummary("")}
            className="text-violet-500 hover:text-violet-400 text-xs mt-2"
          >
            Fechar
          </button>
        </div>
      )}

      <form onSubmit={handleCreate} className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-5">
        <div className="flex gap-3 mb-3">
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="Título da tarefa"
            maxLength={200}
            className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm placeholder-gray-500"
          />
          <select
            value={form.category}
            onChange={(e) => setForm({ ...form, category: e.target.value })}
            className="bg-gray-800 text-white rounded-lg px-3 py-2.5 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-3">
          <input
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Descrição (opcional)"
            maxLength={1000}
            className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2.5 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm placeholder-gray-500"
          />
          <button
            type="submit"
            disabled={creating}
            className="bg-violet-600 hover:bg-violet-500 text-white px-5 py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {creating ? "..." : "Adicionar"}
          </button>
        </div>
      </form>

      <div className="flex items-center gap-2 mb-4">
        {[
          { key: "all", label: "Todas" },
          { key: "pending", label: "Pendentes" },
          { key: "done", label: "Concluídas" },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`text-sm px-4 py-1.5 rounded-full transition-colors ${
              filter === f.key
                ? "bg-violet-600 text-white"
                : "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white"
            }`}
          >
            {f.label}
          </button>
        ))}
        <span className="ml-auto text-gray-600 text-xs">{filtered.length} itens</span>
      </div>

      <div className="space-y-2">
        {filtered.map((task) => (
          <div
            key={task.id}
            className={`bg-gray-900 rounded-xl border p-4 flex items-start gap-3 transition-opacity ${
              task.is_completed ? "border-gray-800 opacity-50" : "border-gray-700"
            }`}
          >
            <button
              onClick={() => handleToggle(task)}
              className={`mt-0.5 w-5 h-5 rounded-full border-2 flex-shrink-0 transition-colors ${
                task.is_completed
                  ? "bg-violet-600 border-violet-600"
                  : "border-gray-600 hover:border-violet-500"
              }`}
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                {task.priority > 0 && (
                  <span className="text-violet-400 text-xs font-mono">#{task.priority}</span>
                )}
                <span
                  className={`text-sm font-medium ${
                    task.is_completed ? "line-through text-gray-500" : "text-white"
                  }`}
                >
                  {task.title}
                </span>
                <span
                  className={`text-xs px-2 py-0.5 rounded-full ${
                    CATEGORY_COLORS[task.category] || CATEGORY_COLORS.geral
                  }`}
                >
                  {task.category}
                </span>
              </div>
              {task.description && (
                <p className="text-gray-500 text-xs mt-1 truncate">{task.description}</p>
              )}
            </div>
            <button
              onClick={() => handleDelete(task.id)}
              className="text-gray-700 hover:text-red-400 transition-colors flex-shrink-0 text-sm px-1"
              title="Excluir"
            >
              ✕
            </button>
          </div>
        ))}
        {filtered.length === 0 && (
          <div className="text-center text-gray-600 py-16 text-sm">
            Nenhuma tarefa aqui.
          </div>
        )}
      </div>
    </div>
  );
}