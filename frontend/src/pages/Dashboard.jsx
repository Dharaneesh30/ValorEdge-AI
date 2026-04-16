import useApi from "../hooks/useApi";
import { ForecastChart, ModelComparisonChart, SentimentTrendChart } from "../components/Charts";
import CompanyPageInsights from "../components/CompanyPageInsights";
import PageAIInsights from "../components/PageAIInsights";
import LiveInference from "../components/LiveInference";
import { useCompanyComparison } from "../context/CompanyContext";
import API_BASE_URL from "../config/api";

function Dashboard() {
  const { data, loading, error } = useApi("/dashboard");
  const { selectedCompany } = useCompanyComparison();

  const downloadReport = async () => {
    try {
      const query = selectedCompany ? `?company=${encodeURIComponent(selectedCompany)}` : "";
      const response = await fetch(`${API_BASE_URL}/report/export${query}`);
      if (!response.ok) throw new Error("Failed to export report");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "valoredge_report.pdf";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      // Minimal UX fallback.
      // eslint-disable-next-line no-alert
      alert(err?.message || "Report export failed");
    }
  };

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading dashboard...</div>;
  if (error) return <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">My Company vs Others</p>
        <h1 className="ve-title">Competitive Performance Dashboard</h1>
        <p className="ve-subtitle">Track your company KPI against peer-driven signals, forecast outlook, and model quality.</p>
        <button type="button" onClick={downloadReport} className="ve-btn-primary mt-3">Download Project Report</button>
      </section>

      <CompanyPageInsights page="dashboard" />

      <LiveInference page="dashboard" data={data} />

      <div className="ve-kpi rounded-2xl p-5 sm:p-6">
        <p className="text-xs uppercase tracking-[0.18em] text-cyan-200">Live Corporate Reputation</p>
        <p className="mt-2 text-4xl font-semibold tracking-tight sm:text-5xl">{Number(data?.reputation_score || 0).toFixed(3)}</p>
        <p className="mt-1 text-sm text-slate-200">Unified score from sentiment, trend, and model performance</p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Best Model</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{data?.best_model || "N/A"}</p>
          <p className="mt-2 text-xs text-slate-600">Lowest error selected from current run</p>
        </div>

        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Forecast Points</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{(data?.forecast || []).length}</p>
          <p className="mt-2 text-xs text-slate-600">Forward-looking reputation signal horizon</p>
        </div>

        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Sentiment Samples</p>
          <p className="mt-2 text-xl font-semibold text-slate-900">{(data?.sentiment_trend || []).length}</p>
          <p className="mt-2 text-xs text-slate-600">Recent datapoints in trend analysis</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <SentimentTrendChart data={data?.sentiment_trend || []} />
        <ForecastChart history={[]} forecast={data?.forecast || []} />
      </div>

      <ModelComparisonChart data={data?.model_summary || []} />

      <div className="ve-card rounded-2xl p-5">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-700">Why This Is Best Model</h3>
        {(() => {
          const rows = [...(data?.model_summary || [])].sort((a, b) => (a?.rmse ?? 1e9) - (b?.rmse ?? 1e9));
          const best = rows[0];
          const second = rows[1];
          if (!best) return <p className="mt-2 text-sm text-slate-600">Model comparison not available yet.</p>;
          return (
            <div className="mt-2 space-y-2 text-sm text-slate-700">
              <p><strong>Selected:</strong> {best.model}</p>
              <p><strong>Metrics:</strong> RMSE {best.rmse}, MAE {best.mae}, R2 {best.r2}</p>
              {second && <p><strong>Runner-up:</strong> {second.model} (RMSE {second.rmse})</p>}
              <p><strong>Justification:</strong> Lowest RMSE with stable MAE and competitive R2.</p>
            </div>
          );
        })()}
      </div>

      <PageAIInsights page="dashboard" data={data} />
    </div>
  );
}

export default Dashboard;
