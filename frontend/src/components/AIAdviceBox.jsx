function AIAdviceBox({ advice, loading, title = "AI Recommendation" }) {
  if (loading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow mt-6 animate-pulse">
        <p className="h-4 w-1/3 mb-2 bg-gray-300 rounded" />
        <p className="h-3 w-2/3 bg-gray-300 rounded" />
      </div>
    );
  }

  if (!advice) {
    return null;
  }

  return (
    <div className="bg-indigo-50 border-l-4 border-indigo-500 rounded-lg p-4 mt-6 shadow">
      <div className="flex items-center gap-2 mb-2 text-indigo-700 font-semibold">
        <span className="text-xl">🤖</span>
        <span>{title}</span>
      </div>
      <p className="text-sm text-slate-700 whitespace-pre-wrap">{advice}</p>
    </div>
  );
}

export default AIAdviceBox;
