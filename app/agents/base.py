from abc import ABC, abstractmethod
from app.core.types import AgentOutput, BusinessIdeaProfile


class BaseAgent(ABC):
    def __init__(self, llm_service, name: str):
        self.llm = llm_service
        self.name = name

    @abstractmethod
    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        pass

    def _build_user_message(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None,
        correction: str | None
    ) -> str:
        founders_str = "; ".join(
            f"{f.name} ({', '.join(f.skills)}, {f.availability})"
            for f in profile.founders
        )
        msg = f"""
PROFILO IDEA DI BUSINESS:
- Nome progetto: {profile.project_name}
- Descrizione idea: {profile.idea_description}
- Bisogno da soddisfare: {profile.need_addressed}
- Tipo prodotto/servizio: {profile.product_type.value}
- Settore: {profile.sector_hint}
- Area geografica target: {profile.target_region}
- Fondatori: {founders_str}
- Capitale proprio disponibile: {profile.available_capital_eur} EUR
- Timeline desiderata: {profile.desired_timeline_months} mesi
- Note: {profile.notes}
"""
        if profile.raw_intake_notes:
            section_key = self.name.lower().replace("agent", "")
            note = profile.raw_intake_notes.get(section_key, "")
            if note:
                msg += f"\nNOTE GREZZE DELL'UTENTE PER QUESTA AREA (dall'intake):\n{note}\n"

        if context:
            msg += f"\nOUTPUT DEGLI AGENTI A MONTE (per riferimento):\n{context}\n"

        if correction:
            msg += f"\nCORREZIONE RICHIESTA DAL SUPERVISORE:\n{correction}\n"
            msg += "Rivedi il tuo output precedente correggendo quanto sopra.\n"

        return msg
