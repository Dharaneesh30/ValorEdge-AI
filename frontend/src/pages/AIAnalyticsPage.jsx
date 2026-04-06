import useApi from "../hooks/useApi";
import { CorrelationHeatmap, FeatureImportanceChart, PcaScatterChart } from "../components/Charts";
import CompanyPageInsights from "../components/CompanyPageInsights";

function AIAnalyticsPage() {
  const { data, loading, error } = useApi("/analytics");

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading analytics...</div>;
  if (error) return <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  const clusterKeywords = data?.cluster_insights?.keywords || {};

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">My Company vs Others</p>
        <h1 className="ve-title">Competitive Root-Cause Analytics</h1>
        <p className="ve-subtitle">Analyze why your company differs from peers through features, clusters, PCA, and correlations.</p>
      </section>

      <CompanyPageInsights page="analytics" />

      <div className="ve-card rounded-2xl p-5">
        <h2 className="text-xl font-semibold tracking-tight text-slate-900">Why It Is Happening</h2>
        <p className="mt-3 text-sm text-slate-700 whitespace-pre-wrap">{data?.root_cause_analysis}</p>
      </div>

      <div className="ve-card rounded-2xl p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Cluster Insights</h3>
        <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-2">
          {Object.entries(clusterKeywords).length === 0 && (
            <p className="text-xs text-slate-500">No cluster keywords available yet. Upload dataset and run pipeline.</p>
          )}
          {Object.entries(clusterKeywords).map(([cluster, words]) => (
            <div key={cluster} className="rounded-xl border border-slate-200/80 bg-white/70 p-3">
              <p className="text-sm font-semibold text-slate-900">Cluster {cluster}</p>
              <p className="mt-1 text-xs text-slate-600">{(words || []).join(", ") || "No keywords"}</p>
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
