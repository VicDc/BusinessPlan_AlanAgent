from fastapi import FastAPI
from app.api.v1.business_plan import router as business_plan_router
from app.api.v1.intake import router as intake_router
from app.api.v1.report import router as report_router
from app.api.v1.health import router as health_router

app = FastAPI(
    title="Business Plan AI",
    description="Sistema multi-agente per la creazione di business plan per SME italiane",
    version="1.0.0"
)

app.include_router(business_plan_router)
app.include_router(intake_router)
app.include_router(report_router)
app.include_router(health_router)
