import useApi from "../hooks/useApi";
import { ForecastChart, ModelComparisonChart, SentimentTrendChart } from "../components/Charts";

function Dashboard() {
  const { data, loading, error } = useApi("/dashboard");

  if (loading) return <div className="p-6">Loading dashboard...</div>;
  if (error) return <div className="p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm xl:col-span-2">
          <p className="text-xs uppercase tracking-wide text-slate-500">Main KPI</p>
          <p className="text-3xl font-bold text-slate-900 mt-2">{Number(data?.reputation_score || 0).toFixed(3)}</p>
          <p className="text-sm text-slate-500 mt-1">Reputation Score</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">Best Model</p>
          <p className="text-xl font-bold text-slate-900 mt-2">{data?.best_model || "N/A"}</p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-wide text-slate-500">Forecast Points</p>
          <p className="text-xl font-bold text-slate-900 mt-2">{(data?.forecast || []).length}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <SentimentTrendChart data={data?.sentiment_trend || []} />
        <ForecastChart history={[]} forecast={data?.forecast || []} />
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <h3 className="font-semibold text-slate-800 mb-3">Model Performance Summary</h3>
        <ModelComparisonChart data={data?.model_summary || []} />
      </div>
    </div>
  );
}

export default Dashboard;
