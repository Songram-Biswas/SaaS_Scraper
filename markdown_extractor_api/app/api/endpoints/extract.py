from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl
from typing import List, Dict
import uuid

from app.api.deps import validate_api_key
from app.core.database import get_db
from app.schemas.extraction import ExtractionRequest, ExtractionResponse
from app.services.extractor import MarkdownExtractor
from app.models.api_key import ApiKey

router = APIRouter()

batch_jobs: Dict[str, dict] = {}

class BatchExtractionRequest(BaseModel):
    urls: List[HttpUrl]

async def process_batch_job(job_id: str, urls: List[HttpUrl]):
    extractor = MarkdownExtractor()
    results = []
    for url in urls:
        res = await extractor.extract(str(url))
        results.append({"url": str(url), "result": res})
    
    batch_jobs[job_id]["status"] = "completed"
    batch_jobs[job_id]["results"] = results

@router.post("/extract", response_model=ExtractionResponse)
async def extract_markdown(
    payload: ExtractionRequest,
    db: AsyncSession = Depends(get_db),
    api_key_obj: ApiKey = Depends(validate_api_key)
):
    if api_key_obj.requests_used >= api_key_obj.request_limit:
        raise HTTPException(status_code=429, detail="Usage limit reached. Please upgrade your plan.")

    extractor = MarkdownExtractor()
    result = await extractor.extract(str(payload.url))

    if "error" in result:
        return {"status": "error", "markdown": result["error"]}

    api_key_obj.requests_used += 1
    await db.commit()

    return {"status": "success", "markdown": result["markdown"]}

@router.post("/extract/batch")
async def extract_markdown_batch(
    payload: BatchExtractionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    api_key_obj: ApiKey = Depends(validate_api_key)
):
    required_requests = len(payload.urls)
    if api_key_obj.requests_used + required_requests > api_key_obj.request_limit:
        raise HTTPException(status_code=429, detail="Batch request exceeds your remaining limit.")

    job_id = str(uuid.uuid4())
    batch_jobs[job_id] = {"status": "processing", "results": []}

    background_tasks.add_task(process_batch_job, job_id, payload.urls)

    api_key_obj.requests_used += required_requests
    await db.commit()

    return {"status": "accepted", "job_id": job_id, "message": "Batch processing started"}

@router.get("/extract/{job_id}/status")
async def get_batch_status(
    job_id: str,
    api_key_obj: ApiKey = Depends(validate_api_key)
):
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return batch_jobs[job_id]