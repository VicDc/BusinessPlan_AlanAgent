import warnings

import httpx
from app.config.settings import settings
from app.services.llm_logging import log_llm_call, new_call_id, Timer


class LLMService:
    """
    Client provider-agnostic. Si connette a LM Studio o Ollama via API
    OpenAI-compatible. Stesso servizio già usato in OrgTransform AI —
    riusalo tale e quale, non serve reimplementarlo.

    ATTENZIONE — provider claude_fast/claude_quality: SPERIMENTALI e NON
    verificati. Il codice sotto riusa lo stesso path OpenAI-compatible del
    provider locale (endpoint /chat/completions, header `Authorization:
    Bearer`, payload con `chat_template_kwargs`). L'API Anthropic reale usa
    invece l'endpoint /v1/messages con header `x-api-key` + `anthropic-version`
    e uno schema di richiesta/risposta diverso. Questi rami non sono mai stati
    eseguiti contro l'API vera (nessuna key in test): trattali come predisposti
    ma da verificare/riscrivere prima dell'uso in produzione. Provider
    supportato e testato: "local".
    """

    def __init__(self):
        provider = settings.LLM_PROVIDER
        if provider == "local":
            self.base_url = settings.LLM_BASE_URL
            self.model = settings.LLM_MODEL
            self._headers: dict = {}
        elif provider == "claude_fast":
            # ponytail: sperimentale, non verificato — vedi docstring classe.
            warnings.warn(
                "LLM_PROVIDER='claude_fast' è sperimentale e non verificato "
                "contro l'API Anthropic reale (usa il path OpenAI-compatible). "
                "Usa 'local' per l'esecuzione supportata.",
                stacklevel=2,
            )
            self.base_url = "https://api.anthropic.com/v1"
            self.model = "claude-haiku-4-5-20251001"
            self._headers = {"Authorization": f"Bearer {settings.ANTHROPIC_API_KEY}"}
        elif provider == "claude_quality":
            # ponytail: sperimentale, non verificato — vedi docstring classe.
            warnings.warn(
                "LLM_PROVIDER='claude_quality' è sperimentale e non verificato "
                "contro l'API Anthropic reale (usa il path OpenAI-compatible). "
                "Usa 'local' per l'esecuzione supportata.",
                stacklevel=2,
            )
            self.base_url = "https://api.anthropic.com/v1"
            self.model = "claude-sonnet-5"
            self._headers = {"Authorization": f"Bearer {settings.ANTHROPIC_API_KEY}"}
        else:
            raise ValueError(
                f"LLM_PROVIDER non valido: '{provider}'. "
                "Valori accettati: 'local', 'claude_fast', 'claude_quality'."
            )
        self.run_id: str | None = None
        self.iteration: int | None = None
        self.last_call_id: str | None = None

    async def generate(
        self, system_prompt: str, user_message: str,
        temperature: float = 0.2, max_tokens: int = 2000,
        agent_name: str | None = None
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "chat_template_kwargs": {"enable_thinking": False}
        }

        call_id = new_call_id()
        self.last_call_id = call_id
        error_msg = None
        prompt_tokens = None
        completion_tokens = None
        total_tokens = None
        latency_seconds = 0.0

        try:
            with Timer() as timer:
                async with httpx.AsyncClient(timeout=3600.0) as client:
                    response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=self._headers)
                    response.raise_for_status()
                    data = response.json()
                    message = data["choices"][0]["message"]
                    content = message["content"]

                    if not content or not content.strip():
                        reasoning_content = message.get("reasoning_content")
                        if reasoning_content:
                            raise ValueError(
                                f"Il modello ha prodotto solo reasoning_content "
                                f"({len(reasoning_content)} token) e nessun contenuto: "
                                "la modalità thinking è probabilmente attiva lato server. "
                                "Disattivala nel prompt template del modello in LM Studio."
                            )
                        raise ValueError("Risposta vuota dal modello")

                    usage = data.get("usage") or {}
                    prompt_tokens = usage.get("prompt_tokens")
                    completion_tokens = usage.get("completion_tokens")
                    total_tokens = usage.get("total_tokens")

                    return _strip_code_fence(content)
        except Exception as e:
            error_msg = str(e)
            raise
        finally:
            latency_seconds = timer.elapsed if 'timer' in locals() else 0.0
            log_llm_call(
                call_id=call_id,
                run_id=self.run_id,
                agent_name=agent_name,
                iteration=self.iteration,
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                latency_seconds=latency_seconds,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                error=error_msg
            )


def _strip_code_fence(text: str) -> str:
    """Gemma a volte avvolge il JSON in ```json ... ``` — stessa utility
    già presente in OrgTransform AI's base.py, riusala identica."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
