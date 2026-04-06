import { useMemo } from "react";
import { useCompanyComparison } from "../context/CompanyContext";

function CompanyPageInsights({ page = "dashboard", allowSelection = false }) {
  const {
    companies,
    selectedCompany,
    setSelectedCompany,
    benchmark,
    loadingCompanies,
    loadingBenchmark,
    error,
  } = useCompanyComparison();

  const topPeer = benchmark?.peer_comparison?.[0];
  const gapToTop = Number(topPeer?.gap_vs_target || 0);
  const targetTrend = Number(benchmark?.target_metrics?.trend || 0);
  const focusWords = benchmark?.focus_keywords_from_peers || [];
  const actions = benchmark?.rule_based_recommendations || [];

  const pageSuggestion = useMemo(() => {
    if (!benchmark) {
      if (page === "upload") return "Upload your dataset to auto-detect your company and compare with preloaded competitors.";
      return "Company comparison will appear after upload completes.";
    }
    if (page === "analytics") {
      return `Prioritize root-cause analysis on: ${focusWords.slice(0, 4).join(", ") || "top missing peer themes"}.`;
    }
    if (page === "graphs") {
      return `Use charts to track gap to top peer (${gapToTop.toFixed(3)}) and monitor trend (${targetTrend.toFixed(3)}).`;
    }
    if (page === "strategy") {
      return actions[0] || "Focus on the largest peer gap and execute one targeted improvement sprint.";
    }
    if (page === "upload") {
      return "After upload, run comparison first to set your company-specific analysis baseline.";
    }
    return `Current top comparison signal: ${gapToTop > 0 ? "peer is ahead" : "your company leads"} vs ${topPeer?.company || "peers"}.`;
  }, [benchmark, page, focusWords, gapToTop, targetTrend, actions, topPeer]);

  return (
    <section className="ve-card rounded-2xl p-4 sm:p-5">
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.16em] text-slate-500">My Company vs Others</p>
          <p className="text-sm font-semibold text-slate-900">{pageSuggestion}</p>
        </div>
        {allowSelection ? (
          <div className="flex items-center gap-2">
            <select
              value={selectedCompany}
              onChange={(e) => setSelectedCompany(e.target.value)}
              className="ve-input min-w-[220px]"
              disabled={loadingCompanies}
            >
              <option value="">Select company</option>
              {companies.map((company) => (
                <option key={company} value={company}>
                  {company}
                </option>
              ))}
            </select>
          </div>
        ) : (
          <div className="rounded-full border border-slate-300 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
            Selected: {selectedCompany || "Auto-detected after upload"}
          </div>
        )}
      </div>

      {error && <p className="mt-2 text-sm text-rose-700">{error}</p>}

      {loadingBenchmark && <p className="mt-2 text-xs text-slate-500">Refreshing company comparison...</p>}

      {benchmark && (
        <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Target Sentiment</p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{benchmark?.target_metrics?.sentiment_mean}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Trend</p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{benchmark?.target_metrics?.trend}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Top Peer</p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{topPeer?.company || "N/A"}</p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-[11px] uppercase tracking-wide text-slate-500">Gap to Top Peer</p>
            <p className="mt-1 text-lg font-semibold text-slate-900">{gapToTop.toFixed(3)}</p>
          </div>
        </div>
      )}
    </section>
  );
}

export default CompanyPageInsights;
