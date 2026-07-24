"""
IntakeAgent non eredita da BaseAgent: la sua forma è diversa (produce il
BusinessIdeaProfile invece di consumarlo, e non partecipa al revision loop
dell'Orchestrator). Ha due responsabilità: generare il template delle domande
e, dato un md compilato, estrarne un profilo strutturato + un report.
"""
import json
from app.core.intake_questions import INTAKE_QUESTIONS
from app.core.prompts import INTAKE_AGENT_PROMPT
from app.core.types import BusinessIdeaProfile, FounderProfile, IntakeReport, ProductType
from app.services.llm_logging import log_agent_result, log_failed_raw_response


class IntakeAgent:
    def __init__(self, llm_service):
        self.llm = llm_service
        self.name = "IntakeAgent"

    def generate_template_markdown(self) -> str:
        """Genera il template .md con tutte le domande, raggruppate per
        sezione. Usato sia dalla CLI (per stampare le domande) sia per
        produrre un file scaricabile via API."""
        lines = ["# Business Plan — Modulo di Intake",
                 "> Compila ogni sezione. Gli hint tra parentesi sono solo "
                 "orientativi: non copiarli come risposta.\n"]
        for section, questions in INTAKE_QUESTIONS.items():
            lines.append(f"## {section}")
            for q in questions:
                lines.append(f"**{q['question']}**")
                if q["hint"]:
                    lines.append(f"*(hint: {q['hint']})*")
                lines.append("> Risposta: \n")
            lines.append("")
        return "\n".join(lines)

    async def parse_brief(self, raw_markdown: str) -> IntakeReport:
        """Estrae un BusinessIdeaProfile strutturato da un file .md compilato
        dall'utente, e produce l'IntakeReport (cancello di verifica prima
        della pipeline a 6 agenti)."""
        raw = await self.llm.generate(
            system_prompt=INTAKE_AGENT_PROMPT,
            user_message=raw_markdown,
            temperature=0.1,
            max_tokens=8000,
            agent_name=self.name
        )
        call_id = self.llm.last_call_id

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            log_failed_raw_response(call_id=call_id, raw_text=raw)
            log_agent_result(
                call_id=call_id,
                run_id=self.llm.run_id,
                agent_name=self.name,
                iteration=None,
                json_valid=False,
                status="error",
                confidence=0.0,
                is_revision=False
            )
            raise

        log_agent_result(
            call_id=call_id,
            run_id=self.llm.run_id,
            agent_name=self.name,
            iteration=None,
            json_valid=True,
            status="success",
            confidence=data.get("confidence", 0.5),
            is_revision=False
        )

        profile = BusinessIdeaProfile(
            project_name=data["project_name"],
            idea_description=data["idea_description"],
            need_addressed=data["need_addressed"],
            product_type=ProductType(data["product_type"]),
            sector_hint=data["sector_hint"],
            target_region=data["target_region"],
            founders=[FounderProfile(**f) for f in data["founders"]],
            available_capital_eur=data["available_capital_eur"],
            desired_timeline_months=data["desired_timeline_months"],
            notes=data.get("notes", ""),
            raw_intake_notes=data.get("raw_section_notes", {})
        )

        return IntakeReport(
            profile=profile,
            needs_clarification=data.get("needs_clarification", []),
            summary_markdown=data.get("summary_markdown", ""),
            confidence=data.get("confidence", 0.5)
        )
