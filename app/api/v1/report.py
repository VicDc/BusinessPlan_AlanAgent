import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.config.settings import settings

router = APIRouter(prefix="/api/v1/report", tags=["report"])


@router.get("/{plan_id}")
async def get_report(plan_id: str):
    filename = f"business_plan_{plan_id}.docx"
    file_path = Path(settings.OUTPUT_DIR) / "reports" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Report business_plan_{plan_id}.docx not found")
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )
