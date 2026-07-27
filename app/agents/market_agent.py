import json
from app.agents.base import BaseAgent, first_words
from app.core.types import AgentOutput, BusinessIdeaProfile
from app.core.prompts import MARKET_AGENT_PROMPT
from app.services.llm_logging import log_agent_result, log_failed_raw_response

_NO_WEB_NOTE = (
    "\n\nNESSUN dato web disponibile: basa l'analisi solo su conoscenze "
    "generali e segnala esplicitamente che i competitor/bandi elencati vanno "
    "verificati.\n"
)


class MarketAgent(BaseAgent):
    def __init__(self, llm_service, web_search_service=None):
        super().__init__(llm_service, "MarketAgent")
        self.web_search = web_search_service

    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        search_results = []
        if self.web_search is None:
            web_status = "unavailable"
        else:
            try:
                distintivo = first_words(profile.need_addressed or profile.idea_description, 4)
                query = " ".join(
                    f"mercato {distintivo} {profile.sector_hint} {profile.target_region}".split()[:10]
                )
                search_results = await self.web_search.search(query, max_results=3)
                web_status = "results" if search_results else "empty"
            except Exception as e:
                # Non blocco l'esecuzione per errori della ricerca
                print(f"[MarketAgent] Errore di ricerca web: {e}")
                web_status = "failed"

        user_message = self._build_user_message(profile, context, correction_context)
        if search_results:
            search_str = "\n".join(
                f"- Title: {r.get('title')}\n  Snippet: {r.get('snippet')}\n  Link: {r.get('link')}"
                for r in search_results
            )
            user_message += f"\n\nRISULTATI RICERCA WEB REAL-TIME DI MERCATO:\n{search_str}\n"
        else:
            user_message += _NO_WEB_NOTE

        raw = await self.llm.generate(
            system_prompt=MARKET_AGENT_PROMPT,
            user_message=user_message,
            temperature=0.2,
            max_tokens=8000,
            agent_name=self.name
        )
        call_id = self.llm.last_call_id
        try:
            data = json.loads(raw)
            log_agent_result(
                call_id=call_id,
                run_id=self.llm.run_id,
                agent_name=self.name,
                iteration=self.llm.iteration,
                json_valid=True,
                status="success",
                confidence=data.get("confidence", 0.7),
                is_revision=bool(correction_context),
                web_search=web_status
            )
            return AgentOutput(
                agent_name=self.name,
                status="success",
                data=data,
                confidence=data.get("confidence", 0.7),
                reasoning="Analisi di mercato e concorrenza completata.",
                revision_count=1 if correction_context else 0
            )
        except json.JSONDecodeError:
            log_failed_raw_response(call_id=call_id, raw_text=raw)
            log_agent_result(
                call_id=call_id,
                run_id=self.llm.run_id,
                agent_name=self.name,
                iteration=self.llm.iteration,
                json_valid=False,
                status="error",
                confidence=0.0,
                is_revision=bool(correction_context),
                web_search=web_status
            )
            return AgentOutput(
                agent_name=self.name,
                status="error",
                data={"raw": raw},
                confidence=0.0,
                reasoning="Parsing JSON fallito."
            )
