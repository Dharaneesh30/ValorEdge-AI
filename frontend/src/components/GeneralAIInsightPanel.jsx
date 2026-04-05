import { useMemo, useState } from "react";

function GeneralAIInsightPanel({ insightText, providerStatus }) {
  const provider = providerStatus?.provider || "unknown";
  const model = providerStatus?.ollama_model || providerStatus?.primary_model || "default";
  const hasError = Boolean(providerStatus?.last_error);
  const [copied, setCopied] = useState(false);
  const [showError, setShowError] = useState(false);

  const availability = useMemo(() => {
    if (!providerStatus) return { label: "No provider info", tone: "text-slate-700 bg-slate-100 border-slate-300" };
    if (providerStatus.provider_ready && !hasError) {
      return { label: "Provider ready", tone: "text-emerald-800 bg-emerald-50 border-emerald-300" };
    }
    if (hasError) {
      return { label: "Provider issue", tone: "text-rose-800 bg-rose-50 border-rose-300" };
    }
    return { label: "Local fallback", tone: "text-amber-900 bg-amber-50 border-amber-300" };
  }, [providerStatus, hasError]);

  const onCopy = async () => {
    const text = insightText || "No AI insight available.";
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1400);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white/90 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-700">GenAI Insight Panel</p>
        <button
          type="button"
          onClick={onCopy}
          className="rounded-lg border border-slate-300 bg-white px-2.5 py-1 text-[11px] font-semibold text-slate-700 hover:bg-slate-50"
        >
          {copied ? "Copied" : "Copy insight"}
        </button>
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-2">
        <span className={`rounded-full border px-2 py-0.5 text-[11px] font-semibold ${availability.tone}`}>
          {availability.label}
        </span>
        <span className="rounded-full border border-slate-300 bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
          Provider: {provider}
        </span>
        <span className="rounded-full border border-slate-300 bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-700">
          Model: {model}
        </span>
      </div>

      <p className="mt-3 whitespace-pre-wrap rounded-xl border border-slate-200 bg-slate-50 p-3 text-sm leading-relaxed text-slate-700">
        {insightText || "No AI insight available yet. Upload dataset and run pipeline to generate recommendations."}
      </p>

      {hasError && (
        <div className="mt-2 rounded-lg border border-rose-200 bg-rose-50 px-2 py-2">
          <button
            type="button"
            onClick={() => setShowError((s) => !s)}
            className="text-xs font-semibold text-rose-700 underline underline-offset-2"
          >
            {showError ? "Hide provider error detail" : "Show provider error detail"}
          </button>
          {showError && (
            <p className="mt-1 whitespace-pre-wrap text-xs text-rose-700">
              {providerStatus.last_error}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default GeneralAIInsightPanel;
