import { useState, useEffect, useRef } from "react";
import { pdfAPI } from "../services/api";
import useStore from "../store/useStore";

const CHAT_KEY = (id) => `pdf_chat_${id}`;

export default function PDFReader() {
  const { pdfs, setPdfs, addPdf, removePdf } = useStore();
  const [selected, setSelected] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const fileRef = useRef();
  const chatEndRef = useRef();

  useEffect(() => {
    pdfAPI.list().then((r) => setPdfs(r.data));
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const saveChat = (pdfId, messages) => {
    try {
      localStorage.setItem(CHAT_KEY(pdfId), JSON.stringify(messages));
    } catch {}
  };

  const loadChat = (pdfId) => {
    try {
      const saved = localStorage.getItem(CHAT_KEY(pdfId));
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  };

  const updateChat = (pdfId, updater) => {
    setChat((prev) => {
      const next = typeof updater === "function" ? updater(prev) : updater;
      saveChat(pdfId, next);
      return next;
    });
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      alert("Apenas arquivos .pdf são aceitos.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      alert("Arquivo muito grande. Máximo 10MB.");
      return;
    }
    setUploading(true);
    try {
      const res = await pdfAPI.upload(file);
      const newPdf = {
        id: res.data.id,
        filename: res.data.filename,
        summary: null,
        created_at: res.data.created_at,
      };
      addPdf(newPdf);
      const initialChat = [
        {
          role: "system",
          content: `PDF "${file.name}" carregado com sucesso! Peça um resumo ou faça perguntas sobre o conteúdo.`,
        },
      ];
      saveChat(newPdf.id, initialChat);
      setSelected(newPdf);
      setChat(initialChat);
    } catch {
      alert("Erro ao enviar PDF. Tente novamente.");
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  const handleSelect = (pdf) => {
    setSelected(pdf);
    const saved = loadChat(pdf.id);
    if (saved && saved.length > 0) {
      setChat(saved);
    } else {
      const initial = [
        {
          role: "system",
          content: `PDF "${pdf.filename}" selecionado. Peça um resumo ou faça perguntas!`,
        },
      ];
      setChat(initial);
      saveChat(pdf.id, initial);
    }
  };

  const handleSummarize = async () => {
    if (!selected || loading) return;
    setLoading(true);
    try {
      const res = await pdfAPI.summarize(selected.id);
      updateChat(selected.id, (prev) => [
        ...prev,
        { role: "user", content: "Resuma este PDF para mim." },
        { role: "assistant", content: res.data.summary },
      ]);
    } catch {
      updateChat(selected.id, (prev) => [
        ...prev,
        { role: "error", content: "Erro ao gerar resumo. Tente novamente." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    const q = question.trim();
    if (!selected || !q || loading) return;
    setQuestion("");
    updateChat(selected.id, (prev) => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res = await pdfAPI.ask(selected.id, q);
      updateChat(selected.id, (prev) => [
        ...prev,
        { role: "assistant", content: res.data.answer },
      ]);
    } catch {
      updateChat(selected.id, (prev) => [
        ...prev,
        { role: "error", content: "Erro ao processar pergunta. Tente novamente." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await pdfAPI.delete(id);
      removePdf(id);
      localStorage.removeItem(CHAT_KEY(id));
      if (selected?.id === id) {
        setSelected(null);
        setChat([]);
      }
    } catch {}
  };

  const handleClearChat = () => {
    if (!selected) return;
    const reset = [
      {
        role: "system",
        content: `Conversa limpa. Faça novas perguntas sobre "${selected.filename}".`,
      },
    ];
    setChat(reset);
    saveChat(selected.id, reset);
  };

  return (
    <div className="flex" style={{ height: "100vh" }}>
      <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col flex-shrink-0">
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-white font-semibold text-sm mb-3">Meus PDFs</h2>
          <button
            onClick={() => fileRef.current.click()}
            disabled={uploading}
            className="w-full bg-violet-600 hover:bg-violet-500 text-white text-sm py-2.5 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {uploading ? "Enviando..." : "+ Carregar PDF"}
          </button>
          <input
            ref={fileRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={handleUpload}
          />
          <p className="text-gray-600 text-xs mt-2 text-center">Máximo 10MB</p>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {pdfs.map((pdf) => (
            <div
              key={pdf.id}
              onClick={() => handleSelect(pdf)}
              className={`rounded-lg p-3 cursor-pointer flex items-start justify-between gap-2 transition-colors ${
                selected?.id === pdf.id
                  ? "bg-violet-900/40 border border-violet-700/50"
                  : "hover:bg-gray-800 border border-transparent"
              }`}
            >
              <div className="min-w-0 flex-1">
                <p className="text-white text-xs font-medium truncate">{pdf.filename}</p>
                <p className="text-gray-500 text-xs mt-0.5">
                  {new Date(pdf.created_at).toLocaleDateString("pt-BR")}
                </p>
                {loadChat(pdf.id)?.length > 1 && (
                  <p className="text-violet-400 text-xs mt-0.5">● histórico salvo</p>
                )}
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); handleDelete(pdf.id); }}
                className="text-gray-600 hover:text-red-400 text-xs flex-shrink-0 mt-0.5"
                title="Excluir PDF"
              >
                ✕
              </button>
            </div>
          ))}
          {pdfs.length === 0 && (
            <p className="text-gray-600 text-xs text-center mt-6 px-2">
              Nenhum PDF enviado ainda.
            </p>
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col overflow-hidden">
        {selected ? (
          <>
            <div className="p-4 border-b border-gray-800 flex items-center justify-between flex-shrink-0">
              <div className="min-w-0">
                <h3 className="text-white font-medium text-sm truncate">{selected.filename}</h3>
                <p className="text-gray-500 text-xs">
                  {chat.filter((m) => m.role !== "system").length} mensagens salvas
                </p>
              </div>
              <div className="flex gap-2 flex-shrink-0 ml-4">
                <button
                  onClick={handleClearChat}
                  className="bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white text-xs px-3 py-2 rounded-lg transition-colors"
                >
                  Limpar chat
                </button>
                <button
                  onClick={handleSummarize}
                  disabled={loading}
                  className="bg-violet-600 hover:bg-violet-500 text-white text-sm px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? "Gerando..." : "Resumir com IA"}
                </button>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {chat.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-2xl rounded-xl px-4 py-3 text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-violet-600 text-white"
                        : msg.role === "error"
                        ? "bg-red-900/40 border border-red-700/50 text-red-300"
                        : msg.role === "system"
                        ? "bg-gray-800 text-gray-400 border border-gray-700 text-xs"
                        : "bg-gray-800 text-gray-100"
                    }`}
                  >
                    <p className="whitespace-pre-line">{msg.content}</p>
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 rounded-xl px-4 py-3">
                    <div className="flex gap-1">
                      {[0, 150, 300].map((delay) => (
                        <span
                          key={delay}
                          className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"
                          style={{ animationDelay: `${delay}ms` }}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <form
              onSubmit={handleAsk}
              className="p-4 border-t border-gray-800 flex gap-3 flex-shrink-0"
            >
              <input
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Faça uma pergunta sobre o PDF..."
                maxLength={500}
                disabled={loading}
                className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm placeholder-gray-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={loading || !question.trim()}
                className="bg-violet-600 hover:bg-violet-500 text-white px-5 py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm flex-shrink-0"
              >
                estampar
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-gray-500 text-2xl">◧</span>
              </div>
              <p className="text-gray-400 font-medium text-sm">Selecione um PDF</p>
              <p className="text-gray-600 text-xs mt-1">ou faça upload de um novo arquivo</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}