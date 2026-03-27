import os
import logging
import warnings
import importlib
from typing import List, Dict, Any
import requests

def _safe_load_dotenv(path: str) -> None:
    try:
        dotenv_module = importlib.import_module("dotenv")
        dotenv_loader = getattr(dotenv_module, "load_dotenv", None)
        if callable(dotenv_loader):
            dotenv_loader(path)
    except Exception:
        pass

genai = None
genai_client = None

try:
    # New SDK path (preferred): pip install google-genai
    from google import genai as genai_client  # type: ignore
except Exception:
    genai_client = None

if genai_client is None:
    try:
        # Legacy SDK path kept for compatibility in this project.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            import google.generativeai as genai  # type: ignore
    except Exception:
        genai = None

logger = logging.getLogger(__name__)


class AIAdviceService:
    def __init__(self):
        self.model = None
        self.client = None
        self.provider_ready = False
        self.provider = "none"
        self.ai_provider = "gemini"
        self.primary_model = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        self.fallback_model = os.environ.get("GEMINI_FALLBACK_MODEL", "gemini-1.5-flash")
        self.hf_model = os.environ.get("HF_MODEL", "google/flan-t5-large")
        self.hf_api_base = os.environ.get("HF_API_BASE", "https://api-inference.huggingface.co/models")
        self.ollama_model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        self._api_key_source = "missing"
        self.last_error = None

        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        _safe_load_dotenv(os.path.join(root_dir, "backend", ".env"))
        _safe_load_dotenv(os.path.join(root_dir, ".env"))

        self.ai_provider = (os.environ.get("AI_PROVIDER", "gemini") or "gemini").strip().lower()
        self.primary_model = os.environ.get("GEMINI_MODEL", self.primary_model)
        self.fallback_model = os.environ.get("GEMINI_FALLBACK_MODEL", self.fallback_model)
        self.hf_model = os.environ.get("HF_MODEL", self.hf_model)
        self.hf_api_base = os.environ.get("HF_API_BASE", self.hf_api_base)
        self.ollama_model = os.environ.get("OLLAMA_MODEL", self.ollama_model)
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", self.ollama_base_url)

        if self.ai_provider == "ollama":
            self._api_key_source = "none-local"
            self.provider = "ollama-local"
            self.provider_ready = True
            return

        if self.ai_provider == "huggingface":
            hf_token = os.environ.get("HF_API_TOKEN")
            if not hf_token:
                return
            self._api_key_source = "HF_API_TOKEN"
            self.provider = "huggingface-inference"
            self.provider_ready = True
            return

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if os.environ.get("GEMINI_API_KEY"):
            self._api_key_source = "GEMINI_API_KEY"
        elif os.environ.get("GOOGLE_API_KEY"):
            self._api_key_source = "GOOGLE_API_KEY"

        if not api_key:
            return

        try:
            if genai_client is not None:
                self.client = genai_client.Client(api_key=api_key)
                self.provider = "google-genai"
            elif genai is not None:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(self.primary_model)
                self.provider = "google-generativeai"
            else:
                return
            self.provider_ready = True
        except Exception as e:
            logger.exception("AI provider initialization failed: %s", e)
            self.client = None
            self.model = None
            self.provider_ready = False
            self.provider = "none"
            self.last_error = str(e)

    def _hf_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {os.environ.get('HF_API_TOKEN', '')}",
            "Content-Type": "application/json",
        }

    def _call_huggingface(self, prompt: str) -> str:
        response = requests.post(
            f"{self.hf_api_base.rstrip('/')}/{self.hf_model}",
            headers=self._hf_headers(),
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 220,
                    "temperature": 0.4,
                    "return_full_text": False,
                },
            },
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(str(data.get("error")))
        if isinstance(data, list) and data and isinstance(data[0], dict):
            generated = data[0].get("generated_text", "")
            return generated.strip() if isinstance(generated, str) else ""
        if isinstance(data, dict):
            generated = data.get("generated_text") or data.get("summary_text") or data.get("text")
            return generated.strip() if isinstance(generated, str) else ""
        if isinstance(data, str):
            return data.strip()
        return ""

    def _call_ollama(self, prompt: str) -> str:
        response = requests.post(
            f"{self.ollama_base_url.rstrip('/')}/api/generate",
            json={
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                },
            },
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and data.get("error"):
            raise RuntimeError(str(data.get("error")))
        text = data.get("response") if isinstance(data, dict) else None
        return text.strip() if isinstance(text, str) else ""

    def _model_candidates(self) -> List[str]:
        env_candidates = os.environ.get("GEMINI_MODEL_CANDIDATES", "")
        configured = [m.strip() for m in env_candidates.split(",") if m.strip()]
        candidates = [self.primary_model, self.fallback_model, "gemini-2.0-flash", "gemini-1.5-flash"] + configured
        unique_models: List[str] = []
        for model_name in candidates:
            if model_name and model_name not in unique_models:
                unique_models.append(model_name)
        return unique_models

    def _extract_text(self, response) -> str:
        # Some SDK versions expose `text` as a property that may raise.
        try:
            text = getattr(response, "text", None)
        except Exception:
            text = None
        if isinstance(text, str) and text.strip():
            return text.strip()

        # Dict-like fallback used by some client wrappers.
        if isinstance(response, dict):
            dict_text = response.get("text")
            if isinstance(dict_text, str) and dict_text.strip():
                return dict_text.strip()

        # New SDK fallback: parse candidates/parts when `text` is empty.
        candidates = getattr(response, "candidates", None) or []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) if content is not None else None
            if not parts:
                continue
            for part in parts:
                part_text = getattr(part, "text", None)
                if isinstance(part_text, str) and part_text.strip():
                    return part_text.strip()

        return ""

    def _fallback_response(self) -> str:
        if self.ai_provider == "ollama":
            provider_hint = "start Ollama and pull the selected model"
        else:
            provider_hint = "HF_API_TOKEN" if self.ai_provider == "huggingface" else "GEMINI_API_KEY"
        return (
            "- AI provider is not configured on this local setup.\n"
            f"- API results are still valid; add `{provider_hint}` to enable generated advice.\n"
            "- Continue with analysis, forecast, and simulation workflows."
        )

    def _call_failure_response(self) -> str:
        error_text = (self.last_error or "").lower()
        if self.ai_provider == "huggingface":
            provider_name = "Hugging Face"
        elif self.ai_provider == "ollama":
            provider_name = "Ollama"
        else:
            provider_name = "Gemini"

        if "resource_exhausted" in error_text or "quota exceeded" in error_text or "429" in error_text:
            return (
                f"- {provider_name} request failed: quota exceeded (429 RESOURCE_EXHAUSTED).\n"
                "- Enable billing or increase quota for this API key/project.\n"
                "- Retry after cooldown or switch to a key/project with active quota."
            )

        if self.ai_provider == "ollama" and ("connection refused" in error_text or "max retries exceeded" in error_text):
            return (
                "- Ollama is not reachable on the configured local URL.\n"
                "- Start Ollama and ensure the model is pulled (for example: `ollama pull llama3.1:8b`).\n"
                "- API results are still valid for analysis, forecast, and simulation."
            )
        if "winerror 10013" in error_text or "failed to establish a new connection" in error_text:
            return (
                f"- {provider_name} request failed: network access is blocked from this machine.\n"
                "- Allow outbound HTTPS (443) for Python/terminal in firewall, proxy, or antivirus.\n"
                "- API results are still valid for analysis, forecast, and simulation."
            )

        return (
            "- AI provider is configured but request failed.\n"
            "- Check backend terminal logs for provider error details (invalid key, API restrictions, or network).\n"
            "- API results are still valid for analysis, forecast, and simulation."
        )

    def _is_provider_failure(self, text: str) -> bool:
        if not isinstance(text, str):
            return True
        lowered = text.lower()
        return (
            "ai provider is configured but request failed" in lowered
            or "ai provider is not configured on this local setup" in lowered
            or "gemini request failed" in lowered
            or "hugging face request failed" in lowered
            or "ollama is not reachable" in lowered
        )

    def _local_dashboard_advice(self, reputation_score: float, prediction_class: str, top_feature: str) -> str:
        score_band = "strong" if reputation_score >= 0.7 else "moderate" if reputation_score >= 0.4 else "weak"
        return (
            f"- Current reputation level is {score_band} ({reputation_score:.2f}) with predicted class `{prediction_class}`.\n"
            f"- Prioritize improvements in `{top_feature}` because it appears to be the strongest driver.\n"
            "- Run a 30-day KPI plan: set weekly targets, monitor movement, and adjust actions quickly."
        )

    def _local_analysis_advice(self, reputation_score: float, top_correlations: Dict[str, float], weak_areas: List[str]) -> str:
        top_items = sorted(top_correlations.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
        top_text = ", ".join([f"{k} ({v:.2f})" for k, v in top_items]) if top_items else "no strong correlation detected"
        weak_text = ", ".join(weak_areas[:3]) if weak_areas else "no critical weak area identified"
        return (
            f"- Reputation score is {reputation_score:.2f}; strongest signals: {top_text}.\n"
            f"- Immediate focus areas: {weak_text}.\n"
            "- Execute one improvement sprint per weak area and compare score change month over month."
        )

    def _local_forecast_advice(self, forecast_values: List[float], trend: str, current_score: float) -> str:
        next_avg = sum(forecast_values) / len(forecast_values) if forecast_values else current_score
        direction = "upward" if next_avg > current_score else "downward" if next_avg < current_score else "flat"
        return (
            f"- Current score is {current_score:.2f} and forecast trend is `{trend}` ({direction}).\n"
            "- If trajectory is downward, act early on sentiment and ESG communication.\n"
            "- Review forecast drivers weekly and re-run model after each new dataset upload."
        )

    def _local_prediction_advice(self, predicted_score: float, reputation_class: str, coefficients: Dict[str, float]) -> str:
        top_feature = "N/A"
        if coefficients:
            top_feature = max(coefficients.items(), key=lambda x: abs(x[1]))[0]
        return (
            f"- Predicted score is {predicted_score:.2f} with class `{reputation_class}`.\n"
            f"- Highest-impact feature appears to be `{top_feature}`; prioritize interventions there.\n"
            "- Create a monthly action checklist and track before/after movement for this feature."
        )

    def _local_simulation_advice(self, column: str, change_percent: float, before_score: float, after_score: float) -> str:
        impact = after_score - before_score
        significance = "high" if abs(impact) >= 1 else "moderate" if abs(impact) >= 0.25 else "low"
        return (
            f"- Simulating `{column}` by {change_percent:+.1f}% changed score by {impact:+.2f} ({significance} impact).\n"
            "- Use this factor as a decision lever in planning scenarios.\n"
            "- Prioritize changes that deliver consistent positive impact across multiple simulation runs."
        )

    def _local_upload_advice(self, columns: List[str], row_count: int, missing_cols: List[str]) -> str:
        missing_text = ", ".join(missing_cols) if missing_cols else "none"
        return (
            f"- Dataset quality check passed with {row_count} rows and {len(columns)} columns.\n"
            f"- Optional missing columns: {missing_text}.\n"
            "- Start with Analysis, then Forecast and Simulation to identify actionable improvement levers."
        )

    def get_generic_fallback_answer(self, question: str, context: str = "") -> str:
        topic = question.strip() if question else "your analysis request"
        context_text = context.strip() if context else "dataset summary"
        return (
            f"- Local AI insight for: `{topic}`.\n"
            f"- Based on available `{context_text}`, focus on trend direction, top-correlated drivers, and weakest metrics first.\n"
            "- Run Analysis -> Prediction -> Simulation, then prioritize the factor with the most consistent positive impact."
        )

    def generate_text(self, prompt: str) -> str:
        if not self.provider_ready:
            return self._fallback_response()

        try:
            if self.ai_provider == "ollama":
                try:
                    text = self._call_ollama(prompt)
                    return text if text else self._call_failure_response()
                except Exception as provider_error:
                    self.last_error = str(provider_error)
                    return self._call_failure_response()

            if self.ai_provider == "huggingface":
                try:
                    text = self._call_huggingface(prompt)
                    return text if text else self._call_failure_response()
                except Exception as provider_error:
                    self.last_error = str(provider_error)
                    return self._call_failure_response()

            if self.client is not None:
                # Try preferred model first, then fallback model for account/model compatibility.
                for model_name in self._model_candidates():
                    try:
                        try:
                            response = self.client.models.generate_content(
                                model=model_name,
                                contents=prompt,
                            )
                        except TypeError:
                            # Compatibility path for client versions expecting a list.
                            response = self.client.models.generate_content(
                                model=model_name,
                                contents=[prompt],
                            )
                        text = self._extract_text(response)
                        if text:
                            return text
                    except Exception as model_error:
                        self.last_error = str(model_error)
                        continue
                return self._call_failure_response()

            if self.model is not None and genai is not None:
                for model_name in self._model_candidates():
                    try:
                        legacy_model = genai.GenerativeModel(model_name)
                        response = legacy_model.generate_content(prompt)
                        text = self._extract_text(response)
                        if text:
                            return text
                    except Exception as model_error:
                        self.last_error = str(model_error)
                        continue
                return self._call_failure_response()

            return self._fallback_response()
        except Exception as e:
            logger.exception("AI generation failed: %s", e)
            self.last_error = str(e)
            return self._call_failure_response()

    def status(self) -> Dict[str, Any]:
        return {
            "provider_ready": self.provider_ready,
            "provider": self.provider,
            "ai_provider": self.ai_provider,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "hf_model": self.hf_model if self.ai_provider == "huggingface" else None,
            "ollama_model": self.ollama_model if self.ai_provider == "ollama" else None,
            "ollama_base_url": self.ollama_base_url if self.ai_provider == "ollama" else None,
            "api_key_source": self._api_key_source,
            "has_google_genai_sdk": genai_client is not None,
            "has_google_generativeai_sdk": genai is not None,
            "last_error": self.last_error,
        }

    def _call_ai(self, prompt: str) -> str:
        return self.generate_text(prompt)

    # Backward-compatible alias; existing routes call this name.
    def _call_claude(self, prompt: str) -> str:
        return self.generate_text(prompt)

    def get_dashboard_advice(self, reputation_score: float, prediction_class: str, top_feature: str) -> str:
        prompt = f"""
You are a corporate reputation analyst for ValorEdge AI.

Company reputation score: {reputation_score:.2f}
Prediction class: {prediction_class}
Most influential factor: {top_feature}

Give 3 specific, actionable recommendations to improve or maintain this reputation.
Be direct and practical. Use bullet points. Max 150 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_dashboard_advice(
            reputation_score, prediction_class, top_feature
        )

    def get_analysis_advice(self, reputation_score: float, top_correlations: Dict[str, float], weak_areas: List[str]) -> str:
        prompt = f"""
You are a corporate reputation analyst for ValorEdge AI.

Reputation score: {reputation_score:.2f}
Top correlated factors: {top_correlations}
Weak areas (low scores): {weak_areas}

Explain what these correlations mean for the company's reputation strategy.
Suggest which factors to prioritize. Max 150 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_analysis_advice(
            reputation_score, top_correlations, weak_areas
        )

    def get_forecast_advice(self, forecast_values: List[float], trend: str, current_score: float) -> str:
        prompt = f"""
You are a corporate reputation analyst for ValorEdge AI.

Current reputation score: {current_score:.2f}
Forecast trend: {trend}
Predicted values for next 3 periods: {forecast_values}

Is this forecast good or concerning? What actions should the company take
right now to influence this trajectory? Max 150 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_forecast_advice(
            forecast_values, trend, current_score
        )

    def get_prediction_advice(self, predicted_score: float, reputation_class: str, coefficients: Dict[str, float]) -> str:
        prompt = f"""
You are a corporate reputation analyst for ValorEdge AI.

Predicted reputation score: {predicted_score:.2f}
Reputation class: {reputation_class}
Feature importance (regression coefficients): {coefficients}

Explain why the model predicted {reputation_class}.
Which factor needs the most improvement? Give 2 specific actions. Max 150 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_prediction_advice(
            predicted_score, reputation_class, coefficients
        )

    def get_simulation_advice(self, column: str, change_percent: float, before_score: float, after_score: float) -> str:
        prompt = f"""
You are a corporate reputation analyst for ValorEdge AI.

Simulated change: {column} changed by {change_percent}%
Reputation score before: {before_score:.2f}
Reputation score after: {after_score:.2f}
Score impact: {after_score - before_score:+.2f}

Is this change significant? What does it tell us about this factor's importance?
What should the company do with this insight? Max 120 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_simulation_advice(
            column, change_percent, before_score, after_score
        )

    def get_upload_advice(self, columns: List[str], row_count: int, missing_cols: List[str]) -> str:
        prompt = f"""
You are a data quality advisor for ValorEdge AI.

Dataset columns: {columns}
Total rows: {row_count}
Missing optional columns: {missing_cols}

Evaluate this dataset's quality for reputation analysis.
Tell the user which analysis to run first and what insights to expect.
Max 100 words.
"""
        ai_text = self.generate_text(prompt)
        return ai_text if not self._is_provider_failure(ai_text) else self._local_upload_advice(
            columns, row_count, missing_cols
        )
