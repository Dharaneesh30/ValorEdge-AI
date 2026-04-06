import useApi from "../hooks/useApi";
import {
  CorrelationHeatmap,
  FeatureImportanceChart,
  ForecastChart,
  ModelComparisonChart,
  PcaScatterChart,
  SentimentTrendChart,
} from "../components/Charts";
import CompanyPageInsights from "../components/CompanyPageInsights";

function GraphsPage() {
  const dashboard = useApi("/dashboard");
  const analytics = useApi("/analytics");

  const loading = dashboard.loading || analytics.loading;
  const error = dashboard.error || analytics.error;
  const dashboardData = dashboard.data || {};
  const analyticsData = analytics.data || {};

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading graph workspace...</div>;
  if (error) return <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  const graphSections = [
    { id: "sentiment", label: "Sentiment + Forecast" },
    { id: "models", label: "Models + Features" },
    { id: "pca", label: "PCA" },
    { id: "correlation", label: "Correlation" },
  ];

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">My Company vs Others</p>
        <h1 className="ve-title">Competitive Graph Workspace</h1>
        <p className="ve-subtitle">
          Compare your company against peers visually across sentiment, forecast, model quality, and structure.
        </p>
      </section>

      <CompanyPageInsights page="graphs" />

      <section className="ve-card rounded-2xl p-5">
        <div className="mt-4 flex flex-wrap gap-2">
          {graphSections.map((item) => (
            <a
              key={item.id}
              href={`#${item.id}`}
              className="rounded-full border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 transition hover:-translate-y-0.5 hover:border-teal-300 hover:text-teal-700"
            >
              {item.label}
            </a>
          ))}
        </div>
      </section>

      <section id="sentiment" className="ve-section grid grid-cols-1 gap-4 xl:grid-cols-2">
        <SentimentTrendChart data={dashboardData?.sentiment_trend || []} />
        <ForecastChart history={[]} forecast={dashboardData?.forecast || []} />
      </section>

      <section id="models" className="ve-section grid grid-cols-1 gap-4 xl:grid-cols-2">
        <ModelComparisonChart data={dashboardData?.model_summary || []} />
        <FeatureImportanceChart data={(analyticsData?.feature_importance || []).slice(0, 20)} />
      </section>

      <section id="pca" className="ve-section">
        <PcaScatterChart data={analyticsData?.pca_components || []} />
      </section>

      <section id="correlation" className="ve-section">
        <CorrelationHeatmap matrix={analyticsData?.correlation_matrix || {}} />
      </section>
    </div>
  );
}

export default GraphsPage;
