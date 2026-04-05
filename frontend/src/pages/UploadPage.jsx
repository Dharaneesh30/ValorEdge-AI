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
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">Pipeline Entry</p>
        <h1 className="ve-title">Upload Dataset</h1>
        <p className="ve-subtitle">Add a CSV to trigger analysis, forecasts, and strategy generation in one run.</p>
      </section>

      <div className="ve-card rounded-2xl p-6 sm:p-7">
        <p className="mt-2 text-sm text-slate-700">
          Required CSV columns: <code>date</code>, <code>text</code>. Optional fields: <code>company</code>, <code>category</code>.
        </p>

        <div className="mt-5 space-y-4">
          <div className="rounded-xl border border-slate-300 bg-white p-3">
            <input
              id="csv-upload-input"
              type="file"
              accept=".csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden"
            />
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <label
                htmlFor="csv-upload-input"
                className="ve-btn-primary inline-flex cursor-pointer items-center justify-center"
              >
                Browse CSV
              </label>
              <p className="text-xs text-slate-600">
                {file ? `Selected: ${file.name}` : "No file selected"}
              </p>
            </div>
          </div>
          {file && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
              Selected file: <span className="font-semibold">{file.name}</span>
            </div>
          )}

          <button
            onClick={onUpload}
            disabled={loading}
            className="ve-btn-primary"
          >
            {loading ? "Running Full Pipeline..." : "Upload & Run Pipeline"}
          </button>
        </div>

        {message && <p className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p>}
        {error && <p className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      </div>
    </div>
  );
}

export default UploadPage;
