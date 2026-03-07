import Charts from "../components/Charts";

function Dashboard() {
  return (
    <div className="p-6">

      <h1 className="text-3xl font-bold mb-6">
        Dashboard
      </h1>

      {/* Cards */}
      <div className="grid grid-cols-3 gap-6">

        <div className="bg-white shadow p-6 rounded-lg">
          <h2 className="text-lg font-semibold">Reputation Score</h2>
          <p className="text-3xl font-bold mt-2">0.74</p>
        </div>

        <div className="bg-white shadow p-6 rounded-lg">
          <h2 className="text-lg font-semibold">Prediction</h2>
          <p className="text-3xl font-bold mt-2 text-green-600">Growth</p>
        </div>

        <div className="bg-white shadow p-6 rounded-lg">
          <h2 className="text-lg font-semibold">Forecast Trend</h2>
          <p className="text-3xl font-bold mt-2">Increasing</p>
        </div>

      </div>

      {/* Chart Section */}
      <Charts />

    </div>
  );
}

export default Dashboard;