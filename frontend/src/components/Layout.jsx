import { Link, useLocation, useNavigate } from "react-router-dom";
import useStore from "../store/useStore";

const navLinks = [
  { to: "/", label: "Dashboard", icon: "▦" },
  { to: "/tasks", label: "Tarefas", icon: "✓" },
  { to: "/pdf", label: "PDF + IA", icon: "◧" },
];

export default function Layout({ children }) {
  const { logout } = useStore();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex h-screen bg-gray-950 overflow-hidden">
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col flex-shrink-0">
        <div className="p-5 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center flex-shrink-0">
              <span className="text-white text-xs font-bold">AI</span>
            </div>
            <div>
              <p className="text-white font-semibold text-sm leading-tight">Task Manager</p>
              <p className="text-gray-500 text-xs">v2.0</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-3 space-y-1">
          {navLinks.map((link) => (
            <Link
              key={link.to}
              to={link.to}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                location.pathname === link.to
                  ? "bg-violet-600 text-white"
                  : "text-gray-400 hover:bg-gray-800 hover:text-white"
              }`}
            >
              <span className="text-base w-4 text-center">{link.icon}</span>
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-400 hover:bg-red-900/30 hover:text-red-400 transition-colors"
          >
            <span>⇥</span> Sair
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto bg-gray-950">
        {children}
      </main>
    </div>
  );
}