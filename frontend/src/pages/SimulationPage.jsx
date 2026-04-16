import { useState } from "react";
import axios from "axios";
import useApi from "../hooks/useApi";
import API_BASE_URL from "../config/api";
import GeneralAIInsightPanel from "../components/GeneralAIInsightPanel";
import CompanyPageInsights from "../components/CompanyPageInsights";
import PageAIInsights from "../components/PageAIInsights";

function StrategyPage() {
  const { data, loading, error } = useApi("/strategy");

  const [text, setText] = useState("");
  const [sentimentAdjustment, setSentimentAdjustment] = useState(0);
  const [clusterWeightAdjustment, setClusterWeightAdjustment] = useState(0);
  const [scenarioResult, setScenarioResult] = useState(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);
  const [scenarioError, setScenarioError] = useState("");
  const runScenario = async () => {
    if (!text.trim()) {
      setScenarioError("Enter scenario text first.");
      return;
    }
    try {
      setScenarioLoading(true);
      setScenarioError("");
      const response = await axios.post(`${API_BASE_URL}/scenario-simulate`, {
        text,
        sentiment_adjustment: sentimentAdjustment,
        cluster_weight_adjustment: clusterWeightAdjustment,
      });
      setScenarioResult(response.data);
    } catch (err) {
      setScenarioError(err?.response?.data?.detail || err.message || "Scenario simulation failed");
      setScenarioResult(null);
    } finally {
      setScenarioLoading(false);
    }
  };

  if (loading) return <div className="ve-card ve-reveal rounded-2xl p-6">Loading strategy...</div>;
  if (error) return <div className="ve-card ve-reveal rounded-2xl p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">My Company vs Others</p>
        <h1 className="ve-title">Competitive Strategy Studio</h1>
        <p className="ve-subtitle">Convert company-vs-peer comparison into actionable improvements and what-if plans.</p>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Current Score</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{data?.what_if_analysis?.current_reputation_score ?? "N/A"}</p>
        </div>
        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Projected Score</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{data?.what_if_analysis?.projected_reputation_score ?? "N/A"}</p>
        </div>
        <div className="ve-card rounded-2xl p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">Relative Lift</p>
          <p className="mt-2 text-2xl font-semibold text-slate-900">{data?.what_if_analysis?.relative_improvement_percent ?? 0}%</p>
        </div>
      </section>

      <CompanyPageInsights page="strategy" />

      <PageAIInsights
        page="strategy"
        data={{
          ...data,
          scenario_result: scenarioResult,
        }}
      />

      <div className="ve-card rounded-2xl p-5 sm:p-6">
        <h2 className="text-2xl font-semibold tracking-tight text-slate-900">Strategy & Recommendations</h2>

        <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
          {(data?.recommendations || []).map((item) => (
            <div key={item} className="rounded-xl border border-slate-200 bg-white/75 p-3 text-sm text-slate-700">
              {item}
            </div>
          ))}
        </div>

        <div className="mt-4">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">AI Recommendations</p>
          <ul className="mt-2 list-disc list-inside text-sm text-slate-700">
            {(data?.recommendations || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="mt-4 rounded-xl border border-cyan-200 bg-cyan-50 p-3 text-sm text-slate-700">
          <p className="font-semibold text-cyan-900">What-if Baseline</p>
          <p className="mt-1">
            {data?.what_if_analysis?.scenario}: reputation moves from {data?.what_if_analysis?.current_reputation_score} to {data?.what_if_analysis?.projected_reputation_score}
            ({data?.what_if_analysis?.relative_improvement_percent}% relative improvement).
          </p>
        </div>

        <div className="mt-4">
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">Risk Alerts</p>
          {(data?.risk_alerts || []).map((alert) => (
            <div key={alert.type} className="mt-2 rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm">
              <p className="font-semibold capitalize text-amber-900">{alert.severity} risk</p>
              <p className="text-amber-800">{alert.message}</p>
            </div>
          ))}
        </div>

        <div className="mt-4">
          <GeneralAIInsightPanel
            insightText={data?.genai_strategy_insights}
            providerStatus={data?.genai_provider_status}
          />
        </div>
      </div>

      <div className="ve-card rounded-2xl p-5 sm:p-6">
        <h3 className="text-lg font-semibold text-slate-900">Interactive What-if Scenario</h3>
        <textarea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="ve-input ve-textarea mt-3"
          placeholder="Example: Company improves customer response time and launches trust campaign"
        />

        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Sentiment Adjustment (%)</label>
            <input type="range" min={-30} max={30} value={sentimentAdjustment} onChange={(e) => setSentimentAdjustment(Number(e.target.value))} className="w-full" />
            <p className="text-xs font-medium text-slate-600">{sentimentAdjustment}%</p>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Cluster Weight Adjustment (%)</label>
            <input type="range" min={-30} max={30} value={clusterWeightAdjustment} onChange={(e) => setClusterWeightAdjustment(Number(e.target.value))} className="w-full" />
            <p className="text-xs font-medium text-slate-600">{clusterWeightAdjustment}%</p>
          </div>
        </div>

        <button onClick={runScenario} disabled={scenarioLoading} className="ve-btn-primary mt-4">
          {scenarioLoading ? "Simulating..." : "Run Scenario"}
        </button>
        {scenarioError && <p className="mt-2 text-sm text-rose-700">{scenarioError}</p>}

        {scenarioResult && (
          <div className="mt-4 space-y-3 rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
              <div className="rounded-lg border border-slate-200 bg-white p-2"><strong>Predicted:</strong> {scenarioResult.predicted_reputation_score}</div>
              <div className="rounded-lg border border-slate-200 bg-white p-2"><strong>Cluster:</strong> {scenarioResult.assigned_cluster}</div>
              <div className="rounded-lg border border-slate-200 bg-white p-2"><strong>Keywords:</strong> {(scenarioResult.cluster_keywords || []).join(", ")}</div>
            </div>
            <p className="whitespace-pre-wrap"><strong>AI Insight:</strong> {scenarioResult.ai_insight}</p>
          </div>
        )}
      </div>

    </div>
  );
}

export default StrategyPage;
