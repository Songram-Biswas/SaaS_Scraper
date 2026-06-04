from fastapi import APIRouter, HTTPException, Query
from app.services.extractor import MarkdownExtractor

router = APIRouter()
extractor = MarkdownExtractor()

@router.get("/extract")
async def extract_url(url: str = Query(..., description="The direct URL of the website to extract markdown from")):
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Invalid URL scheme. Must be http or https.")
        
    result = await extractor.extract(url)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result