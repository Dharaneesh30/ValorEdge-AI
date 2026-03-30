import { useState } from "react";
import axios from "axios";
import useApi from "../hooks/useApi";
import API_BASE_URL from "../config/api";

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

  if (loading) return <div className="p-6">Loading strategy...</div>;
  if (error) return <div className="p-6 text-rose-700">{error?.response?.data?.detail || error.message}</div>;

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <h2 className="text-xl font-bold text-slate-900">Strategy & Recommendations - What To Do</h2>

        <div className="mt-4">
          <p className="text-sm font-semibold text-slate-800">AI Recommendations</p>
          <ul className="list-disc list-inside text-sm text-slate-700 mt-1">
            {(data?.recommendations || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>

        <div className="mt-4 rounded-lg bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700">
          <p className="font-semibold">What-if Analysis</p>
          <p className="mt-1">
            {data?.what_if_analysis?.scenario}: reputation moves from {data?.what_if_analysis?.current_reputation_score} to {data?.what_if_analysis?.projected_reputation_score}
            ({data?.what_if_analysis?.relative_improvement_percent}% relative improvement).
          </p>
        </div>

        <div className="mt-4">
          <p className="text-sm font-semibold text-slate-800">Risk Alerts</p>
          {(data?.risk_alerts || []).map((alert) => (
            <div key={alert.type} className="mt-2 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm">
              <p className="font-semibold capitalize">{alert.severity} risk</p>
              <p>{alert.message}</p>
            </div>
          ))}
        </div>

        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3">
          <p className="text-sm font-semibold text-slate-800">GenAI Insights Panel</p>
          <p className="text-sm text-slate-700 whitespace-pre-wrap mt-1">{data?.genai_strategy_insights}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <h3 className="font-semibold text-slate-800">Interactive What-if Scenario</h3>
        <textarea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          className="mt-3 w-full border border-slate-300 rounded-md p-3 text-sm"
          placeholder="Example: Company improves customer response time and launches trust campaign"
        />

        <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-slate-700">Sentiment Adjustment (%)</label>
            <input type="range" min={-30} max={30} value={sentimentAdjustment} onChange={(e) => setSentimentAdjustment(Number(e.target.value))} className="w-full" />
            <p className="text-sm text-slate-600">{sentimentAdjustment}%</p>
          </div>
          <div>
            <label className="text-sm font-medium text-slate-700">Cluster Weight Adjustment (%)</label>
            <input type="range" min={-30} max={30} value={clusterWeightAdjustment} onChange={(e) => setClusterWeightAdjustment(Number(e.target.value))} className="w-full" />
            <p className="text-sm text-slate-600">{clusterWeightAdjustment}%</p>
          </div>
        </div>

        <button onClick={runScenario} disabled={scenarioLoading} className="mt-4 rounded-lg bg-teal-700 px-4 py-2 text-white font-medium hover:bg-teal-800 disabled:opacity-50">
          {scenarioLoading ? "Simulating..." : "Run Scenario"}
        </button>
        {scenarioError && <p className="mt-2 text-sm text-rose-700">{scenarioError}</p>}

        {scenarioResult && (
          <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm text-slate-700">
            <p><strong>Predicted Reputation:</strong> {scenarioResult.predicted_reputation_score}</p>
            <p><strong>Assigned Cluster:</strong> {scenarioResult.assigned_cluster}</p>
            <p><strong>Cluster Keywords:</strong> {(scenarioResult.cluster_keywords || []).join(", ")}</p>
            <p className="whitespace-pre-wrap mt-2"><strong>AI Insight:</strong> {scenarioResult.ai_insight}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default StrategyPage;
