import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useState } from "react";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import AIAnalyticsPage from "./pages/AIAnalyticsPage";
import StrategyPage from "./pages/SimulationPage";
import GraphsPage from "./pages/GraphsPage";
import { CompanyProvider } from "./context/CompanyContext";

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <CompanyProvider>
      <BrowserRouter>
        <div className="min-h-screen ve-app-bg text-slate-900">
          <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
            <div className="absolute -top-24 -left-20 h-80 w-80 rounded-full bg-cyan-300/30 blur-3xl" />
            <div className="absolute top-1/4 -right-16 h-72 w-72 rounded-full bg-amber-300/30 blur-3xl" />
            <div className="absolute bottom-0 left-1/3 h-72 w-72 rounded-full bg-emerald-300/20 blur-3xl" />
          </div>

          <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

          <main className="min-h-screen transition-all duration-300 lg:ml-72">
            <Navbar onOpenSidebar={() => setSidebarOpen(true)} />
            <div className="mx-auto w-full max-w-[1450px] px-4 py-5 sm:px-6 lg:px-8">
              <Routes>
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/ai-analytics" element={<AIAnalyticsPage />} />
                <Route path="/graphs" element={<GraphsPage />} />
                <Route path="/strategy" element={<StrategyPage />} />
                <Route path="*" element={<Navigate to="/upload" replace />} />
              </Routes>
            </div>
          </main>
        </div>
      </BrowserRouter>
    </CompanyProvider>
  );
}

export default App;
