import json
import uuid
from app.agents.vision_agent import VisionAgent
from app.agents.market_agent import MarketAgent
from app.agents.team_agent import TeamAgent
from app.agents.setup_agent import SetupAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.funding_agent import FundingAgent
from app.core.types import (
    AgentOutput, BusinessIdeaProfile, OrchestratorResult, RevisionStatus
)
from app.core.prompts import ORCHESTRATOR_PROMPT
from app.services.charts import render_chart_specs
from app.services.report_builder import build_draft_markdown, markdown_to_docx, save_markdown_report
from app.services.llm_logging import log_orchestrator_iteration
from app.config.settings import settings


class Orchestrator:
    def __init__(self, llm_service, web_search_service=None):
        self.llm = llm_service
        self.vision_agent = VisionAgent(llm_service)
        self.market_agent = MarketAgent(llm_service, web_search_service)
        self.team_agent = TeamAgent(llm_service)
        self.setup_agent = SetupAgent(llm_service)
        self.financial_agent = FinancialAgent(llm_service)
        self.funding_agent = FundingAgent(llm_service, web_search_service)

    async def run(self, profile: BusinessIdeaProfile) -> OrchestratorResult:
        plan_id = str(uuid.uuid4())[:8]
        self.llm.run_id = plan_id
        self.llm.iteration = 1
        revision_log = []

        # --- FASE 1: agenti paralleli (nessuna dipendenza tra loro) ---
        vision_out = await self.vision_agent.process(profile)
        market_out = await self.market_agent.process(profile)
        team_out = await self.team_agent.process(profile)
        setup_out = await self.setup_agent.process(profile)

        # --- FASE 2: FinancialAgent dipende dagli output di fase 1 ---
        upstream_context = {
            "vision": vision_out.data,
            "market": market_out.data,
            "team": team_out.data,
            "setup": setup_out.data
        }
        self.llm.iteration = 1
        financial_out = await self.financial_agent.process(profile, context=upstream_context)

        # --- FASE 3: FundingAgent dipende da Financial ---
        funding_context = {**upstream_context, "financial": financial_out.data}
        self.llm.iteration = 1
        funding_out = await self.funding_agent.process(profile, context=funding_context)

        agent_outputs = {
            "vision": vision_out,
            "market": market_out,
            "team": team_out,
            "setup": setup_out,
            "financial": financial_out,
            "funding": funding_out
        }

        # --- FASE 4: validation loop dell'Orchestratore ---
        for iteration in range(1, settings.MAX_REVISION_CYCLES + 1):
            self.llm.iteration = iteration
            orchestrator_raw = await self.llm.generate(
                system_prompt=ORCHESTRATOR_PROMPT,
                user_message=self._build_orchestrator_message(profile, agent_outputs, iteration),
                temperature=0.1,
                max_tokens=5000,
                agent_name="Orchestrator"
            )

            try:
                orch_data = json.loads(orchestrator_raw)
            except json.JSONDecodeError:
                break

            log_orchestrator_iteration(
                run_id=plan_id,
                iteration=iteration,
                final_status=orch_data.get("status", "UNKNOWN"),
                revisions_needed_count=len(orch_data.get("revisions_needed", [])),
                agents_flagged=[r["agent"] for r in orch_data.get("revisions_needed", [])]
            )

            draft_md = build_draft_markdown(
                profile, agent_outputs, iteration,
                issues=[r.get("issue", "") for r in orch_data.get("revisions_needed", [])]
            )
            save_markdown_report(
                draft_md, chart_paths=[],
                output_filename=f"business_plan_{plan_id}_iter{iteration}_draft.md"
            )

            if orch_data.get("status") == "APPROVED":
                # Rendering deterministico dei grafici — SOLO qui, dopo APPROVED
                chart_specs = financial_out.data.get("charts_needed", [])
                charts_generated = render_chart_specs(chart_specs)

                markdown = orch_data.get("business_plan_markdown", "")
                docx_path = markdown_to_docx(
                    markdown, chart_paths=charts_generated,
                    output_filename=f"business_plan_{plan_id}.docx"
                )
                md_path = save_markdown_report(
                    markdown, chart_paths=charts_generated,
                    output_filename=f"business_plan_{plan_id}.md"
                )

                return OrchestratorResult(
                    plan_id=plan_id,
                    profile=profile,
                    agent_outputs=agent_outputs,
                    revision_log=revision_log,
                    charts_generated=charts_generated,
                    business_plan_markdown=markdown,
                    business_plan_docx_path=docx_path,
                    business_plan_md_path=md_path,
                    total_iterations=iteration,
                    status=RevisionStatus.APPROVED
                )

            # REVISION_NEEDED: rilancia gli agenti indicati con correction_context
            revisions_raw = orch_data.get("revisions_needed", [])
            
            # Deduplicate by agent
            grouped = {}
            for rev in revisions_raw:
                agent_key = rev.get("agent", "")
                if not agent_key:
                    continue
                agent_normalized = agent_key.lower().replace("agent", "").strip()
                grouped.setdefault(agent_normalized, []).append(rev.get("correction_context", ""))
            
            revisions = []
            for agent_name, contexts in grouped.items():
                if len(contexts) > 1:
                    correction = "\n\n---\n\n".join(f"Correzione {i}:\n{ctx}" for i, ctx in enumerate(contexts, 1))
                else:
                    correction = contexts[0] if contexts else ""
                revisions.append({
                    "agent": agent_name,
                    "correction_context": correction
                })

            revision_log.append({"iteration": iteration, "revisions": revisions})

            # Rilancio di ogni agente modificato
            for rev in revisions:
                agent_name = rev["agent"].lower().replace("agent", "").strip()
                correction = rev["correction_context"]
                self.llm.iteration = iteration

                if agent_name == "vision":
                    agent_outputs["vision"] = await self.vision_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "market":
                    agent_outputs["market"] = await self.market_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "team":
                    agent_outputs["team"] = await self.team_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "setup":
                    agent_outputs["setup"] = await self.setup_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "financial":
                    agent_outputs["financial"] = await self.financial_agent.process(
                        profile,
                        context={k: v.data for k, v in agent_outputs.items()
                                 if k in ("vision", "market", "team", "setup")},
                        correction_context=correction)
                elif agent_name == "funding":
                    agent_outputs["funding"] = await self.funding_agent.process(
                        profile,
                        context={k: v.data for k, v in agent_outputs.items() if k != "funding"},
                        correction_context=correction)

            # Dopo aver rieseguito gli agenti corretti, aggiorniamo il contesto per quelli dipendenti
            # (Ad esempio, se Vision/Market/Team/Setup cambiano, Financial e Funding devono essere rieseguiti o adattarsi)
            # Per robustezza ricalcoliamo le dipendenze degli agenti aggiornati se necessario
            updated_agents = {rev["agent"].lower().replace("agent", "").strip() for rev in revisions}
            if any(a in updated_agents for a in ("vision", "market", "team", "setup")):
                if "financial" not in updated_agents:
                    # Rieseguiamo Financial con il nuovo contesto a monte
                    financial_context = {k: v.data for k, v in agent_outputs.items()
                                         if k in ("vision", "market", "team", "setup")}
                    self.llm.iteration = iteration
                    agent_outputs["financial"] = await self.financial_agent.process(
                        profile, context=financial_context)
            if any(a in updated_agents for a in ("vision", "market", "team", "setup", "financial")):
                if "funding" not in updated_agents:
                    # Rieseguiamo Funding con il nuovo contesto a monte
                    funding_context = {k: v.data for k, v in agent_outputs.items() if k != "funding"}
                    self.llm.iteration = iteration
                    agent_outputs["funding"] = await self.funding_agent.process(
                        profile, context=funding_context)

        # Max iterazioni raggiunte — produce comunque un documento parziale
        fallback_sections = [
            "⚠️ REVISIONE MANUALE RICHIESTA — le sezioni seguenti non sono state "
            "validate per coerenza dall'Orchestrator dopo il numero massimo di cicli di revisione.\n"
        ]
        for agent_key, ao in agent_outputs.items():
            fallback_sections.append(f"\n## {agent_key.capitalize()}\n")
            fallback_sections.append(
                f"```json\n{json.dumps(ao.data, indent=2, ensure_ascii=False)}\n```"
            )
        fallback_markdown = "\n".join(fallback_sections)

        fallback_docx = markdown_to_docx(
            fallback_markdown, chart_paths=[],
            output_filename=f"business_plan_{plan_id}_partial.docx"
        )
        fallback_md = save_markdown_report(
            fallback_markdown, chart_paths=[],
            output_filename=f"business_plan_{plan_id}_partial.md"
        )

        return OrchestratorResult(
            plan_id=plan_id,
            profile=profile,
            agent_outputs=agent_outputs,
            revision_log=revision_log,
            charts_generated=[],
            business_plan_markdown=fallback_markdown,
            business_plan_docx_path=fallback_docx,
            business_plan_md_path=fallback_md,
            total_iterations=settings.MAX_REVISION_CYCLES,
            status=RevisionStatus.REVISION_NEEDED
        )

    def _build_orchestrator_message(
        self, profile: BusinessIdeaProfile, outputs: dict[str, AgentOutput], iteration: int
    ) -> str:
        return f"""
PROGETTO: {profile.project_name} | Settore: {profile.sector_hint}
ITERAZIONE: {iteration}

OUTPUT DEGLI AGENTI:

[VISION_AGENT]
{json.dumps(outputs['vision'].data, indent=2, ensure_ascii=False)}

[MARKET_AGENT]
{json.dumps(outputs['market'].data, indent=2, ensure_ascii=False)}

[TEAM_AGENT]
{json.dumps(outputs['team'].data, indent=2, ensure_ascii=False)}

[SETUP_AGENT]
{json.dumps(outputs['setup'].data, indent=2, ensure_ascii=False)}

[FINANCIAL_AGENT]
{json.dumps(outputs['financial'].data, indent=2, ensure_ascii=False)}

[FUNDING_AGENT]
{json.dumps(outputs['funding'].data, indent=2, ensure_ascii=False)}

Esegui tutti gli step delle tue istruzioni. Output solo JSON valido.
"""
