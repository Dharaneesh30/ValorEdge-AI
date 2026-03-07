function Sidebar() {
  return (
    <div className="w-64 h-screen bg-gray-900 text-white p-6">
      <h1 className="text-2xl font-bold mb-8">ValorEdge AI</h1>

      <ul className="space-y-4">
        <li className="hover:text-blue-400 cursor-pointer">Dashboard</li>
        <li className="hover:text-blue-400 cursor-pointer">Upload Dataset</li>
        <li className="hover:text-blue-400 cursor-pointer">Company Analysis</li>
        <li className="hover:text-blue-400 cursor-pointer">Forecasting</li>
        <li className="hover:text-blue-400 cursor-pointer">AI Insights</li>
        <li className="hover:text-blue-400 cursor-pointer">Simulation</li>
      </ul>
    </div>
  );
}

export default Sidebar;