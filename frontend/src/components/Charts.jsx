import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Fragment } from "react";

export function SentimentTrendChart({ data }) {
  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Sentiment Trend</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data || []}>
          <CartesianGrid stroke="#cbd5e1" strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
          <YAxis domain={[-1, 1]} />
          <Tooltip />
          <Line type="monotone" dataKey="score" stroke="#0f766e" strokeWidth={2.5} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PcaScatterChart({ data }) {
  const points = (data || []).map((item) => ({
    x: item.pc1 ?? 0,
    y: item.pc2 ?? 0,
  }));

  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">PCA Visualization (2D)</h3>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart>
          <CartesianGrid stroke="#cbd5e1" />
          <XAxis type="number" dataKey="x" name="PC1" />
          <YAxis type="number" dataKey="y" name="PC2" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter data={points} fill="#0ea5e9" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ClusterChart({ data }) {
  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Cluster Visualization</h3>
      <ResponsiveContainer width="100%" height={260}>
        <ScatterChart>
          <CartesianGrid stroke="#cbd5e1" />
          <XAxis type="number" dataKey="x" name="PC1" />
          <YAxis type="number" dataKey="y" name="PC2" />
          <Tooltip />
          <Scatter data={data || []} fill="#f97316" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ModelComparisonChart({ data }) {
  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Model Comparison</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data || []}>
          <CartesianGrid stroke="#cbd5e1" strokeDasharray="3 3" />
          <XAxis dataKey="model" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="rmse" fill="#ef4444" />
          <Bar dataKey="r2" fill="#22c55e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ForecastChart({ history, forecast }) {
  const merged = [
    ...(history || []).map((x) => ({ ...x, type: "history" })),
    ...(forecast || []).map((x) => ({ ...x, type: "forecast" })),
  ];

  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">30-Day Forecast</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={merged}>
          <CartesianGrid stroke="#cbd5e1" strokeDasharray="3 3" />
          <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
          <YAxis domain={[-1, 1]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="value" stroke="#1d4ed8" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function FeatureImportanceChart({ data }) {
  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Random Forest Feature Importance</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data || []} layout="vertical" margin={{ left: 40 }}>
          <CartesianGrid stroke="#cbd5e1" strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="feature" type="category" width={120} tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey="importance" fill="#ea580c" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function CorrelationHeatmap({ matrix }) {
  const rows = Object.keys(matrix || {});
  if (!rows.length) {
    return (
      <div className="ve-card rounded-2xl p-4">
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Correlation Heatmap</h3>
        <p className="text-sm text-slate-500">No correlation matrix available.</p>
      </div>
    );
  }

  return (
    <div className="ve-card rounded-2xl p-4">
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-700">Correlation Heatmap</h3>
      <div className="overflow-x-auto">
        <div
          className="grid gap-1 bg-slate-100 p-2 rounded"
          style={{ gridTemplateColumns: `120px repeat(${rows.length}, minmax(72px, 1fr))` }}
        >
          <div className="text-xs font-semibold text-slate-600" />
          {rows.map((col) => (
            <div key={`h-${col}`} className="text-[10px] font-semibold text-slate-600 truncate">{col}</div>
          ))}
          {rows.map((row) => (
            <Fragment key={`row-${row}`}>
              <div className="text-[10px] font-semibold text-slate-600 truncate">{row}</div>
              {rows.map((col) => {
                const value = matrix?.[row]?.[col] ?? 0;
                const normalized = Math.min(1, Math.max(-1, value));
                const intensity = Math.round(Math.abs(normalized) * 180);
                const bg =
                  normalized >= 0
                    ? `rgb(${235 - intensity}, ${255 - intensity / 2}, ${235 - intensity})`
                    : `rgb(${255 - intensity / 2}, ${235 - intensity}, ${235 - intensity})`;
                return (
                  <div
                    key={`${row}-${col}`}
                    className="h-8 text-[10px] rounded flex items-center justify-center"
                    style={{ backgroundColor: bg }}
                  >
                    {Number(value).toFixed(2)}
                  </div>
                );
              })}
            </Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
