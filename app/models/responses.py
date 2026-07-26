from pydantic import BaseModel


class IntakeParseResponse(BaseModel):
    profile: dict
    needs_clarification: list[str]
    summary_markdown: str
    confidence: float


class BusinessPlanResponse(BaseModel):
    plan_id: str
    status: str
    business_plan_markdown: str
    docx_path: str
    md_path: str
    charts_generated: list[str]
    revision_cycles: int
    agent_outputs: dict[str, dict]
    validation_xlsx_path: str = ""
