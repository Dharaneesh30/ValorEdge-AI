import { useState } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const onUpload = async () => {
    if (!file) {
      setError("Select a CSV file first.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setMessage("");
      const formData = new FormData();
      formData.append("file", file);

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setMessage(
        `Pipeline completed. Processed ${response.data?.metadata?.rows_processed ?? 0} rows. Best model: ${response.data?.best_model ?? "n/a"}.`
      );
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
        <h2 className="text-2xl font-bold text-slate-900">Upload Dataset</h2>
        <p className="text-slate-600 mt-1 text-sm">
          Required CSV columns: <code>date</code>, <code>text</code>. Optional: <code>company</code>, <code>category</code>.
        </p>

        <div className="mt-5 space-y-4">
          <input
            type="file"
            accept=".csv"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            className="block w-full rounded-lg border border-slate-300 p-2"
          />

          <button
            onClick={onUpload}
            disabled={loading}
            className="rounded-lg bg-teal-700 px-4 py-2 text-white font-medium hover:bg-teal-800 disabled:opacity-50"
          >
            {loading ? "Running Full Pipeline..." : "Upload & Run Pipeline"}
          </button>
        </div>

        {message && <p className="mt-4 text-emerald-700 text-sm">{message}</p>}
        {error && <p className="mt-4 text-rose-700 text-sm">{error}</p>}
      </div>
    </div>
  );
}

export default UploadPage;
