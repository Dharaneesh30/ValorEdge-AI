import { useLocation } from "react-router-dom";

const pageMap = {
  "/upload": { title: "Dataset Intake", subtitle: "Bring new company signals into the pipeline" },
  "/dashboard": { title: "Performance Dashboard", subtitle: "What is happening now" },
  "/ai-analytics": { title: "AI Analytics", subtitle: "Why changes are happening" },
  "/graphs": { title: "Graph Workspace", subtitle: "All charts in one smooth-scroll page" },
  "/strategy": { title: "Strategy Studio", subtitle: "What to do next" },
};

function Navbar({ onOpenSidebar }) {
  const location = useLocation();
  const page = pageMap[location.pathname] || {
    title: "ValorEdge AI",
    subtitle: "Decision Intelligence Platform",
  };

  return (
    <header className="sticky top-0 z-20 border-b border-white/70 bg-white/70 px-4 py-3 backdrop-blur-xl sm:px-6 lg:px-8">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onOpenSidebar}
            className="inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-700 shadow-sm lg:hidden"
            aria-label="Open menu"
          >
            <span className="text-lg leading-none">Menu</span>
          </button>
          <div>
            <h2 className="text-lg font-semibold tracking-tight text-slate-900 sm:text-xl">{page.title}</h2>
            <p className="text-xs text-slate-600">{page.subtitle}</p>
          </div>
        </div>

        <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-800 sm:inline-flex">
          <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-500" />
          Live Workspace
        </div>
      </div>
    </header>
  );
}

export default Navbar;
