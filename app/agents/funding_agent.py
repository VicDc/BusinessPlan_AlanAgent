import json
from app.agents.base import BaseAgent
from app.core.types import AgentOutput, BusinessIdeaProfile
from app.core.prompts import FUNDING_AGENT_PROMPT
from app.services.llm_logging import log_agent_result, log_failed_raw_response


class FundingAgent(BaseAgent):
    def __init__(self, llm_service, web_search_service=None):
        super().__init__(llm_service, "FundingAgent")
        self.web_search = web_search_service

    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        search_results = []
        if self.web_search:
            try:
                query = f"bandi agevolazioni startup {profile.sector_hint} {profile.target_region}"
                search_results = await self.web_search.search(query, max_results=3)
            except Exception as e:
                # Non blocco l'esecuzione per errori della ricerca
                print(f"[FundingAgent] Errore di ricerca web: {e}")

        user_message = self._build_user_message(profile, context, correction_context)
        if search_results:
            search_str = "\n".join(
                f"- Title: {r.get('title')}\n  Snippet: {r.get('snippet')}\n  Link: {r.get('link')}"
                for r in search_results
            )
            user_message += f"\n\nRISULTATI RICERCA WEB REAL-TIME DI BANDI E FINANZIAMENTI:\n{search_str}\n"

        raw = await self.llm.generate(
            system_prompt=FUNDING_AGENT_PROMPT,
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
                is_revision=bool(correction_context)
            )
            return AgentOutput(
                agent_name=self.name,
                status="success",
                data=data,
                confidence=data.get("confidence", 0.7),
                reasoning="Analisi delle fonti di finanziamento e copertura completata.",
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
                is_revision=bool(correction_context)
            )
            return AgentOutput(
                agent_name=self.name,
                status="error",
                data={"raw": raw},
                confidence=0.0,
                reasoning="Parsing JSON fallito."
            )
