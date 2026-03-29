import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { tasksAPI } from "../services/api";
import useStore from "../store/useStore";

export default function Dashboard() {
  const { tasks, setTasks, pdfs } = useStore();
  const [summary, setSummary] = useState("");
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(true);

  useEffect(() => {
    tasksAPI.list()
      .then((r) => setTasks(r.data))
      .finally(() => setLoadingTasks(false));
  }, []);

  const done = tasks.filter((t) => t.is_completed).length;
  const pending = tasks.filter((t) => !t.is_completed).length;
  const percent = tasks.length > 0 ? Math.round((done / tasks.length) * 100) : 0;

  const categoryCount = tasks.reduce((acc, t) => {
    acc[t.category] = (acc[t.category] || 0) + 1;
    return acc;
  }, {});

  const handleSummary = async () => {
    setLoadingSummary(true);
    setSummary("");
    try {
      const res = await tasksAPI.summary();
      setSummary(res.data.summary);
    } catch {
      setSummary("Erro ao gerar resumo. Tente novamente.");
    } finally {
      setLoadingSummary(false);
    }
  };

  const stats = [
    { label: "Total", value: tasks.length, color: "text-white" },
    { label: "Pendentes", value: pending, color: "text-amber-400" },
    { label: "Concluídas", value: done, color: "text-green-400" },
    { label: "PDFs", value: pdfs.length, color: "text-violet-400" },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Visão geral do seu dia</p>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-6">
        {stats.map((s) => (
          <div key={s.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <p className="text-gray-500 text-xs mb-1">{s.label}</p>
            <p className={`text-3xl font-bold ${s.color}`}>
              {loadingTasks ? "—" : s.value}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-gray-300 text-sm font-medium">Progresso geral</p>
            <span className="text-violet-400 text-sm font-bold">{percent}%</span>
          </div>
          <div className="w-full bg-gray-800 rounded-full h-2 mb-2">
            <div
              className="bg-violet-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${percent}%` }}
            />
          </div>
          <p className="text-gray-500 text-xs">{done} de {tasks.length} tarefas concluídas</p>
        </div>

        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-gray-300 text-sm font-medium mb-3">Por categoria</p>
          <div className="space-y-2">
            {Object.entries(categoryCount).slice(0, 4).map(([cat, count]) => (
              <div key={cat} className="flex items-center justify-between">
                <span className="text-gray-400 text-xs capitalize">{cat}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 bg-gray-800 rounded-full h-1">
                    <div
                      className="bg-violet-600 h-1 rounded-full"
                      style={{ width: `${(count / tasks.length) * 100}%` }}
                    />
                  </div>
                  <span className="text-gray-400 text-xs w-4 text-right">{count}</span>
                </div>
              </div>
            ))}
            {Object.keys(categoryCount).length === 0 && (
              <p className="text-gray-600 text-xs">Nenhuma tarefa ainda.</p>
            )}
          </div>
        </div>
      </div>

      {summary ? (
        <div className="bg-violet-900/20 border border-violet-700/40 rounded-xl p-5 mb-6">
          <div className="flex items-center justify-between mb-3">
            <p className="text-violet-300 text-sm font-medium">Resumo do dia — IA</p>
            <button
              onClick={() => setSummary("")}
              className="text-violet-500 hover:text-violet-400 text-xs"
            >
              Fechar
            </button>
          </div>
          <p className="text-gray-300 text-sm leading-relaxed whitespace-pre-line">{summary}</p>
        </div>
      ) : (
        <button
          onClick={handleSummary}
          disabled={loadingSummary || tasks.length === 0}
          className="w-full bg-gray-900 hover:bg-gray-800 border border-gray-700 hover:border-violet-600 text-gray-300 hover:text-white rounded-xl p-4 text-sm transition-all disabled:opacity-40 disabled:cursor-not-allowed mb-6"
        >
          {loadingSummary ? "Gerando resumo com IA..." : "Gerar resumo inteligente do dia"}
        </button>
      )}

      <div className="grid grid-cols-2 gap-4">
        <Link
          to="/tasks"
          className="bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-violet-600 rounded-xl p-5 transition-all group"
        >
          <div className="w-10 h-10 bg-violet-900/40 group-hover:bg-violet-900/70 rounded-xl flex items-center justify-center mb-3 transition-colors">
            <span className="text-violet-400 text-lg">✓</span>
          </div>
          <p className="text-white font-medium text-sm">Gerenciar Tarefas</p>
          <p className="text-gray-500 text-xs mt-1">{pending} pendentes</p>
        </Link>

        <Link
          to="/pdf"
          className="bg-gray-900 hover:bg-gray-800 border border-gray-800 hover:border-violet-600 rounded-xl p-5 transition-all group"
        >
          <div className="w-10 h-10 bg-violet-900/40 group-hover:bg-violet-900/70 rounded-xl flex items-center justify-center mb-3 transition-colors">
            <span className="text-violet-400 text-lg">◧</span>
          </div>
          <p className="text-white font-medium text-sm">Leitor de PDF com IA</p>
          <p className="text-gray-500 text-xs mt-1">{pdfs.length} PDFs carregados</p>
        </Link>
      </div>
    </div>
  );
}