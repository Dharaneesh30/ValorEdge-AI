import useApi from "../hooks/useApi";
import { CorrelationHeatmap } from "../components/Charts";
import AIAdviceBox from "../components/AIAdviceBox";

function AnalysisPage() {
  const { data, loading, error } = useApi("/api/analysis");
  const aiAdvice = data?.ai_advice || "";

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error.message || "Failed to fetch."}</div>;

  const stats = data?.statistics || {};
  const correlation = data?.correlation || {};

  const renderTable = () => {
    if (!stats) return null;

    const entries = Object.entries(stats);

    return (
      <div className="overflow-x-auto mt-4">
        <table className="w-full text-sm border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-3 py-2">Metric</th>
              <th className="border px-3 py-2">Count</th>
              <th className="border px-3 py-2">Mean</th>
              <th className="border px-3 py-2">Std</th>
              <th className="border px-3 py-2">Min</th>
              <th className="border px-3 py-2">Max</th>
            </tr>
          </thead>
          <tbody>
            {entries.map(([col, values]) => (
              <tr key={col}>
                <td className="border px-3 py-2 font-medium">{col}</td>
                <td className="border px-3 py-2">{values?.count ?? "-"}</td>
                <td className="border px-3 py-2">{values?.mean ?? "-"}</td>
                <td className="border px-3 py-2">{values?.std ?? "-"}</td>
                <td className="border px-3 py-2">{values?.min ?? "-"}</td>
                <td className="border px-3 py-2">{values?.max ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Analysis</h1>
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold">Reputation Score</h2>
        <p className="text-3xl font-bold mt-2">{data?.reputation_score?.toFixed(2) || "N/A"}</p>
      </div>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Descriptive Statistics</h2>
        {renderTable()}
      </div>
      <CorrelationHeatmap matrix={correlation} />
      <AIAdviceBox advice={aiAdvice} loading={loading} title="AI Analysis Advice" />
    </div>
  );
}

export default AnalysisPage;
