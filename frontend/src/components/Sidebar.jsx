import { Link, useLocation } from "react-router-dom";

function Sidebar({ open, onClose }) {
  const location = useLocation();
  const links = [
    { to: "/upload", label: "Upload", sub: "Data Intake" },
    { to: "/dashboard", label: "Dashboard", sub: "Live KPIs" },
    { to: "/ai-analytics", label: "AI Analytics", sub: "Root Cause" },
    { to: "/graphs", label: "Graphs", sub: "Full Layout" },
    { to: "/strategy", label: "Strategy", sub: "What To Do" },
  ];

  return (
    <>
      <div
        onClick={onClose}
        className={`fixed inset-0 z-30 bg-slate-950/40 backdrop-blur-sm transition-opacity duration-300 lg:hidden ${
          open ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
      />
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-700/40 bg-slate-950/90 p-5 text-slate-100 backdrop-blur-xl transition-transform duration-300 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="rounded-2xl border border-cyan-900/50 bg-slate-900/95 p-4 text-slate-100 shadow-lg">
          <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300">ValorEdge AI</p>
          <p className="mt-1 text-sm text-slate-300">Corporate Reputation Intelligence</p>
        </div>

        <nav className="mt-6 space-y-2">
          {links.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onClose}
                className={`group block rounded-xl border px-3 py-2.5 transition-all ${
                  active
                    ? "border-cyan-400/60 bg-cyan-500/15 text-cyan-100 shadow-sm"
                    : "border-transparent text-slate-300 hover:border-slate-700 hover:bg-slate-800/70"
                }`}
              >
                <p className="text-sm font-semibold">{item.label}</p>
                <p className={`text-[11px] ${active ? "text-cyan-200/80" : "text-slate-400"}`}>{item.sub}</p>
              </Link>
            );
          })}
        </nav>

        <div className="mt-8 rounded-xl border border-amber-400/30 bg-amber-500/10 p-3 text-xs text-amber-100">
          Upload a CSV and this panel turns into a live decision cockpit in under a minute.
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
