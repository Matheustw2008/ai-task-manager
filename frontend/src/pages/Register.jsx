import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { authAPI } from "../services/api";

export default function Register() {
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (loading) return;
    if (form.password.length < 6) {
      setError("A senha precisa ter pelo menos 6 caracteres.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await authAPI.register(form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Erro ao criar conta. Tente novamente.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-violet-600 rounded-2xl mb-4">
            <span className="text-white text-2xl font-bold">AI</span>
          </div>
          <h1 className="text-3xl font-bold text-white">Criar conta</h1>
          <p className="text-gray-400 mt-2 text-sm">Comece a usar gratuitamente</p>
        </div>

        <div className="bg-gray-900 rounded-2xl p-8 border border-gray-800">
          {error && (
            <div className="bg-red-900/40 border border-red-700/50 text-red-300 rounded-lg px-4 py-3 mb-5 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} noValidate>
            <div className="mb-4">
              <label className="text-gray-300 text-sm font-medium block mb-2">Nome</label>
              <input
                type="text"
                name="name"
                required
                autoComplete="name"
                value={form.name}
                onChange={handleChange}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm"
                placeholder="Seu nome"
              />
            </div>

            <div className="mb-4">
              <label className="text-gray-300 text-sm font-medium block mb-2">Email</label>
              <input
                type="email"
                name="email"
                required
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm"
                placeholder="seu@email.com"
              />
            </div>

            <div className="mb-6">
              <label className="text-gray-300 text-sm font-medium block mb-2">Senha</label>
              <input
                type="password"
                name="password"
                required
                autoComplete="new-password"
                minLength={6}
                value={form.password}
                onChange={handleChange}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:border-violet-500 focus:outline-none text-sm"
                placeholder="Mínimo 6 caracteres"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-violet-600 hover:bg-violet-500 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {loading ? "Criando conta..." : "Criar conta"}
            </button>
          </form>

          <p className="text-center text-gray-500 text-sm mt-5">
            Já tem conta?{" "}
            <Link to="/login" className="text-violet-400 hover:text-violet-300 font-medium">
              Entrar
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}