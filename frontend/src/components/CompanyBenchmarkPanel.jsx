import { useEffect, useState } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";

function CompanyBenchmarkPanel({ title = "One Company vs Others", description = "Analyze one target company against peers and identify what to improve to outperform them." }) {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState("");
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    const loadCompanies = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/companies`);
        const items = response?.data?.companies || [];
        if (!active) return;
        setCompanies(items);
        if (items.length > 0) setSelectedCompany(items[0]);
      } catch (err) {
        if (!active) return;
        setCompanies([]);
        setError(err?.response?.data?.detail || err.message || "Unable to load company list");
      }
    };

    loadCompanies();
    return () => {
      active = false;
    };
  }, []);

  const runBenchmark = async () => {
    if (!selectedCompany) {
      setError("Select a company first.");
      return;
    }
    try {
      setLoading(true);
      setError("");
      const response = await axios.get(`${API_BASE_URL}/company-benchmark`, {
        params: { company: selectedCompany },
      });
      setBenchmark(response.data);
    } catch (err) {
      setBenchmark(null);
      setError(err?.response?.data?.detail || err.message || "Company benchmark failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ve-card rounded-2xl p-5 sm:p-6">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-600">{description}</p>

      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-[1fr_auto]">
        <select value={selectedCompany} onChange={(e) => setSelectedCompany(e.target.value)} className="ve-input">
          <option value="">Select company</option>
          {companies.map((company) => (
            <option key={company} value={company}>
              {company}
            </option>
          ))}
        </select>
        <button type="button" onClick={runBenchmark} disabled={loading} className="ve-btn-primary">
          {loading ? "Analyzing..." : "Compare & Improve"}
        </button>
      </div>

      {error && <p className="mt-3 text-sm text-rose-700">{error}</p>}

      {benchmark && (
        <div className="mt-4 space-y-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">Target Sentiment</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">{benchmark?.target_metrics?.sentiment_mean}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">Target Trend</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">{benchmark?.target_metrics?.trend}</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">Positive Ratio</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">{benchmark?.target_metrics?.positive_ratio}</p>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">Peer Gap View</p>
            <div className="mt-2 space-y-2">
              {(benchmark?.peer_comparison || []).slice(0, 5).map((peer) => (
                <div key={peer.company} className="rounded-lg border border-slate-200 bg-slate-50 p-2 text-sm">
                  <span className="font-semibold text-slate-900">{peer.company}</span>
                  <span className="ml-2 text-slate-700">Gap vs target: {peer.gap_vs_target}</span>
                  <span className="ml-2 text-slate-700">Trend: {peer.peer_trend}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            <div className="rounded-xl border border-cyan-200 bg-cyan-50 p-3">
              <p className="text-sm font-semibold text-cyan-900">Focus Keywords from Better Peers</p>
              <p className="mt-1 text-sm text-cyan-900">
                {(benchmark?.focus_keywords_from_peers || []).join(", ") || "No additional keywords identified."}
              </p>
            </div>
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-3">
              <p className="text-sm font-semibold text-emerald-900">Rule-based Improvement Actions</p>
              <ul className="mt-1 list-disc list-inside text-sm text-emerald-900">
                {(benchmark?.rule_based_recommendations || []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>

          {benchmark?.ai_recommendation && (
            <div className="rounded-xl border border-slate-200 bg-white p-3">
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">AI Competitive Recommendation</p>
              <p className="mt-1 whitespace-pre-wrap text-sm text-slate-700">{benchmark.ai_recommendation}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default CompanyBenchmarkPanel;
