import { useState, useEffect } from "react";
import { useCompanyComparison } from "../context/CompanyContext";
import usePageInsights from "../hooks/usePageInsights";

function LiveInference({ page, data = null, showStreaming = true }) {
  const [displayedInsights, setDisplayedInsights] = useState([]);
  const { selectedCompany } = useCompanyComparison();
  const { insights, loading } = usePageInsights(page, selectedCompany, data);

  // Show only first 3 insights and stream them
  useEffect(() => {
    if (!insights || insights.length === 0) return;

    if (showStreaming) {
      setDisplayedInsights([]);
      const limited = insights.slice(0, 3); // Show only 3 insights max
      limited.forEach((insight, idx) => {
        setTimeout(() => {
          setDisplayedInsights((prev) => [...prev, insight]);
        }, idx * 150);
      });
    } else {
      setDisplayedInsights(insights.slice(0, 3));
    }
  }, [insights, showStreaming]);

  if (!selectedCompany) {
    return null;
  }

  // Get category color
  const getCategoryColor = (category) => {
    const colors = {
      KPI: "bg-blue-100 border-blue-300",
      MODEL: "bg-purple-100 border-purple-300",
      TREND: "bg-emerald-100 border-emerald-300",
      SCORE: "bg-indigo-100 border-indigo-300",
      RANK: "bg-cyan-100 border-cyan-300",
      DATA: "bg-amber-100 border-amber-300",
      ACTION: "bg-orange-100 border-orange-300",
      REASON: "bg-slate-100 border-slate-300",
    };
    return colors[category] || "bg-slate-100 border-slate-300";
  };

  // Strategy page - more space
  if (page === "strategy" || page === "simulation") {
    return (
      <div className="ve-card rounded-xl p-4 bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 mb-4">
        <div className="flex items-start gap-2 mb-3">
          <span className="text-xl">🤖</span>
          <div className="flex-1">
            <h3 className="font-semibold text-slate-900 text-sm">Quick AI Insights</h3>
          </div>
        </div>

        {loading && (
          <div className="space-y-1">
            {[1, 2].map((i) => (
              <div key={i} className="h-2 bg-slate-200 rounded animate-pulse w-3/4"></div>
            ))}
          </div>
        )}

        {!loading && displayedInsights.length === 0 && (
          <p className="text-xs text-slate-600">Analyzing strategy data...</p>
        )}

        {displayedInsights.length > 0 && !loading && (
          <div className="space-y-2">
            {displayedInsights.map((insight, idx) => (
              <div
                key={idx}
                className={`rounded-lg p-2 text-xs border ${getCategoryColor(insight.category)} transition-all duration-300`}
                style={{
                  animation: `slideInLeft 0.3s ease-out ${idx * 0.1}s backwards`,
                }}
              >
                <p className="font-semibold text-slate-800">{insight.insight}</p>
                {insight.action && (
                  <p className="text-slate-700 mt-1">💡 {insight.action}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  // Standard pages - compact
  return (
    <div className="rounded-lg p-3 bg-gradient-to-r from-cyan-50 to-blue-50 border border-cyan-200 mb-3">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-lg animate-bounce">✨</span>
        <h3 className="font-semibold text-slate-900 text-sm">AI Insights</h3>
      </div>

      {loading && (
        <div className="space-y-1">
          {[1, 2].map((i) => (
            <div key={i} className="h-2 bg-slate-200 rounded animate-pulse w-2/3"></div>
          ))}
        </div>
      )}

      {!loading && displayedInsights.length === 0 && (
        <p className="text-xs text-slate-600">Analyzing page data...</p>
      )}

      {displayedInsights.length > 0 && !loading && (
        <div className="space-y-1.5">
          {displayedInsights.map((insight, idx) => (
            <div
              key={idx}
              className={`rounded-md p-2 text-xs border-l-2 ${getCategoryColor(insight.category)} transition-all duration-300`}
              style={{
                animation: `slideInLeft 0.3s ease-out ${idx * 0.1}s backwards`,
              }}
            >
              <p className="font-medium text-slate-800 leading-tight">{insight.insight}</p>
              {insight.action && (
                <p className="text-slate-600 font-light mt-0.5">Reason: {insight.action}</p>
              )}
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes slideInLeft {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
}

export default LiveInference;
