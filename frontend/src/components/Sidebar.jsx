import { Link, useLocation } from "react-router-dom";

function Sidebar() {
  const location = useLocation();
  const links = [
    { to: "/upload", label: "Upload" },
    { to: "/dashboard", label: "Dashboard" },
    { to: "/ai-analytics", label: "AI Analytics" },
    { to: "/strategy", label: "Strategy" },
  ];

  return (
    <aside className="w-64 min-h-screen bg-slate-900 text-slate-100 p-5">
      <h1 className="text-xl font-bold">ValorEdge AI</h1>
      <p className="text-xs text-slate-400 mt-1">Decision Intelligence Platform</p>
      <nav className="mt-6 space-y-2">
        {links.map((item) => {
          const active = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`block rounded-lg px-3 py-2 text-sm ${active ? "bg-teal-700 text-white" : "hover:bg-slate-800 text-slate-200"}`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

export default Sidebar;
