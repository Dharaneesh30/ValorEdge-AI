import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";

const CACHE_TTL_MS = 60 * 1000;
const insightsCache = new Map();
const inFlightRequests = new Map();

function buildContextSignature(page, contextData) {
  const safe = contextData || {};

  if (page === "dashboard") {
    return JSON.stringify({
      reputation_score: safe.reputation_score ?? null,
      best_model: safe.best_model ?? null,
      trend_points: Array.isArray(safe.sentiment_trend) ? safe.sentiment_trend.length : 0,
      forecast_points: Array.isArray(safe.forecast) ? safe.forecast.length : 0,
    });
  }

  if (page === "analytics") {
    return JSON.stringify({
      feature_count: Array.isArray(safe.feature_importance) ? safe.feature_importance.length : 0,
      cluster_keys: Object.keys(safe.cluster_insights || {}).length,
      pca_points: Array.isArray(safe.pca_components) ? safe.pca_components.length : 0,
    });
  }

  if (page === "strategy" || page === "simulation") {
    const whatIf = safe.what_if_analysis || {};
    return JSON.stringify({
      current_reputation_score: whatIf.current_reputation_score ?? null,
      projected_reputation_score: whatIf.projected_reputation_score ?? null,
      relative_improvement_percent: whatIf.relative_improvement_percent ?? null,
    });
  }

  if (page === "upload") {
    const meta = safe.metadata || {};
    return JSON.stringify({
      rows_processed: meta.rows_processed ?? null,
      best_model: safe.best_model ?? null,
    });
  }

  return JSON.stringify({
    page,
    marker: safe?.reputation_score ?? safe?.best_model ?? null,
  });
}

function getCacheKey(page, company, signature) {
  return `${page}::${company}::${signature}`;
}

export default function usePageInsights(page, selectedCompany, contextData = null) {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const signature = useMemo(() => buildContextSignature(page, contextData), [page, contextData]);

  useEffect(() => {
    if (!selectedCompany) {
      setInsights(null);
      setLoading(false);
      setError("");
      return;
    }

    let isMounted = true;
    const key = getCacheKey(page, selectedCompany, signature);

    const run = async () => {
      const now = Date.now();
      const cached = insightsCache.get(key);
      if (cached && cached.expiresAt > now) {
        setInsights(cached.insights);
        setLoading(false);
        setError("");
        return;
      }

      setLoading(true);
      setError("");

      try {
        let requestPromise = inFlightRequests.get(key);
        if (!requestPromise) {
          requestPromise = axios
            .post(
              `${API_BASE_URL}/api/ai/page-insights`,
              {
                page,
                company: selectedCompany,
                context_data: contextData || {},
              },
              { timeout: 15000 }
            )
            .then((response) => response?.data?.insights || [])
            .catch(() => [])
            .finally(() => {
              inFlightRequests.delete(key);
            });
          inFlightRequests.set(key, requestPromise);
        }

        const fetchedInsights = await requestPromise;
        insightsCache.set(key, {
          insights: fetchedInsights,
          expiresAt: Date.now() + CACHE_TTL_MS,
        });

        if (isMounted) {
          setInsights(fetchedInsights);
        }
      } catch (err) {
        if (isMounted) {
          setInsights([]);
          setError(err?.message || "Unable to load insights");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    run();
    return () => {
      isMounted = false;
    };
  }, [page, selectedCompany, signature, contextData]);

  return { insights, loading, error };
}
