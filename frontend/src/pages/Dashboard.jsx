import useApi from "../hooks/useApi";
import { ForecastChart, ModelComparisonChart, SentimentTrendChart } from "../components/Charts";
import CompanyBenchmarkPanel from "../components/CompanyBenchmarkPanel";

function Dashboard() {
  const { data, loading, error } = useApi("/dashboard");

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading dashboard...</div>;
  if (error) return <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">Overview</p>
        <h1 className="ve-title">Performance Dashboard</h1>
        <p className="ve-subtitle">Unified view of KPI movement, forecast outlook, and model quality.</p>
      </section>

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

      <CompanyBenchmarkPanel
        title="Benchmark This Company"
        description="Pick a company and compare against all peers to identify where it can outperform."
      />
    </div>
  );
}

export default Dashboard;
