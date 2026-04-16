import { createContext, useContext, useEffect, useMemo, useState } from "react";
import axios from "axios";
import API_BASE_URL from "../config/api";

const CompanyContext = createContext(null);

export function CompanyProvider({ children }) {
  const [companies, setCompanies] = useState([]);
  const [selectedCompany, setSelectedCompany] = useState(() => localStorage.getItem("ve_selected_company") || "");
  const [benchmark, setBenchmark] = useState(null);
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  const [loadingBenchmark, setLoadingBenchmark] = useState(false);
  const [error, setError] = useState("");

  const refreshCompanies = async () => {
    try {
      setLoadingCompanies(true);
      setError("");
      const response = await axios.get(`${API_BASE_URL}/companies`);
      const list = response?.data?.companies || [];
      setCompanies(list);
      if (!selectedCompany && list.length > 0) {
        setSelectedCompany(list[0]);
      } else if (selectedCompany && !list.includes(selectedCompany) && list.length > 0) {
        setSelectedCompany(list[0]);
      }
    } catch (err) {
      setCompanies([]);
      setBenchmark(null);
      setError(err?.response?.data?.detail || err.message || "Unable to load companies");
    } finally {
      setLoadingCompanies(false);
    }
  };

  useEffect(() => {
    refreshCompanies();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedCompany) {
      localStorage.setItem("ve_selected_company", selectedCompany);
    }
  }, [selectedCompany]);

  const refreshBenchmark = async () => {
    if (!selectedCompany) {
      setBenchmark(null);
      return;
    }
    try {
      setLoadingBenchmark(true);
      setError("");
      const response = await axios.get(`${API_BASE_URL}/company-benchmark`, {
        params: { company: selectedCompany },
      });
      setBenchmark(response.data);
    } catch (err) {
      setBenchmark(null);
      setError(err?.response?.data?.detail || err.message || "Unable to load company comparison");
    } finally {
      setLoadingBenchmark(false);
    }
  };

  useEffect(() => {
    refreshBenchmark();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCompany]);

  const value = useMemo(
    () => ({
      companies,
      selectedCompany,
      setSelectedCompany,
      benchmark,
      loadingCompanies,
      loadingBenchmark,
      error,
      refreshCompanies,
      refreshBenchmark,
    }),
    [companies, selectedCompany, benchmark, loadingCompanies, loadingBenchmark, error]
  );

  return <CompanyContext.Provider value={value}>{children}</CompanyContext.Provider>;
}

export function useCompanyComparison() {
  const ctx = useContext(CompanyContext);
  if (!ctx) {
    // During HMR/hot reload, context might be temporarily unavailable
    // Return safe defaults to prevent unmounting during development
    if (import.meta.env.DEV) {
      return {
        companies: [],
        selectedCompany: null,
        setSelectedCompany: () => {},
        benchmark: null,
        loadingCompanies: false,
        loadingBenchmark: false,
        error: "Context loading...",
        refreshCompanies: async () => {},
        refreshBenchmark: async () => {},
      };
    }
    throw new Error("useCompanyComparison must be used inside CompanyProvider");
  }
  return ctx;
}
