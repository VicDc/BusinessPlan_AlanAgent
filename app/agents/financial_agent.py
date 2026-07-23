import json
from app.agents.base import BaseAgent
from app.core.types import AgentOutput, BusinessIdeaProfile
from app.core.prompts import FINANCIAL_AGENT_PROMPT
from app.services.llm_logging import log_agent_result, log_failed_raw_response


class FinancialAgent(BaseAgent):
    def __init__(self, llm_service):
        super().__init__(llm_service, "FinancialAgent")

    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        user_message = self._build_user_message(profile, context, correction_context)
        raw = await self.llm.generate(
            system_prompt=FINANCIAL_AGENT_PROMPT,
            user_message=user_message,
            temperature=0.2,
            max_tokens=3000,
            agent_name=self.name
        )
        call_id = self.llm.last_call_id
        try:
            data = json.loads(raw)
            # NOTA: data["charts_needed"] contiene solo le SPECIFICHE dei grafici
            # (dati + tipo + titolo). Il rendering vero avviene in
            # services/charts.py, chiamato dall'Orchestrator dopo APPROVED —
            # questo agente non disegna nulla, produce solo la struttura dati.
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
                reasoning="Modello economico-finanziario completato.",
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
