import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import UploadPage from "./pages/UploadPage";
import AIAnalyticsPage from "./pages/AIAnalyticsPage";
import StrategyPage from "./pages/SimulationPage";

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100 text-slate-900 flex">
        <Sidebar />
        <main className="flex-1">
          <Navbar />
          <div className="p-6">
            <Routes>
              <Route path="/upload" element={<UploadPage />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/ai-analytics" element={<AIAnalyticsPage />} />
              <Route path="/strategy" element={<StrategyPage />} />
              <Route path="*" element={<Navigate to="/upload" replace />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
