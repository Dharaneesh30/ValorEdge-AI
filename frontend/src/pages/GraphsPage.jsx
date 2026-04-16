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
import PageAIInsights from "../components/PageAIInsights";

function GraphsPage() {
  const dashboard = useApi("/dashboard");
  const analytics = useApi("/analytics");

  const loading = dashboard.loading || analytics.loading;
  const error = dashboard.error || analytics.error;
  const dashboardData = dashboard.data || {};
  const analyticsData = analytics.data || {};

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading graph workspace...</div>;
  
  if (error) {
    console.error("Graphs error:", error);
    return (
      <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">
        <p className="font-semibold">Error loading graphs</p>
        <p className="text-sm mt-2">Please upload a dataset first</p>
      </div>
    );
  }

  if (!dashboardData || !analyticsData || (Object.keys(dashboardData).length === 0 && Object.keys(analyticsData).length === 0)) {
    return (
      <div className="ve-page ve-reveal">
        <section className="ve-hero">
          <p className="ve-pill">My Company vs Others</p>
          <h1 className="ve-title">Competitive Graph Workspace</h1>
          <p className="ve-subtitle">Compare your company against peers visually across sentiment, forecast, model quality, and structure.</p>
        </section>
        <div className="ve-card rounded-2xl p-8 text-center text-amber-700 bg-amber-50 border border-amber-200">
          <p className="text-lg font-semibold">📊 No data available</p>
          <p className="mt-2">Please upload a dataset first to see graphs</p>
          <a href="/upload" className="inline-block mt-4 px-6 py-2 bg-amber-600 text-white rounded-lg font-semibold hover:bg-amber-700">
            Go to Upload
          </a>
        </div>
      </div>
    );
  }

  const graphSections = [
    { id: "sentiment", label: "Sentiment + Forecast" },
    { id: "models", label: "Models + Features" },
    { id: "pca", label: "PCA" },
    { id: "correlation", label: "Correlation" },
  ];

  // Combine data for AI insights
  const combinedData = {
    ...dashboardData,
    ...analyticsData,
  };

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

      <PageAIInsights page="graphs" data={combinedData} />

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
        {dashboardData?.sentiment_trend && dashboardData.sentiment_trend.length > 0 && (
          <SentimentTrendChart data={dashboardData.sentiment_trend} />
        )}
        {dashboardData?.forecast && dashboardData.forecast.length > 0 && (
          <ForecastChart history={[]} forecast={dashboardData.forecast} />
        )}
      </section>

      <section id="models" className="ve-section grid grid-cols-1 gap-4 xl:grid-cols-2">
        {dashboardData?.model_summary && dashboardData.model_summary.length > 0 && (
          <ModelComparisonChart data={dashboardData.model_summary} />
        )}
        {analyticsData?.feature_importance && analyticsData.feature_importance.length > 0 && (
          <FeatureImportanceChart data={analyticsData.feature_importance.slice(0, 20)} />
        )}
      </section>

      {analyticsData?.pca_components && analyticsData.pca_components.length > 0 && (
        <section id="pca" className="ve-section">
          <PcaScatterChart data={analyticsData.pca_components} />
        </section>
      )}

      {analyticsData?.correlation_matrix && Object.keys(analyticsData.correlation_matrix).length > 0 && (
        <section id="correlation" className="ve-section">
          <CorrelationHeatmap matrix={analyticsData.correlation_matrix} />
        </section>
      )}

    </div>
  );
}

export default GraphsPage;
