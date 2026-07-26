from fastapi import APIRouter, HTTPException
from app.core.types import BusinessIdeaProfile
from app.models.requests import BusinessPlanRequest
from app.models.responses import BusinessPlanResponse
from app.agents.orchestrator import Orchestrator
from app.services.llm import LLMService
from app.services.web_search import WebSearchService

router = APIRouter(prefix="/api/v1", tags=["business-plan"])


@router.post("/business-plan", response_model=BusinessPlanResponse)
async def create_business_plan(request: BusinessPlanRequest):
    profile = BusinessIdeaProfile(
        project_name=request.project_name,
        idea_description=request.idea_description,
        need_addressed=request.need_addressed,
        product_type=request.product_type,
        sector_hint=request.sector_hint,
        target_region=request.target_region,
        founders=request.founders,
        available_capital_eur=request.available_capital_eur,
        desired_timeline_months=request.desired_timeline_months,
        notes=request.notes
    )

    llm = LLMService()
    web_search = WebSearchService()
    orchestrator = Orchestrator(llm, web_search)

    try:
        result = await orchestrator.run(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BusinessPlanResponse(
        plan_id=result.plan_id,
        status=result.status.value,
        business_plan_markdown=result.business_plan_markdown,
        docx_path=result.business_plan_docx_path,
        md_path=result.business_plan_md_path,
        charts_generated=result.charts_generated,
        revision_cycles=result.total_iterations,
        agent_outputs={k: v.data for k, v in result.agent_outputs.items()},
        validation_xlsx_path=result.validation_xlsx_path
    )
