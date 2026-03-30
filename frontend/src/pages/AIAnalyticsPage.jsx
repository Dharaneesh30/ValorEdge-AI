import useApi from "../hooks/useApi";
import { CorrelationHeatmap, FeatureImportanceChart, PcaScatterChart } from "../components/Charts";

function AIAnalyticsPage() {
  const { data, loading, error } = useApi("/analytics");

  if (loading) return <div className="p-6">Loading analytics...</div>;
  if (error) return <div className="p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  const clusterKeywords = data?.cluster_insights?.keywords || {};

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900">AI Analytics - Why It Is Happening</h2>
        <p className="text-sm text-slate-600 mt-2 whitespace-pre-wrap">{data?.root_cause_analysis}</p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
        <h3 className="font-semibold text-slate-800 mb-2">Cluster Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
          {Object.entries(clusterKeywords).map(([cluster, words]) => (
            <div key={cluster} className="rounded-lg bg-slate-50 p-3">
              <p className="font-semibold">Cluster {cluster}</p>
              <p className="text-slate-600 mt-1">{(words || []).join(", ") || "No keywords"}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <FeatureImportanceChart data={(data?.feature_importance || []).slice(0, 15)} />
        <PcaScatterChart data={data?.pca_components || []} />
      </div>

      <CorrelationHeatmap matrix={data?.correlation_matrix || {}} />
    </div>
  );
}

export default AIAnalyticsPage;
