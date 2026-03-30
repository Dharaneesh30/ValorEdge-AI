import useApi from "../hooks/useApi";
import { ForecastChart } from "../components/Charts";
import AIAdviceBox from "../components/AIAdviceBox";

function ForecastPage() {
  const { data, loading, error } = useApi("/api/forecast");
  const aiAdvice = data?.ai_advice || "";

  if (loading) return <div className="p-6">Loading...</div>;
  if (error) return <div className="p-6 text-red-600">Error: {error.message || "Unable to fetch forecast"}</div>;

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Forecasting</h1>

      <ForecastChart arima={data?.arima_forecast} smoothing={data?.smoothing_forecast} />

      <div className="bg-white rounded-lg shadow p-6 mt-6">
        <h2 className="text-xl font-semibold mb-4">Forecast Values</h2>
        <table className="w-full text-sm border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-100">
              <th className="border px-3 py-2">Step</th>
              <th className="border px-3 py-2">ARIMA</th>
              <th className="border px-3 py-2">Smoothing</th>
            </tr>
          </thead>
          <tbody>
            {Array.from({ length: Math.max(data?.arima_forecast?.length || 0, data?.smoothing_forecast?.length || 0) }).map((_, i) => (
              <tr key={i}>
                <td className="border px-3 py-2">{i + 1}</td>
                <td className="border px-3 py-2">{data?.arima_forecast?.[i]?.toFixed(2) ?? "-"}</td>
                <td className="border px-3 py-2">{data?.smoothing_forecast?.[i]?.toFixed(2) ?? "-"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <AIAdviceBox advice={aiAdvice} loading={loading} title="AI Forecast Advice" />
    </div>
  );
}

export default ForecastPage;
