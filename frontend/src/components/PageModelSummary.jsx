function toNum(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function safeFixed(value, digits = 3) {
  return toNum(value).toFixed(digits);
}

function summarizeDashboard(data) {
  const rows = [...(data?.model_summary || [])].sort((a, b) => toNum(a?.rmse, 1e9) - toNum(b?.rmse, 1e9));
  const best = rows[0];
  const trend = data?.forecast || [];
  const direction =
    trend.length >= 2
      ? toNum(trend[trend.length - 1]?.value) > toNum(trend[0]?.value)
        ? "improving"
        : "softening"
      : "stable";

  return [
    `Company reputation score is ${safeFixed(data?.reputation_score)} with a ${direction} forecast trajectory.`,
    best
      ? `Best performing model is ${best.model} (RMSE ${safeFixed(best.rmse)}, MAE ${safeFixed(best.mae)}, R2 ${safeFixed(best.r2)}).`
      : "Model comparison is not available yet.",
    `This page combines ${trend.length} forecast points and ${(data?.sentiment_trend || []).length} sentiment trend points for current monitoring.`,
  ];
}

function summarizeAnalytics(data) {
  const featureRows = data?.feature_importance || [];
  const topFeatures = featureRows.slice(0, 3).map((f) => f?.feature).filter(Boolean);
  const clusterSizes = data?.cluster_insights?.sizes || {};
  const largestCluster = Object.entries(clusterSizes).sort((a, b) => toNum(b[1]) - toNum(a[1]))[0];
  const largestLabel = largestCluster ? `Cluster ${largestCluster[0]} (${largestCluster[1]} records)` : "No dominant cluster";

  return [
    data?.root_cause_analysis || "Root-cause summary will appear after pipeline execution.",
    topFeatures.length > 0
      ? `Top model drivers on this page are ${topFeatures.join(", ")}.`
      : "Top feature importance is not available yet.",
    `Cluster analysis indicates ${largestLabel} and ${Object.keys(clusterSizes).length} total segments.`,
  ];
}

function summarizeStrategy(data) {
  const current = toNum(data?.what_if_analysis?.current_reputation_score, null);
  const projected = toNum(data?.what_if_analysis?.projected_reputation_score, null);
  const lift = toNum(data?.what_if_analysis?.relative_improvement_percent, null);
  const alerts = data?.risk_alerts || [];
  const topAlert = alerts[0];

  return [
    current !== null && projected !== null
      ? `Strategy baseline shows score moving from ${current.toFixed(4)} to ${projected.toFixed(4)} in the what-if scenario.`
      : "Strategy what-if baseline is not available yet.",
    lift !== null
      ? `Expected relative improvement is ${lift.toFixed(2)}% based on the current model assumptions.`
      : "Relative improvement is not available yet.",
    topAlert ? `Current key risk alert: ${topAlert.severity} risk - ${topAlert.message}` : "No risk alert generated yet.",
  ];
}

function summarizeGraphs(data) {
  const modelRows = data?.model_summary || [];
  const best = [...modelRows].sort((a, b) => toNum(a?.rmse, 1e9) - toNum(b?.rmse, 1e9))[0];
  return [
    `Graph workspace covers ${(data?.sentiment_trend || []).length} sentiment points and ${(data?.forecast || []).length} forecast points.`,
    best
      ? `Model comparison trend indicates ${best.model} currently leads with RMSE ${safeFixed(best.rmse)}.`
      : "Model comparison trend is unavailable.",
    `Feature and structure views include ${(data?.feature_importance || []).length} feature rows and ${(data?.pca_components || []).length} PCA points.`,
  ];
}

function buildSummary(page, data) {
  if (page === "dashboard") return summarizeDashboard(data);
  if (page === "analytics") return summarizeAnalytics(data);
  if (page === "strategy" || page === "simulation") return summarizeStrategy(data);
  if (page === "graphs") return summarizeGraphs(data);
  return ["Summary is not available for this page yet."];
}

function PageModelSummary({ page, data }) {
  const summaryLines = buildSummary(page, data);

  return (
    <div className="ve-card rounded-2xl p-5 sm:p-6">
      <h3 className="text-lg font-semibold text-slate-900">Company Result Summary</h3>
      <div className="mt-3 space-y-2 text-sm text-slate-700">
        {summaryLines.map((line) => (
          <p key={line}>{line}</p>
        ))}
      </div>
    </div>
  );
}

export default PageModelSummary;
