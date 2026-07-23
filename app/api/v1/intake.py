from fastapi import APIRouter
from app.agents.intake_agent import IntakeAgent
from app.services.llm import LLMService
from app.models.requests import IntakeParseRequest
from app.models.responses import IntakeParseResponse

router = APIRouter(prefix="/api/v1/intake", tags=["intake"])


@router.get("/template")
async def get_intake_template():
    agent = IntakeAgent(LLMService())
    return agent.generate_template_markdown()


@router.post("/parse", response_model=IntakeParseResponse)
async def parse_intake(request: IntakeParseRequest):
    agent = IntakeAgent(LLMService())
    report = await agent.parse_brief(request.raw_markdown)
    # Profile needs to be parsed correctly. report.profile is BusinessIdeaProfile dataclass.
    # We should convert it to dict (including nested Founders) or match the schema expected by response
    return IntakeParseResponse(
        profile=report.profile,
        needs_clarification=report.needs_clarification,
        summary_markdown=report.summary_markdown,
        confidence=report.confidence
    )
