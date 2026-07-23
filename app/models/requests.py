from pydantic import BaseModel
from app.core.types import ProductType, FounderProfile


class IntakeParseRequest(BaseModel):
    raw_markdown: str


class BusinessPlanRequest(BaseModel):
    project_name: str
    idea_description: str
    need_addressed: str
    product_type: ProductType
    sector_hint: str
    target_region: str
    founders: list[FounderProfile]
    available_capital_eur: float
    desired_timeline_months: int
    notes: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_name": "Fermenta",
                "idea_description": "Produzione artigianale di bevande fermentate km0",
                "need_addressed": "Mancanza di alternative analcoliche serie all'aperitivo",
                "product_type": "physical",
                "sector_hint": "food & beverage artigianale",
                "target_region": "Napoli e provincia",
                "founders": [
                    {"name": "Fondatore 1", "skills": ["ricette", "produzione"], "availability": "full-time"},
                    {"name": "Fondatore 2", "skills": ["rete bar/ristoranti"], "availability": "part-time 20h/settimana"}
                ],
                "available_capital_eur": 4000,
                "desired_timeline_months": 12,
                "notes": "Laboratorio condiviso in valutazione"
            }
        }
    }
