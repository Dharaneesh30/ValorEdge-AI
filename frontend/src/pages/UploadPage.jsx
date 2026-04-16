import { useState } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";
import { useCompanyComparison } from "../context/CompanyContext";
import CompanyPageInsights from "../components/CompanyPageInsights";

function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const {
    setSelectedCompany,
    refreshCompanies,
    refreshBenchmark,
  } = useCompanyComparison();

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
      formData.append("include_preloaded_competitors", "true");
      formData.append("treat_upload_as_my_company", "true");

      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      const inferredCompany = response?.data?.metadata?.my_company;
      if (inferredCompany) {
        setSelectedCompany(inferredCompany);
      }
      const fastMode = Boolean(response?.data?.metadata?.fast_mode);
      const rowsOriginal = response?.data?.metadata?.rows_original;
      const rowsProcessed = response?.data?.metadata?.rows_processed;
      const rowsRemoved = response?.data?.metadata?.rows_removed || 0;
      const operation = response?.data?.metadata?.operation || "insert";
      const wasLimited = Number(rowsOriginal || 0) > Number(rowsProcessed || 0);

      let operationText = "";
      if (operation === "update" && rowsRemoved > 0) {
        operationText = ` (Updated: removed ${rowsRemoved} old records, added new ones).`;
      } else {
        operationText = ` (New company added to dataset).`;
      }

      setMessage(
        `Pipeline completed. Processed ${rowsProcessed ?? 0} rows${wasLimited ? ` (from ${rowsOriginal})` : ""}. Best model: ${response.data?.best_model ?? "n/a"}. Selected company: ${inferredCompany || "N/A"}${operationText}${fastMode ? " Fast mode enabled." : ""}`
      );
      
      await refreshCompanies();
      await refreshBenchmark();
    } catch (err) {
      const isNetworkError =
        !err?.response &&
        (String(err?.message || "").toLowerCase().includes("network error") ||
          String(err?.code || "").toUpperCase() === "ERR_NETWORK");
      if (isNetworkError) {
        setError("Cannot reach backend API at http://127.0.0.1:8000. Start the backend server and retry.");
      } else {
        setError(err?.response?.data?.detail || err.message || "Upload failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ve-page ve-reveal">
      <section className="ve-hero">
        <p className="ve-pill">My Company vs Others</p>
        <h1 className="ve-title">Upload and Compare</h1>
        <p className="ve-subtitle">Upload your dataset, run the pipeline, then use comparison-guided insights across all pages.</p>
      </section>

      <CompanyPageInsights page="upload" />

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
              <label htmlFor="csv-upload-input" className="ve-btn-primary inline-flex cursor-pointer items-center justify-center">
                Browse CSV
              </label>
              <p className="text-xs text-slate-600">{file ? `Selected: ${file.name}` : "No file selected"}</p>
            </div>
          </div>

          <div className="rounded-xl border border-cyan-200 bg-cyan-50 p-3 text-xs text-cyan-900">
            Preloaded competitor dataset is merged automatically to run comparison.
          </div>

          {file && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs text-emerald-800">
              Selected file: <span className="font-semibold">{file.name}</span>
            </div>
          )}

          <button onClick={onUpload} disabled={loading} className="ve-btn-primary">
            {loading ? "Uploading..." : "Upload"}
          </button>
        </div>

        {message && <p className="mt-4 rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">{message}</p>}
        {error && <p className="mt-4 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
      </div>
    </div>
  );
}

export default UploadPage;
