import { useLocation } from "react-router-dom";

const pageMap = {
  "/upload": "Upload",
  "/dashboard": "Dashboard (What)",
  "/ai-analytics": "AI Analytics (Why)",
  "/strategy": "Strategy (What To Do)",
};

function Navbar() {
  const location = useLocation();
  const page = pageMap[location.pathname] || "ValorEdge AI";

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between">
      <h2 className="font-semibold text-slate-900">{page}</h2>
      <span className="text-xs text-slate-500">Dashboard | Analytics | Strategy</span>
    </header>
  );
}

export default Navbar;
