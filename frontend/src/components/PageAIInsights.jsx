import { useCompanyComparison } from "../context/CompanyContext";
import usePageInsights from "../hooks/usePageInsights";

function PageAIInsights({ page, data = null }) {
  const { selectedCompany } = useCompanyComparison();
  const { insights, loading } = usePageInsights(page, selectedCompany, data);

  if (!selectedCompany) {
    return null;
  }

  if (loading) {
    return (
      <div className="ve-card rounded-2xl p-5 sm:p-6 bg-gradient-to-r from-cyan-50 to-blue-50">
        <div className="animate-pulse flex space-x-4">
          <div className="flex-shrink-0 text-2xl">✨</div>
          <div className="flex-1 space-y-3">
            <div className="h-3 bg-slate-300 rounded w-3/4"></div>
            <div className="h-3 bg-slate-300 rounded w-5/6"></div>
            <div className="h-3 bg-slate-300 rounded w-1/2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!insights || insights.length === 0) {
    return (
      <div className="ve-card rounded-2xl p-5 sm:p-6 bg-gradient-to-r from-slate-50 to-slate-100 border border-slate-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 text-2xl">📊</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm text-slate-600">Analyzing your data...</p>
          </div>
        </div>
      </div>
    );
  }

  // Different layouts based on page type
  if (page === "strategy" || page === "simulation") {
    return (
      <div className="ve-card rounded-2xl p-5 sm:p-6 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 text-2xl">🤖</div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-slate-900 mb-3">
              Overall AI Analytics & Strategy
            </h3>
            <div className="space-y-3">
              {insights.map((insight, idx) => (
                <div
                  key={idx}
                  className="rounded-lg bg-white/60 p-3 border-l-4 border-amber-400"
                >
                  <div className="flex gap-2 items-start">
                    <span className="text-xs font-bold text-amber-600 uppercase tracking-wide flex-shrink-0 mt-0.5">
                      {insight.category}
                    </span>
                  </div>
                  <p className="mt-2 text-sm text-slate-700">{insight.insight}</p>
                  {insight.action && (
                    <p className="mt-2 text-xs text-amber-600 font-semibold">
                      → {insight.action}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Standard layout for other pages
  return (
    <div className="ve-card rounded-2xl p-5 sm:p-6 bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 text-2xl">✨</div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-slate-900 mb-3">
            AI Analysis & Insights
          </h3>
          <div className="space-y-2">
            {insights.map((insight, idx) => (
              <div key={idx} className="text-sm text-slate-700">
                <div className="flex gap-2">
                  <span className="text-cyan-600 font-bold flex-shrink-0">•</span>
                  <div className="flex-1">
                    <span>{insight.insight}</span>
                    {insight.category && (
                      <span className="ml-2 text-xs text-cyan-600 font-semibold uppercase">
                        ({insight.category})
                      </span>
                    )}
                    {insight.action && (
                      <p className="mt-1 text-xs text-slate-600">
                        How to improve score: <span className="font-semibold text-cyan-700">{insight.action}</span>
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PageAIInsights;
